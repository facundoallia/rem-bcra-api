#!/usr/bin/env python3
# read REM.py
"""
Parser robusto para REM (BCRA)
- Lee el XLSX más reciente en ./data
- Detecta bloques en "Cuadros de resultados"
- Normaliza columnas, convierte fechas y números
- Salva rem_bloques.json (maestro) + archivos por bloque en ./data
"""
from pathlib import Path
import pandas as pd
import numpy as np
import re
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def encontrar_archivo_rem():
    """Encuentra el archivo REM más reciente."""
    archivos = sorted(
        DATA_DIR.glob("tablas-relevamiento-expectativas-mercado-*.xlsx"),
        key=lambda p: p.stat().st_mtime, 
        reverse=True
    )
    if not archivos:
        raise FileNotFoundError("No se encontró ningún archivo REM en ./data")
    return archivos[0]

def limpiar_nombre_columna(s) -> str:
    """Limpia y normaliza nombres de columnas."""
    if pd.isna(s) or s is None:
        return "col"
    
    s = str(s).strip()
    if not s or s.lower() in ["nan", "none", ""]:
        return "col"
    
    # Remover caracteres especiales y normalizar
    s = s.replace("%", "pct")
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'_+', '_', s)
    s = s.strip('_').lower()
    
    return s if s else "col"

def es_fila_vacia(row, umbral=0.8):
    """Verifica si una fila está mayormente vacía."""
    total = len(row)
    vacios = sum(1 for val in row if pd.isna(val) or str(val).strip() == "")
    return (vacios / total) >= umbral

def es_titulo_bloque(texto):
    """Detecta si un texto es título de bloque."""
    if not isinstance(texto, str):
        return False
    
    texto_original = texto.strip()
    texto = texto_original.lower()
    
    # Lista de títulos exactos o muy específicos
    titulos_exactos = [
        "precios minoristas (ipc nivel general-nacional; indec)",
        "precios minoristas (ipc núcleo-nacional; indec)",
        "tasa de interés (tamar)",
        "tipo de cambio nominal",
        "exportaciones",
        "importaciones",
        "resultado primario del spnf",
        "desocupación abierta",
        "pib a precios constantes"
    ]
    
    # Verificar coincidencia exacta (con tolerancia a variaciones)
    for titulo_exacto in titulos_exactos:
        if titulo_exacto in texto or texto in titulo_exacto:
            return True
    
    # Palabras clave que indican títulos de bloques (más específicas)
    palabras_clave = [
        "precios minoristas",
        "ipc nivel general",
        "ipc núcleo",
        "tasa de interés",
        "tamar",
        "tipo de cambio nominal",
        "resultado primario",
        "spnf",
        "desocupación",
        "pib a precios constantes"
    ]
    
    # Verificar longitud mínima (más flexible)
    if len(texto_original) < 3:
        return False
    
    # Para títulos cortos como "Exportaciones" o "Importaciones"
    if texto_original in ["Exportaciones", "Importaciones", "PIB a precios constantes"]:
        return True
    
    # Debe contener al menos una palabra clave
    tiene_clave = any(palabra in texto for palabra in palabras_clave)
    
    if not tiene_clave:
        return False
    
    # No debe ser demasiado largo (los títulos suelen ser concisos)
    longitud_ok = len(texto) < 200
    
    # No debe contener muchos números (indicaría que es dato)
    numeros = len(re.findall(r'\d', texto))
    ratio_numeros = numeros / len(texto) if len(texto) > 0 else 0
    pocos_numeros = ratio_numeros < 0.3
    
    return tiene_clave and longitud_ok and pocos_numeros

