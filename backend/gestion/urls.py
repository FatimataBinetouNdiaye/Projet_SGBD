from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciceViewSet, SoumissionViewSet

# Création du routeur DRF
router = DefaultRouter()
router.register(r'exercices', ExerciceViewSet)
router.register(r'soumissions', SoumissionViewSet)

# Définition des routes
urlpatterns = [
    # path('', api_root, name='api-root'),  # Page d'accueil de l'API
    # path('', include(router.urls)),  # Inclusion des routes DRF
    path('', include(router.urls)),  # Inclusion automatique des routes API

]



