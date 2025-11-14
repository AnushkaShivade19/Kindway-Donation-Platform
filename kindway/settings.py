from pathlib import Path
import os
from dotenv import load_dotenv

from urllib.parse import urlparse, parse_qsl

load_dotenv() 

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SECURITY AND DEBUG ---
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key-for-dev-only')
DEBUG = True

# Railway provides the hostname automatically
import os

ALLOWED_HOSTS = [
    '.vercel.app',      # allow all vercel subdomains
    '127.0.0.1',        # local testing
    'localhost',
]


# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',   # ✅ REQUIRED for allauth

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Your project apps
    'core',
    'users',
    'donations',
    'messaging',
    'communications',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    #'whitenoise.middleware.WhiteNoiseMiddleware',
 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This Site ID must match the one in your Django Admin
SITE_ID = 3

ROOT_URLCONF = 'kindway.urls'

TEMPLATES = [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 
                'DIRS': [os.path.join(BASE_DIR, 'templates')], 
                'APP_DIRS': True,
                'OPTIONS': { 'context_processors': [ 'django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', ], }, }, ]

WSGI_APPLICATION = 'kindway.wsgi.application'



# Replace the DATABASES section of your settings.py with this
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
        'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
    }
}


CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

# --- Allauth & Users Configuration ---
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
    'allauth.account.auth_backends.AuthenticationBackend'
]

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'index'
AUTH_USER_MODEL = 'users.CustomUser'
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none' # Set to 'none' for auto-login, was 'optional'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_ALLOW_LOGIN_AS_STAFF = True

#SOCIALACCOUNT_PROVIDERS = { 'google': { 'SCOPE': ['profile', 'email'], 'AUTH_PARAMS': {'access_type': 'online'} } }

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I_18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# This is for WhiteNoise IN PRODUCTION ONLY
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey' 
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'shivadeanushka003@gmail.com') 

# --- Database ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'