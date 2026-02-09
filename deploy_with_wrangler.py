#!/usr/bin/env python3
"""
deploy_with_wrangler.py
-----------------------
Sube archivos JSON a Cloudflare R2 usando Wrangler CLI
Estructura: data/YYYY/MM/rem_*.json
Multiplataforma: Windows y Linux
"""

import os
import subprocess
import sys
import platform
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Configuración de Cloudflare - USAR VARIABLES DE ENTORNO
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
API_KEY = os.environ.get("CLOUDFLARE_API_KEY")  # Global API Key (alternativa)
EMAIL = os.environ.get("CLOUDFLARE_EMAIL")  # Email (solo con API Key)
ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
BUCKET_NAME = "rem-data"

# Verificar que tengamos credenciales válidas (API Token O API Key+Email)
if not ACCOUNT_ID:
    print("❌ ERROR: Variable de entorno CLOUDFLARE_ACCOUNT_ID requerida")
    sys.exit(1)

if not API_TOKEN and not (API_KEY and EMAIL):
    print("❌ ERROR: Credenciales de Cloudflare requeridas")
    print("")
    print("Opción 1 - API Token (recomendado):")
    print("  $env:CLOUDFLARE_API_TOKEN = 'tu_token_aqui'")
    print("  $env:CLOUDFLARE_ACCOUNT_ID = 'tu_account_id_aqui'")
    print("")
    print("Opción 2 - Global API Key:")
    print("  $env:CLOUDFLARE_API_KEY = 'tu_api_key_aqui'")
    print("  $env:CLOUDFLARE_EMAIL = 'tu_email_aqui'")
    print("  $env:CLOUDFLARE_ACCOUNT_ID = 'tu_account_id_aqui'")
    sys.exit(1)

def get_publication_date():
    """
    Detecta la fecha de publicación del REM desde el nombre del archivo XLSX.
    Retorna (año, mes) como strings.
    """
    xlsx_files = list(DATA_DIR.glob("*.xlsx"))
    if not xlsx_files:
        # Fallback a fecha actual
        now = datetime.now()
        return str(now.year), f"{now.month:02d}"
    
    # Buscar patrón en nombre de archivo: "nov-2025" o "2025-11"
    filename = xlsx_files[0].stem.lower()
    
    # Mapeo de meses en español
    meses = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }
    
    # Intentar extraer año y mes del nombre
    for mes_nombre, mes_num in meses.items():
        if mes_nombre in filename:
            # Buscar año (4 dígitos)
            import re
            year_match = re.search(r'20\d{2}', filename)
            if year_match:
                year = year_match.group()
                return year, mes_num
    
    # Si no se encuentra, usar fecha actual
    now = datetime.now()
    return str(now.year), f"{now.month:02d}"

def setup_env():
    """Configura variables de entorno para wrangler (multiplataforma)."""
    # Configurar autenticación según método disponible
    if API_TOKEN:
        os.environ["CLOUDFLARE_API_TOKEN"] = API_TOKEN
        print("🔑 Usando API Token para autenticación")
    elif API_KEY and EMAIL:
        os.environ["CLOUDFLARE_API_KEY"] = API_KEY
        os.environ["CLOUDFLARE_EMAIL"] = EMAIL
        print("🔑 Usando Global API Key para autenticación")

    os.environ["CLOUDFLARE_ACCOUNT_ID"] = ACCOUNT_ID

    # Agregar npm global a PATH (multiplataforma)
    if platform.system() == "Windows":
        # Windows: usar APPDATA
        npm_path = os.path.join(os.environ.get("APPDATA", ""), "npm")
        path_separator = ";"
    else:
        # Linux/Mac: paths comunes de npm
        npm_path = "/usr/local/bin"
        path_separator = ":"

    if npm_path and npm_path not in os.environ["PATH"]:
        os.environ["PATH"] = f"{npm_path}{path_separator}{os.environ['PATH']}"

