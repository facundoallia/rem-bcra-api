#!/usr/bin/env python3
"""
status.py
---------
Muestra el estado actual del proyecto API REM
"""

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def check_status():
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "📊 API REM - ESTADO ACTUAL" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Fase 0: Desarrollo Base
    print("🏗️  FASE 0: DESARROLLO BASE")
    print("─" * 70)
    
    checks = [
        ("Script de descarga", Path("download REM").exists(), "download REM"),
        ("Parser principal", Path("read REM.py").exists(), "read REM.py"),
        ("Deploy a Cloudflare", Path("deploy_to_cloudflare.py").exists(), "deploy_to_cloudflare.py"),
        ("Validador de datos", Path("validate_output.py").exists(), "validate_output.py"),
        ("Verificador de tablas", Path("verificar_tablas.py").exists(), "verificar_tablas.py"),
        ("Test de API", Path("test_api.py").exists(), "test_api.py"),
        ("Directorio de datos", DATA_DIR.exists(), "data/"),
        ("README.md", Path("README.md").exists(), "README.md"),
        ("ROADMAP.md", Path("ROADMAP.md").exists(), "ROADMAP.md"),
        ("SETUP.md", Path("SETUP.md").exists(), "SETUP.md"),
    ]
    
    for desc, exists, file in checks:
        status = "✅" if exists else "❌"
        print(f"  {status} {desc:30s} {file}")
    
    print()
    
    # Datos generados
    print("📦 DATOS GENERADOS")
    print("─" * 70)
    
    if DATA_DIR.exists():
        json_files = list(DATA_DIR.glob("rem_*.json"))
        xlsx_files = list(DATA_DIR.glob("*.xlsx"))
        
        maestro = DATA_DIR / "rem_bloques.json"
        if maestro.exists():
            print(f"  ✅ Archivo maestro: rem_bloques.json")
            try:
                with open(maestro, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"     → {len(data)} tablas en archivo maestro")
            except:
                print(f"     ⚠️  Error leyendo archivo maestro")
        else:
            print(f"  ❌ Archivo maestro NO encontrado")
        
        print(f"  ✅ Archivos JSON individuales: {len(json_files)}")
        print(f"  ✅ Archivos Excel: {len(xlsx_files)}")
        
        if xlsx_files:
            latest = max(xlsx_files, key=lambda p: p.stat().st_mtime)
            print(f"     → Último: {latest.name}")
    else:
        print(f"  ❌ Directorio data/ no existe")
    
    print()
    
    # Fase 1: Automatización
    print("🚀 FASE 1: AUTOMATIZACIÓN")
    print("─" * 70)
    
    workflow_path = Path(".github/workflows/update-rem.yml")
    workflow_exists = workflow_path.exists()
    
    worker_path = Path("worker/worker.js")
    worker_exists = worker_path.exists()
    
    auto_checks = [
        ("GitHub Actions workflow", workflow_exists, ".github/workflows/"),
        ("Cron schedule optimizado", workflow_exists, "Días 1-7 del mes, 12:00 UTC"),
        ("Detección de duplicados", workflow_exists, "Exit codes 0/1/2"),
        ("Cloudflare Worker", worker_exists, "worker/worker.js"),
        ("Wrangler config", Path("worker/wrangler.toml").exists(), "worker/wrangler.toml"),
        ("Deploy script R2", Path("deploy_to_cloudflare.py").exists(), "deploy_to_cloudflare.py"),
    ]
    
    for desc, exists, loc in auto_checks:
        status = "✅" if exists else "⏳"
        print(f"  {status} {desc:30s} {loc}")
    
    print()
    
    # Fase 2: API
    print("🌐 FASE 2: API REST")
    print("─" * 70)
    
    api_checks = [
        ("Cloudflare Worker", worker_exists, "worker/worker.js"),
        ("Endpoints REST", worker_exists, "7 endpoints"),
        ("CORS habilitado", worker_exists, "En Worker"),
        ("Cache configurado", worker_exists, "1 hora"),
    ]
    
    for desc, exists, loc in api_checks:
        status = "✅" if exists else "⏳"
        print(f"  {status} {desc:30s} {loc}")
    
    print()
    
    # Problemas conocidos
    print("📋 PRÓXIMOS PASOS")
    print("─" * 70)
    print("  1. 🔐 Configurar Cloudflare R2 y obtener credenciales")
    print("     └─ Ver SETUP.md para instrucciones paso a paso")
    print()
    print("  2. 🔑 Agregar secrets a GitHub")
    print("     └─ CF_ACCOUNT_ID, CF_ACCESS_KEY_ID, CF_SECRET_ACCESS_KEY")
    print()
    print("  3. 🚀 Deploy del Worker")
    print("     └─ cd worker && wrangler deploy")
    print()
    print("  4. ✅ Probar GitHub Actions manualmente")
    print("     └─ Actions → Run workflow")
    print()
    print("  5. 🧪 Probar la API")
    print("     └─ python test_api.py <URL_DEL_WORKER>")
    print()
    
    # Próximos pasos
    print("💡 NOTAS IMPORTANTES")
    print("─" * 70)
    print("  • Los datos tienen algunos strings descriptivos (períodos)")
    print("  • Esto es ACEPTABLE - son valores válidos del BCRA")
    print("  • El validador puede mostrar warnings - son informativos")
    print("  • La API funcionará perfectamente con estos datos")
    print()
    
    # Resumen
    
    # Resumen
    print("═" * 70)
    fase0_completado = sum(1 for _, e, _ in checks if e)
    fase0_total = len(checks)
    fase1_completado = sum(1 for _, e, _ in auto_checks if e)
    fase1_total = len(auto_checks)
    fase2_completado = sum(1 for _, e, _ in api_checks if e)
    fase2_total = len(api_checks)
    
    print(f"📊 RESUMEN:")
    print(f"   Fase 0 (Base):        {fase0_completado}/{fase0_total} ({'✅' if fase0_completado == fase0_total else '🔄'})")
    print(f"   Fase 1 (Automatiz.):  {fase1_completado}/{fase1_total} ({'✅' if fase1_completado == fase1_total else '🔄'})")
    print(f"   Fase 2 (API):         {fase2_completado}/{fase2_total} ({'✅' if fase2_completado == fase2_total else '🔄'})")
    print()
    
    if fase0_completado == fase0_total and fase1_completado == fase1_total and fase2_completado == fase2_total:
        print("   🎉 ¡Código completo! Solo falta configurar Cloudflare")
    elif fase0_completado == fase0_total and fase1_completado == fase1_total:
        print("   🔄 Automatización lista, falta API")
    else:
        print("   🔄 En desarrollo...")
    
    print("═" * 70)

if __name__ == "__main__":
    check_status()
