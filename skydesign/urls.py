"""
URL Configuration for Sky Design Platform
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Authentication - Django Allauth
    path('accounts/', include('allauth.urls')),
    
    # Apps
    path('api/accounts/', include('accounts.urls')),
    path('api/designs/', include('designs.urls')),
    path('api/games/', include('games.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/manager/', include('manager.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)