from rest_framework import viewsets, generics
from .models import User
from .serializers import UserRegisterSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status







class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # Accessible à tous




def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        try:
            # On vérifie si un utilisateur avec ce mail et ce rôle existe
            user = User.objects.get(email=email, role=role)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie.")
                return redirect('/')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        except User.DoesNotExist:
            messages.error(request, "Aucun utilisateur avec cet email et ce rôle.")
    
    return render(request, 'login.html')
