# from django.db import models
# from django.core.validators import FileExtensionValidator
# from plateforme_eval.settings import MEDIA_URL

# class Exercice(models.Model):
#     professeur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
#     titre = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     fichier_pdf = models.FileField(upload_to='exercices/', validators=[FileExtensionValidator(['pdf'])])
#     date_creation = models.DateTimeField(auto_now_add=True)

# class Soumission(models.Model):
#     etudiant = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
#     exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
#     fichier_pdf = models.FileField(upload_to='soumissions/', validators=[FileExtensionValidator(['pdf'])])
#     note = models.FloatField(null=True, blank=True)
#     feedback = models.TextField(blank=True, null=True)
#     date_soumission = models.DateTimeField(auto_now_add=True)
