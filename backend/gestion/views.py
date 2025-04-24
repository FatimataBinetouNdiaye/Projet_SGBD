
import os
from django.http import JsonResponse

from plateforme_eval import settings

from .models import update_correction_model 

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from .models import *
from .serializers import UtilisateurSerializer, ClasseSerializer, ExerciceSerializer, SoumissionSerializer, CorrectionSerializer, ExerciceListSerializer, RecentSubmissionSerializer, TeacherSubmissionSerializer
from rest_framework.permissions import AllowAny  # <-- Ajoutez cette importation


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
from django.contrib.auth.models import AnonymousUser

class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class ExerciceListView(generics.ListAPIView):
    """
    Vue spécialisée uniquement pour lister les exercices
    avec les URLs des fichiers correctement formatées
    """
    serializer_class = ExerciceListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Exercice.objects.select_related('professeur', 'classe')
        
        if user.role == Utilisateur.PROFESSEUR:
            return queryset.filter(professeur=user)
        return queryset.filter(
            est_publie=True,
            date_limite__gte=timezone.now()
        ).order_by('-date_creation')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['absolute_uri'] = self.request.build_absolute_uri('/')
        return context
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print("Données renvoyées:", response.data)  # Vérifiez les URLs dans la réponse
        return response

class ExerciceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des exercices avec :
    - Filtrage par rôle utilisateur
    - Gestion des soumissions
    - Publication/dépublication
    """
    serializer_class = ExerciceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']  # Désactive PUT
    
    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        
        queryset = Exercice.objects.select_related('professeur', 'classe')
        
        if user.role == Utilisateur.PROFESSEUR:
            # Professeurs voient leurs exercices + stats soumissions
            queryset = queryset.filter(professeur=user)
        else:
            # Étudiants voient seulement les exercices publiés et non expirés
            queryset = queryset.filter(
                est_publie=True,
                date_limite__gte=now,
                
            )
        
        # Optimisation pour la liste
        if self.action == 'list':
            queryset = queryset.prefetch_related(
                Prefetch('soumissions', 
                       queryset=Soumission.objects.select_related('etudiant')
                       .only('id', 'date_soumission', 'etudiant__last_name', 'etudiant__first_name'))
            )
        
        return queryset.order_by('-date_creation')

    def perform_create(self, serializer):
        """Associe automatiquement le professeur connecté"""
        if self.request.user.role != Utilisateur.PROFESSEUR:
            raise PermissionDenied("Seuls les professeurs peuvent créer des exercices")
        serializer.save(professeur=self.request.user)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Liste des soumissions pour un exercice"""
        exercice = self.get_object()
        
        # Vérification des permissions
        if request.user.role == Utilisateur.ETUDIANT:
            if not exercice.est_publie or exercice.date_limite < timezone.now():
                raise PermissionDenied("Exercice non disponible")
        
        # Préchargement optimisé
        soumissions = exercice.soumissions.select_related(
            'etudiant'
        ).prefetch_related(
            'exercice'
        )
        
        if request.user.role == Utilisateur.ETUDIANT:
            soumissions = soumissions.filter(etudiant=request.user)
        
        page = self.paginate_queryset(soumissions)
        serializer = SoumissionSerializer(
            page if page is not None else soumissions,
            many=True,
            context={'request': request}
        )
        
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publication/Dépublication d'un exercice"""
        exercice = self.get_object()
        
        if exercice.professeur != request.user:
            raise PermissionDenied("Action réservée au professeur propriétaire")
        
        exercice.est_publie = not exercice.est_publie
        exercice.save()
        
        return Response({
            'status': 'published' if exercice.est_publie else 'unpublished',
            'date_limite': exercice.date_limite,
            'exercice_id': exercice.id
        })

    @action(detail=False, methods=['get'])
    def actifs(self, request):
        try:
            # Debug: Affiche l'utilisateur et son rôle
            print(f"Utilisateur connecté : {request.user.id} - Rôle : {request.user.role}")
            
            queryset = Exercice.objects.filter(
                est_publie=True,
                date_limite__gte=timezone.now()
            ).select_related('professeur')
            
            # Debug: Affiche les exercices trouvés
            print(f"Exercices trouvés : {queryset.count()}")
            for ex in queryset[:3]:  # Affiche les 3 premiers pour debug
                print(f"Exercice {ex.id}: {ex.titre} - Date limite: {ex.date_limite}")

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'count': queryset.count(),
                'data': serializer.data
            })
        
        except Exception as e:
            import traceback
            traceback.print_exc()  # Affiche la stack trace complète
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_update(self, serializer):
        """
        Effectuer la mise à jour de l'exercice.
        Nous vérifions si l'exercice est déjà publié. Si c'est le cas,
        on permet la modification de la date limite (ou non, selon ta logique).
        """

        serializer.save()


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from .models import Soumission, Exercice, Utilisateur
from .serializers import SoumissionSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from gestion.tasks import get_ai_correction, process_submission  # Importer la tâche Celery

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Soumission
from .tasks import process_submission  # Importer la tâche Celery

