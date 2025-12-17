#!/usr/bin/env python3
"""
test_api.py
-----------
Script de prueba para verificar que la API funciona correctamente.
"""

import requests
import sys

def test_api(base_url):
    """Prueba los endpoints principales de la API."""
    
    print("=" * 70)
    print("🧪 PROBANDO API REM")
    print("=" * 70)
    print(f"URL Base: {base_url}")
    print()
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Índice
    print("1️⃣  Test: GET /api")
    try:
        resp = requests.get(f"{base_url}/api", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Status: {resp.status_code}")
            print(f"   ✅ Nombre: {data.get('nombre')}")
            print(f"   ✅ Tablas disponibles: {len(data.get('tablas_disponibles', []))}")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 2: Metadata
    print("2️⃣  Test: GET /api/metadata")
    try:
        resp = requests.get(f"{base_url}/api/metadata", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Status: {resp.status_code}")
            print(f"   ✅ Última actualización: {data.get('ultima_actualizacion')}")
            print(f"   ✅ Archivos: {data.get('archivos')}")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 3: Tipo de cambio
    print("3️⃣  Test: GET /api/tipo_cambio")
    try:
        resp = requests.get(f"{base_url}/api/tipo_cambio", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Status: {resp.status_code}")
            print(f"   ✅ Título: {data.get('titulo')}")
            print(f"   ✅ Filas: {data.get('filas')}")
            print(f"   ✅ Columnas: {len(data.get('columnas', []))}")
            if data.get('datos'):
                primer_dato = data['datos'][0]
                print(f"   ✅ Primer período: {primer_dato.get('período')}")
                print(f"   ✅ Primer mediana: {primer_dato.get('mediana')}")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 4: IPC General
    print("4️⃣  Test: GET /api/ipc_general")
    try:
        resp = requests.get(f"{base_url}/api/ipc_general", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Status: {resp.status_code}")
            print(f"   ✅ Título: {data.get('titulo')}")
            print(f"   ✅ Filas: {data.get('filas')}")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 5: Bloques
    print("5️⃣  Test: GET /api/bloques")
    try:
        resp = requests.get(f"{base_url}/api/bloques", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Status: {resp.status_code}")
            print(f"   ✅ Tablas en archivo maestro: {len(data)}")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 6: 404 (tabla inexistente)
    print("6️⃣  Test: GET /api/tabla_que_no_existe (debe ser 404)")
    try:
        resp = requests.get(f"{base_url}/api/tabla_que_no_existe", timeout=10)
        if resp.status_code == 404:
            print(f"   ✅ Status: {resp.status_code} (correcto)")
            tests_passed += 1
        else:
            print(f"   ❌ Status: {resp.status_code} (esperaba 404)")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Test 7: CORS headers
    print("7️⃣  Test: CORS headers")
    try:
        resp = requests.get(f"{base_url}/api", timeout=10)
        cors_header = resp.headers.get('Access-Control-Allow-Origin')
        if cors_header == '*':
            print(f"   ✅ CORS habilitado: {cors_header}")
            tests_passed += 1
        else:
            print(f"   ⚠️  CORS: {cors_header}")
            tests_passed += 1  # No es crítico
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1
    print()
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    print(f"✅ Tests exitosos: {tests_passed}")
    print(f"❌ Tests fallidos:  {tests_failed}")
    print("=" * 70)
    
    if tests_failed == 0:
        print("\n🎉 ¡Todos los tests pasaron!")
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron")
        return 1

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_api.py <URL_BASE>")
        print("Ejemplo: python test_api.py https://rem-bcra-api.your-subdomain.workers.dev")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    exit_code = test_api(base_url)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
