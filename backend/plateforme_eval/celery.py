from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery, signals
from django.conf import settings

# Configuration du logger
logger = logging.getLogger(__name__)

# Initialisation Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_eval.settings')

# Création de l'application Celery
app = Celery('plateforme_eval')

# Configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuration spécifique pour Windows
if os.name == 'nt':
    app.conf.worker_pool = 'solo'
    app.conf.worker_concurrency = 1

# Configuration optimisée pour vos tâches
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=300000,  # 300MB
)

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'verification-api-periodique': {
        'task': 'gestion.tasks.verifier_statut_api',
        'schedule': 900.0,  # Toutes les 15 minutes
    },
}

@signals.worker_ready.connect
def setup_worker(sender=None, **kwargs):
    logger.info("Worker Celery prêt à recevoir des tâches")

@signals.task_prerun.connect
def task_prerun(task_id, task, **kwargs):
    logger.info(f"Début traitement tâche {task_id} - {task.name}")

@signals.task_postrun.connect
def task_postrun(task_id, task, **kwargs):
    logger.info(f"Fin traitement tâche {task_id}")

# Découverte automatique des tâches
app.autodiscover_tasks()

# Tâche de test
@app.task(bind=True)
def debug_task(self):
    logger.info(f"Tâche test exécutée - ID: {self.request.id}")
    return {'status': 'success'}