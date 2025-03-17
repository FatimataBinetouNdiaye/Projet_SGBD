from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView

urlpatterns = [
    # Inscription d'un nouvel utilisateur
    path('register/', RegisterView.as_view(), name='register'),

    # Connexion avec JWT (obtenir un token)
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Rafraîchir le token JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Authentification via Google, GitHub, Microsoft (OAuth2)
    path('oauth/', include('rest_framework_social_oauth2.urls')),
]
