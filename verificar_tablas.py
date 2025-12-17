#!/usr/bin/env python3
import json
from pathlib import Path

data_file = Path(r"C:\Desarrollos\api REM\data\rem_bloques.json")
data = json.load(open(data_file, encoding='utf-8'))

print("RESUMEN DE TABLAS PROCESADAS")
print("=" * 80)

# Agrupar por hoja
cuadros = []
top10 = []

for clave, tabla in data.items():
    if "TOP 10" in tabla["hoja"]:
        top10.append(tabla)
    else:
        cuadros.append(tabla)

print(f"\n📊 CUADROS DE RESULTADOS ({len(cuadros)} tablas):")
print("-" * 80)
for i, tabla in enumerate(sorted(cuadros, key=lambda x: x["titulo"]), 1):
    print(f"  {i}. {tabla['titulo']:52s} {tabla['filas']:2d} filas")

print(f"\n🏆 RESULTADOS TOP 10 ({len(top10)} tablas):")
print("-" * 80)
for i, tabla in enumerate(sorted(top10, key=lambda x: x["titulo"]), 1):
    print(f"  {i}. {tabla['titulo']:52s} {tabla['filas']:2d} filas")

print(f"\n{'=' * 80}")
print(f"✅ TOTAL: {len(data)} tablas procesadas correctamente")
print(f"{'=' * 80}")
