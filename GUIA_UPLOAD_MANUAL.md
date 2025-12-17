# 📁 GUÍA: Subir Archivos Manualmente al Dashboard de Cloudflare

## 📋 Estructura de Carpetas

```
rem-data (bucket)
├── data/
│   ├── latest/           # ← Última versión (se actualiza cada mes)
│   │   ├── rem_bloques.json
│   │   ├── rem_tipo_cambio.json
│   │   ├── rem_ipc_general.json
│   │   ├── ... (19 archivos)
│   │   └── _metadata.json
│   │
│   └── 2025/
│       ├── 11/           # ← Noviembre 2025 (histórico permanente)
│       │   ├── rem_bloques.json
│       │   ├── rem_tipo_cambio.json
│       │   ├── ... (19 archivos)
│       │   └── _metadata.json
│       │
│       ├── 12/           # ← Diciembre 2025
│       │   └── ...
│       │
│       └── ...
│
└── 2026/
    ├── 01/               # ← Enero 2026
    │   └── ...
    └── ...
```

## 🎯 Pasos para Subir Archivos (Hoy - Noviembre 2025)

### 1. Abrir Dashboard de Cloudflare R2

**URL directa:** https://dash.cloudflare.com/b716491d6afe361dba0e016519df6cb3/r2/buckets/rem-data

### 2. Crear Estructura de Carpetas

**Opción A: Desde la interfaz web**
1. Click en **"Create folder"**
2. Nombre: `data` → Create
3. Entrar a `data/` → Click **"Create folder"**
4. Nombre: `latest` → Create
5. Volver a `data/` → Click **"Create folder"**
6. Nombre: `2025` → Create
7. Entrar a `2025/` → Click **"Create folder"**
8. Nombre: `11` → Create

**Resultado esperado:**
```
✅ data/latest/
✅ data/2025/11/
```

### 3. Subir Archivos a `data/2025/11/`

1. **Navegar a:** `data/2025/11/`
2. Click en **"Upload"** → **"Upload files"**
3. **Seleccionar todos estos archivos desde** `C:\Desarrollos\api REM\data\`:
   ```
   ✅ rem_bloques.json
   ✅ rem_desocupacion.json
   ✅ rem_desocupacion_top10.json
   ✅ rem_exportaciones.json
   ✅ rem_exportaciones_top10.json
   ✅ rem_importaciones.json
   ✅ rem_importaciones_top10.json
   ✅ rem_ipc_general.json
   ✅ rem_ipc_general_top10.json
   ✅ rem_ipc_nucleo.json
   ✅ rem_ipc_nucleo_top10.json
   ✅ rem_pbi.json
   ✅ rem_pbi_top10.json
   ✅ rem_resultado_primario.json
   ✅ rem_resultado_primario_top10.json
   ✅ rem_tasa_interes.json
   ✅ rem_tasa_interes_top10.json
   ✅ rem_tipo_cambio.json
   ✅ rem_tipo_cambio_top10.json
   ```
4. Click **"Upload"** y esperar confirmación (19 archivos)

### 4. Subir los MISMOS Archivos a `data/latest/`

1. **Navegar a:** `data/latest/`
2. Click en **"Upload"** → **"Upload files"**
3. **Seleccionar los mismos 19 archivos** desde `C:\Desarrollos\api REM\data\`
4. Click **"Upload"**

**⚠️ IMPORTANTE:** `latest/` siempre contiene la última versión publicada. Cuando salga el REM de diciembre, se reemplazarán estos archivos.

### 5. Verificar Upload

Deberías ver en el dashboard:
```
✅ data/2025/11/ → 19 archivos
✅ data/latest/ → 19 archivos
Total: 38 archivos
```

---

## 🌐 Acceso Remoto (Desde Casa sin Proxy)

### URLs de la API

**✅ SÍ funcionará desde tu casa sin proxy corporativo:**

```
https://rem-bcra-api.facujallia.workers.dev/api
https://rem-bcra-api.facujallia.workers.dev/api/metadata
https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio
https://rem-bcra-api.facujallia.workers.dev/api/ipc_general
```

**Consultar períodos históricos:**
```
https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio?periodo=2025-11
https://rem-bcra-api.facujallia.workers.dev/api/ipc_general?year=2025&month=11
```

### Probar desde Casa

**Desde navegador:**
```
https://rem-bcra-api.facujallia.workers.dev/api
```

**Desde Python:**
```python
import requests
import json

