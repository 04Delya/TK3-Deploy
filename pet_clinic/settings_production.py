from .settings import *

# Production-specific settings
DEBUG = False

# Database configuration for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.owqvarxnrapljqejlypk',
        'PASSWORD': 'KopiSusuForji',
        'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
