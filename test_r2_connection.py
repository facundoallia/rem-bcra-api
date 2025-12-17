#!/usr/bin/env python3
"""
test_r2_connection.py
--------------------
Diagnóstico de conexión a Cloudflare R2
"""

import boto3
from botocore.config import Config
import urllib3

# Deshabilitar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tus credenciales
ACCESS_KEY_ID = "b753044c51bbd1293e7319a2404eb964"
SECRET_ACCESS_KEY = "214e6763c4bb1a53657843b666ecb2ec5e37ab7e47b3a1922aa5512187181a02"
ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
# Probar con el formato de endpoint que usa Account ID
ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"
BUCKET_NAME = "rem-data"

print("=" * 70)
print("🔍 DIAGNÓSTICO CLOUDFLARE R2")
print("=" * 70)
print()
print(f"Endpoint:    {ENDPOINT}")
print(f"Access Key:  {ACCESS_KEY_ID[:10]}...")
print(f"Bucket:      {BUCKET_NAME}")
print()

# Crear cliente
config = Config(
    signature_version='s3v4',
    s3={'addressing_style': 'path'}
)

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
    region_name="auto",
    config=config,
    verify=False
)

print("✅ Cliente creado")
print()

# Test 1: Listar buckets
print("📋 Test 1: Listar buckets...")
try:
    response = s3.list_buckets()
    print(f"✅ Éxito! Buckets encontrados: {len(response['Buckets'])}")
    for bucket in response['Buckets']:
        print(f"   - {bucket['Name']}")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 2: Listar objetos del bucket
print(f"📋 Test 2: Listar objetos en '{BUCKET_NAME}'...")
try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=10)
    if 'Contents' in response:
        print(f"✅ Éxito! Objetos encontrados: {response['KeyCount']}")
        for obj in response.get('Contents', [])[:5]:
            print(f"   - {obj['Key']} ({obj['Size']} bytes)")
    else:
        print(f"✅ Bucket vacío (sin objetos)")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 3: Subir archivo de prueba
print("📋 Test 3: Subir archivo de prueba...")
try:
    test_content = '{"test": "hello from Python", "timestamp": "2025-12-17"}'
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key='test/hello.json',
        Body=test_content.encode('utf-8'),
        ContentType='application/json'
    )
    print(f"✅ Archivo de prueba subido exitosamente!")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 4: Leer archivo de prueba
print("📋 Test 4: Leer archivo de prueba...")
try:
    response = s3.get_object(Bucket=BUCKET_NAME, Key='test/hello.json')
    content = response['Body'].read().decode('utf-8')
    print(f"✅ Archivo leído: {content[:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 70)
