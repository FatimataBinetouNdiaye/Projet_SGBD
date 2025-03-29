from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from gestion.views import api_root  # Import de la vue API root

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('', include('gestion.urls')),  
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