def detectar_bloques_mejorado(df):
    """
    Detecta bloques de datos en el DataFrame.
    Retorna lista de tuplas: (titulo, fila_inicio_datos, fila_fin_datos)
    """
    bloques = []
    nrows = df.shape[0]
    i = 0
    
    while i < nrows:
        # Buscar fila con título
        fila = df.iloc[i]
        
        # Revisar todas las celdas de la fila buscando título
        titulo = None
        for val in fila:
            if es_titulo_bloque(val):
                titulo = str(val).strip()
                break
        
        if titulo:
            # Encontramos un título, ahora buscar el encabezado y datos
            j = i + 1
            header_idx = None
            
            # Buscar fila de encabezado (siguiente fila no vacía)
            while j < min(i + 10, nrows):
                if not es_fila_vacia(df.iloc[j]):
                    # Verificar que parezca un encabezado
                    fila_test = df.iloc[j]
                    texto_fila = ' '.join([str(v) for v in fila_test if pd.notna(v)]).lower()
                    
                    # Un encabezado suele tener palabras como "período", "mes", "año", etc.
                    if any(palabra in texto_fila for palabra in ["período", "periodo", "mes", "año", "trimestre", "referencia", "fecha"]):
                        header_idx = j
                        break
                j += 1
            
            if header_idx is None:
                # Si no encontramos encabezado explícito, usar la siguiente fila no vacía
                j = i + 1
                while j < min(i + 10, nrows) and es_fila_vacia(df.iloc[j]):
                    j += 1
                if j < nrows:
                    header_idx = j
            
            if header_idx is not None:
                # Buscar fin del bloque (próximo título o final)
                k = header_idx + 1
                fin_bloque = nrows
                
                # Contar filas de datos consecutivas
                filas_vacias_consecutivas = 0
                while k < nrows:
                    # Verificar si es un nuevo título
                    fila_k = df.iloc[k]
                    es_nuevo_titulo = False
                    for val in fila_k:
                        if es_titulo_bloque(val):
                            es_nuevo_titulo = True
                            break
                    
                    if es_nuevo_titulo:
                        fin_bloque = k
                        break
                    
                    # Contar filas vacías consecutivas
                    if es_fila_vacia(df.iloc[k]):
                        filas_vacias_consecutivas += 1
                        # Si hay 3+ filas vacías, probablemente terminó el bloque
                        if filas_vacias_consecutivas >= 3:
                            fin_bloque = k - filas_vacias_consecutivas + 1
                            break
                    else:
                        filas_vacias_consecutivas = 0
                    
                    k += 1
                
                # Agregar bloque si tiene datos
                if fin_bloque > header_idx + 1:
                    bloques.append({
                        'titulo': titulo,
                        'fila_titulo': i,
                        'fila_header': header_idx,
                        'fila_inicio_datos': header_idx + 1,
                        'fila_fin_datos': fin_bloque
                    })
                    i = fin_bloque
                    continue
        
        i += 1
    
    return bloques

def normalizar_bloque(df, bloque):
    """
    Normaliza un bloque de datos extraído.
    """
    header_idx = bloque['fila_header']
    inicio = bloque['fila_inicio_datos']
    fin = bloque['fila_fin_datos']
    
    # Extraer encabezado
    header = df.iloc[header_idx].tolist()
    
    # Limpiar nombres de columnas
    columnas_limpias = []
    contador = {}
    
    for col in header:
        nombre_limpio = limpiar_nombre_columna(col)
        
        # Evitar duplicados agregando sufijo numérico
        if nombre_limpio in contador:
            contador[nombre_limpio] += 1
            nombre_limpio = f"{nombre_limpio}_{contador[nombre_limpio]}"
        else:
            contador[nombre_limpio] = 0
        
        columnas_limpias.append(nombre_limpio)
    
    # Extraer datos
    df_datos = df.iloc[inicio:fin].copy()
    df_datos.columns = columnas_limpias[:len(df_datos.columns)]
    
    # Resetear índice
    df_datos = df_datos.reset_index(drop=True)
    
    # Eliminar filas completamente vacías
    df_datos = df_datos.dropna(how='all')
    
    # Eliminar columnas completamente vacías
    df_datos = df_datos.dropna(axis=1, how='all')
    
    # Identificar columna de período/fecha
    columna_periodo = None
    for col in df_datos.columns:
        if 'period' in col or 'per_od' in col or 'fecha' in col or 'mes' in col or 'trimestre' in col:
            columna_periodo = col
            break
    
    # Convertir columna de período
    if columna_periodo:
        df_datos[columna_periodo] = df_datos[columna_periodo].apply(convertir_fecha)
    
    # Convertir columnas numéricas
    for col in df_datos.columns:
        if col == columna_periodo:
            continue
        
        df_datos[col] = df_datos[col].apply(convertir_numero)
    
    return df_datos

