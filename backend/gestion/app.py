from django.apps import AppConfig

class GestionConfig(AppConfig):
    name = 'gestion'

    def ready(self):
        import gestion.signals  # 👈 important pour que les signaux soient enregistrés
