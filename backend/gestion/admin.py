from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Soumission, Exercice, Correction
from django.http import HttpResponse
from .tasks import process_submission  # Importer la tâche Celery qui traite la soumission

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    ordering = ('email',)  # Changé de 'username' à 'email'
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'matricule')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),  
    )

class SoumissionAdmin(admin.ModelAdmin):
    list_display = ('exercice', 'etudiant', 'date_soumission', 'get_score', 'en_retard', 'correction_status')
    list_filter = ('en_retard', 'exercice__classe')
    search_fields = ('etudiant__email', 'exercice__titre')
    readonly_fields = ('date_soumission',)

    # Méthode pour récupérer la note de la correction IA
    def get_score(self, obj):
        return obj.correction.note if hasattr(obj, 'correction') else None
    get_score.short_description = 'Score'

    # Méthode pour afficher le statut de la correction
    def correction_status(self, obj):
        if hasattr(obj, 'correction'):
            return 'Corrigé' if obj.correction.est_validee else 'En attente'
        return 'Non corrigé'
    correction_status.short_description = 'Statut de la correction'

    # Action pour générer la correction IA
    def generate_ia_correction(self, request, queryset):
        for soumission in queryset:
            # Lancer la tâche Celery pour la correction automatique de l'IA
            process_submission.delay(soumission.id)  # Utiliser Celery pour le traitement asynchrone
        self.message_user(request, "Corrections générées avec succès pour les soumissions sélectionnées.")

    # Ajouter l'action à l'admin
    generate_ia_correction.short_description = "Générer correction IA pour la soumission"
    actions = [generate_ia_correction]

admin.site.register(Utilisateur, CustomUserAdmin)
admin.site.register(Soumission, SoumissionAdmin)
admin.site.register(Exercice)
admin.site.register(Correction)
