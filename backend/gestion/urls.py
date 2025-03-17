from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciceViewSet, SoumissionViewSet, UserViewSet

router = DefaultRouter()
router.register(r'exercices', ExerciceViewSet)
router.register(r'soumissions', SoumissionViewSet)
router.register(r'users', UserViewSet)  # 📌 Nouvelle route API pour récupérer les utilisateurs

urlpatterns = [
    path('', include(router.urls)),  # Inclusion des routes API
]
