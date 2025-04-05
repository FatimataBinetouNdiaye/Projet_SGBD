from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import  UserRegisterView, login_view
from . import views


router = DefaultRouter()
router.register(r'classes', views.ClasseViewSet)
router.register(r'exercices', views.ExerciceViewSet, basename='exercice')
router.register(r'soumissions', views.SoumissionViewSet, basename='soumission')
router.register(r'corrections', views.CorrectionViewSet, basename='correction')

urlpatterns = [
    path('', include(router.urls)),  # Routes API existantes
    path('signup/', UserRegisterView.as_view(), name='signup'),  # Route pour l'inscription
    path('login/', login_view, name='login'),
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('exercices/<int:exercice_id>/soumettre/', views.UploadSoumissionView.as_view(), name='upload-soumission'),

]