class SoumissionViewSet(viewsets.ModelViewSet):
    queryset = Soumission.objects.all()
    serializer_class = SoumissionSerializer
    
    
    def perform_create(self, serializer):
        # Crée la soumission avec les données fournies dans le formulaire
        soumission = serializer.save(
            etudiant=self.request.user,  # Associe l'étudiant connecté
            nom_original=self.request.FILES['fichier_pdf'].name,  # Enregistre le nom du fichier
            taille_fichier=self.request.FILES['fichier_pdf'].size  # Enregistre la taille du fichier
        )

        # Lancer la tâche Celery pour effectuer la correction
        process_submission.delay(soumission.id)  # Lancer la tâche Celery en arrière-plan

        # Retourner une réponse immédiate pour informer l'utilisateur
        return Response({'message': 'Soumission reçue, correction en cours...'}, status=status.HTTP_201_CREATED)


class CorrectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CorrectionSerializer
    permission_classes = [IsAuthenticated]  # Assure-toi que l'utilisateur est authentifié

    def get_queryset(self):
        user = self.request.user

        # Vérifie si l'utilisateur est authentifié
        if not user.is_authenticated:
            raise PermissionDenied("Vous devez être authentifié pour accéder à cette ressource.")

        # Vérifie le rôle de l'utilisateur
        if user.role == Utilisateur.ETUDIANT:
            return Correction.objects.filter(soumission__etudiant=user)
        return Correction.objects.filter(soumission__exercice__professeur=user)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from django.utils import timezone
from .models import Soumission, Exercice, PerformanceEtudiant
from .serializers import DashboardSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from django.utils import timezone
from .models import Soumission, Exercice, PerformanceEtudiant
from .serializers import DashboardSerializer
import logging

logger = logging.getLogger(__name__)

from django.db.models import Avg, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Soumission, Exercice
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Sum, F, Count
from .models import Soumission, Exercice, PerformanceEtudiant
from .serializers import RecentSubmissionSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_data(request):
    try:
        student = request.user
        
        # 1. Récupération de toutes les soumissions avec correction
        all_submissions = Soumission.objects.filter(
            etudiant=student
        ).select_related('exercice', 'correction').prefetch_related('exercice__classe')
        
        # 2. Récupération des exercices disponibles
        all_exercises = Exercice.objects.filter(classe__etudiants=student)
        total_exercises = all_exercises.count()
        
        # 3. Calcul des statistiques
        completed_count = all_submissions.filter(correction__isnull=False).count()
        
        # 4. Calcul de la moyenne
        average_score = calculate_weighted_average(student)
        
        # 5. Prochaine échéance améliorée
        next_deadline = get_next_deadline(student, all_exercises)
        
        # 6. Préparation des données
        stats = {
            'completed': completed_count,
            'total': total_exercises,
            'average_score': average_score,
            'next_deadline': next_deadline,
            'unsubmitted_count': total_exercises - all_submissions.count(),
            'late_submissions': all_submissions.filter(en_retard=True).count()
        }
        
        return Response({
            'stats': stats,
            'recent_submissions': RecentSubmissionSerializer(
                all_submissions.order_by('-date_soumission')[:5],
                many=True
            ).data
        })
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        return Response({'error': 'Une erreur est survenue'}, status=500)

def calculate_weighted_average(student):
    """Calcule la moyenne pondérée par les coefficients"""
    result = Soumission.objects.filter(
        etudiant=student,
        correction__isnull=False
    ).annotate(
        weighted_score=F('correction__note') * F('exercice__coefficient')
    ).aggregate(
        total_score=Sum('weighted_score'),
        total_coefficient=Sum('exercice__coefficient')
    )
    
    if result['total_coefficient'] and result['total_score']:
        return round(result['total_score'] / result['total_coefficient'], 2)
    return 0.0

