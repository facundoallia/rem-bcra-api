#!/usr/bin/env python3
"""
Listar archivos en R2 usando la API de Cloudflare
"""

import requests
import json

API_TOKEN = "Cm8qe2j5U9GW5qncg-z6iGc7LAV58DYlve1Iyd_T"
ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
BUCKET_NAME = "rem-data"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets/{BUCKET_NAME}/objects"

print("=" * 70)
print("📦 ARCHIVOS EN R2 BUCKET: rem-data")
print("=" * 70)
print()

response = requests.get(url, headers=headers, verify=False, params={"per_page": 100})

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        objects = data.get('result', {}).get('objects', [])
        print(f"✅ Encontrados {len(objects)} archivos:")
        print()
        for obj in objects:
            key = obj.get('key', 'N/A')
            size = obj.get('size', 0)
            print(f"  📄 {key}")
            print(f"     Size: {size} bytes ({size/1024:.1f} KB)")
    else:
        print(f"❌ Error: {data.get('errors')}")
else:
    print(f"❌ HTTP {response.status_code}")
    print(f"Response: {response.text[:500]}")

print()
print("=" * 70)
