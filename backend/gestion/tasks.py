import json
from traceback import extract_tb
from celery import shared_task
from django.conf import settings
import re


import requests

from .models import Soumission, Correction
import requests

import subprocess, tempfile, os

def extract_text_from_pdf(path: str) -> str:
    # crée un .txt temporaire
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        txt_path = tf.name
    try:
        # -layout préserve un peu la mise en page
        subprocess.run(['pdftotext', '-layout', path, txt_path], check=True)
        return open(txt_path, encoding='utf-8').read()
    finally:
        os.remove(txt_path)
        
        

def call_deepseek_api(pdf_path: str) -> dict:
    texte = extract_text_from_pdf(pdf_path)

    if not texte.strip():
        raise RuntimeError("Le PDF ne contient aucun texte exploitable.")

    texte = texte[:4000]

    prompt = (
        "Tu es un correcteur automatique.\n"
        "Tu DOIS répondre uniquement dans CE FORMAT EXACT (pas d'autres mots) :\n\n"
        "Note : <nombre>/20\n"
        "Feedback : <une phrase claire sur les erreurs ou réussites>\n"
        "Points forts : <liste ou texte court>\n"
        "Points faibles : <liste ou texte court>\n\n"
        "=== TRAVAIL ÉTUDIANT ===\n"
        f"{texte}\n"
        "=== FIN DU TRAVAIL ÉTUDIANT ===\n\n"
        "Ne commence PAS ta réponse par <think> ou autre réflexion. Écris directement :\n"
        "Note :"
    )


    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": prompt,
        "stream": False
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=(10, 600))
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur API : {e}")
        return {"error": str(e)}
    except json.JSONDecodeError:
        print("Erreur JSON : réponse brute =", resp.text)
        return {"error": "Réponse JSON invalide", "raw_response": resp.text}

    text = data.get("response", "").strip()
    if not text:
        return {"error": "Réponse vide", "raw_response": data}

    result = {
        "note": None,
        "feedback": None,
        "points_forts": None,
        "points_faibles": None
    }

    note_match = re.search(r"Note\s*[:\-–]?\s*(\d+(?:\.\d+)?)(?:\s*/\s*20)?", text, re.IGNORECASE)
    if note_match:
        result["note"] = float(note_match.group(1))

    feedback_match = re.search(r"Feedback\s*[:\-–]?\s*(.+?)(?=Points forts|Points faibles|$)", text, re.IGNORECASE | re.DOTALL)
    if feedback_match:
        result["feedback"] = feedback_match.group(1).strip()

    pf_match = re.search(r"Points forts\s*[:\-–]?\s*(.+?)(?=Points faibles|$)", text, re.IGNORECASE | re.DOTALL)
    if pf_match:
        result["points_forts"] = pf_match.group(1).strip()

    pfb_match = re.search(r"Points faibles\s*[:\-–]?\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    if pfb_match:
        result["points_faibles"] = pfb_match.group(1).strip()

    # Cas : IA a répondu mais pas dans le bon format
    if not result["note"] and "note" in text.lower():
        result["raw"] = text
        print("Format non conforme, contenu brut stocké.")

    return result

@shared_task(bind=True)
def process_submission(self, soumission_id):
    from gestion.models import Soumission, Correction

    try:
        soumission = Soumission.objects.get(id=soumission_id)
    except Soumission.DoesNotExist:
        print(f"Soumission {soumission_id} introuvable.")
        return

    # 🔒 Vérifier si une correction existe déjà
    if Correction.objects.filter(soumission=soumission).exists():
        print(f"Correction déjà existante pour la soumission {soumission_id}.")
        return

    # 🧠 Appel à l'IA
    raw = call_deepseek_api(soumission.fichier_pdf.path)

    # 🔎 Vérifie si tous les champs sont bien extraits, sinon indique que le format est incorrect
    note = raw.get("note")
    feedback = raw.get("feedback")
    points_forts = raw.get("points_forts")
    points_faibles = raw.get("points_faibles")
    raw_text = raw.get("raw")

    if not all([note, feedback, points_forts, points_faibles]):
        feedback = "⚠️ Format de la réponse IA non conforme. Voir champ brut."
        points_forts = points_forts or ""
        points_faibles = points_faibles or ""

    # 💾 Enregistrement sécurisé
    Correction.objects.create(
        soumission=soumission,
        note=note or 0,
        feedback=feedback,
        points_forts=points_forts,
        points_faibles=points_faibles,
        modele_ia_utilise='DeepSeek-Ollama',
        contenu_brut=raw_text or ""
    )




def external_api_call(file_path):
    url = "http://localhost:11434/"  # URL de l'API que tu utilises
    headers = {
        'Authorization': 'Bearer id_ed25519.pub',  # Remplace par ta clé API
        'Content-Type': 'application/json'
    }

    files = {'file': open(file_path, 'rb')}  # Ouvre le fichier PDF pour l'envoyer

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()  # Lève une exception si la requête échoue

        api_data = response.json()  # Supposons que l'API renvoie un JSON avec 'note' et 'feedback'
        
        files['file'].close()
        return api_data

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel API : {e}")
        raise




def validate_sql_query(query):
    """
    Valide la syntaxe d'une requête SQL à l'aide de l'IA (DeepSeek via Ollama).
    """
    try:
        # Appel à l'API de validation SQL (DeepSeek ou Ollama)
        valid_syntax = call_sql_validation_api(query)  # Remplacer par l'appel réel à l'API
        
        if valid_syntax['valid']:
            return True, "La requête SQL est valide."
        else:
            return False, f"Erreur de syntaxe : {valid_syntax['error_message']}"

    except Exception as e:
        # Gérer les erreurs d'appel d'API ou autres exceptions
        return False, f"Erreur lors de la validation de la requête SQL : {str(e)}"


    
def calculate_intelligent_grade(note, feedback):
    """
    Calcule une note intelligente en fonction de la note de l'IA et des erreurs identifiées dans le feedback.
    Tu peux affiner cette logique selon tes besoins.
    """
    # Exemple simple : ajuster la note en fonction de la qualité du feedback
    if 'correct' in feedback.lower():
        note += 2  # Augmenter la note si le feedback est positif
    elif 'improvement' in feedback.lower():
        note -= 1  # Diminuer la note si des améliorations sont suggérées
    return min(max(note, 0), 20)  # Assurer que la note est entre 0 et 20

def call_sql_validation_api(query):
    """
    Valide la syntaxe d'une requête SQL à l'aide d'une API externe (par exemple, DeepSeek ou Ollama).
    """
    # Exemple d'appel à l'API de validation SQL
    url = "http://localhost:11434/"  # Remplace par l'URL réelle de l'API
    headers = {
        'Authorization': 'Bearer id_ed25519.pub',  # Remplace par ta clé API réelle
        'Content-Type': 'application/json'
    }
    data = {"query": query}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lève une exception si la requête échoue
        api_data = response.json()  # Supposons que l'API renvoie un JSON avec 'valid' et 'error_message'
        return api_data
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs d'appel API
        print(f"Erreur lors de l'appel API pour la validation SQL : {e}")
        raise





# utils.py ou services.py dans ton dossier d'application


def get_ai_correction(fichier_pdf):
    """
    Fonction pour envoyer un fichier PDF à l'API Ollama pour obtenir une correction IA.

    :param fichier_pdf: Le fichier PDF à corriger (soumission de l'étudiant)
    :return: Un dictionnaire avec les résultats de la correction (note, feedback, points forts, points faibles)
    """
    ollama_url = "http://localhost:11434/"  # Assure-toi que c'est bien l'URL de ton API locale
    headers = {
        "Authorization": f"Bearer {settings.OLLAMA_API_KEY}"  # Utilisation de ta clé API Ollama
    }

    # Ouvre le fichier PDF et l'envoie à l'API
    with open(fichier_pdf, 'rb') as f:
        files = {'file': f}
        response = requests.post(ollama_url, headers=headers, files=files)

    # Vérifier que la requête a réussi
    if response.status_code == 200:
        # Analyser la réponse de l'API et la retourner
        correction_data = response.json()
        return {
            'note': correction_data.get('note'),
            'feedback': correction_data.get('feedback'),
            'points_forts': correction_data.get('points_forts'),
            'points_faibles': correction_data.get('points_faibles')
        }
    else:
        raise Exception(f"Erreur lors de la correction par l'IA : {response.text}")
