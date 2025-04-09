from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Soumission, Exercice, Correction

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
    list_display = ('exercice', 'etudiant', 'date_soumission', 'get_score', 'en_retard')
    list_filter = ('en_retard', 'exercice__classe')
    search_fields = ('etudiant__email', 'exercice__titre')
    readonly_fields = ('date_soumission',)

    def get_score(self, obj):
        return obj.correction.note if hasattr(obj, 'correction') else None
    get_score.short_description = 'Score'

admin.site.register(Utilisateur, CustomUserAdmin)
admin.site.register(Soumission, SoumissionAdmin)
admin.site.register(Exercice)
admin.site.register(Correction)