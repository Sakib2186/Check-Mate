"""
Django settings for check_mate project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'system_administrator',
    'sass_processor',
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

ROOT_URLCONF = 'check_mate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'check_mate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if(os.environ.get('SETTINGS')=='dev'):
    DATABASES = {
        'default': {
                    
            #Postgres in localhost
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DEV_DATABASE_NAME'),
            'USER': os.environ.get('DEV_DATABASE_USER'),
            'PASSWORD': os.environ.get('DEV_DATABASE_PASSWORD'),
            'HOST': os.environ.get('DEV_DATABASE_HOST'),
            'PORT':'', 
            

        }
    }
if(os.environ.get('SETTINGS')=='prod'):
    DATABASES = {
        
        # MySQL in Production
        'default': {
            
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': os.environ.get('PROD_DATABASE_NAME'),
            'USER': os.environ.get('PROD_DATABASE_USER'),
            'PASSWORD': os.environ.get('PROD_DATABASE_PASSWORD'),
            'HOST': os.environ.get('PROD_DATABASE_HOST'),
            'PORT': '3306',
            
        }
        
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


STATIC_URL = 'static/'
#static directory
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFIlES_DIRS=(os.path.join(BASE_DIR,'static/'))

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Media Files
MEDIA_ROOT= os.path.join(BASE_DIR, 'User Files/')
MEDIA_URL= "/media_files/" 

# RESIZING IMAGE
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_SCALE = 1.0
DJANGORESIZED_DEFAULT_QUALITY = 90
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

#EMAIL SETTINGS
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER=os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_PASSWORD')
EMAIL_USE_TLS=True

# SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Sessions expire when the browser is closed
# SESSION_COOKIE_AGE = 3600  # Set the session cookie to expire after a specific time (in seconds)

LOGIN_URL = '/users/login/'
LOGOUT_REDIRECT_URL='users:logoutUser'
LOGIN_URL='users:login'
