# API REM - BCRA Expectativas de Mercado

Parser y API para el Relevamiento de Expectativas de Mercado (REM) del Banco Central de la República Argentina.

## 📁 Estructura del Proyecto

```
api REM/
├── data/                          # Archivos generados
│   ├── 2025/
│   │   └── 11/
│   │       ├── rem_*.json        # 18 tablas individuales
│   │       └── _metadata.json    # Info del período
│   ├── latest/                    # Siempre apunta a la última versión
│   │   ├── rem_*.json
│   │   └── _metadata.json
│   └── tablas-*.xlsx             # XLSX descargados
├── download REM                   # Script de descarga del XLSX
├── read REM.py                    # Parser principal (XLSX → JSON)
├── deploy_with_wrangler.py       # Deploy a R2 con estructura año/mes
└── worker/
    ├── worker.js                  # API REST con soporte de períodos
    └── wrangler.toml             # Configuración del Worker
```

## 🎯 Estado Actual

### ✅ Completado

1. **Descarga automática inteligente** (`download REM.py`)
   - Detecta URL del REM más reciente en bcra.gob.ar
   - Verifica si el archivo ya fue descargado (por tamaño)
   - Descarga XLSX solo si hay una versión nueva
   - Manejo de SSL y timeouts
   - Exit codes: 0=nuevo, 1=actualizado, 2=error

2. **Parser robusto** (`read REM.py`)
   - Procesa 2 hojas: "Principales Variables" y "Agregados Monetarios"
   - Genera 18 tablas JSON individuales + versiones top10
   - Archivo maestro `rem_bloques.json` con índice de tablas
   - Conversión de fechas a ISO 8601
   - Conversión de números con manejo de decimales
   - Nombres de columnas normalizados

3. **Deploy con estructura año/mes** (`deploy_with_wrangler.py`)
   - Extrae fecha de publicación del nombre del archivo XLSX
   - Sube archivos a `data/{año}/{mes}/` para histórico
   - Actualiza `data/latest/` con la versión más reciente
   - Genera metadata con información del período
   - Usa wrangler CLI para upload a Cloudflare R2

4. **Worker desplegado** (Cloudflare Workers)
   - URL: https://rem-bcra-api.facujallia.workers.dev
   - Soporte de consultas históricas: `?periodo=2025-11`
   - Endpoints para 18 tablas individuales
   - CORS habilitado para consumo público
   - Cache-Control: 1 hora

5. **Automatización optimizada** (GitHub Actions)
   - Cron: `0 12 1-7 * *` (diario, días 1-7 del mes)
   - Solo procesa cuando detecta archivo nuevo
   - Deploy automático a Cloudflare R2
   - Logs detallados de cada ejecución

### ⏳ Pendiente (Manual desde Casa)

- **Subir archivos JSON iniciales a R2** (ver `GUIA_UPLOAD_MANUAL.md`)
- Configurar GitHub Secrets: `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID`
- Probar API desde ordenador personal

4. **API REST** (Cloudflare Worker)
   - 7 endpoints públicos
   - CORS habilitado
   - Cache de 1 hora
   - Sin autenticación (público)

5. **Verificación básica** (`verificar_tablas.py`)
   - Cuenta tablas por hoja
   - Muestra resumen de filas procesadas

### 📋 Tablas Generadas (18 total)

#### Cuadros de Resultados (9 tablas)
1. `rem_ipc_general.json` - IPC nivel general
2. `rem_ipc_nucleo.json` - IPC núcleo
3. `rem_tasa_interes.json` - Tasa TAMAR
4. `rem_tipo_cambio.json` - Tipo de cambio nominal
5. `rem_exportaciones.json` - Exportaciones
6. `rem_importaciones.json` - Importaciones
7. `rem_resultado_primario.json` - Resultado Primario SPNF
8. `rem_desocupacion.json` - Desocupación abierta
9. `rem_pbi.json` - PIB a precios constantes

#### Resultados TOP 10 (9 tablas)
10-18. Las mismas con sufijo `_top10`

## 🚀 API REST

La API está desplegada en: **https://rem-bcra-api.facujallia.workers.dev**

