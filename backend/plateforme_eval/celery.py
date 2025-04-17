from __future__ import absolute_import, unicode_literals
import os
from celery import Celery




# Assure-toi que Django est configuré avant d'initialiser Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_eval.settings')

# Créer l'application Celery
app = Celery('plateforme_eval')

# Utiliser Redis comme broker
app.config_from_object('django.conf:settings', namespace='CELERY')

# Spécifier le broker Redis
app.conf.broker_url = 'redis://localhost:6379/0'  # Assure-toi que Redis est bien sur ce port

# Découvrir les tâches automatiquement dans les applications Django installées
app.autodiscover_tasks()

# Tester la configuration
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))