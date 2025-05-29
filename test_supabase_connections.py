#!/usr/bin/env python
import psycopg2
import os

# Test different Supabase connection configurations

configs = [
    {
        'name': 'Pooler (Port 5432)',
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': '5432',
    },
    {
        'name': 'Pooler (Port 6543)', 
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': '6543',
    },
    {
        'name': 'Direct Connection (try this host format)',
        'host': 'db.owqvarxnrapljqejlypk.supabase.co',
        'port': '5432',
    }
]

common_params = {
    'database': 'postgres',
    'user': 'postgres.owqvarxnrapljqejlypk',
    'password': 'KopiSusuForji',
    'sslmode': 'require'
}

print("Testing different Supabase connection configurations...\n")

for config in configs:
    print(f"Testing: {config['name']}")
    print(f"Host: {config['host']}, Port: {config['port']}")
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            **common_params
        )
        print("✅ SUCCESS - Connection established!")
        conn.close()
        print(f"Use this configuration in your settings:\nHOST: {config['host']}\nPORT: {config['port']}\n")
        break
    except Exception as e:
        print(f"❌ FAILED - {e}")
    
    print("-" * 50)

print("\nIf none work, you need to check your Supabase dashboard for the correct connection details.")
print("Look for 'Direct Connection' settings, not the pooler URL.")
