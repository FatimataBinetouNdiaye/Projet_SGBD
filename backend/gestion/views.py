from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsProfesseur, IsEtudiant

User = get_user_model()

# ✅ Vue d'inscription
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]  # Tout le monde peut s'inscrire

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Utilisateur créé avec succès",
            "user": response.data
        }, status=status.HTTP_201_CREATED)


# ✅ Vue pour la connexion avec JWT (ajout du rôle utilisateur dans le token)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ✅ Vue pour les professeurs uniquement
class ProfesseurView(generics.ListAPIView):
    queryset = User.objects.filter(role="professeur")
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsProfesseur]  # Seuls les professeurs authentifiés peuvent y accéder


# ✅ Vue pour les étudiants uniquement
class EtudiantView(generics.ListAPIView):
    queryset = User.objects.filter(role="etudiant")
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsEtudiant]  # Seuls les étudiants authentifiés peuvent y accéder