def convertir_fecha(val):
    """Intenta convertir un valor a fecha en formato ISO."""
    if pd.isna(val):
        return None
    
    try:
        # Si ya es datetime
        if isinstance(val, (pd.Timestamp, datetime)):
            return val.strftime('%Y-%m-%d')
        
        val_str = str(val).strip()
        
        # Intentar parsear diferentes formatos
        formatos = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%Y',
            '%Y/%m',
            '%Y',
        ]
        
        for fmt in formatos:
            try:
                fecha = datetime.strptime(val_str, fmt)
                return fecha.strftime('%Y-%m-%d')
            except:
                continue
        
        # Intentar con pandas
        fecha = pd.to_datetime(val, errors='coerce')
        if pd.notna(fecha):
            return fecha.strftime('%Y-%m-%d')
        
        # Si no se puede convertir, devolver el string original
        return val_str
    except:
        return str(val) if pd.notna(val) else None

def convertir_numero(val):
    """Intenta convertir un valor a número."""
    if pd.isna(val):
        return None
    
    try:
        # Si ya es número
        if isinstance(val, (int, float, np.integer, np.floating)):
            return float(val) if not np.isnan(val) else None
        
        val_str = str(val).strip()
        
        # Remover símbolos comunes
        val_str = val_str.replace('%', '').replace('$', '').replace(',', '.')
        val_str = val_str.replace(' ', '').replace('\xa0', '')
        
        # Intentar convertir
        if val_str:
            numero = float(val_str)
            return numero if not np.isnan(numero) else None
    except:
        pass
    
    # Si no se puede convertir, devolver el valor original
    return str(val).strip() if pd.notna(val) else None

def generar_clave_bloque(titulo, hoja, usado=None):
    """Genera una clave única para un bloque basada en su título y hoja."""
    if usado is None:
        usado = set()
    
    titulo_lower = titulo.lower()
    
    # Determinar sufijo por hoja
    sufijo_hoja = "_top10" if "top" in hoja.lower() else ""
    
    # Mapeo de títulos a claves
    if 'ipc nivel general' in titulo_lower or ('nivel general' in titulo_lower and 'ipc' in titulo_lower):
        clave_base = 'ipc_general'
    elif 'ipc núcleo' in titulo_lower or 'ipc nucleo' in titulo_lower or ('núcleo' in titulo_lower and 'ipc' in titulo_lower):
        clave_base = 'ipc_nucleo'
    elif 'tamar' in titulo_lower or 'tasa de interés' in titulo_lower or 'tasa de interes' in titulo_lower:
        clave_base = 'tasa_interes'
    elif 'tipo de cambio' in titulo_lower:
        clave_base = 'tipo_cambio'
    elif 'exportaciones' in titulo_lower:
        clave_base = 'exportaciones'
    elif 'importaciones' in titulo_lower:
        clave_base = 'importaciones'
    elif 'resultado primario' in titulo_lower or 'spnf' in titulo_lower:
        clave_base = 'resultado_primario'
    elif 'desocupación' in titulo_lower or 'desocupacion' in titulo_lower:
        clave_base = 'desocupacion'
    elif 'pib' in titulo_lower or 'producto bruto' in titulo_lower:
        clave_base = 'pbi'
    else:
        # Generar clave genérica
        clave_base = re.sub(r'[^\w\s]', '', titulo_lower)
        clave_base = re.sub(r'\s+', '_', clave_base)
        clave_base = clave_base[:30]
    
    # Combinar con sufijo de hoja
    clave = f"{clave_base}{sufijo_hoja}"
    
    # Evitar duplicados
    if clave not in usado:
        usado.add(clave)
        return clave
    
    contador = 2
    while f"{clave}_{contador}" in usado:
        contador += 1
    clave_final = f"{clave}_{contador}"
    usado.add(clave_final)
    return clave_final

