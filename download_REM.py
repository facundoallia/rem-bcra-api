#!/usr/bin/env python3
"""
descargar_rem.py (con verify=False y ruta absoluta segura)
----------------------------------
1. Detecta la URL correcta del REM
2. Descarga el XLSX a data/ dentro de la carpeta del script
----------------------------------
"""

import os
from datetime import datetime
from pathlib import Path
import requests

# -------------------------------
# CONFIG: directorio seguro
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MESES = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr",
    5: "may", 6: "jun", 7: "jul", 8: "ago",
    9: "sep", 10: "oct", 11: "nov", 12: "dic"
}

def url_rem(year, month):
    mes_txt = MESES[month]
    return f"https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-{mes_txt}-{year}.xlsx"

def safe_head(url):
    try:
        return requests.head(url, timeout=10, verify=False)
    except Exception as e:
        print(f"⚠ Error HEAD {url}: {e}")
        return None

def safe_get(url):
    try:
        return requests.get(url, timeout=60, verify=False)
    except Exception as e:
        print(f"⚠ Error GET {url}: {e}")
        return None

def find_latest_rem_url():
    today = datetime.today()
    year = today.year
    month = today.month

    candidatos = [(year, month - 1), (year, month - 2)]

    if month == 1:
        candidatos.append((year - 1, 12))
        candidatos.append((year - 1, 11))

    urls_a_probar = []

    for y, m in candidatos:
        if m <= 0:
            y -= 1
            m = 12
        urls_a_probar.append(url_rem(y, m))

    for u in urls_a_probar:
        print(f"Probando URL: {u}")
        r = safe_head(u)
        if r and r.status_code == 200:
            print(f"✔ Archivo REM encontrado: {u}")
            return u

    raise RuntimeError("No se encontró ningún archivo REM válido.")

def descargar_archivo(url):
    """Descarga archivo solo si no existe o es diferente."""
    filename = os.path.basename(url)
    filepath = DATA_DIR / filename
    
    # Verificar si ya existe el archivo
    if filepath.exists():
        print(f"ℹ️  El archivo ya existe: {filename}")
        print(f"   Verificando si es la versión más reciente...")
        
        # Hacer HEAD request para obtener tamaño del archivo remoto
        r = safe_head(url)
        if r:
            remote_size = int(r.headers.get('Content-Length', 0))
            local_size = filepath.stat().st_size
            
            if remote_size == local_size:
                print(f"✅ Archivo ya está actualizado (mismo tamaño: {local_size} bytes)")
                print(f"   No es necesario descargar de nuevo.")
                return filepath, False  # False = no hubo descarga nueva
            else:
                print(f"⚠️  Tamaño diferente: Local={local_size}, Remoto={remote_size}")
                print(f"   Descargando nueva versión...")
        else:
            print(f"⚠️  No se pudo verificar tamaño remoto, descargando por seguridad...")
    
    print(f"📥 Descargando: {url}")
    r = safe_get(url)
    if not r or r.status_code != 200:
        raise RuntimeError(f"No se pudo descargar el archivo desde: {url}")

    with open(filepath, "wb") as f:
        f.write(r.content)

    print(f"✅ Archivo descargado correctamente en: {filepath}")
    print(f"   Tamaño: {len(r.content)} bytes")
    return filepath, True  # True = archivo nuevo descargado

def main():
    print("=" * 70)
    print("DESCARGA REM - BCRA")
    print("=" * 70)
    print()
    
    try:
        url = find_latest_rem_url()
        filepath, es_nuevo = descargar_archivo(url)
        
        print()
        print("=" * 70)
        if es_nuevo:
            print("✅ DESCARGA EXITOSA - ARCHIVO NUEVO")
            print("   Se debe ejecutar el parser y deploy.")
            return 0  # Exit code 0 = nuevo archivo
        else:
            print("ℹ️  ARCHIVO YA ESTABA ACTUALIZADO")
            print("   No es necesario procesar de nuevo.")
            return 1  # Exit code 1 = no hay cambios
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        return 2  # Exit code 2 = error

if __name__ == "__main__":
    import sys
    sys.exit(main())
# ---------------------------------------------