### Endpoints Disponibles

```bash
# Índice de tablas disponibles
GET /api

# Tabla específica (versión latest)
GET /api/{tabla}
GET /api/tipo_cambio
GET /api/inflacion
GET /api/tasa_badlar

# Consultas históricas
GET /api/tipo_cambio?periodo=2025-11
GET /api/tipo_cambio?year=2025&month=11

# Metadata del período
GET /api/metadata
```

### Ejemplo de Uso

```python
import requests

# Obtener tipo de cambio actual
r = requests.get('https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio')
data = r.json()

# Obtener inflación de noviembre 2025
r = requests.get('https://rem-bcra-api.facujallia.workers.dev/api/inflacion?periodo=2025-11')
historico = r.json()
```

## 🔧 Setup desde Casa

### 1. Subir Archivos Iniciales a R2

Sigue la guía completa en **`GUIA_UPLOAD_MANUAL.md`**:

1. Acceder a https://dash.cloudflare.com
2. Ir al bucket `rem-data`
3. Crear carpetas: `data/latest/` y `data/2025/11/`
4. Subir los 19 archivos JSON a ambas carpetas

### 2. Configurar GitHub Secrets

En https://github.com/facundoallia/carry-trade-analyzer/settings/secrets/actions:

```
CLOUDFLARE_API_TOKEN = Cm8qe2j5U9GW5qncg-z6iGc7LAV58DYlve1Iyd_T
CLOUDFLARE_ACCOUNT_ID = b716491d6afe361dba0e016519df6cb3
```

### 3. Probar la API

```bash
# PowerShell
Invoke-RestMethod -Uri "https://rem-bcra-api.facujallia.workers.dev/api"

# Python
import requests
requests.get('https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio').json()

# Excel/Power BI
# Web → Desde Web → https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio
```

## 📝 Próximos Pasos Automáticos

Una vez configurados los GitHub Secrets:
- GitHub Actions se ejecutará automáticamente días 1-7 de cada mes
- Descargará nuevo REM si está disponible
- Lo parseará a JSON
- Lo subirá a R2 en `data/{año}/{mes}/` y actualizará `data/latest/`
- Todo sin intervención manual
```
https://rem-bcra-api.facujallia.workers.dev
```

### Endpoints Disponibles

#### `GET /api`
Índice de la API con documentación

```bash
curl https://rem-bcra-api.facujallia.workers.dev/api
```

#### `GET /api/metadata`
Información sobre la última actualización

```bash
curl https://rem-bcra-api.facujallia.workers.dev/api/metadata
```

#### `GET /api/bloques`
Archivo maestro con todas las tablas (última versión)

```bash
curl https://rem-bcra-api.facujallia.workers.dev/api/bloques
```

#### `GET /api/{tabla}`
Obtener tabla específica

**Última versión (latest):**
```bash
curl https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio
curl https://rem-bcra-api.facujallia.workers.dev/api/ipc_general
```

**Período específico:**
```bash
# Con formato periodo
curl https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio?periodo=2025-11

# Con parámetros separados
curl https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio?year=2025&month=11
```

### Estructura de Datos en R2

```
data/
├── latest/              # Siempre contiene la última versión
│   ├── rem_*.json      # Tablas actuales
│   └── _metadata.json
│
└── YYYY/               # Histórico por año
    └── MM/             # Histórico por mes
        ├── rem_*.json
        └── _metadata.json

Ejemplos:
- data/latest/rem_tipo_cambio.json    → Último REM publicado
- data/2025/11/rem_tipo_cambio.json   → REM de noviembre 2025
- data/2025/12/rem_tipo_cambio.json   → REM de diciembre 2025
```

Respuesta:
```json
{
  "ultima_actualizacion": "2025-12-17T10:30:00Z",
  "archivos": 19,
  "tablas": ["ipc_general", "tipo_cambio", ...],
  "version": "1.0"
}
```

#### `GET /api/bloques`
Archivo maestro con todas las tablas

```bash
curl https://rem-bcra-api.your-subdomain.workers.dev/api/bloques
```

#### `GET /api/{tabla}`
Obtener una tabla específica

