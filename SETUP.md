# 🚀 Guía de Configuración y Deploy

## Requisitos Previos

1. ✅ Cuenta de Cloudflare (gratis)
2. ✅ GitHub Actions habilitado en el repo
3. ✅ Node.js instalado (para Wrangler CLI)

---

## PASO 1: Configurar Cloudflare R2

### 1.1 Crear cuenta Cloudflare
1. Ve a https://dash.cloudflare.com/sign-up
2. Crea una cuenta gratuita
3. Verifica tu email

### 1.2 Crear R2 Bucket
1. En Cloudflare Dashboard → **R2**
2. Click **Create bucket**
3. Nombre: `rem-bcra-data`
4. Región: **Automatic**
5. Click **Create bucket**

### 1.3 Obtener credenciales API
1. En R2 → **Manage R2 API Tokens**
2. Click **Create API token**
3. Nombre: `github-actions-rem`
4. Permisos:
   - **Object Read & Write**
   - Aplicar a bucket: `rem-bcra-data`
5. Click **Create API Token**
6. **GUARDAR** estos valores (no se vuelven a mostrar):
   ```
   Access Key ID: xxxxxxxxxxxxxxxxx
   Secret Access Key: yyyyyyyyyyyyyyyy
   ```

### 1.4 Obtener Account ID
1. En R2 Dashboard, lado derecho verás **Account ID**
2. Copiar el Account ID (ej: `abc123def456...`)

---

## PASO 2: Configurar GitHub Secrets

### 2.1 Agregar secrets al repositorio
1. Ve a tu repo en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Agregar estos 3 secrets:

#### Secret 1: CF_ACCOUNT_ID
- Name: `CF_ACCOUNT_ID`
- Secret: `[tu account ID de Cloudflare]`

#### Secret 2: CF_ACCESS_KEY_ID
- Name: `CF_ACCESS_KEY_ID`
- Secret: `[Access Key ID del paso 1.3]`

#### Secret 3: CF_SECRET_ACCESS_KEY
- Name: `CF_SECRET_ACCESS_KEY`
- Secret: `[Secret Access Key del paso 1.3]`

---

## PASO 3: Instalar Wrangler CLI (local)

```bash
# Instalar Wrangler globalmente
npm install -g wrangler

# O con pnpm
pnpm add -g wrangler

# Verificar instalación
wrangler --version
```

### 3.1 Login a Cloudflare
```bash
wrangler login
```
Esto abrirá tu navegador para autenticar.

---

## PASO 4: Configurar Cloudflare Worker

### 4.1 Crear Worker
```bash
cd "api REM/worker"

# Editar wrangler.toml si es necesario
# Cambiar el nombre del worker si quieres

# Deploy del worker
wrangler deploy
```

Esto desplegará el Worker y te dará una URL como:
```
https://rem-bcra-api.your-subdomain.workers.dev
```

### 4.2 Vincular R2 al Worker (si no se hizo automático)
```bash
wrangler r2 bucket create rem-bcra-data
```

---

## PASO 5: Probar el Flujo Completo

### 5.1 Test Local (antes de GitHub Actions)

```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd "C:\Desarrollos\api REM"

# Configurar variables de entorno temporalmente (PowerShell)
$env:CF_ACCOUNT_ID="tu_account_id"
$env:CF_ACCESS_KEY_ID="tu_access_key"
$env:CF_SECRET_ACCESS_KEY="tu_secret_key"

# Ejecutar el flujo completo
python "download REM"
python "read REM.py"
python deploy_to_cloudflare.py
```

Si todo funciona, verás:
```
✅ Deploy exitoso
🌐 Los datos están disponibles en: ...
```

### 5.2 Probar la API

```bash
# Probar Worker
curl https://rem-bcra-api.your-subdomain.workers.dev/api

# Probar endpoint específico
curl https://rem-bcra-api.your-subdomain.workers.dev/api/tipo_cambio

# Probar metadata
curl https://rem-bcra-api.your-subdomain.workers.dev/api/metadata
```

