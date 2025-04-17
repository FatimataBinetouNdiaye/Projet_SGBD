from celery import shared_task
from django.forms import ValidationError
from .models import Soumission, Correction
import time
import logging
import requests


logger = logging.getLogger(__name__)


@shared_task
def test_task():
    print("La tâche Celery fonctionne!")


@shared_task(bind=True)
def process_submission(self, submission_id):
    """
    Tâche Celery pour traiter une soumission étudiant de manière asynchrone
    avec l'intégration de DeepSeek via Ollama pour la correction.
    """
    try:
        # Obtenez la soumission de la base de données
        submission = Soumission.objects.get(id=submission_id)
        logger.info(f"Début du traitement de la soumission {submission_id}")

        # Vérifier si un fichier est bien soumis
        if not submission.fichier_pdf:
            raise ValidationError("Aucun fichier PDF soumis")
        
        # URL et clé d'API pour DeepSeek
        url = "https://api.deepseek.com/correct"
        headers = {
            "Authorization": "Bearer sk-a933d53d12854201a5f78f6ef19df0af"
        }
        data = {
            "file": submission.fichier_pdf.path  # Envoi du chemin du fichier PDF
        }

        # Appel à l'API DeepSeek pour la correction
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            logger.info("Correction réussie")

            # Récupérer les données de la réponse de l'API
            correction_data = response.json()
            note = correction_data['note']
            feedback = correction_data['feedback']

            # Créer une correction dans la base de données
            correction = Correction.objects.create(
                soumission=submission,
                note=note,
                feedback=feedback,
                modele_ia_utilise="deepseek-v1",
                temps_correction=correction_data.get('temps_execution', 0)
            )
            
            logger.info(f"Correction créée pour la soumission {submission_id}")
            return correction.id
        else:
            logger.error(f"Erreur lors de l'appel API : {response.status_code} {response.text}")
            raise Exception(f"API call failed with status {response.status_code}")
        
    except Soumission.DoesNotExist:
        logger.error(f"Soumission {submission_id} introuvable")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la soumission {submission_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    
def call_deepseek_api(file_path):
    """
    Appel à l'API DeepSeek pour corriger la soumission et générer une note intelligente.
    Cette fonction prend en compte différentes approches possibles pour résoudre l'exercice.
    """
    url = "https://api.deepseek.com/correct"  # Assurez-vous que cette URL est correcte
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',  # Remplacez par votre clé API
        'Content-Type': 'application/json'
    }

    # Charger le fichier à envoyer dans la requête
    data = {
        'file': file_path  # Remplacez avec le chemin du fichier PDF
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        # Traitez la réponse de l'API
        api_data = response.json()  # Supposons que l'API renvoie une réponse JSON

        return api_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel à l'API : {e}")
        raise Exception("Erreur lors de l'appel à l'API de correction")



def external_api_call(file_path):
    url = "https://api.deepseek.com/correct"  # URL de l'API que tu utilises
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',  # Remplace par ta clé API
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

def call_deepseek_correction(file_path):
    """
    Appel à l'API DeepSeek pour corriger la soumission et générer une note intelligente.
    Cette fonction prend en compte différentes approches possibles pour résoudre l'exercice.
    """
    # Logique pour appeler l'API et obtenir la correction
    response = external_api_call(file_path)  # Remplace par l'appel réel à l'API
    note = response['note']
    feedback = response['feedback']
    
    # Calculer la note basée sur plusieurs solutions possibles
    intelligent_note = calculate_intelligent_grade(note, feedback)
    return {'note': intelligent_note, 'feedback': feedback, 'temps_execution': response['temps_execution']}

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
    url = "https://api.sql-validator.com/validate"  # Remplace par l'URL réelle de l'API
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',  # Remplace par ta clé API réelle
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