# Datos actuales (latest)
r = requests.get('https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio')
data = r.json()
print(f"Registros: {len(data)}")
print(json.dumps(data[:2], indent=2, ensure_ascii=False))

# Datos históricos (noviembre 2025)
r = requests.get('https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio?periodo=2025-11')
data = r.json()
print(f"Registros Nov 2025: {len(data)}")
```

**Desde curl (Linux/Mac):**
```bash
curl https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio | jq
```

**Desde PowerShell (Windows):**
```powershell
Invoke-RestMethod https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio | ConvertTo-Json -Depth 10
```

---

## 🤖 Ejecución Automática (GitHub Actions)

### ¿Se ejecutará de forma remota?

**✅ SÍ, completamente automático**

**Cuándo:** Todos los días entre el 1 y 7 de cada mes a las 12:00 UTC (9:00 AM Argentina)

**Qué hace:**
1. ✅ Descarga el XLSX del REM desde BCRA
2. ✅ Verifica si ya fue procesado (exit code)
3. ✅ Parsea 18 tablas a JSON
4. ✅ Sube a R2 en `data/YYYY/MM/` (detecta automáticamente el mes)
5. ✅ Actualiza `data/latest/` con la nueva versión
6. ✅ No requiere intervención manual

**Configuración necesaria:**

1. **Agregar GitHub Secrets** (una sola vez):
   ```
   Settings → Secrets and variables → Actions → New repository secret
   
   CLOUDFLARE_API_TOKEN = Cm8qe2j5U9GW5qncg-z6iGc7LAV58DYlve1Iyd_T
   CLOUDFLARE_ACCOUNT_ID = b716491d6afe361dba0e016519df6cb3
   ```

2. **Workflow ya configurado en:**
   `.github/workflows/update-rem.yml`

**Ver logs:**
https://github.com/facundoallia/carry-trade-analyzer/actions

---

## 📊 Ventajas de esta Estructura

### Para Usuarios de la API:
✅ **URL simple:** `https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio` (siempre devuelve lo más reciente)
✅ **Histórico fácil:** `?periodo=2025-11` para consultar meses anteriores
✅ **Sin cambios de URL:** Mismo endpoint, datos actualizados automáticamente

### Para Análisis de Datos:
✅ **Comparaciones mensuales:** Descargar nov vs dic para análisis de tendencias
✅ **Histórico completo:** Todos los períodos guardados permanentemente
✅ **Trazabilidad:** Saber exactamente qué datos había en cada fecha

### Para Mantenimiento:
✅ **No se sobrescribe histórico:** Datos de nov 2025 siempre estarán en `data/2025/11/`
✅ **Rollback fácil:** Si hay error, se puede copiar de período anterior
✅ **Auditoría:** Ver evolución de datos mes a mes

---

## ⏱️ Tiempos

- **Subir manualmente hoy:** 10 minutos
- **Configurar GitHub Secrets:** 2 minutos
- **Total setup:** 12 minutos

Después de eso, **100% automático** cada mes. Nunca más tendrás que subir archivos manualmente.

---

## 🎯 Checklist Final

- [ ] Crear carpetas: `data/latest/` y `data/2025/11/`
- [ ] Subir 19 archivos JSON a `data/2025/11/`
- [ ] Subir los mismos 19 archivos a `data/latest/`
- [ ] Probar API desde el navegador: https://rem-bcra-api.facujallia.workers.dev/api
- [ ] Probar tabla específica: https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio
- [ ] Agregar secrets en GitHub
- [ ] Esperar a diciembre y verificar que se actualiza solo 🎉

---

**¿Todo claro? Una vez que subas los archivos, avísame y probamos la API juntos desde tu casa (sin proxy) para confirmar que funciona.**
