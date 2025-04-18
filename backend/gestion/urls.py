from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from gestion.views import CustomTokenObtainPairView
from .views import utilisateur_connecte  # ← Cette ligne est essentielle
from .views import GoogleSocialAuthView
from .views import student_dashboard_data

router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'classes', views.ClasseViewSet)
router.register(r'exercices', views.ExerciceViewSet, basename='exercice')
router.register(r'soumissions', views.SoumissionViewSet, basename='soumission')
router.register(r'corrections', views.CorrectionViewSet, basename='correction')


urlpatterns = [
    path('', lambda request: redirect('api/')),  # Redirige vers l'API ou une autre page
    path('api/', include(router.urls)),
    path('api/student/dashboard/', student_dashboard_data, name='student_dashboard'),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/utilisateur-connecte/', utilisateur_connecte),
    path('google-auth/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path('api/signup/', views.signup, name='signup'), 
    path('api/student/dashboard/', student_dashboard_data, name='student-dashboard'),

    
    
]