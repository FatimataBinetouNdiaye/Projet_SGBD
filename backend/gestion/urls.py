from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from gestion.views import CustomTokenObtainPairView
from .views import process_ai_correction, utilisateur_connecte  # ← Cette ligne est essentielle
from .views import GoogleSocialAuthView
from .views import student_dashboard_data
from .views import ExerciceListView,  professor_classes_list, student_submissions, get_submission_pdf,CurrentProfessorView


router = DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'classes', views.ClasseViewSet)
router.register(r'exercices', views.ExerciceViewSet, basename='exercice')
router.register(r'soumissions', views.SoumissionViewSet, basename='soumission')
router.register(r'corrections', views.CorrectionViewSet, basename='correction')

urlpatterns = [
    path('', lambda request: redirect('api/')),
    path('api/', include(router.urls)),

    # endpoints “classiques” (fonction-based ou APIView)
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.StatsView.as_view(), name='stats'),
    path('api/student/dashboard/', views.student_dashboard_data, name='student_dashboard_data'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/utilisateur-connecte/', utilisateur_connecte, name='utilisateur_connecte'),
    path('api/signup/', views.signup, name='signup'),
    path('google-auth/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path('api/feedback/<int:correction_id>/', views.update_feedback, name='update_feedback'),
    path('ollama/models/', views.get_models, name='get_models'),
    path('api/correction/<int:soumission_id>/', views.process_ai_correction, name='process_ai_correction'),
    path('api/generate/<int:soumission_id>/', process_ai_correction, name='generate_correction'),
    path('api/generate/', views.generate_without_id, name='generate_no_id'),
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.StatsView.as_view(), name='stats'),
    path('api/exercices/list/', ExerciceListView.as_view(), name='exercice-list'),
    path('api/professor/classes/', professor_classes_list, name='professor-classes-list'),
    path('api/professor/students/<int:student_id>/submissions/', student_submissions, name='student-submissions'),
    path('api/professor/students/<int:student_id>/submissions/', views.student_submissions),
    path('api/soumissions/<int:soumission_id>/pdf/', views.soumission_pdf),
    path('api/teacher/submissions/', views.teacher_submissions, name='teacher-submissions'),
    path('api/corrections/<int:submission_id>/', views.update_correction, name='update-correction'),
    path('api/submissions/<int:submission_id>/pdf/', get_submission_pdf, name='get_submission_pdf'),
    path('api/corrections/<int:soumission_id>/update/', views.update_correction, name='update_correction'),
     path('api/corrections/<int:soumission_id>/update/', views.update_correction, name='update_correction'),
    path('api/soumissions/<int:submission_id>/pdf/', get_submission_pdf, name='get_submission_pdf'),
    path('api/professor/class/evolution/', views.evolution_classe, name='evolution_classe'),
    path('api/professors/me/', CurrentProfessorView.as_view(), name='current-professor'),


]



