#!/usr/bin/env python3
"""
deploy_to_cloudflare.py
-----------------------
Sube los archivos JSON a Cloudflare R2 después de procesar.
Requiere: pip install boto3
Configurar variables de entorno:
  - CF_ACCOUNT_ID
  - CF_ACCESS_KEY_ID
  - CF_SECRET_ACCESS_KEY
  - CF_BUCKET_NAME
"""

import os
import sys
from pathlib import Path
import json
import boto3
from botocore.config import Config
import urllib3
from datetime import datetime

# Deshabilitar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Configuración de Cloudflare R2
ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "b716491d6afe361dba0e016519df6cb3")
ACCESS_KEY_ID = os.environ.get("CF_ACCESS_KEY_ID", "b753044c51bbd1293e7319a2404eb964")
SECRET_ACCESS_KEY = os.environ.get("CF_SECRET_ACCESS_KEY", "214e6763c4bb1a53657843b666ecb2ec5e37ab7e47b3a1922aa5512187181a02")
BUCKET_NAME = os.environ.get("CF_BUCKET_NAME", "rem-data")

def validate_config():
    """Valida que estén las variables de entorno necesarias."""
    missing = []
    if not ACCOUNT_ID:
        missing.append("CF_ACCOUNT_ID")
    if not ACCESS_KEY_ID:
        missing.append("CF_ACCESS_KEY_ID")
    if not SECRET_ACCESS_KEY:
        missing.append("CF_SECRET_ACCESS_KEY")
    
    if missing:
        print(f"❌ Faltan variables de entorno: {', '.join(missing)}")
        print("\nConfigura en GitHub Secrets:")
        print("  Settings → Secrets and variables → Actions → New repository secret")
        return False
    return True

def get_r2_client():
    """Crea cliente S3 compatible con R2."""
    # Endpoint específico de tu bucket
    endpoint_url = "https://b716491d6afe361dba0e016519df6cb3.r2.cloudflarestorage.com"
    
    # Configuración para deshabilitar verificación SSL (común en desarrollo local)
    config = Config(
        signature_version='s3v4',
        s3={'addressing_style': 'path'}
    )
    
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="auto",
        config=config,
        verify=False  # Deshabilitar verificación SSL
    )

def upload_file_to_r2(client, file_path, object_key):
    """Sube un archivo a R2."""
    try:
        # Leer archivo
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determinar content type
        content_type = 'application/json' if file_path.suffix == '.json' else 'application/octet-stream'
        
        # Subir
        client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=content,
            ContentType=content_type,
            CacheControl='public, max-age=3600'  # Cache 1 hora
        )
        
        return True
    except Exception as e:
        print(f"❌ Error subiendo {object_key}: {e}")
        return False

def deploy():
    """Ejecuta el deploy completo."""
    print("=" * 70)
    print("🚀 DEPLOY A CLOUDFLARE R2")
    print("=" * 70)
    print()
    
    # Validar configuración
    if not validate_config():
        sys.exit(1)
    
    # Verificar que existan archivos
    if not DATA_DIR.exists():
        print("❌ No existe directorio data/")
        sys.exit(1)
    
    json_files = list(DATA_DIR.glob("rem_*.json"))
    if not json_files:
        print("❌ No hay archivos JSON para subir")
        sys.exit(1)
    
    print(f"📦 Archivos a subir: {len(json_files)}")
    print()
    
    # Crear cliente R2
    try:
        r2 = get_r2_client()
        print("✅ Cliente R2 conectado")
    except Exception as e:
        print(f"❌ Error conectando a R2: {e}")
        sys.exit(1)
    
    # Verificar bucket (ya existe, no intentar crear)
    try:
        r2.head_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Bucket '{BUCKET_NAME}' existe")
    except Exception as e:
        print(f"⚠️  No se pudo verificar bucket (probablemente ya existe): {e}")
        print(f"   Continuando con el upload...")
    
    print()
    print("📤 Subiendo archivos...")
    print("-" * 70)
    
    # Subir cada archivo
    success_count = 0
    fail_count = 0
    
    for json_file in json_files:
        # Clave en R2: data/rem_xxx.json
        object_key = f"data/{json_file.name}"
        
        print(f"  Subiendo {json_file.name}...", end=" ")
        
        if upload_file_to_r2(r2, json_file, object_key):
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1
    
    print("-" * 70)
    
    # Crear y subir metadata
    metadata = {
        "ultima_actualizacion": datetime.utcnow().isoformat() + "Z",
        "archivos": len(json_files),
        "tablas": [f.stem.replace("rem_", "") for f in json_files if f.name != "rem_bloques.json"],
        "version": "1.0"
    }
    
    metadata_path = DATA_DIR / "_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"  Subiendo metadata...", end=" ")
    if upload_file_to_r2(r2, metadata_path, "data/_metadata.json"):
        print("✅")
        success_count += 1
    else:
        print("❌")
        fail_count += 1
    
    print()
    print("=" * 70)
    print(f"📊 RESUMEN DEL DEPLOY")
    print("=" * 70)
    print(f"  ✅ Exitosos: {success_count}")
    print(f"  ❌ Fallidos:  {fail_count}")
    print()
    
    if fail_count > 0:
        print("⚠️  Deploy completado con errores")
        sys.exit(1)
    else:
        print("✅ Deploy exitoso")
        print()
        print(f"🌐 Los datos están disponibles en:")
        print(f"   https://{BUCKET_NAME}.{ACCOUNT_ID}.r2.cloudflarestorage.com/data/rem_bloques.json")
        print()
        print("💡 Próximo paso: Configurar Cloudflare Worker para API pública")

if __name__ == "__main__":
    deploy()
