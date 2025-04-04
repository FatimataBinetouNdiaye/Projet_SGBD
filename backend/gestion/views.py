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
from django.db.models import Prefetch
from .serializers import ExerciceSerializer, SoumissionSerializer
from rest_framework.exceptions import ValidationError  # Ajoutez cette ligne
from rest_framework import serializers  # Si vous utilisez aussi serializers
from rest_framework.permissions import IsAuthenticated

class ExerciceViewSet(viewsets.ModelViewSet):
    queryset = Exercice.objects.all()
    serializer_class = ExerciceSerializer
    permission_classes = [IsAuthenticated]  # ✅ Important
    def perform_create(self, serializer):
        serializer.save(professeur=self.request.user)


    def get_queryset(self):
        user = self.request.user

        if user.role == Utilisateur.PROFESSEUR:
        # Un professeur voit ses propres exercices, publiés ou non
            queryset = Exercice.objects.filter(professeur=user)
        else:
        # Étudiants : ne voient que les exos publiés
            queryset = Exercice.objects.filter(est_publie=True)

    # Préchargement des relations
        queryset = queryset.select_related('professeur', 'classe')

        return queryset.order_by('-date_creation')


    def get_serializer_context(self):
        """Passe le contexte (request) au sérialiseur"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Endpoint personnalisé pour les soumissions d'un exercice"""
        exercice = self.get_object()
        
        if isinstance(request.user, AnonymousUser):
            return Response(
                {"error": "Authentification requise"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Préchargement optimisé
        soumissions = exercice.soumissions.select_related('etudiant', 'exercice')
        
        if request.user.role == Utilisateur.ETUDIANT:
            soumissions = soumissions.filter(etudiant=request.user)
        
        serializer = SoumissionSerializer(
            soumissions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """Version optimisée de la liste avec pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Préchargement supplémentaire pour la liste
        queryset = queryset.prefetch_related(
            Prefetch('soumissions', 
                   queryset=Soumission.objects.select_related('etudiant'))
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Action personnalisée pour publier/dépublier un exercice"""
        exercice = self.get_object()
        
        if exercice.professeur != request.user:
            return Response(
                {"error": "Seul le professeur propriétaire peut publier"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        exercice.est_publie = not exercice.est_publie
        exercice.save()
        
        return Response({
            'status': 'published' if exercice.est_publie else 'unpublished',
            'exercice_id': exercice.id
        })
class SoumissionViewSet(viewsets.ModelViewSet):
    serializer_class = SoumissionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == Utilisateur.ETUDIANT:
            return Soumission.objects.filter(etudiant=user)
        return Soumission.objects.filter(exercice__professeur=user)

class CorrectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CorrectionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == Utilisateur.ETUDIANT:
            return Correction.objects.filter(soumission__etudiant=user)
        return Correction.objects.filter(soumission__exercice__professeur=user)

class DashboardView(APIView):    
    def get(self, request):
        return student_dashboard_data(request)

class UploadSoumissionView(APIView):
    parser_classes = [MultiPartParser]
    
    def post(self, request, exercice_id):
        exercice = get_object_or_404(Exercice, pk=exercice_id)
        if request.user.role != Utilisateur.ETUDIANT:
            return Response({"error": "Seuls les étudiants peuvent soumettre des travaux"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        if not exercice.classe.etudiants.filter(id=request.user.id).exists():
            return Response({"error": "Vous n'êtes pas dans cette classe"}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        fichier_pdf = request.FILES.get('fichier')
        if not fichier_pdf:
            return Response({"error": "Fichier manquant"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        soumission = Soumission.objects.create(
            exercice=exercice,
            etudiant=request.user,
            fichier_pdf=fichier_pdf,
            nom_original=fichier_pdf.name,
            taille_fichier=fichier_pdf.size
        )
        
        return Response(
            {"status": "success", "submission_id": soumission.id},
            status=status.HTTP_201_CREATED
        )

@api_view(['GET'])
def student_dashboard_data(request):
    student = request.user
    
    average_score = PerformanceEtudiant.objects.filter(
        etudiant=student
    ).aggregate(average=Avg('note'))['average'] or 0
    
    next_deadline = Exercice.objects.filter(
        classe__etudiants=student,
        date_limite__gt=timezone.now()
    ).exclude(
        pk__in=Soumission.objects.filter(etudiant=student).values('exercice')
    ).order_by('date_limite').first()
    
    recent_submissions = Soumission.objects.filter(
        etudiant=student
    ).select_related('exercice', 'correction').order_by('-date_soumission')[:3]
    
    data = {
        'stats': {
            'completed': Soumission.objects.filter(etudiant=student).count(),
            'total': Exercice.objects.filter(classe__etudiants=student).count(),
            'average_score': round(average_score, 1),
            'next_deadline': {
                'days_left': (next_deadline.date_limite - timezone.now()).days if next_deadline else None,
                'exercise_title': next_deadline.titre if next_deadline else None
            }
        },
        'recent_submissions': [
            {
                'id': sub.id,
                'exercise_title': sub.exercice.titre,
                'submission_date': sub.date_soumission,
                'score': sub.correction.note if hasattr(sub, 'correction') else None,
                'exercise_id': sub.exercice.id
            }
            for sub in recent_submissions
        ]
    }
    
    return Response(data)




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
