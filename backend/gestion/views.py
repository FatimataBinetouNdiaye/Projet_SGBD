from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg
from .models import Utilisateur, Classe, Exercice, Soumission, Correction, PerformanceEtudiant
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
class SoumissionViewSet(viewsets.ModelViewSet):
    queryset = Soumission.objects.all()
    serializer_class = SoumissionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            etudiant=self.request.user,
            nom_original=self.request.FILES['fichier_pdf'].name,
            taille_fichier=self.request.FILES['fichier_pdf'].size
        )

class CorrectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CorrectionSerializer

    def get_queryset(self):
        user = self.request.user
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_data(request):
    student = request.user
    student = request.user
    print(f"\n=== DEBUG USER ===")
    print(f"User ID: {student.id}, Email: {student.email}")
    
    # Debug 1: Vérifiez les soumissions existantes
    all_subs = Soumission.objects.filter(etudiant=student)
    print(f"\n=== SOUMISSIONS EXISTANTES ===")
    print(f"Total: {all_subs.count()}")
    for sub in all_subs:
        print(f"ID: {sub.id}, Exercice: {sub.exercice.titre}, Date: {sub.date_soumission}")

    # Debug 2: Vérifiez les exercices
    exercices = Exercice.objects.filter(classe__etudiants=student)
    print(f"\n=== EXERCICES ACCESSIBLES ===")
    print(f"Total: {exercices.count()}")
    try:
        # Calcul des statistiques
        stats = {
            'completed': Soumission.objects.filter(etudiant=student).count(),
            'total': Exercice.objects.filter(classe__etudiants=student).count(),
            'average_score': get_average_score(student),
            'next_deadline': get_next_deadline(student)
        }
        
        # Récupération des soumissions avec optimisation des requêtes
        recent_submissions = Soumission.objects.filter(
            etudiant=student
        ).select_related(
            'exercice',
            'correction'
        ).order_by('-date_soumission')[:5]
        
        # Logs de débogage
        logger.info(f"Dashboard data requested by {student.email}")
        logger.debug(f"Found {recent_submissions.count()} submissions")
        
        data = {
            'stats': stats,
            'recent_submissions': recent_submissions
        }
        
        serializer = DashboardSerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}", exc_info=True)
        return Response({"error": "Une erreur est survenue"}, status=500)

def get_average_score(student):
    avg = PerformanceEtudiant.objects.filter(
        etudiant=student
    ).aggregate(average=Avg('note'))['average']
    return round(avg, 1) if avg is not None else 0

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
            'date_limite': next_ex.date_limite,
            'days_left': (next_ex.date_limite - timezone.now()).days
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
