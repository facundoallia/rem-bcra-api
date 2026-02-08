#!/usr/bin/env python3
"""
download_REM.py - Descarga archivos REM del BCRA
-------------------------------------------------
1. Detecta la URL correcta del REM (nueva estructura 2026+)
2. Fallback a URL antigua si la nueva falla
3. Descarga el XLSX a data/ dentro de la carpeta del script
-------------------------------------------------
"""

import os
from datetime import datetime
from pathlib import Path
import requests
import warnings
import time

# Suprimir warnings de SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

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

# Headers para evitar bloqueos del servidor
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def url_rem_nueva(year, month):
    """
    URL NUEVA (desde enero 2026):
    https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx
    """
    mes_txt = MESES[month]
    return f"https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-{mes_txt}-{year}.xlsx"

def url_rem_antigua(year, month):
    """
    URL ANTIGUA (hasta diciembre 2025):
    https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-dic-2025.xlsx
    """
    mes_txt = MESES[month]
    return f"https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-{mes_txt}-{year}.xlsx"

def safe_head(url, headers=None):
    """HEAD request con retry y mejor manejo de errores."""
    try:
        response = requests.head(
            url,
            headers=headers or HEADERS,
            timeout=15,
            verify=False,
            allow_redirects=True
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"⚠  Error HEAD {url}: {e}")
        return None

def safe_get(url, headers=None, retries=3):
    """GET request con retry y mejor manejo de errores."""
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers=headers or HEADERS,
                timeout=60,
                verify=False,
                allow_redirects=True,
                stream=True
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"⚠  Intento {attempt + 1}/{retries} falló: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"❌ Error GET después de {retries} intentos: {e}")
                return None
    return None

def find_latest_rem_url():
    """
    Busca la URL más reciente del REM.
    Prueba primero la nueva estructura (2026+), luego fallback a la antigua.

    IMPORTANTE: El REM se publica con 1 mes de retraso.
    Por ejemplo, en febrero 2026 el REM más reciente es enero 2026.
    """
    today = datetime.today()
    year = today.year
    month = today.month

    # Candidatos: empezar desde mes ANTERIOR (el REM se publica con 1 mes de retraso)
    candidatos = [
        (year, month - 1),  # Mes anterior (lo más reciente que puede existir)
        (year, month - 2),  # 2 meses atrás
        (year, month - 3),  # 3 meses atrás (por seguridad)
    ]

    # Ajustar para enero/febrero/marzo
    if month == 1:
        candidatos = [
            (year - 1, 12),  # Diciembre año anterior
            (year - 1, 11),  # Noviembre año anterior
            (year - 1, 10),  # Octubre año anterior
        ]
    elif month == 2:
        candidatos = [
            (year, 1),       # Enero año actual
            (year - 1, 12),  # Diciembre año anterior
            (year - 1, 11),  # Noviembre año anterior
        ]
    elif month == 3:
        candidatos = [
            (year, 2),       # Febrero año actual
            (year, 1),       # Enero año actual
            (year - 1, 12),  # Diciembre año anterior
        ]

    print(f"📅 Fecha actual: {today.strftime('%Y-%m-%d')} ({MESES[month].capitalize()} {year})")
    print(f"ℹ️  El REM se publica con 1 mes de retraso")
    print(f"🔍 Buscando REM más reciente (desde {MESES[candidatos[0][1]].capitalize()} {candidatos[0][0]})...\n")

    urls_probadas = []

    for y, m in candidatos:
        # Ajustar año/mes si es necesario
        if m <= 0:
            y -= 1
            m = 12 + m

        # Probar PRIMERO nueva URL (desde enero 2026)
        url_nueva = url_rem_nueva(y, m)
        print(f"   Probando (nueva): {url_nueva}")
        r = safe_head(url_nueva)

        if r and r.status_code == 200:
            print(f"   ✅ Archivo REM encontrado (URL nueva)")
            print(f"   📍 {url_nueva}\n")
            return url_nueva
        else:
            status = r.status_code if r else "No response"
            print(f"   ❌ No encontrado (status: {status})")
            urls_probadas.append((url_nueva, status))

        # Fallback a URL antigua (hasta diciembre 2025)
        url_antigua = url_rem_antigua(y, m)
        print(f"   Probando (antigua): {url_antigua}")
        r = safe_head(url_antigua)

        if r and r.status_code == 200:
            print(f"   ✅ Archivo REM encontrado (URL antigua)")
            print(f"   📍 {url_antigua}\n")
            return url_antigua
        else:
            status = r.status_code if r else "No response"
            print(f"   ❌ No encontrado (status: {status})\n")
            urls_probadas.append((url_antigua, status))

    # Si no se encontró nada, mostrar todas las URLs probadas
    print("=" * 70)
    print("❌ No se encontró ningún archivo REM válido")
    print("=" * 70)
    print("\nURLs probadas:")
    for url, status in urls_probadas:
        print(f"  - {url}")
        print(f"    Status: {status}\n")

    raise RuntimeError(
        "No se encontró ningún archivo REM válido. "
        "Posibles causas:\n"
        "  1. BCRA aún no publicó el REM del mes actual\n"
        "  2. BCRA cambió la estructura de URLs nuevamente\n"
        "  3. Problemas de conectividad con bcra.gob.ar"
    )

