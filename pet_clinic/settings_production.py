from .settings import *

# Production-specific settings
DEBUG = False

# Allow Koyeb hosts
ALLOWED_HOSTS = ['*']  # For Koyeb deployment

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = '/workspace/staticfiles'  # Koyeb workspace path

# Use only main/static to avoid duplicate files
STATICFILES_DIRS = [
    BASE_DIR / 'main' / 'static',
]

# Add whitenoise middleware for serving static files in production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Force PostgreSQL database for production - Use direct connection instead of pooler
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.owqvarxnrapljqejlypk',
        'PASSWORD': 'KopiSusuForji',
        'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',  # Try direct connection
        'PORT': '6543',  # Direct connection port (not pooler)
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