**Ejemplos:**

```bash
# Tipo de cambio
curl https://rem-bcra-api.your-subdomain.workers.dev/api/tipo_cambio

# IPC General
curl https://rem-bcra-api.your-subdomain.workers.dev/api/ipc_general

# PBI
curl https://rem-bcra-api.your-subdomain.workers.dev/api/pbi

# Exportaciones
curl https://rem-bcra-api.your-subdomain.workers.dev/api/exportaciones
```

**Tablas disponibles:**
- `ipc_general` / `ipc_general_top10`
- `ipc_nucleo` / `ipc_nucleo_top10`
- `tasa_interes` / `tasa_interes_top10`
- `tipo_cambio` / `tipo_cambio_top10`
- `exportaciones` / `exportaciones_top10`
- `importaciones` / `importaciones_top10`
- `resultado_primario` / `resultado_primario_top10`
- `desocupacion` / `desocupacion_top10`
- `pbi` / `pbi_top10`

### Ejemplo de Uso en Python

```python
import requests

# Obtener tipo de cambio
response = requests.get('https://rem-bcra-api.your-subdomain.workers.dev/api/tipo_cambio')
data = response.json()

print(f"Título: {data['titulo']}")
print(f"Filas: {data['filas']}")
print(f"\nPrimeros datos:")
for row in data['datos'][:3]:
    print(f"  {row['período']}: {row['mediana']} {row['referencia']}")
```

### Ejemplo de Uso en JavaScript

```javascript
// Obtener IPC
fetch('https://rem-bcra-api.your-subdomain.workers.dev/api/ipc_general')
  .then(res => res.json())
  .then(data => {
    console.log(`Título: ${data.titulo}`);
    console.log(`Filas: ${data.filas}`);
    console.log('Datos:', data.datos);
  });
```

### CORS
La API tiene CORS habilitado, así que puede ser consumida desde navegadores web.

### Cache
Las respuestas tienen cache de 1 hora (`Cache-Control: public, max-age=3600`)

---

## 🔧 Uso

## 📊 Formato de Salida

Cada archivo JSON tiene la siguiente estructura:

```json
{
  "titulo": "Tipo de cambio nominal",
  "hoja": "Cuadros de resultados",
  "clave": "tipo_cambio",
  "filas": 9,
  "columnas": ["período", "referencia", "mediana", "promedio", ...],
  "datos": [
    {
      "período": "2025-12-31",
      "referencia": "$/USD",
      "mediana": 1472.94,
      "promedio": 1468.86,
      ...
    }
  ]
}
```

## 🌐 Arquitectura Recomendada

```
BCRA Website (https://www.bcra.gob.ar)
    ↓
[GitHub Actions] (Cron: semanal, lunes 10:00 UTC)
    ↓
1. download REM      →  data/tablas-*.xlsx
2. read REM.py       →  data/rem_*.json (18 tablas)
3. validate (skip)   →  Verifica integridad básica
4. deploy R2         →  Sube JSONs a Cloudflare R2
    ↓
[Cloudflare R2]      →  Storage de archivos JSON
    ↓
[Cloudflare Worker]  →  API REST pública con cache
    ↓
Usuarios/Apps (múltiples consumidores)
    ↓
Tu app, dashboards, análisis, etc.
```

### ✅ Ventajas de esta arquitectura

- **Escalable**: CDN global de Cloudflare
- **Rápido**: Cache en edge, baja latencia
- **Gratis**: 10GB R2 + 100K requests/día
- **Separación**: Código (GitHub) vs Datos (R2)
- **Público**: API accesible para múltiples usuarios
- **Versionado**: Git para código, R2 para datos

---

## 📝 Notas Técnicas

- **Encoding**: UTF-8 para todos los archivos
- **Fechas**: ISO 8601 (YYYY-MM-DD)
- **Números**: Float con punto decimal
- **Valores nulos**: `null` en JSON
- **SSL**: `verify=False` para descarga (certificado BCRA)

## 📄 Licencia

Datos públicos del BCRA. Script open source.

---

**Estado**: ✅ Parser funcionando, pendiente automatización y API
