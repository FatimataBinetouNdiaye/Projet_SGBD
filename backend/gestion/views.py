from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from .models import Exercice, Soumission
from .serializers import ExerciceSerializer, SoumissionSerializer

def api_root(request):
    return JsonResponse({
        "message": "Bienvenue sur l'API d'évaluation des exercices.",
        "endpoints": {
            "Exercices": "/api/exercices/",
            "Soumissions": "/api/soumissions/"
        }
    })

class ExerciceViewSet(viewsets.ModelViewSet):
    queryset = Exercice.objects.all()
    serializer_class = ExerciceSerializer

class SoumissionViewSet(viewsets.ModelViewSet):
    queryset = Soumission.objects.all()
    serializer_class = SoumissionSerializer