def main():
    """Función principal."""
    print("=" * 60)
    print("Parser REM - BCRA")
    print("=" * 60)
    
    # Encontrar archivo
    archivo = encontrar_archivo_rem()
    print(f"\n📄 Archivo: {archivo.name}")
    
    # Leer Excel
    print("📖 Leyendo Excel...")
    try:
        xls = pd.ExcelFile(archivo, engine="openpyxl")
    except Exception as e:
        print(f"❌ Error al leer archivo: {e}")
        return
    
    print(f"   Hojas encontradas: {xls.sheet_names}")
    
    # Hojas a procesar
    hojas_procesar = ["Cuadros de resultados", "Resultados TOP 10"]
    
    # Verificar hojas
    for hoja in hojas_procesar:
        if hoja not in xls.sheet_names:
            print(f"⚠️  Advertencia: No existe hoja '{hoja}'")
    
    # Procesar todas las hojas
    resultado = {}
    claves_usadas = set()
    total_bloques = 0
    
    for nombre_hoja in hojas_procesar:
        if nombre_hoja not in xls.sheet_names:
            continue
        
        print(f"\n{'='*60}")
        print(f"📊 Procesando hoja: {nombre_hoja}")
        print(f"{'='*60}")
        
        # Leer hoja
        df = xls.parse(nombre_hoja, header=None)
        print(f"   Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
        
        # Detectar bloques
        print("\n🔍 Detectando bloques...")
        bloques = detectar_bloques_mejorado(df)
        print(f"   Encontrados: {len(bloques)} bloques")
        
        if not bloques:
            print("⚠️  No se detectaron bloques en esta hoja")
            continue
        
        # Procesar bloques
        print("\n⚙️  Procesando bloques...")
        
        for idx, bloque in enumerate(bloques, 1):
            titulo = bloque['titulo']
            print(f"\n   [{idx}/{len(bloques)}] {titulo}")
            
            try:
                # Normalizar bloque
                df_normalizado = normalizar_bloque(df, bloque)
                
                # Generar clave
                clave = generar_clave_bloque(titulo, nombre_hoja, claves_usadas)
                
                # Crear entrada
                entrada = {
                    'titulo': titulo,
                    'hoja': nombre_hoja,
                    'clave': clave,
                    'filas': len(df_normalizado),
                    'columnas': df_normalizado.columns.tolist(),
                    'datos': df_normalizado.to_dict(orient='records')
                }
                
                resultado[clave] = entrada
                
                # Guardar archivo individual
                archivo_individual = DATA_DIR / f"rem_{clave}.json"
                with open(archivo_individual, 'w', encoding='utf-8') as f:
                    json.dump(entrada, f, ensure_ascii=False, indent=2)
                
                print(f"      ✓ {len(df_normalizado)} filas, {len(df_normalizado.columns)} columnas")
                print(f"      ✓ Guardado: rem_{clave}.json")
                
                total_bloques += 1
                
            except Exception as e:
                print(f"      ❌ Error procesando bloque: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # Guardar archivo maestro
    if resultado:
        archivo_maestro = DATA_DIR / "rem_bloques.json"
        with open(archivo_maestro, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ Proceso completado")
        print(f"{'='*60}")
        print(f"   📦 Archivo maestro: rem_bloques.json")
        print(f"   📦 Archivos individuales: {len(resultado)}")
        print(f"   📊 Total de bloques procesados: {total_bloques}")
        print(f"   📁 Ubicación: {DATA_DIR}")
    else:
        print("\n❌ No se procesaron bloques correctamente")

if __name__ == "__main__":
    main()
