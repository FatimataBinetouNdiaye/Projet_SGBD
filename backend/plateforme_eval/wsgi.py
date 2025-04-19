"""
WSGI config for plateforme_eval project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import os
import sys

# Ajoute le répertoire racine à sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_eval.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
