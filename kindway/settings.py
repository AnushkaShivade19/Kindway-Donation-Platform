# /kindway/settings.py

from pathlib import Path
import os
import dj_database_url  # <-- Import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SECURITY AND DEBUG ---
# Vercel will set this to your secret value.
SECRET_KEY = os.getenv('SECRET_KEY')

# Vercel will set this to 'False'. Locally, it will default to 'True'.
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    '.vercel.app',  # Allow all vercel subdomains
    '127.0.0.1',
    'localhost',
]

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Third-party apps
    'widget_tweaks',
    'storages',  # <-- For AWS S3

    # Your project apps
    'core',
    'users',
    'donations',
    'messaging',
    'communications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise is removed. Vercel handles static files via 'staticfiles'.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', # <-- allauth middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This Site ID must match the one in your Django Admin
# We use an env var for production and default to 1 for local dev
SITE_ID = int(os.environ.get('SITE_ID', 1))

ROOT_URLCONF = 'kindway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'messaging.context_processors.unread_message_count', # <-- Your unread msg counter
            ],
        },
    },
]

WSGI_APPLICATION = 'kindway.wsgi.application'

# --- Simplified Database Configuration ---
# Uses dj-database-url to parse the DATABASE_URL from .env or Vercel
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,  # 10 min persistent connection
        ssl_require=True   # Neon requires SSL
    )
}

# --- Security ---
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'http://127.0.0.1',
    'http://localhost',
]

# --- Allauth & Users Configuration (Updated to fix warnings) ---
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
    'allauth.account.auth_backends.AuthenticationBackend'
]

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'index'

# --- Allauth settings (Cleaned up) ---
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_LOGIN_METHODS = ['email']          # <-- New, correct setting
ACCOUNT_SIGNUP_FIELDS = ['email']          # <-- New, correct setting
ACCOUNT_EMAIL_VERIFICATION = 'none'        # Was 'optional', 'none' is simpler
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_ALLOW_LOGIN_AS_STAFF = True
# --- (Old deprecated settings have been removed) ---

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES (S3 for Production, Local for Dev) ---
if DEBUG:
    # --- LOCAL DEVELOPMENT SETTINGS ---
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_dev') # Use a different root for dev
    
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

else:
    # --- PRODUCTION (S3 for Media, Vercel for Static) SETTINGS ---
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False # Don't overwrite files with the same name

    # STORAGES config tells Django what to use for media vs static
    STORAGES = {
        "default": {
            # Use S3 for all user-uploaded media files
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "LOCATION": "media", # Store media files in the /media/ folder in S3
        },
        "staticfiles": {
            # Use Vercel's default storage for static files
            # 'collectstatic' will dump files into STATIC_ROOT
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # URL to access MEDIA files (which are on S3)
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    
    # URL to access STATIC files (which are served by Vercel)
    STATIC_URL = '/static/' 
    # Directory where 'collectstatic' will put all files for Vercel to find
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Vercel's "Output Directory" in project settings should be "staticfiles"


# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey' 
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'your-default-email@example.com') 

# --- Database ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'