#!/usr/bin/env python3
"""
verify_setup.py
---------------
Script de verificación que comprueba que todas las configuraciones
de seguridad y mejoras estén correctamente implementadas.
"""

import os
import sys
from pathlib import Path
import json

def print_header(text):
    """Imprime encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_env_vars():
    """Verifica que las variables de entorno estén configuradas."""
    print_header("🔐 VARIABLES DE ENTORNO")
    
    required_vars = {
        "CLOUDFLARE_API_TOKEN": "Token de API de Cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "Account ID de Cloudflare"
    }
    
    all_ok = True
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mostrar solo primeros/últimos caracteres por seguridad
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: NO CONFIGURADA")
            print(f"     Descripción: {description}")
            all_ok = False
    
    return all_ok

def check_files():
    """Verifica que los archivos críticos existan."""
    print_header("📁 ARCHIVOS CRÍTICOS")
    
    base_dir = Path(__file__).parent
    
    required_files = {
        ".env.example": "Plantilla de variables de entorno",
        "SECURITY.md": "Guía de seguridad",
        "SETUP_RATE_LIMITING.md": "Guía de rate limiting",
        "CHANGELOG.md": "Registro de cambios",
        "worker/worker.js": "Worker principal",
        "worker/wrangler.toml": "Configuración de Cloudflare",
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}: NO ENCONTRADO")
            print(f"     Descripción: {description}")
            all_ok = False
    
    return all_ok

def check_gitignore():
    """Verifica que .gitignore proteja archivos sensibles."""
    print_header("🔒 PROTECCIÓN .gitignore")
    
    base_dir = Path(__file__).parent
    gitignore_path = base_dir / ".gitignore"
    
    if not gitignore_path.exists():
        print("  ❌ .gitignore no encontrado")
        return False
    
    content = gitignore_path.read_text(encoding='utf-8')
    
    required_patterns = {
        ".env": "Variables de entorno",
        "*.log": "Archivos de log",
        "__pycache__": "Cache de Python",
        "node_modules": "Módulos de Node.js"
    }
    
    all_ok = True
    for pattern, description in required_patterns.items():
        if pattern in content:
            print(f"  ✅ {pattern} (protegido)")
        else:
            print(f"  ⚠️  {pattern}: No encontrado en .gitignore")
            print(f"     Descripción: {description}")
            all_ok = False
    
    return all_ok

def check_wrangler_config():
    """Verifica la configuración de wrangler.toml."""
    print_header("⚙️  CONFIGURACIÓN WRANGLER")
    
    base_dir = Path(__file__).parent
    wrangler_path = base_dir / "worker" / "wrangler.toml"
    
    if not wrangler_path.exists():
        print("  ❌ wrangler.toml no encontrado")
        return False
    
    content = wrangler_path.read_text(encoding='utf-8')
    
    checks = {
        'name = "bcra-rem-api"': "Nombre profesional del worker",
        "R2_BUCKET": "Binding de R2 bucket",
        "RATE_LIMIT_KV": "Binding de KV para rate limiting",
    }
    
    all_ok = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}: No configurado")
            print(f"     Buscar: {check}")
            all_ok = False
    
    # Verificar que no haya nombre personal en la URL
    if "facujallia" in content.lower() or "facundoallia" in content.lower():
        print("  ⚠️  ADVERTENCIA: Posible nombre personal en configuración")
        all_ok = False
    
    return all_ok

def check_worker_code():
    """Verifica el código del worker."""
    print_header("🔧 CÓDIGO DEL WORKER")
    
    base_dir = Path(__file__).parent
    worker_path = base_dir / "worker" / "worker.js"
    
    if not worker_path.exists():
        print("  ❌ worker.js no encontrado")
        return False
    
    content = worker_path.read_text(encoding='utf-8')
    
    checks = {
        "RATE_LIMIT": "Configuración de rate limiting",
        "checkRateLimit": "Función de rate limiting",
        "handleStats": "Handler de estadísticas",
        "/api/stats": "Endpoint de estadísticas",
        "429": "Código de error rate limit",
    }
    
    all_ok = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}: No implementado")
            all_ok = False
    
    return all_ok

def check_python_files():
    """Verifica que no haya credenciales hardcodeadas."""
    print_header("🔍 VERIFICACIÓN DE CREDENCIALES")
    
    base_dir = Path(__file__).parent
    
    python_files = [
        "deploy_with_wrangler.py",
        "get_account_info.py",
    ]
    
    all_ok = True
    for file_name in python_files:
        file_path = base_dir / file_name
        if not file_path.exists():
            print(f"  ⚠️  {file_name}: No encontrado")
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        # Buscar patrones de credenciales hardcodeadas
        suspicious_patterns = [
            ('"Cm8qe2j5U9GW5qncg', "API Token hardcodeado"),
            ('"b716491d6afe361dba0e', "Account ID hardcodeado"),
            ('API_TOKEN = "', "Posible token hardcodeado"),
        ]
        
        has_issue = False
        for pattern, description in suspicious_patterns:
            if pattern in content:
                print(f"  ❌ {file_name}: {description}")
                has_issue = True
                all_ok = False
        
        if not has_issue:
            # Verificar que use variables de entorno
            if 'os.environ.get' in content:
                print(f"  ✅ {file_name}: Usa variables de entorno")
            else:
                print(f"  ⚠️  {file_name}: No parece usar variables de entorno")
    
    return all_ok

def main():
    """Ejecuta todas las verificaciones."""
    print("\n" + "🔍 VERIFICACIÓN DE CONFIGURACIÓN DE SEGURIDAD".center(70))
    print("rem-bcra-api".center(70))
    
    results = {
        "Variables de entorno": check_env_vars(),
        "Archivos críticos": check_files(),
        "Protección .gitignore": check_gitignore(),
        "Configuración Wrangler": check_wrangler_config(),
        "Código del Worker": check_worker_code(),
        "Credenciales en Python": check_python_files(),
    }
    
    print_header("📊 RESUMEN")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check}")
    
    print("\n" + "─" * 70)
    print(f"  Total: {passed}/{total} verificaciones pasadas")
    print("─" * 70)
    
    if passed == total:
        print("\n  🎉 ¡Todas las verificaciones pasaron!")
        print("  ✅ El repositorio está seguro y listo para producción")
        return 0
    else:
        print("\n  ⚠️  Algunas verificaciones fallaron")
        print("  📖 Revisa SECURITY.md y SETUP_RATE_LIMITING.md para más información")
        return 1

if __name__ == "__main__":
    sys.exit(main())
