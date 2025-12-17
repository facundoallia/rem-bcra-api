# ⏰ Optimización del Cron Schedule

## Problema Original

El pipeline inicial usaba un cron schedule semanal:
```yaml
cron: '0 10 * * 1'  # Cada lunes a las 10:00 UTC
```

**Problemas identificados:**
1. **Ineficiencia**: El REM se publica solo una vez al mes (días 1-5 del mes siguiente)
2. **Latencia**: Si el BCRA publica un martes, el pipeline esperaría hasta el siguiente lunes (hasta 6 días de retraso)
3. **Procesamiento innecesario**: Ejecutaba el pipeline incluso cuando no había datos nuevos

## Solución Implementada

### 1. Cron Schedule Optimizado
```yaml
cron: '0 12 1-7 * *'  # Diario, días 1-7 del mes, 12:00 UTC (9:00 AM Argentina)
```

**Ventajas:**
- ✅ Ejecuta solo durante la ventana de publicación del BCRA
- ✅ Reduce latencia máxima de 6 días a 1 día
- ✅ Mantiene el procesamiento contenido a la primera semana de cada mes

### 2. Detección Inteligente de Duplicados

El script `download REM` ahora retorna exit codes específicos:

```python
def descargar_archivo(url):
    """Descarga archivo solo si no existe o es diferente."""
    filepath = DATA_DIR / filename
    
    if filepath.exists():
        # Verificar tamaño del archivo remoto
        r = safe_head(url)
        remote_size = int(r.headers.get('Content-Length', 0))
        local_size = filepath.stat().st_size
        
        if remote_size == local_size:
            print("✅ Archivo ya está actualizado")
            return filepath, False  # Exit code 1
    
    # Descargar archivo nuevo
    return filepath, True  # Exit code 0
```

**Exit Codes:**
- `0`: Archivo nuevo descargado → **Continúa pipeline** (parse + deploy)
- `1`: Archivo ya actualizado → **Detiene pipeline** (sin error)
- `2`: Error en descarga → **Detiene pipeline** (con error)

### 3. Workflow con Conditional Steps

```yaml
- name: Descargar REM desde BCRA
  id: download
  run: |
    python "download REM"
    exit_code=$?
    if [ $exit_code -eq 1 ]; then
      echo "ℹ️ Archivo ya actualizado - no hay cambios"
      exit 0
    fi

- name: Parsear Excel a JSON
  if: steps.download.outputs.download_status == '0'
  run: python "read REM.py"
```

## Comportamiento Esperado

### Primera Semana del Mes (días 1-7)

**Día 1 (BCRA aún no publicó):**
```
12:00 UTC - Workflow ejecuta
  → Download: Archivo no existe
  → Error: No se encuentra el REM del mes actual
  → Exit code 2
  → Pipeline termina con error (esperado)
```

**Día 3 (BCRA publicó):**
```
12:00 UTC - Workflow ejecuta
  → Download: Archivo nuevo detectado
  → Parse: 18 tablas generadas
  → Deploy: Subido a R2
  → Exit code 0
  → ✅ Pipeline completo exitoso
```

**Día 4-7 (Después de primera descarga exitosa):**
```
12:00 UTC - Workflow ejecuta
  → Download: Archivo ya existe, mismo tamaño
  → Exit code 1
  → ℹ️ Pipeline termina (sin error, sin procesar)
```

### Días 8-31 del mes
```
❌ Workflow NO ejecuta
```

## Métricas de Optimización

### Antes (Cron Semanal)
- **Ejecuciones/mes**: 4-5 (todos los lunes)
- **Latencia máxima**: 6 días
- **Procesamiento innecesario**: 3-4 ejecuciones/mes

### Después (Cron Optimizado)
- **Ejecuciones/mes**: 7 (días 1-7)
- **Latencia máxima**: 1 día
- **Procesamiento innecesario**: 0 (detección de duplicados)
- **Procesamiento efectivo**: 1 ejecución/mes (solo cuando hay datos nuevos)

## Ventajas Adicionales

1. **Menor consumo de recursos**: GitHub Actions solo procesa cuando hay datos nuevos
2. **Logs más limpios**: Fácil identificar cuando NO hay datos nuevos (exit code 1)
3. **Flexibilidad**: Si BCRA cambia fecha de publicación, aún cae en ventana de 7 días
4. **Idempotencia**: Ejecutar múltiples veces no causa problemas

## Monitoreo

Para verificar el comportamiento del pipeline:

```bash
# Ver logs de GitHub Actions
gh run list --workflow=update-rem.yml --limit 10

# Ver última ejecución
gh run view --log

# Ver exit code del paso de descarga
gh run view --log | grep "download_status"
```

## Alternativas Consideradas

### ❌ Opción 1: Webhook del BCRA
**Problema**: BCRA no ofrece webhooks ni API de notificación

### ❌ Opción 2: Cron diario (todos los días del mes)
**Problema**: Ejecutaría 30 veces/mes con solo 1 ejecución útil (desperdicio de recursos)

### ❌ Opción 3: Cron mensual (día 5 fijo)
**Problema**: Si BCRA publica antes del día 5, tendría latencia de varios días

### ✅ Opción 4: Cron diario + detección duplicados (IMPLEMENTADA)
**Ventaja**: Balance perfecto entre latencia, recursos y confiabilidad
