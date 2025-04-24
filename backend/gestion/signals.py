from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Soumission
from .services import generer_correction_automatique

@receiver(post_save, sender=Soumission)
def corriger_soumission_auto(sender, instance, created, **kwargs):
    if created:
        print(f"Nouvelle soumission détectée : {instance.id}")
        generer_correction_automatique(instance)
