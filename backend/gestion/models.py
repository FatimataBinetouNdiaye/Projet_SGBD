from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class User(AbstractUser):  # Étend le modèle User de Django
    ROLE_CHOICES = [
        ('professeur', 'Professeur'),
        ('etudiant', 'Étudiant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    def __str__(self):
        return self.username

class Exercice(models.Model):
    professeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    fichier_pdf = models.FileField(upload_to='exercices/', validators=[FileExtensionValidator(['pdf'])])
    date_creation = models.DateTimeField(auto_now_add=True)

class Soumission(models.Model):
    etudiant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    fichier_pdf = models.FileField(upload_to='soumissions/', validators=[FileExtensionValidator(['pdf'])])
    note = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    date_soumission = models.DateTimeField(auto_now_add=True)

# 📌 Ajouter un professeur et un étudiant par défaut après migration
@receiver(post_migrate)
def create_default_users(sender, **kwargs):
    if sender.name == "gestion":  # Vérifie que ça s'exécute pour l'app gestion
        User = sender.get_model("User")

        if not User.objects.filter(username="prof1").exists():
            prof = User.objects.create_user(username="prof1", password="password123", role="professeur")
            prof.save()
            print("✅ Professeur 'prof1' ajouté avec succès !")

        if not User.objects.filter(username="etudiant1").exists():
            etudiant = User.objects.create_user(username="etudiant1", password="password123", role="etudiant")
            etudiant.save()
            print("✅ Étudiant 'etudiant1' ajouté avec succès !")
