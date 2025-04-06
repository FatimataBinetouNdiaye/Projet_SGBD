from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(MiddlewareMixin):
    """
    Middleware personnalisé pour gérer les problèmes CSRF et CORS
    """
    
    def process_request(self, request):
        """
        Traite la requête entrante avant qu'elle n'atteigne la vue
        """
        # Log utile pour le débogage
        logger.debug(f"Processing request: {request.path}")
        
        # Vous pouvez ajouter ici une logique pré-requête si nécessaire
        return None

    def process_response(self, request, response):
        """
        Traite la réponse avant qu'elle ne soit envoyée au client
        """
        # Ajoute les headers CORS nécessaires pour toutes les réponses API
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'X-CSRFToken'
            
            # Pour les requêtes OPTIONS (pré-vol)
            if request.method == 'OPTIONS':
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        
        # Configure les cookies CSRF pour les environnements de développement
        if settings.DEBUG and hasattr(request, 'csrf_cookie_needs_reset'):
            response.set_cookie(
                settings.CSRF_COOKIE_NAME,
                request.META['CSRF_COOKIE'],
                max_age=settings.CSRF_COOKIE_AGE,
                domain=settings.CSRF_COOKIE_DOMAIN,
                path=settings.CSRF_COOKIE_PATH,
                secure=settings.CSRF_COOKIE_SECURE,
                httponly=settings.CSRF_COOKIE_HTTPONLY,
                samesite=settings.CSRF_COOKIE_SAMESITE
            )
        
        return response
from django.middleware.csrf import get_token
class CsrfCookieMiddleware(MiddlewareMixin):
    """
    Middleware pour s'assurer que le cookie CSRF est toujours défini
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Force la création d'un cookie CSRF si non présent
        if not request.META.get('CSRF_COOKIE'):
            request.META['CSRF_COOKIE'] = get_token(request)
            request.csrf_cookie_needs_reset = True
        return None