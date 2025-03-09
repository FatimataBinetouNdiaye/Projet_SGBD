from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsProfesseur, IsEtudiant

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        user = User.objects.create_user(
            username=request.data["username"],
            email=request.data["email"],
            password=request.data["password"],
            role=request.data["role"]
        )
        return Response(CustomUserSerializer(user).data, status=status.HTTP_201_CREATED)



class SomeProfesseurView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsProfesseur]
    
class SomeEtudiantView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsEtudiant]
