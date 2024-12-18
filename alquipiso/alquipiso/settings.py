"""
Django settings for alquipiso project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(!*d%n-f(9+kb6crztc+4yo++kyc*0^0l@-6uxx5zhnq1zn+pg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'modules.alquileres.apps.AlquileresConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'alquipiso.urls'

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
                'modules.alquileres.context_processors.notificaciones',
            ],
        },
    },
]

WSGI_APPLICATION = 'alquipiso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'alquipiso.db'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_REDIRECT_URL = 'alquileres:index'  # or the desired URL to redirect after login
LOGIN_URL = 'alquileres:login'

# URL for serving media files in development
MEDIA_URL = '/media/'
# The absolute filesystem path to the directory where media files will be stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STRIPE_SECRET_KEY = 'sk_test_51QPNbqFSJFG8C7sOxyEAUk2v9hbyiZuFDJPpqQdATQ1DhWZM58Z1eD1qzReX1HpmQiNjWHKWugPeeyv51yGRoHUE003juwGGeN'
STRIPE_PUBLIC_KEY = 'pk_test_51QPNbqFSJFG8C7sO5n4Ooe1Uc2sA827AuPqhc70kYNxiUhW9KW0uE4ccty8YV8v3WRdHjWfbZi2pFEC1XpZmLgRy00dsXZoUeZ'
STRIPE_ENDPOINT_SECRET = "whsec_MC7m9v4urGaQATOaYdviqNxmnisxkXdT"


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'alejandronb01@gmail.com'  
EMAIL_HOST_PASSWORD = 'vaby pfwy kepf czvw'  


CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',    # Asegúrate de que el puerto coincida con el puerto donde tu contenedor está ejecutándose
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',     # Si usas '0.0.0.0' para exponer el contenedor
]
