from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'classes', views.ClasseViewSet)
router.register(r'exercices', views.ExerciceViewSet, basename='exercice')
router.register(r'soumissions', views.SoumissionViewSet, basename='soumission')
router.register(r'corrections', views.CorrectionViewSet, basename='correction')


urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('exercices/<int:exercice_id>/soumettre/', views.UploadSoumissionView.as_view(), name='upload-soumission'),
    path('auth/', include('rest_framework.urls')),
   # path('auth/jwt/', include('rest_framework_simplejwt.urls')),
]
