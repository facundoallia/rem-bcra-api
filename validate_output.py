#!/usr/bin/env python3
"""
validate_output.py
------------------
Valida la integridad y consistencia de los archivos JSON generados.
Detecta:
- Fechas inválidas (1970-01-01, futuro lejano)
- Tipos de datos incorrectos
- Valores faltantes críticos
- Rangos numéricos anormales
- Estructura JSON inconsistente
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
import sys

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

class ValidationError(Exception):
    """Error de validación personalizado."""
    pass

class Validator:
    def __init__(self):
        self.errores = []
        self.warnings = []
        self.validaciones_ok = 0
        
    def error(self, mensaje):
        """Registra un error crítico."""
        self.errores.append(f"❌ ERROR: {mensaje}")
        
    def warning(self, mensaje):
        """Registra una advertencia."""
        self.warnings.append(f"⚠️  WARNING: {mensaje}")
        
    def ok(self, mensaje):
        """Registra una validación exitosa."""
        self.validaciones_ok += 1
        
    def validar_fecha(self, fecha_str, campo, contexto):
        """Valida que una fecha sea razonable."""
        if not fecha_str:
            return
            
        try:
            # Intentar parsear diferentes formatos
            if isinstance(fecha_str, (int, float)):
                # Podría ser año
                if 2020 <= fecha_str <= 2030:
                    return True
                else:
                    self.warning(f"{contexto}: año fuera de rango esperado: {fecha_str}")
                    return False
            
            # Parsear fecha ISO
            if 'T' in str(fecha_str):
                fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            elif ' ' in str(fecha_str):
                # Formato datetime con espacio
                fecha = datetime.strptime(str(fecha_str)[:10], '%Y-%m-%d')
            else:
                fecha = datetime.strptime(str(fecha_str), '%Y-%m-%d')
            
            # Validar rango razonable
            hoy = datetime.now()
            hace_5_años = hoy - timedelta(days=365*5)
            en_5_años = hoy + timedelta(days=365*5)
            
            # Detectar fecha Unix epoch (1970-01-01)
            if fecha.year == 1970 and fecha.month == 1 and fecha.day == 1:
                self.error(f"{contexto}: Fecha epoch detectada (1970-01-01) en '{campo}'")
                return False
            
            # Verificar rango razonable (últimos 5 años a próximos 5 años)
            if not (hace_5_años <= fecha <= en_5_años):
                self.warning(f"{contexto}: Fecha fuera de rango esperado: {fecha_str}")
                return False
                
            return True
            
        except Exception as e:
            self.error(f"{contexto}: Error parseando fecha '{fecha_str}': {e}")
            return False
    
    def validar_numero(self, valor, campo, contexto, rango_min=None, rango_max=None):
        """Valida que un número esté en un rango razonable."""
        if valor is None or valor == "":
            return True  # Valores nulos son aceptables
            
        try:
            num = float(valor)
            
            # Detectar valores sospechosos
            if num == 0 and "median" in campo.lower():
                self.warning(f"{contexto}: Mediana en cero podría ser sospechoso")
            
            # Validar rangos si se especifican
            if rango_min is not None and num < rango_min:
                self.warning(f"{contexto}: Valor {num} < {rango_min} en '{campo}'")
                return False
                
            if rango_max is not None and num > rango_max:
                self.warning(f"{contexto}: Valor {num} > {rango_max} en '{campo}'")
                return False
                
            return True
            
        except (ValueError, TypeError):
            # No es número, podría ser texto válido
            return True
    
    def validar_estructura_tabla(self, clave, tabla):
        """Valida la estructura de una tabla individual."""
        contexto = f"Tabla '{clave}'"
        
        # Verificar campos obligatorios
        campos_requeridos = ['titulo', 'hoja', 'clave', 'filas', 'columnas', 'datos']
        for campo in campos_requeridos:
            if campo not in tabla:
                self.error(f"{contexto}: Falta campo obligatorio '{campo}'")
                return False
        
        # Verificar tipos
        if not isinstance(tabla['titulo'], str):
            self.error(f"{contexto}: 'titulo' debe ser string")
            
        if not isinstance(tabla['columnas'], list):
            self.error(f"{contexto}: 'columnas' debe ser lista")
            
        if not isinstance(tabla['datos'], list):
            self.error(f"{contexto}: 'datos' debe ser lista")
        
        # Verificar coherencia
        num_filas = len(tabla['datos'])
        if num_filas != tabla['filas']:
            self.warning(f"{contexto}: 'filas' ({tabla['filas']}) no coincide con len(datos) ({num_filas})")
        
        # Verificar que todas las filas tengan las columnas esperadas
        columnas_esperadas = set(tabla['columnas'])
        for i, fila in enumerate(tabla['datos']):
            columnas_fila = set(fila.keys())
            if columnas_fila != columnas_esperadas:
                diff = columnas_fila.symmetric_difference(columnas_esperadas)
                self.warning(f"{contexto}: Fila {i} tiene columnas diferentes: {diff}")
                break  # Solo reportar la primera discrepancia
        
        self.ok(f"{contexto}: Estructura válida")
        return True
    
    def validar_datos_tabla(self, clave, tabla):
        """Valida los datos de una tabla."""
        contexto = f"Tabla '{clave}'"
        
        # Buscar columna de período/fecha
        columna_periodo = None
        for col in tabla['columnas']:
            if 'per' in col.lower() or 'fecha' in col.lower():
                columna_periodo = col
                break
        
        # Validar cada fila
        for i, fila in enumerate(tabla['datos']):
            fila_ctx = f"{contexto}, fila {i}"
            
            # Validar fecha si existe
            if columna_periodo and columna_periodo in fila:
                self.validar_fecha(fila[columna_periodo], columna_periodo, fila_ctx)
            
            # Validar campos numéricos según el tipo de tabla
            for campo, valor in fila.items():
                if campo == columna_periodo or campo == 'referencia':
                    continue
                
                # Rangos específicos según tipo de dato
                if 'ipc' in clave or 'inflacion' in clave:
                    # Inflación: -50% a 200% mensual es razonable (contexto argentino)
                    self.validar_numero(valor, campo, fila_ctx, -50, 200)
                    
                elif 'tipo_cambio' in clave:
                    # Tipo de cambio: > 0 (no puede ser negativo)
                    self.validar_numero(valor, campo, fila_ctx, 0, 100000)
                    
                elif 'tasa' in clave:
                    # Tasas: 0% a 300% anual
                    self.validar_numero(valor, campo, fila_ctx, 0, 300)
                    
                elif 'pbi' in clave:
                    # PBI: -20% a +20% variación trimestral
                    self.validar_numero(valor, campo, fila_ctx, -20, 20)
                    
                elif 'exportaciones' in clave or 'importaciones' in clave:
                    # Comercio exterior: > 0
                    self.validar_numero(valor, campo, fila_ctx, 0, 50000)
                    
                elif 'desocupacion' in clave:
                    # Desocupación: 0% a 50%
                    self.validar_numero(valor, campo, fila_ctx, 0, 50)
        
        self.ok(f"{contexto}: Datos validados")
        return True
    
    def validar_archivo_maestro(self):
        """Valida el archivo maestro rem_bloques.json."""
        archivo = DATA_DIR / "rem_bloques.json"
        
        if not archivo.exists():
            self.error(f"No existe archivo maestro: {archivo}")
            return False
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.error(f"Error parseando JSON maestro: {e}")
            return False
        except Exception as e:
            self.error(f"Error leyendo archivo maestro: {e}")
            return False
        
        # Verificar que sea un diccionario
        if not isinstance(data, dict):
            self.error("Archivo maestro debe ser un objeto JSON (diccionario)")
            return False
        
        # Verificar número de tablas
        num_tablas = len(data)
        if num_tablas != 18:
            self.warning(f"Se esperan 18 tablas, se encontraron {num_tablas}")
        else:
            self.ok(f"Archivo maestro contiene {num_tablas} tablas")
        
        # Validar cada tabla
        for clave, tabla in data.items():
            self.validar_estructura_tabla(clave, tabla)
            self.validar_datos_tabla(clave, tabla)
        
        return True
    
    def validar_archivos_individuales(self):
        """Valida que existan los archivos individuales."""
        patron = "rem_*.json"
        archivos = list(DATA_DIR.glob(patron))
        
        # Excluir el archivo maestro
        archivos = [f for f in archivos if f.name != "rem_bloques.json"]
        
        if not archivos:
            self.error("No se encontraron archivos JSON individuales")
            return False
        
        self.ok(f"Encontrados {len(archivos)} archivos individuales")
        
        # Validar cada archivo
        for archivo in archivos:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    tabla = json.load(f)
                
                clave = archivo.stem.replace('rem_', '')
                self.validar_estructura_tabla(clave, tabla)
                self.validar_datos_tabla(clave, tabla)
                
            except Exception as e:
                self.error(f"Error validando {archivo.name}: {e}")
        
        return True
    
    def ejecutar(self):
        """Ejecuta todas las validaciones."""
        print("=" * 70)
        print("VALIDACIÓN DE DATOS REM")
        print("=" * 70)
        print()
        
        # Verificar que exista el directorio
        if not DATA_DIR.exists():
            self.error(f"No existe directorio de datos: {DATA_DIR}")
            return False
        
        # Ejecutar validaciones
        print("🔍 Validando archivo maestro...")
        self.validar_archivo_maestro()
        
        print("\n🔍 Validando archivos individuales...")
        self.validar_archivos_individuales()
        
        # Mostrar resumen
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN")
        print("=" * 70)
        print(f"✅ Validaciones exitosas: {self.validaciones_ok}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        print(f"❌ Errores: {len(self.errores)}")
        
        # Mostrar warnings
        if self.warnings:
            print("\n⚠️  ADVERTENCIAS:")
            for w in self.warnings[:10]:  # Mostrar máximo 10
                print(f"   {w}")
            if len(self.warnings) > 10:
                print(f"   ... y {len(self.warnings) - 10} más")
        
        # Mostrar errores
        if self.errores:
            print("\n❌ ERRORES CRÍTICOS:")
            for e in self.errores:
                print(f"   {e}")
        
        print("=" * 70)
        
        # Retornar código de salida
        if self.errores:
            print("\n❌ VALIDACIÓN FALLIDA - Hay errores críticos")
            return False
        elif self.warnings:
            print("\n⚠️  VALIDACIÓN COMPLETADA CON ADVERTENCIAS")
            return True
        else:
            print("\n✅ VALIDACIÓN EXITOSA")
            return True

def main():
    validator = Validator()
    exito = validator.ejecutar()
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
