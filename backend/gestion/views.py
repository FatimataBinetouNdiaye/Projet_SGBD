from rest_framework import viewsets
from .models import Exercice, Soumission, User
from .serializers import ExerciceSerializer, SoumissionSerializer, UserSerializer
from rest_framework.permissions import AllowAny

class ExerciceViewSet(viewsets.ModelViewSet):
    queryset = Exercice.objects.all()
    serializer_class = ExerciceSerializer
    permission_classes = []  # Suppression de la restriction JWT

class SoumissionViewSet(viewsets.ModelViewSet):
    queryset = Soumission.objects.all()
    serializer_class = SoumissionSerializer
    permission_classes = []  # Suppression de la restriction JWT

# 📌 Nouvelle vue API pour récupérer les utilisateurs
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Tout le monde peut voir la liste des utilisateurs
