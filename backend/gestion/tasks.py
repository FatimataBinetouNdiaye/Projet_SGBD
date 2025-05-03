import os
import re
import json
import time
import logging
import tempfile
import subprocess
from traceback import format_exc
from typing import Dict, List, Optional, Tuple

import requests
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Soumission, Correction
from .similarity import PlagiarismDetector

logger = logging.getLogger(__name__)
# Dans settings.py ou en haut de votre fichier tasks.py
OLLAMA_API_URL = "http://localhost:11434"
DEEPSEEK_API_URL = f"{OLLAMA_API_URL}/api/generate"  # Notez le /api/generate
# Configuration des constantes
MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
MIN_TEXT_LENGTH = 50
API_TIMEOUT = 30
PDF_EXTRACTION_TIMEOUT = 15

class PDFProcessingError(Exception):
    """Exception personnalisée pour les erreurs de traitement PDF"""
    pass

def extract_text_from_pdf(pdf_path: str, max_attempts: int = 3) -> str:
    """
    Version robuste de l'extraction de texte depuis un PDF avec gestion des erreurs améliorée.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        max_attempts: Nombre maximal de tentatives d'extraction
        
    Returns:
        Texte extrait
        
    Raises:
        PDFProcessingError: Si l'extraction échoue après plusieurs tentatives
    """
    def try_extraction(file_path: str) -> str:
        """Tente une extraction avec pdftotext"""
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', file_path, '-'],
                capture_output=True,
                text=True,
                timeout=PDF_EXTRACTION_TIMEOUT,
                check=True
            )
            text = result.stdout.strip()
            if text and len(text) >= MIN_TEXT_LENGTH:
                return text
            raise PDFProcessingError("Texte trop court ou vide")
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout pdftotext pour {file_path}")
            raise
        except subprocess.CalledProcessError as e:
            logger.warning(f"Échec pdftotext (code {e.returncode}): {e.stderr}")
            raise

    # Vérification initiale du fichier
    if not os.path.exists(pdf_path):
        raise PDFProcessingError(f"Fichier {pdf_path} introuvable")
    
    if os.path.getsize(pdf_path) == 0:
        raise PDFProcessingError("Fichier PDF vide")

    # Tentative principale avec pdftotext
    for attempt in range(max_attempts):
        try:
            return try_extraction(pdf_path)
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Échec extraction après {max_attempts} tentatives")
                raise PDFProcessingError(f"Échec extraction: {str(e)}")
            
            time.sleep(1)  # Attente avant nouvelle tentative
            logger.info(f"Nouvelle tentative d'extraction ({attempt + 1}/{max_attempts})")

    # Fallback avec extraction brute si pdftotext échoue
    try:
        with open(pdf_path, 'rb') as f:
            return f.read().decode('latin-1', errors='ignore')[:50000]
    except Exception as e:
        logger.error(f"Échec extraction brute: {str(e)}")
        raise PDFProcessingError("Aucune méthode d'extraction n'a fonctionné")

def call_deepseek_api(pdf_path: str) -> dict:
    """
    Fonction principale pour appeler l'API de correction
    Retourne un dictionnaire structuré avec les résultats
    """
    texte = extract_text_from_pdf(pdf_path)
    if not texte.strip():
        raise RuntimeError("Le PDF ne contient aucun texte exploitable")
    
    texte = texte[:4000].strip()

    prompt = f"""
Tu es un correcteur automatique d’exercices SQL. Réponds UNIQUEMENT dans le format STRICT suivant :

Note : [x]/20
Feedback : [commentaire concis sur la qualité globale]
Points forts : [liste des qualités, séparées par des virgules]
Points faibles : [liste des défauts, séparées par des virgules]

--- Exemple ---
Note : 17/20
Feedback : Bonne maîtrise globale mais quelques imprécisions
Points forts : Bonne structuration, compréhension des jointures
Points faibles : Syntaxe parfois imprécise, peu de commentaires
--- Fin ---

Corrige ce texte :

{texte}

NE DONNE AUCUNE AUTRE INFORMATION EN DEHORS DU FORMAT PRÉCIS CI-DESSUS.
"""

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": prompt,
                "stream": False
            },
            timeout=390
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "").strip()
        
        return parse_ai_response(text)
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur API : {e}")
        return error_response("Erreur de connexion à l'API")
    except json.JSONDecodeError:
        print("Erreur JSON : réponse brute =", response.text)
        return error_response("Réponse API invalide")