def verify_authentication():
    """Verifica que la autenticación con Cloudflare funcione."""
    try:
        wrangler_cmd = "wrangler.cmd" if platform.system() == "Windows" else "wrangler"

        # Verificar que wrangler esté instalado
        version_cmd = [wrangler_cmd, "--version"]
        version_result = subprocess.run(
            version_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        print(f"✅ Wrangler version: {version_result.stdout.strip()}")

        # Listar buckets para verificar autenticación
        # Wrangler 4.x usa solo variables de entorno, no flags
        list_cmd = [wrangler_cmd, "r2", "bucket", "list"]

        list_result = subprocess.run(
            list_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            env=os.environ.copy()
        )

        print(f"✅ Autenticación exitosa")
        print(f"   Account ID: {ACCOUNT_ID[:8]}...")

        # Verificar que el bucket existe
        list_stdout = list_result.stdout or ""
        if BUCKET_NAME in list_stdout:
            print(f"✅ Bucket '{BUCKET_NAME}' encontrado")
            return True
        else:
            print(f"⚠️  Advertencia: Bucket '{BUCKET_NAME}' no encontrado en la lista")
            print(f"   Buckets disponibles:")
            print(f"   {list_stdout}")
            return True  # Continuar de todos modos

    except subprocess.CalledProcessError as e:
        print(f"❌ Error de autenticación:")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        print()
        print("Verifica:")
        print(f"   - CLOUDFLARE_ACCOUNT_ID: {ACCOUNT_ID[:8] if ACCOUNT_ID else 'NO SET'}...")
        if API_TOKEN:
            print(f"   - CLOUDFLARE_API_TOKEN: {'SET' if API_TOKEN else 'NO SET'} (length: {len(API_TOKEN) if API_TOKEN else 0})")
        else:
            print(f"   - CLOUDFLARE_API_KEY: {'SET' if API_KEY else 'NO SET'} (length: {len(API_KEY) if API_KEY else 0})")
            print(f"   - CLOUDFLARE_EMAIL: {EMAIL if EMAIL else 'NO SET'}")
        return False
    except FileNotFoundError:
        print(f"❌ Wrangler no encontrado")
        return False

def upload_file_with_wrangler(local_path, object_key):
    """Sube un archivo usando wrangler CLI (multiplataforma)."""
    try:
        # Comando de wrangler según el sistema operativo
        if platform.system() == "Windows":
            # Windows: usar wrangler.cmd
            wrangler_cmd = "wrangler.cmd"
        else:
            # Linux/Mac: usar wrangler directamente
            wrangler_cmd = "wrangler"

        # Wrangler 4.x usa solo variables de entorno para account-id
        cmd = [
            wrangler_cmd, "r2", "object", "put",
            f"{BUCKET_NAME}/{object_key}",
            f"--file={local_path}",
            "--remote"  # IMPORTANTE: subir al bucket remoto, no local
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            env=os.environ.copy()  # Asegurar que se pasen las variables de entorno
        )

        return True
    except subprocess.CalledProcessError as e:
        print(f"      Error stdout: {e.stdout[:200]}")
        print(f"      Error stderr: {e.stderr[:200]}")
        return False
    except FileNotFoundError:
        print(f"      Error: wrangler no encontrado en PATH")
        print(f"      Sistema: {platform.system()}")
        print(f"      PATH: {os.environ.get('PATH', '')[:200]}")
        return False

def deploy():
    """Ejecuta el deploy completo."""
    print("=" * 70)
    print("🚀 DEPLOY A CLOUDFLARE R2 (WRANGLER)")
    print("=" * 70)
    print()

    # Setup
    setup_env()

    # Verificar autenticación
    print("🔐 Verificando autenticación con Cloudflare...")
    print("-" * 70)
    if not verify_authentication():
        print()
        print("❌ Falló la verificación de autenticación")
        sys.exit(1)
    print("-" * 70)
    print()

    # Detectar fecha de publicación
    year, month = get_publication_date()
    print(f"📅 Fecha detectada: {year}/{month}")
    print()
    
    # Verificar archivos
    if not DATA_DIR.exists():
        print("❌ No existe directorio data/")
        sys.exit(1)
    
    json_files = list(DATA_DIR.glob("rem_*.json"))
    if not json_files:
        print("❌ No hay archivos JSON para subir")
        sys.exit(1)
    
    print(f"📦 Archivos a subir: {len(json_files)}")
    print(f"📍 Destino: data/{year}/{month}/")
    print()
    
    # Subir archivos
    print("📤 Subiendo archivos...")
    print("-" * 70)
    
    exitosos = 0
    fallidos = 0
    
    for json_file in json_files:
        # Subir a data/YYYY/MM/filename.json en R2
        object_key = f"data/{year}/{month}/{json_file.name}"
        print(f"  Subiendo {json_file.name}... ", end="", flush=True)
        
        if upload_file_with_wrangler(json_file, object_key):
            print("✅")
            exitosos += 1
        else:
            print("❌")
            fallidos += 1
    
    print("-" * 70)
    
    # Generar y subir metadata
    print()
    print("📋 Generando metadata...")
    
    metadata = {
        "ultima_actualizacion": datetime.now().isoformat() + "Z",
        "año": year,
        "mes": month,
        "periodo": f"{year}-{month}",
        "archivos": [f"data/{year}/{month}/{f.name}" for f in json_files],
        "total_archivos": len(json_files),
        "version": "1.0"
    }
    
    metadata_file = DATA_DIR / "_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Subir metadata al período específico Y a la raíz para "latest"
    print(f"  Subiendo metadata periodo... ", end="", flush=True)
    if upload_file_with_wrangler(metadata_file, f"data/{year}/{month}/_metadata.json"):
        print("✅")
        exitosos += 1
    else:
        print("❌")
        fallidos += 1
    
    print(f"  Subiendo metadata latest... ", end="", flush=True)
    if upload_file_with_wrangler(metadata_file, "data/latest/_metadata.json"):
        print("✅")
        exitosos += 1
    else:
        print("❌")
        fallidos += 1
    
    # Copiar todos los archivos también a latest/
    print()
    print("📋 Copiando a latest/...")
    for json_file in json_files:
        object_key = f"data/latest/{json_file.name}"
        print(f"  {json_file.name}... ", end="", flush=True)
        
        if upload_file_with_wrangler(json_file, object_key):
            print("✅")
            exitosos += 1
        else:
            print("❌")
            fallidos += 1
    
    # Resumen
    print()
    print("=" * 70)
    print("📊 RESUMEN DEL DEPLOY")
    print("=" * 70)
    print(f"  ✅ Exitosos: {exitosos}")
    print(f"  ❌ Fallidos:  {fallidos}")
    print()
    
    if fallidos == 0:
        print("🎉 Deploy completado exitosamente!")
        print()
        print("📍 URLs públicas:")
        print(f"   https://pub-<subdomain>.r2.dev/data/_metadata.json")
        print(f"   https://pub-<subdomain>.r2.dev/data/rem_bloques.json")
        print()
        print("⚠️  Nota: Debes configurar un dominio público en Cloudflare R2")
        print("   Dashboard → R2 → rem-data → Settings → Public Access")
        return 0
    else:
        print("⚠️  Deploy completado con errores")
        return 1

if __name__ == "__main__":
    sys.exit(deploy())
