from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static # <-- Make sure this is imported
from core import views as core_views
from .admin import kindway_admin_site

urlpatterns = [
    path('admin/dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    path('admin/', kindway_admin_site.urls), 
    path('', include('core.urls')), 
    path('users/', include('users.urls')),
    path('donations/', include('donations.urls')),
    path('events/', include('communications.urls')),
    path('messages/', include('messaging.urls')),
    path('accounts/', include('allauth.urls')), 
]

# --- THIS IS THE CRITICAL FIX ---
# This block tells Django's development server how to serve both
# STATIC files (your images, videos, css) and MEDIA files (user uploads).
if settings.DEBUG:
    # Add this line to serve your static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    
    # This line serves your media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)