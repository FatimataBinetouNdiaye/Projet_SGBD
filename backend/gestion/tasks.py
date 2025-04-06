from celery import shared_task
from .models import Soumission, Correction
from .utils import check_sql_syntax, generate_feedback
import ollama
import logging

# Logger pour les erreurs et les informations
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_submission(self, submission_id):
    """
    Tâche asynchrone pour traiter une soumission d'exercice, analyser la requête SQL
    et générer une correction avec feedback détaillé via Ollama et DeepSeek.
    """
    try:
        # Récupérer la soumission de l'étudiant
        submission = Soumission.objects.get(id=submission_id)
        student_solution = submission.fichier_pdf.read()  # Lire le contenu du PDF (ou l'extraire d'un autre format)

        # Connexion à Ollama et analyse avec DeepSeek
        model = ollama.create_model("deepseek-v1")  # Créer une instance de modèle DeepSeek
        result = model.process(student_solution)

        # Vérification syntaxique SQL et retour des erreurs
        sql_syntax_valid = check_sql_syntax(result)  # Fonction de validation SQL

        # Générer un feedback détaillé sur la réponse
        feedback = generate_feedback(result, sql_syntax_valid)

        # Attribuer une note basée sur l'analyse de la réponse (ici, simplifié)
        note = result.get("note", 10)  # Exemple, dans un cas réel, la note dépendra de plusieurs critères

        # Création d'une correction dans la base de données
        correction = Correction.objects.create(
            soumission=submission,
            note=note,
            feedback=feedback["feedback"],
            points_forts=feedback["points_forts"],
            points_faibles=feedback["points_faibles"],
            modele_ia_utilise="deepseek-v1",
            temps_correction=feedback["temps_execution"]
        )

        logger.info(f"Correction générée pour la soumission {submission_id} avec la note {note}/20")
        return correction.id

    except Soumission.DoesNotExist:
        logger.error(f"Soumission {submission_id} introuvable")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la soumission {submission_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)