def get_next_deadline(student, all_exercises):
    """Récupère la prochaine échéance avec plus de détails"""
    submitted_exercises = Soumission.objects.filter(
        etudiant=student
    ).values_list('exercice_id', flat=True)

    # Exercices non soumis triés par date
    unsibmitted_exercises = all_exercises.exclude(
        id__in=submitted_exercises
    ).order_by('date_limite')

    now = timezone.now()
    
    # Prochain deadline futur
    next_future = unsibmitted_exercises.filter(
        date_limite__gt=now
    ).first()

    if next_future:
        return {
            'exercise_id': next_future.id,
            'exercise_title': next_future.titre,
            'date_limite': next_future.date_limite,
            'is_past_due': False,
            'days_remaining': (next_future.date_limite - now).days
        }
    
    # Sinon, premier exercice en retard
    first_past_due = unsibmitted_exercises.filter(
        date_limite__lte=now
    ).first()

    if first_past_due:
        return {
            'exercise_id': first_past_due.id,
            'exercise_title': first_past_due.titre,
            'date_limite': first_past_due.date_limite,
            'is_past_due': True,
            'days_late': (now - first_past_due.date_limite).days
        }
    
    return None
    
# users/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UtilisateurSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def utilisateur_connecte(request):
    serializer = UtilisateurSerializer(request.user)
    return Response(serializer.data)

from rest_framework import status
from .google_auth import google_validate_id_token, register_or_login_social_user

