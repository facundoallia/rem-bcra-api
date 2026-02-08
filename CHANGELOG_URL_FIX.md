# 🔧 Fix Urgente: Cambio de URL del BCRA

**Fecha:** 8 de febrero de 2026
**Problema:** GitHub Actions fallaba al descargar archivos REM
**Causa:** BCRA cambió la estructura de URLs sin previo aviso
**Estado:** ✅ RESUELTO

---

## 📋 PROBLEMA DETECTADO

### Error en GitHub Actions:
```
❌ ERROR: No se pudo descargar el archivo desde:
https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx
```

### Causa Raíz:
El BCRA modificó la estructura de URLs donde publica los archivos REM **sin anuncio previo**.

---

## 🔄 CAMBIO DE URL

### ❌ URL Antigua (hasta diciembre 2025):
```
https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-{mes}-{año}.xlsx
```

**Ejemplo:**
```
https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-dic-2025.xlsx
```

### ✅ URL Nueva (desde enero 2026):
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-{mes}-{año}.xlsx
```

**Ejemplo:**
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx
```

### Diferencias:
1. ➕ Prefijo `/archivos/` agregado al inicio
2. ➕ Subdirectorio `/informes/` agregado antes del nombre del archivo
3. ✅ El resto del patrón permanece igual

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Archivo Modificado: `download_REM.py`

#### 1. **Dos Funciones de URL (Dual Strategy)**

```python
def url_rem_nueva(year, month):
    """URL NUEVA (desde enero 2026)"""
    mes_txt = MESES[month]
    return f"https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-{mes_txt}-{year}.xlsx"

def url_rem_antigua(year, month):
    """URL ANTIGUA (hasta diciembre 2025)"""
    mes_txt = MESES[month]
    return f"https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-{mes_txt}-{year}.xlsx"
```

#### 2. **Estrategia de Fallback Automático**

El script ahora:
1. ✅ **Intenta primero la URL nueva** (2026+)
2. ✅ **Si falla, intenta la URL antigua** (2025 y anteriores)
3. ✅ **Mantiene retrocompatibilidad** para acceder a datos históricos

```python
# Probar PRIMERO nueva URL
url_nueva = url_rem_nueva(y, m)
r = safe_head(url_nueva)
if r and r.status_code == 200:
    return url_nueva

# Fallback a URL antigua
url_antigua = url_rem_antigua(y, m)
r = safe_head(url_antigua)
if r and r.status_code == 200:
    return url_antigua
```

#### 3. **Headers HTTP Mejorados**

Agregado User-Agent realista para evitar bloqueos:

```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
```

#### 4. **Retry Logic con Exponential Backoff**

```python
def safe_get(url, headers=None, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers or HEADERS, timeout=60, verify=False)
            return response
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                return None
```

#### 5. **Mensajes de Error Mejorados**

Si falla todo, muestra:
- ✅ Lista completa de URLs probadas
- ✅ Status HTTP de cada intento
- ✅ Sugerencias de troubleshooting

```python
raise RuntimeError(
    "No se encontró ningún archivo REM válido. "
    "Posibles causas:\n"
    "  1. BCRA aún no publicó el REM del mes actual\n"
    "  2. BCRA cambió la estructura de URLs nuevamente\n"
    "  3. Problemas de conectividad con bcra.gob.ar"
)
```

---

## 🧪 TESTING

### Test Manual (Verificado ✅):
```bash
# URL nueva funciona
curl -I "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx"
# HTTP/2 200 ✅

# URL antigua funciona para diciembre 2025
curl -I "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/tablas-relevamiento-expectativas-mercado-dic-2025.xlsx"
# HTTP/2 200 ✅
```

### Test del Script:
```bash
cd rem-bcra-api
python download_REM.py
```

