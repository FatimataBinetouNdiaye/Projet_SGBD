import json
import re
import os
import subprocess
import tempfile
import requests
from celery import shared_task
from django.conf import settings
from traceback import extract_tb
from .models import Soumission, Correction
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(path: str) -> str:
    """Extrait le texte d'un PDF en conservant la mise en page"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        txt_path = tf.name

    try:
        subprocess.run(
            [r'D:\Release-24.08.0-0\poppler-24.08.0\Library\bin\pdftotext.exe', 
             '-layout', path, txt_path],
            check=True
        )
        with open(txt_path, encoding='utf-8') as f:
            return f.read()
    finally:
        os.remove(txt_path)

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
            "http://localhost:11434/api/generate",
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

def parse_ai_response(text: str) -> dict:
    """Parse la réponse texte en dictionnaire structuré"""
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
        result["note"] = float(result["note"]) if result["note"] else 0
    except (ValueError, TypeError):
        result["note"] = 0
    
    return result

def error_response(message: str) -> dict:
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
    retry_backoff=5,
    max_retries=3,
    time_limit=300,
    soft_time_limit=270,
    priority=6
)
def process_submission(self, soumission_id):
    """Version améliorée de la tâche de soumission"""
    try:
        with transaction.atomic():
            logger.info(f"Début traitement soumission {soumission_id}")
            
            soumission = Soumission.objects.select_for_update().get(id=soumission_id)
            
            if Correction.objects.filter(soumission=soumission).exists():
                logger.warning(f"Correction existante pour {soumission_id}")
                return {'status': 'duplicate'}

            result = call_deepseek_api(soumission.fichier_pdf.path)
            
            if not all([result.get("note"), result.get("feedback")]):
                logger.error("Réponse IA incomplète")
                raise ValueError("Réponse IA incomplète")

            Correction.objects.update_or_create(
                soumission=soumission,
                defaults={
                    'note': result["note"],
                    'feedback': result["feedback"],
                    'points_forts': result.get("points_forts", ""),
                    'points_faibles': result.get("points_faibles", ""),
                    'contenu_brut': result.get("raw", "")
                    
                }
            )
            
            logger.info(f"Soumission {soumission_id} traitée avec succès")
            return {'status': 'success', 'note': result["note"]}

    except SoftTimeLimitExceeded:
        logger.warning(f"Timeout sur la soumission {soumission_id}")
        return {'status': 'timeout'}
    except Soumission.DoesNotExist:
        logger.error(f"Soumission {soumission_id} introuvable")
        raise self.retry(countdown=60)
    except Exception as e:
        logger.error(f"Erreur traitement {soumission_id}: {str(e)}")
        raise self.retry(exc=e)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=10,
    max_retries=2
)
def verifier_statut_api():
    """Vérification améliorée du statut de l'API"""
    try:
        response = requests.get("http://localhost:11434/api/status", timeout=10)
        status = response.status_code
        
        if status == 200:
            logger.info("API disponible et fonctionnelle")
            return {'status': 'ok'}
        else:
            logger.warning(f"API retourne statut {status}")
            raise ValueError(f"Statut API: {status}")
            
    except Exception as e:
        logger.error(f"Erreur vérification API: {str(e)}")
        raise

def validate_sql_query(query: str) -> tuple:
    """
    Valide une requête SQL via l'API
    Retourne un tuple (bool, str)
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-coder:6.7b",
                "prompt": f"Valide cette requête SQL :\n{query}\nRéponds uniquement par 'VALID' ou 'INVALID: [raison]'",
                "stream": False
            },
            timeout=15
        )
        
        text = response.json().get("response", "").strip()
        if text.startswith("VALID"):
            return True, "Requête valide"
        else:
            return False, text.replace("INVALID:", "").strip()
            
    except Exception as e:
        return False, f"Erreur de validation : {str(e)}"
    
def get_ai_correction(fichier_pdf):
    """Wrapper pour compatibilité avec l'ancien code"""
    try:
        result = call_deepseek_api(fichier_pdf)
        return {
            'note': result.get("note", 0),
            'feedback': result.get("feedback", ""),
            'points_forts': result.get("points_forts", ""),
            'points_faibles': result.get("points_faibles", "")
        }
    except Exception as e:
        logger.error(f"Erreur dans get_ai_correction: {str(e)}")
        return {
            'note': 0,
            'feedback': f"Erreur de correction: {str(e)}",
            'points_forts': "",
            'points_faibles': ""
        }
