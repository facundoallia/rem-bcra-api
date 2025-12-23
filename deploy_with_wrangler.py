#!/usr/bin/env python3
"""
deploy_with_wrangler.py
-----------------------
Sube archivos JSON a Cloudflare R2 usando Wrangler CLI
Estructura: data/YYYY/MM/rem_*.json
"""

import os
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Configuración de Cloudflare - USAR VARIABLES DE ENTORNO
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
BUCKET_NAME = "rem-data"

if not API_TOKEN or not ACCOUNT_ID:
    print("❌ ERROR: Variables de entorno CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID requeridas")
    print("")
    print("En PowerShell:")
    print("  $env:CLOUDFLARE_API_TOKEN = 'tu_token_aqui'")
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
    """Configura variables de entorno para wrangler."""
    os.environ["CLOUDFLARE_API_TOKEN"] = API_TOKEN
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = ACCOUNT_ID
    # Agregar npm global a PATH
    npm_path = os.path.join(os.environ["APPDATA"], "npm")
    if npm_path not in os.environ["PATH"]:
        os.environ["PATH"] = f"{npm_path};{os.environ['PATH']}"

def upload_file_with_wrangler(local_path, object_key):
    """Sube un archivo usando wrangler CLI."""
    try:
        # Usar wrangler.cmd en Windows
        wrangler_cmd = os.path.join(os.environ["APPDATA"], "npm", "wrangler.cmd")
        
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
            check=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"      Error: {e.stderr[:100]}")
        return False
    except FileNotFoundError:
        print(f"      Error: wrangler no encontrado en PATH")
        return False

def deploy():
    """Ejecuta el deploy completo."""
    print("=" * 70)
    print("🚀 DEPLOY A CLOUDFLARE R2 (WRANGLER)")
    print("=" * 70)
    print()
    
    # Setup
    setup_env()
    
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
