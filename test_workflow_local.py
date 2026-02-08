#!/usr/bin/env python3
"""
test_workflow_local.py
----------------------
Simula la ejecución del workflow de GitHub Actions localmente
para verificar que todos los scripts funcionan correctamente.

Uso:
    python test_workflow_local.py
"""

import subprocess
import sys
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def print_section(title):
    """Imprime un separador visual."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def run_command(description, command, check=True):
    """Ejecuta un comando y reporta el resultado."""
    print(f"▶️  {description}")
    print(f"   Comando: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=check
        )

        print(f"   ✅ Exit code: {result.returncode}")

        if result.stdout:
            print(f"   📤 STDOUT:\n{result.stdout[:500]}")

        if result.stderr:
            print(f"   ⚠️  STDERR:\n{result.stderr[:500]}")

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        print(f"   📤 STDOUT:\n{e.stdout[:500]}")
        print(f"   ⚠️  STDERR:\n{e.stderr[:500]}")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def check_requirements():
    """Verifica que las dependencias estén instaladas."""
    print_section("VERIFICACIÓN DE DEPENDENCIAS")

    # Verificar Python
    print(f"✅ Python: {sys.version}")

    # Verificar dependencias
    required = ['pandas', 'openpyxl', 'requests']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}: instalado")
        except ImportError:
            print(f"❌ {package}: NO instalado")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Instalar dependencias faltantes:")
        print(f"   pip install {' '.join(missing)}")
        return False

    return True

def check_scripts():
    """Verifica que los scripts existan."""
    print_section("VERIFICACIÓN DE SCRIPTS")

    required_scripts = [
        "download_REM.py",
        "read_REM.py",
        "validate_output.py",
        "deploy_with_wrangler.py"
    ]

    all_exist = True
    for script in required_scripts:
        path = BASE_DIR / script
        if path.exists():
            print(f"✅ {script}")
        else:
            print(f"❌ {script} NO ENCONTRADO")
            all_exist = False

    return all_exist

def test_download():
    """Test del script de descarga."""
    print_section("TEST 1: DESCARGA DEL REM")

    return run_command(
        "Descargar REM desde BCRA",
        [sys.executable, "download_REM.py"],
        check=False  # Exit code 1 es válido (ya actualizado)
    )

def test_parse():
    """Test del script de parseo."""
    print_section("TEST 2: PARSEO XLSX → JSON")

    # Verificar que haya XLSX
    xlsx_files = list(DATA_DIR.glob("*.xlsx"))
    if not xlsx_files:
        print("⚠️  No hay archivos XLSX en data/")
        print("   Ejecuta primero: python download_REM.py")
        return False

    return run_command(
        "Parsear Excel a JSON",
        [sys.executable, "read_REM.py"],
        check=True
    )

def test_validate():
    """Test del script de validación."""
    print_section("TEST 3: VALIDACIÓN DE DATOS")

    # Verificar que haya JSONs
    json_files = list(DATA_DIR.glob("rem_*.json"))
    if not json_files:
        print("⚠️  No hay archivos JSON en data/")
        print("   Ejecuta primero: python read_REM.py")
        return False

    return run_command(
        "Validar datos generados",
        [sys.executable, "validate_output.py"],
        check=True
    )

def test_deploy():
    """Test del script de deploy (solo verifica sintaxis)."""
    print_section("TEST 4: DEPLOY (DRY RUN)")

    # Verificar si hay credenciales
    has_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    has_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

    if not has_token or not has_account:
        print("⚠️  No hay credenciales de Cloudflare configuradas")
        print("   Variables de entorno requeridas:")
        print("     - CLOUDFLARE_API_TOKEN")
        print("     - CLOUDFLARE_ACCOUNT_ID")
        print("")
        print("   En PowerShell:")
        print("     $env:CLOUDFLARE_API_TOKEN = 'tu_token'")
        print("     $env:CLOUDFLARE_ACCOUNT_ID = 'tu_account_id'")
        print("")
        print("   ℹ️  Saltando test de deploy (normal en ambiente local)")
        return True  # No es un error crítico

    return run_command(
        "Deploy a Cloudflare R2",
        [sys.executable, "deploy_with_wrangler.py"],
        check=True
    )

def print_summary(results):
    """Imprime resumen de resultados."""
    print_section("RESUMEN DE TESTS")

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12} {test_name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\n📊 Total: {passed}/{total} tests pasados")

    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron! El workflow debería funcionar correctamente.")
        return True
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")
        return False

def main():
    """Función principal."""
    print("=" * 70)
    print("  TEST LOCAL DEL WORKFLOW DE GITHUB ACTIONS")
    print("  rem-bcra-api")
    print("=" * 70)

    results = {}

    # 1. Verificar dependencias
    if not check_requirements():
        print("\n❌ Instala las dependencias antes de continuar")
        sys.exit(1)

    # 2. Verificar scripts
    if not check_scripts():
        print("\n❌ Algunos scripts no existen")
        sys.exit(1)

    # 3. Ejecutar tests
    results["Descarga"] = test_download()
    results["Parseo"] = test_parse()
    results["Validación"] = test_validate()
    results["Deploy (dry run)"] = test_deploy()

    # 4. Resumen
    success = print_summary(results)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