def parse_ai_response(text: str) -> Dict:
    """Parse la réponse de l'API en dictionnaire structuré"""
    patterns = {
        "note": r"Note\s*:\s*(\d+\.?\d*)(?:\s*/\s*20)?",
        "feedback": r"Feedback\s*:\s*(.+?)(?=\nPoints forts|$)",
        "points_forts": r"Points forts\s*:\s*(.+?)(?=\nPoints faibles|$)",
        "points_faibles": r"Points faibles\s*:\s*(.+)"
    }
    
    result = {"raw": text}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        result[key] = match.group(1).strip() if match else None
    
    try:
        result["note"] = min(20, max(0, float(result["note"]))) if result["note"] else 0
    except (ValueError, TypeError):
        result["note"] = 0
    
    return result

def error_response(message: str) -> Dict:
    """Génère une réponse d'erreur standard"""
    return {
        "note": 0,
        "feedback": message,
        "points_forts": "",
        "points_faibles": "",
        "raw": ""
    }

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    time_limit=600,
    soft_time_limit=550,
    priority=6
)
def process_submission(self, soumission_id: int) -> Dict:
    """
    Traite une soumission complète avec :
    - Gestion robuste des fichiers Minio
    - Extraction sécurisée du texte PDF
    - Correction automatique
    - Détection de plagiat
    - Gestion des erreurs complète
    """
    # Configuration avec valeurs par défaut
    DEFAULT_THRESHOLD = 0.75
    DEFAULT_MIN_LENGTH = 50
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB

    try:
        with transaction.atomic():
            # 1. Récupération de la soumission
            try:
                soumission = Soumission.objects.select_for_update().get(id=soumission_id)
                logger.info(f"Début traitement soumission {soumission_id} - Fichier: {soumission.fichier_pdf.name}")
            except Soumission.DoesNotExist:
                logger.error(f"Soumission {soumission_id} introuvable")
                return {'status': 'error', 'message': 'Soumission introuvable'}

            # 2. Vérification doublon
            if Correction.objects.filter(soumission=soumission).exists():
                logger.warning(f"Correction existante pour {soumission_id}")
                return {'status': 'duplicate'}

            # 3. Configuration du détecteur avec fallback
            detector = PlagiarismDetector(min_text_length=30)


            # 4. Environnement temporaire sécurisé
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, f"sub_{soumission_id}.pdf")
                
                # 5. Téléchargement depuis Minio avec vérifications
                try:
                    # Vérification existence
                    if not default_storage.exists(soumission.fichier_pdf.name):
                        raise FileNotFoundError(f"Fichier {soumission.fichier_pdf.name} introuvable dans Minio")

                    # Vérification taille
                    file_size = default_storage.size(soumission.fichier_pdf.name)
                    if file_size > MAX_PDF_SIZE:
                        raise ValueError(f"Fichier trop volumineux ({file_size} octets > {MAX_PDF_SIZE} octets max)")

                    # Téléchargement sécurisé
                    with default_storage.open(soumission.fichier_pdf.name, 'rb') as minio_file:
                        with open(pdf_path, 'wb') as local_file:
                            for chunk in minio_file.chunks():
                                local_file.write(chunk)
                            os.fsync(local_file.fileno())  # Synchronisation disque

                    # Vérification finale
                    if os.path.getsize(pdf_path) == 0:
                        raise ValueError("Fichier PDF vide après téléchargement")

                except Exception as e:
                    logger.error(f"Erreur téléchargement Minio: {str(e)}")
                    raise PDFProcessingError(f"Erreur fichier: {str(e)}")

                # 6. Extraction du texte avec gestion d'erreur
                try:
                    texte = extract_text_from_pdf(pdf_path)
                    if not texte or len(texte.strip()) < getattr(settings, 'MIN_TEXT_LENGTH', DEFAULT_MIN_LENGTH):
                        raise ValueError("Texte non extractible ou trop court")
                except Exception as e:
                    logger.error(f"Échec extraction texte: {str(e)}")
                    raise

                # 7. Correction automatique
                try:
                    correction_data = call_deepseek_api(pdf_path)
                    if not correction_data or 'note' not in correction_data:
                        raise ValueError("Réponse de correction invalide")
                except Exception as e:
                    logger.error(f"Échec correction automatique: {str(e)}")
                    raise

                # 8. Détection de plagiat
                comparisons = []
                plagiarism_cases = []
                
                autres_soumissions = Soumission.objects.filter(
                    exercice=soumission.exercice,
                    date_soumission__lt=soumission.date_soumission
                ).exclude(id=soumission.id).select_related('etudiant')[:100]

                for autre in autres_soumissions:
                    try:
                        with tempfile.NamedTemporaryFile(dir=temp_dir, suffix='.pdf', delete=False) as tmp_file:
                            # Téléchargement depuis Minio
                            with default_storage.open(autre.fichier_pdf.name, 'rb') as minio_file:
                                for chunk in minio_file.chunks():
                                    tmp_file.write(chunk)
                                tmp_file.flush()
                                os.fsync(tmp_file.fileno())
                            
                            # Extraction et comparaison
                            autre_text = extract_text_from_pdf(tmp_file.name)
                            if autre_text and len(autre_text.strip()) >= getattr(settings, 'MIN_TEXT_LENGTH', DEFAULT_MIN_LENGTH):
                                similarity_score = detector.compare_texts(texte, autre_text)
                                comparison = {
                                    'submission_id': autre.id,
                                    'student_id': autre.etudiant.id,
                                    'student_name': str(autre.etudiant),
                                    'similarity_score': similarity_score,  # Utilise directement le float
                                    'is_plagiarism': similarity_score >= detector.threshold,  # Condition basée sur le score
                                    'date': autre.date_soumission.isoformat()
                                }

                                comparisons.append(comparison)
                                
                                if comparison['is_plagiarism']:
                                    plagiarism_cases.append(comparison)
                    except Exception as e:
                        logger.warning(f"Erreur comparaison {autre.id}: {str(e)}")
                        continue
                    finally:
                        try:
                            os.unlink(tmp_file.name)
                        except:
                            pass

                # 9. Préparation des résultats
                max_similarity = max([c['similarity_score'] for c in comparisons]) if comparisons else 0.0
                has_plagiarism = any([c['is_plagiarism'] for c in comparisons])

                # 10. Sauvegarde en base
                correction = Correction.objects.create(
                    soumission=soumission,
                    note=float(correction_data['note']),
                    feedback=correction_data.get('feedback', '')[:2000],
                    est_plagiat=has_plagiarism,
                    points_forts=correction_data.get('points_forts', '')[:1000],
                    points_faibles=correction_data.get('points_faibles', '')[:1000],
                    contenu_brut=texte[:10000],
                    plagiarism_report={
                        'cases': plagiarism_cases,
                        'summary': {
                            'max_similarity': float(max_similarity),
                            'plagiarism_count': len(plagiarism_cases),
                            'threshold': detector.threshold
                        }
                    },
                    plagiarism_score=float(max_similarity),
                    modele_ia_utilise='deepseek-coder:6.7b'
                )

                # 11. Mise à jour soumission si plagiat
                if has_plagiarism:
                    soumission.est_plagiat = True
                    soumission.score_plagiat = max_similarity
                    soumission.save(update_fields=['est_plagiat', 'score_plagiat'])

                logger.info(f"Traitement réussi {soumission_id} - Note: {correction.note} - Plagiat: {has_plagiarism}")
                return {
                    'status': 'success',
                    'correction_id': correction.id,
                    'note': correction.note,
                    'plagiarism_detected': has_plagiarism,
                    'plagiarism_score': max_similarity
                }

    except Exception as e:
        logger.error(f"Échec traitement {soumission_id}:\n{format_exc()}")
        try:
            Correction.objects.update_or_create(
                soumission_id=soumission_id,
                defaults={
                    'note': 0,
                    'feedback': f"Erreur traitement: {str(e)[:500]}",
                    'est_plagiat': False,
                    'plagiarism_report': {
                        'error': str(e),
                        'trace': format_exc()
                    }
                }
            )
        except Exception as db_error:
            logger.error(f"Échec sauvegarde erreur: {str(db_error)}")

        if self.request.retries >= self.max_retries:
            raise MaxRetriesExceededError(f"Échec après {self.max_retries} tentatives")
        raise self.retry(exc=e, countdown=min(60 * (self.request.retries + 1), 300))
        # Après avoir obtenu les résultats de plagiat

