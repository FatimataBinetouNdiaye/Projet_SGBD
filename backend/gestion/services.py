from .ia_utils import corriger_soumission_avec_ia
from .models import Correction

def generer_correction_automatique(soumission):
    resultat = corriger_soumission_avec_ia(soumission)

    if resultat:
        correction = Correction.objects.create(
            soumission=soumission,
            note=resultat.get("note", 0),
            feedback=resultat.get("feedback", ""),
            points_forts=resultat.get("points_forts", ""),
            points_faibles=resultat.get("points_faibles", ""),
        )
        return correction

    return None
