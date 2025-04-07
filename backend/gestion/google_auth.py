import json
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.exceptions import AuthenticationFailed
from .models import Utilisateur
from rest_framework_simplejwt.tokens import RefreshToken
import uuid


def google_validate_id_token(token):
    try:
        # Vérifier le token avec Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return idinfo
    except ValueError:
        raise AuthenticationFailed('Le token Google est invalide ou a expiré.')

def register_or_login_social_user(email, nom, first_name, provider, photo_url=None, role='ET'):
    user = Utilisateur.objects.filter(email=email).first()
    
    if user:
        if user.auth_provider != provider:
            raise AuthenticationFailed(
                detail=f"Veuillez vous connecter avec {user.auth_provider}"
            )
        
        refresh = RefreshToken.for_user(user)
        return {
            'email': user.email,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
    else:
        # Génération d'un matricule unique pour les inscriptions Google
        matricule = f"GOOGLE_{email.split('@')[0].upper()}_{str(uuid.uuid4())[:8]}"
        
        new_user = Utilisateur.objects.create_user(
            email=email,
            first_name=first_name,  # changé ici
            last_name=nom,
            matricule=matricule,
            role=role,
            auth_provider=provider,
            is_verified=True
        )
        
        if photo_url:
            new_user.photo_profil = photo_url
            new_user.save()
        
        refresh = RefreshToken.for_user(new_user)
        return {
            'email': new_user.email,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'is_new_user': True  # Important pour le frontend
        }
