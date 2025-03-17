from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include



urlpatterns = [
      path('admin/', admin.site.urls),
      # path('', api_root, name='api-root'),  # Change '/' pour afficher directement l'API
      # path('api/', include('gestion.urls')),
       # Page d'administration Django
      path('', include('gestion.urls')),  
]

# Ajouter cette ligne pour servir les fichiers médias pendant le développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



