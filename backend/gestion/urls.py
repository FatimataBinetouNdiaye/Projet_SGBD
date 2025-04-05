from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  UserRegisterView, login_view



router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),  # Routes API existantes
    path('signup/', UserRegisterView.as_view(), name='signup'),  # Route pour l'inscription
    path('login/', login_view, name='login'),


]