# Fonctions utilitaires supplémentaires
def verifier_statut_api() -> Dict:
    """Vérifie le statut de l'API DeepSeek"""
    try:
        response = requests.get(
            f"{settings.DEEPSEEK_API_URL}/status", 
            timeout=10
        )
        response.raise_for_status()
        return {'status': 'ok', 'response': response.json()}
    except Exception as e:
        logger.error(f"Erreur vérification API: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    Valide une requête SQL via l'API
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        response = requests.post(
            f"{settings.DEEPSEEK_API_URL}/generate",
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": f"Valide cette requête SQL :\n{query}\nRéponds par 'VALID' ou 'INVALID: [raison]'",
                "stream": False
            },
            timeout=15
        )
        text = response.json().get("response", "").strip()
        return (True, "Valide") if text.startswith("VALID") else (False, text[8:])
    except Exception as e:
        return False, f"Erreur de validation: {str(e)}"

def get_ai_correction(file_obj) -> Dict:
    """
    Wrapper pour obtenir une correction depuis un objet fichier
    Args:
        file_obj: Objet fichier (Django FileField ou similaire)
    Returns:
        Résultats de la correction
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp_file:
            file_obj.download(tmp_file.name)
            return call_deepseek_api(tmp_file.name)
    except Exception as e:
        logger.error(f"Erreur get_ai_correction: {str(e)}")
        return error_response(f"Erreur interne: {str(e)}")