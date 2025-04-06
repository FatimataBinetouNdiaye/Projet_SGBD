from django.contrib.auth.backends import ModelBackend
from gestion.models import Utilisateur

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Utilisateur.objects.get(email=email)
            if user.check_password(password):
                return user
        except Utilisateur.DoesNotExist:
            return None
