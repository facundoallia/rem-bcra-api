# 🔧 Solución: Error de Autenticación en GitHub Actions

## ❌ Error Reportado

```
Failed to fetch /accounts/b716491d6afe361dba0e016519d
```

Este error indica que Wrangler no puede autenticarse con la API de Cloudflare.

## ✅ Soluciones Aplicadas

### 1. Mejoras en el Script de Deploy

Se actualizó `deploy_with_wrangler.py` con:

- ✅ **Paso explícito del Account ID**: Ahora se pasa `--account-id` directamente al comando wrangler
- ✅ **Verificación de autenticación**: Se añadió una función que verifica la conexión antes de subir archivos
- ✅ **Mejor manejo de errores**: Muestra tanto stdout como stderr para debugging
- ✅ **Variables de entorno explícitas**: Se asegura que las variables se pasen correctamente

### 2. Pasos para Configurar los Secrets de GitHub

#### A. Verificar/Crear el API Token de Cloudflare

1. Ve a: https://dash.cloudflare.com/profile/api-tokens

2. **Opción 1: Usar token existente "R2 REM Pipeline"**
   - Si ya existe, verifica que tenga estos permisos:
     - Account → Account Settings → Read
     - Account → Workers R2 Storage → Edit

3. **Opción 2: Crear un nuevo token**
   - Click en "Create Token"
   - Usa la plantilla "Edit Cloudflare Workers" o personaliza con:
     ```
     Permissions:
     - Account → Account Settings → Read
     - Account → Workers R2 Storage → Edit
     - Account → Workers Scripts → Edit (opcional)

     Account Resources:
     - Include: Tu cuenta específica
     ```
   - Click "Continue to summary" → "Create Token"
   - **IMPORTANTE**: Copia el token, Cloudflare solo lo muestra una vez

#### B. Obtener el Account ID

El Account ID completo es: `b716491d6afe361dba0e016519df6cb3`

Puedes verificarlo en:
- URL del dashboard: https://dash.cloudflare.com/`[ACCOUNT_ID]`/...
- Cloudflare Dashboard → Account Home → Sidebar derecho

#### C. Configurar Secrets en GitHub

1. Ve al repositorio: https://github.com/[tu-usuario]/rem-bcra-api

2. Click en **Settings** → **Secrets and variables** → **Actions**

3. Añade o actualiza estos secrets:

   **CLOUDFLARE_API_TOKEN**
   ```
   [Tu token de API - empieza con algo como "XbKj..." ]
   ```

   **CLOUDFLARE_ACCOUNT_ID**
   ```
   b716491d6afe361dba0e016519df6cb3
   ```

4. Verifica que los nombres coincidan **exactamente** (case-sensitive)

## 🧪 Verificar la Configuración Localmente

Antes de ejecutar el GitHub Action, prueba localmente:

```powershell
# Windows PowerShell
$env:CLOUDFLARE_API_TOKEN = "tu_token_aqui"
$env:CLOUDFLARE_ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"

python deploy_with_wrangler.py
```

```bash
# Linux/Mac
export CLOUDFLARE_API_TOKEN="tu_token_aqui"
export CLOUDFLARE_ACCOUNT_ID="b716491d6afe361dba0e016519df6cb3"

python deploy_with_wrangler.py
```

### ✅ Output Esperado

Si la configuración es correcta, deberías ver:

```
======================================================================
🚀 DEPLOY A CLOUDFLARE R2 (WRANGLER)
======================================================================

🔐 Verificando autenticación con Cloudflare...
----------------------------------------------------------------------
✅ Wrangler version: 3.x.x
✅ Autenticación exitosa
   Account ID: b716491d...
✅ Bucket 'rem-data' encontrado
----------------------------------------------------------------------

📅 Fecha detectada: 2025/01
...
```

### ❌ Si Falla

Si ves alguno de estos errores:

**"Failed to fetch /accounts/..."**
- ❌ API Token incorrecto o expirado
- ❌ Account ID incorrecto
- ❌ Token sin permisos suficientes

**"Bucket 'rem-data' no encontrado"**
- ⚠️ El bucket no existe o el token no tiene permisos para verlo
- Solución: Verifica en Cloudflare Dashboard → R2 que el bucket exista

## 🔄 Re-ejecutar el GitHub Action

Una vez configurados los secrets:

1. Ve a: https://github.com/[tu-usuario]/rem-bcra-api/actions

2. Selecciona el workflow "Actualizar REM BCRA"

3. Click en **"Run workflow"** → **"Run workflow"**

4. Observa los logs:
   - El paso "Deploy a Cloudflare R2" debe mostrar el output de verificación
   - Si falla, revisa los logs completos para ver el error específico

## 📋 Checklist de Troubleshooting

- [ ] El API token existe y está copiado correctamente
- [ ] El API token tiene permisos de "Account Settings Read" y "R2 Storage Edit"
- [ ] El Account ID es exactamente: `b716491d6afe361dba0e016519df6cb3`
- [ ] Los secrets están configurados en GitHub con nombres exactos
- [ ] El bucket `rem-data` existe en Cloudflare R2
- [ ] La prueba local funciona correctamente
- [ ] Wrangler está instalado globalmente (`npm install -g wrangler`)

## 🆘 Si Persiste el Error

Si después de seguir todos los pasos el error persiste:

1. **Regenera el API Token**
   - Elimina el token viejo en Cloudflare
   - Crea uno nuevo con los permisos correctos
   - Actualiza el secret en GitHub

2. **Verifica permisos del bucket**
   - Dashboard → R2 → rem-data → Settings
   - Asegúrate que el bucket no tenga restricciones de acceso

3. **Revisa los logs completos del GitHub Action**
   - Busca el mensaje exacto de error en stderr
   - Comparte el log completo para diagnóstico específico

4. **Prueba con Global API Key** (temporal, solo para testing)
   ```yaml
   env:
     CLOUDFLARE_EMAIL: ${{ secrets.CLOUDFLARE_EMAIL }}
     CLOUDFLARE_API_KEY: ${{ secrets.CLOUDFLARE_API_KEY }}
     CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
   ```

   Nota: Esto requiere añadir los secrets CLOUDFLARE_EMAIL y CLOUDFLARE_API_KEY,
   pero usa permisos más amplios (menos seguro).

## 📚 Referencias

- [Cloudflare API Tokens](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [Wrangler Authentication](https://developers.cloudflare.com/workers/wrangler/commands/#authentication)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
