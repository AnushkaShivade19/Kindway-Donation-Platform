# kindway/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from .admin import kindway_admin_site

urlpatterns = [
    # The custom dashboard must be defined first
    path('admin/dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    
    # The main admin site comes second
    path('admin/', kindway_admin_site.urls), 
    
    # All other app URLs
    path('', include('core.urls')), 
    path('users/', include('users.urls')),
    path('donations/', include('donations.urls')),
    path('events/', include('communications.urls')),
    path('messages/', include('messaging.urls')),
    path('accounts/', include('allauth.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)