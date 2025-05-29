#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_clinic.settings')

# Add project directory to path (for production)
project_home = '/home/dermada/pet_clinic'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables (same as WSGI)
os.environ['DB_HOST'] = 'aws-0-ap-southeast-1.pooler.supabase.com'
os.environ['DB_NAME'] = 'postgres'
os.environ['DB_USER'] = 'postgres.owqvarxnrapljqejlypk'
os.environ['DB_PASSWORD'] = 'KopiSusuForji'
os.environ['DB_PORT'] = '5432'

django.setup()

from django.conf import settings

print("=== Database Configuration Debug ===")
print(f"Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
print(f"Database Name: {settings.DATABASES['default']['NAME']}")
print(f"Database User: {settings.DATABASES['default']['USER']}")
print(f"Database Host: {settings.DATABASES['default']['HOST']}")
print(f"Database Port: {settings.DATABASES['default']['PORT']}")

print("\n=== Environment Variables ===")
for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
    print(f"{key}: {os.environ.get(key, 'NOT SET')}")

print("\n=== Testing Database Connection ===")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ Database connection successful!")
        print(f"Connected to: {connection.settings_dict['HOST']}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
