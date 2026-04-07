import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()] or (['*'] if DEBUG else [])

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'corsheaders',
    'accounts',
    'circles',
    'events',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PG_NAME', 'circles_db'),
        'USER': os.environ.get('PG_USER', 'circleapp'),
        'PASSWORD': os.environ.get('PG_PASSWORD', ''),
        'HOST': os.environ.get('PG_HOST', 'localhost'),
        'PORT': os.environ.get('PG_PORT', '5432'),
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Cache (used for login rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_FAILURE_VIEW = 'project.utils.csrf_failure_view'

frontend_url = os.environ.get('FRONTEND_URL', '')
app_url = os.environ.get('APP_URL', '')
CSRF_TRUSTED_ORIGINS = [u for u in [frontend_url, app_url] if u] + [
    'https://*.preview.emergentagent.com',
    'https://*.preview.emergentcf.cloud',
    'https://*.emergentcf.cloud',
    'http://localhost:3000',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.preview\.emergentagent\.com$',
    r'^https://.*\.preview\.emergentcf\.cloud$',
    r'^https://.*\.emergentcf\.cloud$',
    r'^http://localhost:\d+$',
]

USE_X_FORWARDED_HOST = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True
TIME_ZONE = 'UTC'
APPEND_SLASH = True

# Rate limiting: max login attempts per IP+email in a window
LOGIN_RATE_LIMIT_MAX = int(os.environ.get('LOGIN_RATE_LIMIT_MAX', '10'))
LOGIN_RATE_LIMIT_WINDOW = int(os.environ.get('LOGIN_RATE_LIMIT_WINDOW', '300'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}
