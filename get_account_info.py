#!/usr/bin/env python3
"""
Obtener Account ID de Cloudflare usando el API Token
"""

import requests
import json
import os
import sys

# Tu API Token de Cloudflare - USAR VARIABLE DE ENTORNO
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

if not API_TOKEN:
    print("❌ ERROR: Variable de entorno CLOUDFLARE_API_TOKEN requerida")
    print("")
    print("En PowerShell:")
    print("  $env:CLOUDFLARE_API_TOKEN = 'tu_token_aqui'")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🔍 OBTENER INFORMACIÓN DE CUENTA CLOUDFLARE")
print("=" * 70)
print()

# Obtener información de la cuenta
print("📋 Obteniendo Account ID...")
response = requests.get(
    "https://api.cloudflare.com/client/v4/accounts",
    headers=headers,
    verify=False
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        accounts = data.get('result', [])
        print(f"✅ Encontradas {len(accounts)} cuenta(s)")
        print()
        for acc in accounts:
            print(f"📌 Account ID: {acc['id']}")
            print(f"   Name: {acc['name']}")
            print()
            
            # Listar buckets R2 de esta cuenta
            print(f"   📦 Buckets R2 en esta cuenta:")
            r2_response = requests.get(
                f"https://api.cloudflare.com/client/v4/accounts/{acc['id']}/r2/buckets",
                headers=headers,
                verify=False
            )
            if r2_response.status_code == 200:
                r2_data = r2_response.json()
                if r2_data.get('success'):
                    buckets = r2_data.get('result', {}).get('buckets', [])
                    for bucket in buckets:
                        print(f"      - {bucket['name']}")
                        print(f"        Created: {bucket.get('creation_date', 'N/A')}")
                else:
                    print(f"      ❌ Error: {r2_data.get('errors')}")
            else:
                print(f"      ❌ Error HTTP {r2_response.status_code}")
    else:
        print(f"❌ Error en respuesta: {data.get('errors')}")
else:
    print(f"❌ Error HTTP {response.status_code}")
    print(f"   Response: {response.text[:200]}")

print()
print("=" * 70)
