from celery import shared_task
from .models import Soumission, Correction
import time
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_submission(self, submission_id):
    """
    Tâche Celery pour traiter une soumission étudiant de manière asynchrone
    """
    try:
        submission = Soumission.objects.get(id=submission_id)
        logger.info(f"Début du traitement de la soumission {submission_id}")
        
        # Simulation de traitement - remplacer par votre logique IA réelle
        # Cette partie devrait appeler votre modèle DeepSeek via Ollama
        time.sleep(5)  # Simulation du temps de traitement
        
        # Exemple de résultat de correction
        correction_data = {
            'note': 15 + (submission_id % 5),  # Note aléatoire pour l'exemple
            'feedback': "Votre solution est globalement bonne mais pourrait être améliorée...",
            'temps_execution': 5.2
        }
        
        # Création de l'objet Correction
        correction = Correction.objects.create(
            soumission=submission,
            note=correction_data['note'],
            feedback=correction_data['feedback'],
            modele_ia_utilise="deepseek-v1",
            temps_correction=correction_data['temps_execution']
        )
        
        logger.info(f"Correction créée pour la soumission {submission_id}")
        return correction.id
        
    except Soumission.DoesNotExist:
        logger.error(f"Soumission {submission_id} introuvable")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la soumission {submission_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)