class GoogleSocialAuthView(APIView):
    def post(self, request):
        token = request.data.get('token')
        role = request.data.get('role', 'ET')
        
        if not token:
            return Response(
                {'error': 'Token manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Valider le token Google
            user_data = google_validate_id_token(token)
            
            # Enregistrer ou connecter l'utilisateur
            auth_data = register_or_login_social_user(
                email=user_data['email'],
                last_name=user_data.get('family_name', ''),  
                first_name=user_data.get('given_name', ''), 
                provider='google',
                photo_url=user_data.get('picture'),
                role=role
            )
            
            return Response(auth_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # Pour permettre l'accès à tous les utilisateurs
from rest_framework.response import Response
from rest_framework import status
from .serializers import UtilisateurSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # Permet à tout le monde d'accéder à cette vue
def signup(request):
    if request.method == 'POST':
        serializer = UtilisateurSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Créer un nouvel utilisateur
            return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def update_feedback(request, correction_id):
    professor_feedback = request.data['feedback']
    
    correction = Correction.objects.get(id=correction_id)
    correction.commentaire_professeur = professor_feedback
    correction.save()
    
    retrain_ai_model(professor_feedback)  # Réentraîner l'IA avec le feedback du professeur
    
    return Response({'message': 'Feedback mis à jour et utilisé pour améliorer l\'IA.'})


#VUE DE IA


# Créer une nouvelle vue pour traiter la correction par l'IA


@api_view(['POST'])
def process_ai_correction(request, soumission_id):
    try:
        soumission = Soumission.objects.get(id=soumission_id)
    except Soumission.DoesNotExist:
        return Response({"error": "Soumission non trouvée."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Appeler la fonction pour obtenir la correction
        correction = get_ai_correction(soumission.fichier_pdf.path)  # Vérifie que le fichier est accessible
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    Correction.objects.create(
        soumission=soumission,
        note=correction['note'],
        feedback=correction['feedback'],
        points_forts=correction['points_forts'],
        points_faibles=correction['points_faibles'],
        modele_ia_utilise='deepseek-coder:6.7b',  # S'assurer d'utiliser le modèle correct
    )

    return Response({"message": "Correction effectuée par l'IA"}, status=status.HTTP_200_OK)




# Gérer les retours des professeurs
@api_view(['POST'])
def update_feedback(request, correction_id):
    professor_feedback = request.data['feedback']
    
    # Enregistrer le feedback pour analyse future
    feedback_entry = Feedback(feedback_text=professor_feedback)
    feedback_entry.save()

    # Mettre à jour la correction avec le feedback du professeur
    update_correction_model(professor_feedback, correction_id)

    # Réentraîner l'IA avec ce feedback
    retrain_ai_model(professor_feedback)

    return Response({'message': 'Feedback mis à jour et utilisé pour améliorer l\'IA.'})


def update_correction_model(professor_feedback, correction_id):
    """
    Met à jour la correction avec le feedback du professeur.
    """
    correction = Correction.objects.get(id=correction_id)
    correction.commentaire_professeur = professor_feedback  # Met à jour le commentaire du professeur
    correction.save()  # Sauvegarde la correction mise à jour


@api_view(['GET'])
def get_models(request):
    models_dir = getattr(settings, 'OLLAMA_MODELS', None)
    if not models_dir:
        return JsonResponse(
            {'error': 'Le paramètre OLLAMA_MODELS n’est pas défini.'},
            status=500
        )

    # Convertir en str si c'est un Path
    models_dir = str(models_dir)

    if not os.path.isdir(models_dir):
        return JsonResponse(
            {'error': f'Le répertoire des modèles est introuvable ({models_dir}).'},
            status=500
        )

    models = [
        fname for fname in os.listdir(models_dir)
        if os.path.isfile(os.path.join(models_dir, fname))
    ]
    return JsonResponse({'models': models})

@api_view(['POST'])
def generate_without_id(request):
    sid = request.data.get('soumission_id')
    if not sid:
        return Response({'error':'Il faut passer `soumission_id`'}, status=400)
    return process_ai_correction(request, sid)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return student_dashboard_data(request)
    
    
class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Statistiques générales du système.",
            "utilisateur": request.user.email
        })
    
from django.db.models import Q
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def professor_classes_list(request):
    if request.user.role != 'PR':
        return Response({"error": "Accès réservé aux professeurs"}, status=403)
    
    try:
        classes = Classe.objects.filter(
            Q(professeur=request.user) | 
            Q(professeurs_supplementaires=request.user)
        ).distinct().prefetch_related(
            Prefetch('etudiants', 
                   queryset=Utilisateur.objects.filter(role='ET')
                   .only('id', 'first_name', 'last_name', 'email', 'matricule'))
        )
        
        classes_data = []
        for classe in classes:
            etudiants = classe.etudiants.all()
            classes_data.append({
                'id': classe.id,
                'nom': classe.nom,
                'code': classe.code,
                'etudiants_count': etudiants.count(),
                'etudiants': [
                    {
                        'id': etudiant.id,
                        'matricule': etudiant.matricule,
                        'prenom': etudiant.first_name,
                        'nom': etudiant.last_name,
                        'email': etudiant.email,
                        'soumissions_count': etudiant.soumissions.count()  # Nouveau champ
                    }
                    for etudiant in etudiants
                ]
            })
        
        return Response(classes_data)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({"error": str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submissions(request, student_id):
    if request.user.role != 'PR':
        return Response({"error": "Accès réservé aux professeurs"}, status=403)
    
    try:
        soumissions = Soumission.objects.filter(
            etudiant_id=student_id
        ).select_related('exercice', 'correction').order_by('-date_soumission')
        
        submissions_data = []
        for soumission in soumissions:
            submissions_data.append({
                'id': soumission.id,
                'exercice': soumission.exercice.titre,
                'date_soumission': soumission.date_soumission,
                'note': soumission.correction.note if hasattr(soumission, 'correction') else None,
                'statut': 'Corrigé' if hasattr(soumission, 'correction') else 'En attente'
            })
        
        return Response({
            'etudiant': {
                'id': soumissions[0].etudiant.id if soumissions else None,
                'nom_complet': f"{soumissions[0].etudiant.last_name} {soumissions[0].etudiant.first_name}" if soumissions else None,
                'matricule': soumissions[0].etudiant.matricule if soumissions else None
            },
            'soumissions': submissions_data
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({"error": str(e)}, status=500)    
    


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Soumission, Utilisateur
import os
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_submissions(request, student_id):
    # Vérifier si l'utilisateur est professeur ou l'étudiant lui-même
    if not (request.user.role == Utilisateur.PROFESSEUR or request.user.id == student_id):
        return Response({"detail": "Accès non autorisé"}, status=403)
    
    soumissions = Soumission.objects.filter(
        etudiant_id=student_id
    ).select_related('exercice').order_by('-date_soumission')
    
    if not soumissions.exists():
        return Response({"detail": "Aucune soumission trouvée"}, status=404)
    
    etudiant = soumissions.first().etudiant
    data = {
        'etudiant': {
            'nom_complet': f"{etudiant.first_name} {etudiant.last_name}",
            'matricule': etudiant.username,
        },
        'soumissions': [
            {
                'id': soumission.id,
                'exercice': soumission.exercice.titre,
                'date_soumission': soumission.date_soumission,
                'statut': 'Corrigé' if hasattr(soumission, 'correction') else 'En attente',
                'note': soumission.correction.note if hasattr(soumission, 'correction') else None,
                'en_retard': soumission.en_retard,
                'est_plagiat': soumission.est_plagiat,
            }
            for soumission in soumissions
        ]
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def soumission_pdf(request, soumission_id):
    soumission = get_object_or_404(Soumission, id=soumission_id)
    
    # Vérification des permissions
    if not (request.user == soumission.etudiant or request.user.role == Utilisateur.PROFESSEUR):
        return Response({"detail": "Accès non autorisé"}, status=403)
    
    if not soumission.fichier_pdf:
        return Response({"detail": "Fichier PDF introuvable"}, status=404)
    
    try:
        file_path = soumission.fichier_pdf.path
        if os.path.exists(file_path):
            response = FileResponse(
                open(file_path, 'rb'),
                content_type='application/pdf',
                as_attachment=False  # Permet l'affichage dans le navigateur
            )
            response['Content-Disposition'] = f'inline; filename="{soumission.nom_original}"'
            return response
        return Response({"detail": "Fichier non trouvé sur le serveur"}, status=404)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)


# views.py
# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_submissions(request):
    try:
        user = request.user

        # Vérifie si l'utilisateur est professeur (principal ou supplémentaire)
        if user.role != Utilisateur.PROFESSEUR:
            return Response({'error': 'Accès réservé aux professeurs'}, status=403)

        class_id = request.query_params.get('class_id')
        exercise_id = request.query_params.get('exercise_id')

        # Récupère toutes les soumissions des classes où le prof enseigne
        queryset = Soumission.objects.filter(
            Q(exercice__classe__professeur=user) | 
            Q(exercice__classe__professeurs_supplementaires=user)
        ).select_related(
            'etudiant',
            'exercice',
            'exercice__classe',
            'correction'
        ).order_by('-date_soumission')

        if class_id:
            queryset = queryset.filter(exercice__classe__id=class_id)

        if exercise_id:
            queryset = queryset.filter(exercice__id=exercise_id)

        serializer = TeacherSubmissionSerializer(queryset, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Erreur dans teacher_submissions: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Une erreur est survenue lors de la récupération des soumissions'},
            status=500
        )
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_correction(request, soumission_id):
    if request.user.role != 'PR':
        return Response({"error": "Accès interdit"}, status=403)

    try:
        correction = Correction.objects.get(soumission__id=soumission_id)

        # Champs modifiables par le professeur
        correction.note = request.data.get('note', correction.note)
        correction.feedback = request.data.get('feedback', correction.feedback)
        correction.points_forts = request.data.get('points_forts', correction.points_forts)
        correction.points_faibles = request.data.get('points_faibles', correction.points_faibles)
        correction.commentaire_professeur = request.data.get('commentaire_professeur', correction.commentaire_professeur)

        est_validee = request.data.get('est_validee')
        if est_validee is not None:
            correction.est_validee = est_validee
            correction.date_validation = timezone.now() if est_validee else None

        correction.save()
        return Response({"message": "Correction mise à jour avec succès"})

    except Correction.DoesNotExist:
        return Response({"error": "Correction introuvable"}, status=404)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from .models import Soumission

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission_pdf(request, submission_id):
    try:
        soumission = Soumission.objects.get(id=submission_id)
        
        # Vérifie que l'utilisateur a le droit d'accéder
        if request.user.role != 'PR':
            return Response({"error": "Accès interdit"}, status=403)
        
        if not soumission.fichier_pdf:
            raise Http404("Fichier introuvable")

        return FileResponse(soumission.fichier_pdf.open('rb'), content_type='application/pdf')
    except Soumission.DoesNotExist:
        raise Http404("Soumission non trouvée")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evolution_classe(request):
    if request.user.role != 'PR':
        return Response({"error": "Accès interdit"}, status=403)

    evolution = []

    exercices = Exercice.objects.all()
    for exo in exercices:
        soums = Soumission.objects.filter(exercice=exo, correction__isnull=False)
        moyenne = soums.aggregate(moy=Avg('correction__note'))['moy']
        if moyenne is not None:
            evolution.append({
                "exercice": exo.titre,
                "note_moyenne": round(moyenne, 2)
            })

    return Response(evolution)



class CurrentProfessorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == Utilisateur.PROFESSEUR:
            serializer = UtilisateurSerializer(user)
            return Response(serializer.data)
        return Response({"detail": "Vous n'êtes pas un professeur."}, status=status.HTTP_403_FORBIDDEN)