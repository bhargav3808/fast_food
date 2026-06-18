# fastfood_project/settings.py

import os
from pathlib import Path
import pymysql
pymysql.install_as_MySQLdb()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key' 
DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = 'fastfood_project.urls'
WSGI_APPLICATION = 'fastfood_project.wsgi.application'

# --- INSTALLED APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'food_app', 
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- TEMPLATES ---
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'fastfood_db',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }



# fastfood_db
# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- AUTHENTICATION ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# --- Added by assistant: ensure templates/static/media paths are configured ---
try:
    from pathlib import Path as _Path
    BASE_DIR = _Path(__file__).resolve().parent.parent
    # ensure TEMPLATES dirs include project and app templates
    if 'TEMPLATES' in globals():
        try:
            TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates', BASE_DIR / 'food_app' / 'templates']
        except Exception:
            pass
    STATIC_URL = globals().get('STATIC_URL', '/static/')
    STATICFILES_DIRS = globals().get('STATICFILES_DIRS', []) + [BASE_DIR / 'static']
    MEDIA_URL = globals().get('MEDIA_URL', '/media/')
    MEDIA_ROOT = globals().get('MEDIA_ROOT', BASE_DIR / 'media')
except Exception:
    pass

