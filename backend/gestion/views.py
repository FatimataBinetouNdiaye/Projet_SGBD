
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
from .serializers import UtilisateurSerializer, ClasseSerializer, ExerciceSerializer, SoumissionSerializer, CorrectionSerializer
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

class DashboardView(APIView):    
    def get(self, request):
        return student_dashboard_data(request)


from .models import (
    PerformanceEtudiant, 
    Exercice, 
    Soumission, 
    Utilisateur,
    Correction
)
from .serializers import (
    DashboardSerializer,
    RecentSubmissionSerializer,
    NextDeadlineSerializer
)
from rest_framework.decorators import permission_classes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_data(request):
    student = request.user
    
    # Calcul des statistiques
    stats = {
        'completed': Soumission.objects.filter(etudiant=student).count(),
        'total': Exercice.objects.filter(classe__etudiants=student).count(),
        'average_score': round(
            PerformanceEtudiant.objects.filter(etudiant=student)
            .aggregate(average=Avg('note'))['average'] or 0,
        1
        ),
        'next_deadline': get_next_deadline(student)
    }
    
    # Récupération des soumissions récentes
    recent_submissions = Soumission.objects.filter(
        etudiant=student
    ).select_related('exercice', 'correction') \
     .order_by('-date_soumission')[:5]
    
    data = {
        'stats': stats,
        'recent_submissions': recent_submissions
    }
    
    serializer = DashboardSerializer(data)
    return Response(serializer.data)

def get_next_deadline(student):
    next_ex = Exercice.objects.filter(
        classe__etudiants=student,
        date_limite__gt=timezone.now()
    ).exclude(
        pk__in=Soumission.objects.filter(etudiant=student).values('exercice')
    ).order_by('date_limite').first()
    
    if next_ex:
        return {
            'exercise_id': next_ex.id,
            'exercise_title': next_ex.titre,
            'deadline_date': next_ex.date_limite,
            'days_left': (next_ex.date_limite - timezone.now()).days
        }
    return None


@api_view(['GET'])
def global_stats(request):
    stats = {
        'total': {
            'exercices': Exercice.objects.count(),
            'soumissions': Soumission.objects.count(),
            'etudiants': Utilisateur.objects.filter(role=Utilisateur.ETUDIANT).count(),
            'professeurs': Utilisateur.objects.filter(role=Utilisateur.PROFESSEUR).count()
        },
        'moyennes': {
            'notes': Correction.objects.aggregate(avg=Avg('note'))['avg'] or 0,
            'soumissions_par_exercice': Soumission.objects.count() / max(1, Exercice.objects.count())
        },
        'recent': {
            'exercices': ExerciceSerializer(
                Exercice.objects.order_by('-date_creation')[:5],
                many=True
            ).data,
            'soumissions': SoumissionSerializer(
                Soumission.objects.select_related('exercice', 'etudiant')
                                .order_by('-date_soumission')[:5],
                many=True
            ).data
        }
    }
    return Response(stats)

from django.db.models import Count

class StatsView(APIView):
    def get(self, request):
        # Exemple de statistiques simples
        stats = {
            'total_exercices': Exercice.objects.count(),
            'total_soumissions': Soumission.objects.count(),
            'exercices_par_classe': Exercice.objects.values('classe__nom').annotate(total=Count('id'))
        }
        return Response(stats)
    
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
        modele_ia_utilise='DeepSeek',  # S'assurer d'utiliser le modèle correct
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