from django.db import models

from django.core.validators import FileExtensionValidator
from plateforme_eval.settings import MEDIA_URL
from django.conf import settings
from django.contrib.auth.models import AbstractUser

MEDIA_URL = settings.MEDIA_URL
MEDIA_URL = settings.MEDIA_URL


class User(AbstractUser):  # Étend le modèle User de Django
    ROLE_CHOICES = [
        ('professeur', 'Professeur'),
        ('etudiant', 'Étudiant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    def __str__(self):
        return self.username

class Exercice(models.Model):
    professeur = models.ForeignKey('gestion.User', on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    fichier_pdf = models.FileField(upload_to='exercices/', validators=[FileExtensionValidator(['pdf'])])
    date_creation = models.DateTimeField(auto_now_add=True)

class Soumission(models.Model):
    etudiant = models.ForeignKey('gestion.User', on_delete=models.CASCADE)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    fichier_pdf = models.FileField(upload_to='soumissions/', validators=[FileExtensionValidator(['pdf'])])
    note = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
