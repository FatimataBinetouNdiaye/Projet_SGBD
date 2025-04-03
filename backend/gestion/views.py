from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Exercice, Soumission, Correction, PerformanceEtudiant

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.AllowAny]

class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer

    def perform_create(self, serializer):
        # Associe automatiquement l'utilisateur connecté comme professeur
        if self.request.user.role == 'PR':
            serializer.save(professeur=self.request.user)
        else:
            raise serializers.ValidationError(
                {"professeur": "Seuls les professeurs peuvent créer des classes."}
            )

class ExerciceViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciceSerializer
    queryset = Exercice.objects.none()  # Initialisation vide
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'PR':  # Professeur
                return Exercice.objects.filter(professeur=user)
            return Exercice.objects.filter(classe__etudiants=user)
        return Exercice.objects.none()

class SoumissionViewSet(viewsets.ModelViewSet):
    serializer_class = SoumissionSerializer
    queryset = Soumission.objects.none()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Soumission.objects.filter(etudiant=user)
        return Soumission.objects.none()

class CorrectionViewSet(viewsets.ReadOnlyModelViewSet):  # Lecture seule
    serializer_class = CorrectionSerializer
    queryset = Correction.objects.none()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Correction.objects.filter(soumission__etudiant=user)
        return Correction.objects.none()

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implémentation vue précédente...
        pass
from rest_framework.parsers import MultiPartParser, FormParser
class UploadSoumissionView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, exercice_id):
        exercice = get_object_or_404(Exercice, pk=exercice_id)
        if not exercice.classe.etudiants.filter(id=request.user.id).exists():
            return Response({"error": "Accès non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        fichier_pdf = request.FILES.get('fichier')
        if not fichier_pdf:
            return Response({"error": "Fichier manquant"}, status=status.HTTP_400_BAD_REQUEST)
        
        soumission = Soumission.objects.create(
            exercice=exercice,
            etudiant=request.user,
            fichier_pdf=fichier_pdf,
            nom_original=fichier_pdf.name
        )
        
        # Démarrer la correction automatique
        from .tasks import process_submission
        process_submission.delay(soumission.id)
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


        