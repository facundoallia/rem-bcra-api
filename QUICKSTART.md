# 🚀 Guía de Inicio Rápido

## ✅ Estado del Proyecto

**TODO EL CÓDIGO ESTÁ COMPLETO Y LISTO** 🎉

- ✅ Parser funcional (18 tablas)
- ✅ GitHub Actions configurado
- ✅ Cloudflare Worker desarrollado
- ✅ Deploy automático implementado
- ✅ API REST con 7 endpoints

**Solo falta: Configurar Cloudflare (30-60 min)**

---

## 🎯 Configuración en 5 Pasos

### 1. Crear cuenta Cloudflare (5 min)
```
https://dash.cloudflare.com/sign-up
→ Verifica email
→ Plan gratuito
```

### 2. Crear R2 Bucket (5 min)
```
Dashboard → R2 → Create bucket
Nombre: rem-bcra-data
Región: Automatic
```

### 3. Obtener credenciales (10 min)
```
R2 → Manage R2 API Tokens → Create API token
Nombre: github-actions-rem
Permisos: Object Read & Write
Aplicar a: rem-bcra-data

COPIAR:
- Access Key ID
- Secret Access Key
- Account ID (en dashboard)
```

### 4. Configurar GitHub Secrets (5 min)
```
GitHub repo → Settings → Secrets and variables → Actions
New repository secret (crear 3):

1. CF_ACCOUNT_ID = [tu account ID]
2. CF_ACCESS_KEY_ID = [tu access key]
3. CF_SECRET_ACCESS_KEY = [tu secret key]
```

### 5. Deploy Worker (10 min)
```bash
# Instalar Wrangler CLI
npm install -g wrangler

# Login a Cloudflare
wrangler login

# Deploy Worker
cd "api REM/worker"
wrangler deploy
```

**¡LISTO!** Tu API estará en:
```
https://rem-bcra-api.xxx.workers.dev
```

---

## 🧪 Probar Todo

### Probar Manualmente (local)

```bash
cd "C:\Desarrollos\api REM"

# 1. Descargar datos
python "download REM"

# 2. Parsear Excel
python "read REM.py"

# 3. Verificar
python verificar_tablas.py

# 4. Deploy a R2 (configurar env vars primero)
$env:CF_ACCOUNT_ID="xxx"
$env:CF_ACCESS_KEY_ID="xxx"
$env:CF_SECRET_ACCESS_KEY="xxx"

python deploy_to_cloudflare.py
```

### Probar GitHub Actions

```
GitHub → Actions → "Actualizar REM BCRA"
→ Run workflow
→ Esperar ~2 min
→ Verificar logs
```

### Probar API

```bash
# Test automático
python test_api.py https://rem-bcra-api.xxx.workers.dev

# Test manual
curl https://rem-bcra-api.xxx.workers.dev/api
curl https://rem-bcra-api.xxx.workers.dev/api/tipo_cambio
curl https://rem-bcra-api.xxx.workers.dev/api/ipc_general
```

---

## 📊 Endpoints de la API

Una vez desplegado:

### Base
```
GET /api
→ Índice con documentación
```

### Metadata
```
GET /api/metadata
→ Última actualización, tablas disponibles
```

### Archivo Maestro
```
GET /api/bloques
→ Todas las 18 tablas en un JSON
```

### Tablas Individuales
```
GET /api/tipo_cambio
GET /api/ipc_general
GET /api/ipc_nucleo
GET /api/tasa_interes
GET /api/exportaciones
GET /api/importaciones
GET /api/resultado_primario
GET /api/desocupacion
GET /api/pbi

# Versiones TOP 10
GET /api/tipo_cambio_top10
GET /api/ipc_general_top10
... etc
```

---

## 🔄 Flujo Automático

Una vez configurado, el sistema funciona solo:

```
Lunes 10:00 UTC (7:00 AM Argentina)
↓
GitHub Actions se ejecuta automáticamente
↓
1. Descarga XLSX del BCRA
2. Parsea a 18 JSONs
3. Valida datos
4. Sube a Cloudflare R2
5. Actualiza metadata
↓
API pública se actualiza automáticamente
↓
Tus apps consumen la nueva data
```

**Cero intervención manual requerida** ✨

---

## 📖 Documentación Completa

- **README.md** - Descripción general y uso
- **SETUP.md** - Instrucciones detalladas paso a paso
- **ROADMAP.md** - Plan de desarrollo y mejoras futuras
- **QUICKSTART.md** (este archivo) - Inicio rápido

---

## 🆘 Solución de Problemas

### Error: "Bucket not found"
```bash
wrangler r2 bucket create rem-bcra-data
```

### Error: "Unauthorized" en Actions
→ Verificar que los 3 secrets estén configurados correctamente

### Worker no responde
```bash
# Ver logs en tiempo real
cd worker
wrangler tail
```

### API devuelve 404
→ Verificar que R2 tenga los archivos:
```bash
wrangler r2 object list rem-bcra-data --prefix data/
```

---

## 💡 Consejos

1. **Primera vez**: Ejecuta el workflow manualmente para ver que todo funcione
2. **Logs**: Revisa los logs de GitHub Actions si algo falla
3. **Cache**: La API tiene cache de 1 hora - datos se actualizan c/hora como máximo
4. **CORS**: Ya está habilitado - puedes consumir desde navegadores
5. **Gratis**: Todo es gratis dentro de los límites generosos de Cloudflare

---

## 🎯 Uso en Otros Proyectos

### Python
```python
import requests

# Obtener tipo de cambio
resp = requests.get('https://rem-bcra-api.xxx.workers.dev/api/tipo_cambio')
data = resp.json()

print(f"Último dato: {data['datos'][0]}")
```

### JavaScript/TypeScript
```javascript
// Fetch
const resp = await fetch('https://rem-bcra-api.xxx.workers.dev/api/ipc_general');
const data = await resp.json();

console.log(data.titulo);
console.log(data.datos);
```

### curl/bash
```bash
# Descargar localmente
curl -o tipo_cambio.json https://rem-bcra-api.xxx.workers.dev/api/tipo_cambio

# Ver en terminal
curl https://rem-bcra-api.xxx.workers.dev/api/metadata | jq
```

---

## 📈 Próximas Mejoras (Opcional)

- [ ] Dominio personalizado (api.tudominio.com)
- [ ] Histórico de releases mensuales
- [ ] Filtros por fecha en endpoints
- [ ] WebSocket para updates en tiempo real
- [ ] Dashboard de visualización
- [ ] Rate limiting por usuario

**Pero la versión actual ya es completamente funcional** ✅

---

## ✨ Resumen

**Lo que tienes:**
- ✅ API REST pública con 18 tablas de datos del BCRA
- ✅ Actualización automática semanal
- ✅ CDN global de Cloudflare (rápido en todo el mundo)
- ✅ 100% gratis (dentro de límites generosos)
- ✅ Código open source y documentado

**Lo que necesitas hacer:**
1. Configurar Cloudflare (30-60 min)
2. Agregar secrets a GitHub (5 min)
3. Deploy Worker (5 min)

**Total: ~1 hora de configuración inicial**

Después de eso: **cero mantenimiento** 🚀

---

**¿Listo para empezar?** → Ver **SETUP.md** para instrucciones detalladas

**¿Dudas?** → Revisa los logs de GitHub Actions o Worker

**¡A consumir datos! 🎉**
