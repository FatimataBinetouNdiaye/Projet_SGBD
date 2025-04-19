from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_eval.settings')
django.setup()

# Créer l'app Celery
app = Celery('plateforme_eval')

# Charger la configuration depuis settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Windows : éviter les erreurs de multiprocessing
app.conf.worker_pool = 'solo'

# Découverte automatique des tâches dans INSTALLED_APPS
app.autodiscover_tasks()

# (facultatif) tâche de test
@app.task(bind=True)
def debug_task(self):
    print(f'Requête reçue : {self.request}')