---

## PASO 6: Ejecutar GitHub Actions

### 6.1 Ejecución Manual (primera vez)
1. Ve a tu repo → **Actions**
2. Selecciona workflow **"Actualizar REM BCRA"**
3. Click **Run workflow**
4. Selecciona branch `main`
5. Click **Run workflow**

### 6.2 Verificar Logs
1. Click en el workflow ejecutándose
2. Revisa cada paso:
   - ✅ Descargar REM
   - ✅ Parsear Excel
   - ✅ Validar (puede tener warnings)
   - ✅ Deploy a R2

### 6.3 Si hay errores
- Revisa los logs del paso que falló
- Verifica que los secrets estén configurados correctamente
- Verifica que el bucket R2 exista

---

## PASO 7: Configuración Automática (Cron)

El workflow ya está configurado para ejecutarse:
- **Todos los lunes a las 10:00 UTC** (7:00 AM Argentina)

Para cambiar la frecuencia, edita `.github/workflows/update-rem.yml`:

```yaml
on:
  schedule:
    # Cron syntax: minuto hora día mes día-semana
    - cron: '0 10 * * 1'  # Lunes 10:00 UTC
    # Ejemplos:
    # - cron: '0 12 * * *'     # Diario a las 12:00 UTC
    # - cron: '0 9 * * 1,4'    # Lunes y Jueves 9:00 UTC
```

---

## PASO 8: Dominio Personalizado (Opcional)

### 8.1 Si tienes un dominio en Cloudflare
1. Workers & Pages → tu worker
2. **Settings** → **Triggers** → **Custom Domains**
3. Click **Add Custom Domain**
4. Ingresa: `api.tudominio.com`
5. Cloudflare configurará DNS automáticamente

Ahora tu API estará en: `https://api.tudominio.com/api`

---

## 🔍 Troubleshooting

### Error: "Bucket not found"
```bash
# Crear bucket manualmente
wrangler r2 bucket create rem-bcra-data
```

### Error: "Unauthorized" en GitHub Actions
- Verifica que los 3 secrets estén configurados
- Verifica que los nombres sean exactos (case-sensitive)
- Regenera las credenciales de R2 si es necesario

### Error: "Module not found" en Worker
```bash
# Reinstalar dependencias
cd worker
wrangler deploy --dry-run  # Test local primero
wrangler deploy             # Deploy real
```

### La API no responde
1. Verifica que el Worker esté desplegado:
   ```bash
   wrangler deployments list
   ```
2. Verifica que R2 tenga los archivos:
   ```bash
   wrangler r2 object list rem-bcra-data --prefix data/
   ```

---

## 📊 Monitoreo

### Ver logs del Worker
```bash
wrangler tail
```

Esto mostrará requests en tiempo real.

### Ver métricas en Cloudflare
1. Workers & Pages → tu worker
2. **Metrics** tab
3. Verás: requests/día, errores, latencia

---

## 🎯 URLs Finales

Después de configurar todo:

- **API Base**: `https://rem-bcra-api.[tu-subdomain].workers.dev/api`
- **Tipo de Cambio**: `.../api/tipo_cambio`
- **IPC General**: `.../api/ipc_general`
- **Todas las tablas**: `.../api/bloques`
- **Metadata**: `.../api/metadata`

---

## ✅ Checklist de Configuración

- [ ] Cuenta Cloudflare creada
- [ ] Bucket R2 `rem-bcra-data` creado
- [ ] Credenciales API de R2 obtenidas
- [ ] 3 secrets configurados en GitHub
- [ ] Wrangler CLI instalado
- [ ] Worker desplegado
- [ ] Test local exitoso
- [ ] GitHub Actions ejecutado manualmente
- [ ] API funcionando correctamente
- [ ] Cron configurado

---

## 🆘 Soporte

- **Docs Cloudflare R2**: https://developers.cloudflare.com/r2/
- **Docs Workers**: https://developers.cloudflare.com/workers/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**¡Listo!** Tu API REM está configurada y desplegada 🚀
