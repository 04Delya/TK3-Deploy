import psycopg2
import os

# Test database connection
try:
    conn = psycopg2.connect(
        host='aws-0-ap-southeast-1.pooler.supabase.com',
        database='postgres',
        user='postgres.owqvarxnrapljqejlypk',
        password='KopiSusuForji',
        port='5432',
        sslmode='require'
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