def descargar_archivo(url):
    """
    Descarga archivo solo si no existe o es diferente.
    Usa headers mejorados y retry logic.
    """
    filename = os.path.basename(url)
    filepath = DATA_DIR / filename

    print(f"\n📂 Archivo destino: {filename}")

    # Verificar si ya existe el archivo
    if filepath.exists():
        print(f"ℹ️  El archivo ya existe localmente")
        print(f"   Verificando si es la versión más reciente...")

        # Hacer HEAD request para obtener tamaño del archivo remoto
        r = safe_head(url)
        if r and r.status_code == 200:
            remote_size = int(r.headers.get('Content-Length', 0))
            local_size = filepath.stat().st_size

            print(f"   Tamaño local:  {local_size:,} bytes")
            print(f"   Tamaño remoto: {remote_size:,} bytes")

            if remote_size > 0 and remote_size == local_size:
                print(f"   ✅ Archivo ya está actualizado (mismo tamaño)")
                print(f"   No es necesario descargar de nuevo.\n")
                return filepath, False  # False = no hubo descarga nueva
            else:
                print(f"   ⚠️  Tamaño diferente, descargando nueva versión...")
        else:
            print(f"   ⚠️  No se pudo verificar tamaño remoto")
            print(f"   Descargando por seguridad...")

    print(f"\n📥 Descargando desde BCRA...")
    print(f"   URL: {url}")

    r = safe_get(url)

    if not r:
        raise RuntimeError(
            f"No se pudo descargar el archivo después de varios intentos.\n"
            f"URL: {url}\n"
            f"Verifica:\n"
            f"  1. Conectividad a internet\n"
            f"  2. Acceso a bcra.gob.ar\n"
            f"  3. Que el archivo exista en el servidor"
        )

    if r.status_code != 200:
        raise RuntimeError(
            f"Error HTTP {r.status_code} al descargar el archivo.\n"
            f"URL: {url}\n"
            f"Respuesta: {r.text[:200] if r.text else 'Sin contenido'}"
        )

    # Descargar contenido
    content = r.content

    if len(content) == 0:
        raise RuntimeError(f"El archivo descargado está vacío (0 bytes)")

    # Guardar archivo
    with open(filepath, "wb") as f:
        f.write(content)

    print(f"   ✅ Descarga exitosa")
    print(f"   📁 Guardado en: {filepath}")
    print(f"   📊 Tamaño: {len(content):,} bytes\n")

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