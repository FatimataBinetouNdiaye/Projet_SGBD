from django.db.models import Avg, Count
from .models import Soumission

def statistiques():
    stats = Soumission.objects.aggregate(
        moyenne_note=Avg('note'),
        nombre_soumissions=Count('id')
    )
    return stats