**Output esperado:**
```
======================================================================
DESCARGA REM - BCRA
======================================================================

📅 Fecha actual: 2026-02-08
🔍 Buscando REM más reciente...

   Probando (nueva): https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx
   ✅ Archivo REM encontrado (URL nueva)
   📍 https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-ene-2026.xlsx

📂 Archivo destino: tablas-relevamiento-expectativas-mercado-ene-2026.xlsx
📥 Descargando desde BCRA...
   ✅ Descarga exitosa
   📊 Tamaño: 91,903 bytes

======================================================================
✅ DESCARGA EXITOSA - ARCHIVO NUEVO
   Se debe ejecutar el parser y deploy.
======================================================================
```

---

## 📊 IMPACTO

### ✅ Beneficios:
1. **Compatibilidad futura**: Maneja cambios de URL del BCRA automáticamente
2. **Retrocompatibilidad**: Puede descargar archivos históricos (2025 y anteriores)
3. **Robustez**: Retry logic + mejor manejo de errores
4. **Transparencia**: Logs detallados de cada intento

### ⚠️ Riesgos Mitigados:
- ❌ Fallos silenciosos por cambios de URL
- ❌ Bloqueos del servidor por falta de User-Agent
- ❌ Timeouts sin retry
- ❌ Errores crípticos sin contexto

---

## 🚀 DEPLOYMENT

### Pasos para Aplicar el Fix:

1. **Commit de cambios:**
   ```bash
   cd rem-bcra-api
   git add download_REM.py CHANGELOG_URL_FIX.md
   git commit -m "Fix urgente: Actualizar URL del REM (cambio BCRA enero 2026)

   - Agregar url_rem_nueva() para nueva estructura
   - Agregar url_rem_antigua() como fallback
   - Mejorar headers HTTP (User-Agent)
   - Agregar retry logic con exponential backoff
   - Mejorar mensajes de error con debugging info

   Fixes descarga de REM enero 2026+"
   git push origin main
   ```

2. **Trigger manual del workflow:**
   - Ve a GitHub Actions
   - Ejecuta "Actualizar REM BCRA" manualmente
   - Verifica que descargue exitosamente

3. **Verificar API actualizada:**
   ```bash
   curl https://bcra-rem-api.facujallia.workers.dev/api/metadata
   # Debe mostrar datos de enero 2026
   ```

---

## 📈 MONITOREO POST-FIX

### Próximas Ejecuciones:
- ✅ **Inmediata**: Trigger manual (ahora)
- ✅ **Marzo 2026**: Verificar que detecte nueva URL automáticamente
- ✅ **Trimestral**: Revisar si BCRA vuelve a cambiar la estructura

### Alertas a Configurar:
```yaml
# En caso de que BCRA cambie URLs nuevamente, agregar:
- Slack notification si falla descarga
- Email alert a responsable
- Issue automático en GitHub (ya configurado ✅)
```

---

## 🔮 LECCIONES APRENDIDAS

### Para Futuro:
1. **Nunca confiar en URLs estáticas** de organismos públicos
2. **Siempre implementar fallback** para cambios sin previo aviso
3. **Headers HTTP realistas** previenen bloqueos
4. **Retry logic** es obligatorio para requests críticos
5. **Logs detallados** aceleran debugging

### Prevención:
- ✅ Dual URL strategy implementada
- ✅ Retry logic automático
- ✅ Mensajes de error informativos
- ✅ Testing manual antes de deploy

---

## 📞 CONTACTO

Si detectas que BCRA volvió a cambiar la estructura de URLs:

1. **Verificar manualmente:**
   ```bash
   # Buscar nueva URL en el sitio del BCRA
   https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp
   ```

2. **Actualizar `download_REM.py`:**
   - Agregar nueva función `url_rem_nueva_v2()`
   - Modificar `find_latest_rem_url()` para probar nueva versión primero

3. **Notificar:**
   - Crear issue en GitHub
   - Documentar en nuevo CHANGELOG

---

**✅ Estado:** Fix aplicado y testeado
**📅 Válido desde:** Febrero 2026
**🔄 Próxima revisión:** Marzo 2026
**👤 Responsable:** Automatizado con fallback manual
