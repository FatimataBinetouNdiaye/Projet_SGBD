from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from gestion.views import CustomTokenObtainPairView
from django.urls import path
from .views import utilisateur_connecte  # ← Cette ligne est essentielle


router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'classes', views.ClasseViewSet)
router.register(r'exercices', views.ExerciceViewSet, basename='exercice')
router.register(r'soumissions', views.SoumissionViewSet, basename='soumission')
router.register(r'corrections', views.CorrectionViewSet, basename='correction')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.StatsView.as_view(), name='stats'),  # <-- Nouvelle route
    path('api/exercices/<int:exercice_id>/soumettre/', views.UploadSoumissionView.as_view(), name='upload-soumission'),
    path('api/auth/', include('rest_framework.urls')),
    path('api/student/dashboard/', views.student_dashboard_data, name='student_dashboard_data'),
    path('', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # urls.py
    path('api/utilisateur-connecte/', utilisateur_connecte),


]