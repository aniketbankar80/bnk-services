"""
Django settings for bnk_web project.

Generated by 'django-admin startproject' using Django 4.2.19.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-$&o0cuvz(0d$j*5&@8kzp$%k#bq*j1(l$fhm1tgnug@*n6@zzw')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'import_export',
    'django_cleanup.apps.CleanupConfig',
    'widget_tweaks',
    'debug_toolbar',
    'storages',
    'members',
    'admin_portal',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bnk_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bnk_web.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Storage Configuration
USE_S3 = os.getenv('USE_S3', 'False') == 'True'

if USE_S3:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_VERIFY = True
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # CORS Configuration
    AWS_S3_CORS_ALLOWED_ORIGINS = ['http://127.0.0.1:8000']
    AWS_S3_CORS_ALLOWED_METHODS = ['GET', 'HEAD', 'OPTIONS']
    AWS_S3_CORS_ALLOWED_HEADERS = ['*']
    AWS_S3_CORS_EXPOSE_HEADERS = ['ETag']
    AWS_S3_CORS_MAX_AGE_SECONDS = 86400
    
    # Content Type Settings
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
        'ContentDisposition': 'inline'
    }
    AWS_S3_USE_GZIP = True
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    
    # S3 Media Settings
    MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'bnk_web.storage_backends.MediaStorage'
    
    # File Upload Settings
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    MAX_UPLOAD_SIZE = 5242880  # 5MB
else:
    # Local Storage Settings
    MEDIA_URL = 'protected-media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    
    # Protect media files
    MEDIA_PROTECTED = True
    
    # Local Storage Organization
    CUSTOMER_DOCUMENT_PATH = 'customer_documents'
    LOAN_DOCUMENT_PATH = 'loan_documents'
    PAYOUT_DOCUMENT_PATH = 'payout_documents'
    
    # File Upload Settings
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    MAX_UPLOAD_SIZE = 5242880  # 5MB
    ALLOWED_UPLOAD_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']

# Backup Configuration
BACKUP_ROOT = BASE_DIR / 'backups'
BACKUP_COUNT = 30  # Number of backups to keep

# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'https://*.ngrok.app',
    'https://*.serveo.net',
    'https://bnk.rest'
]

# Additional CSRF Settings
CSRF_COOKIE_SECURE = False if DEBUG else True  # Only require secure cookies in production
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True

# Session Settings
SESSION_COOKIE_AGE = 86400 * 7  # 7 days in seconds
SESSION_COOKIE_SECURE = False if DEBUG else True  # Only require secure cookies in production
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
