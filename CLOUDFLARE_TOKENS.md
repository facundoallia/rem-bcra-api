# 🔑 Crear Token de Cloudflare para Workers

Tu token actual "R2 REM Pipeline" solo tiene permisos para R2. Para desplegar Workers necesitas crear un token adicional.

## Pasos:

1. Ve a: https://dash.cloudflare.com/b716491d6afe361dba0e016519df6cb3/api-tokens

2. Click en **"Create Token"**

3. Usa la plantilla **"Edit Cloudflare Workers"**  
   O crea un token personalizado con estos permisos:

   **Permissions:**
   - Account → Workers Scripts → Edit
   - Account → Workers R2 Storage → Edit
   - Account → Workers KV Storage → Edit (opcional, pero recomendado)

4. **Account Resources:**
   - Include: Tu cuenta (Facujallia@gmail.com's Account)

5. **Zone Resources:** (opcional)
   - Skip

6. **Client IP Address Filtering:** (opcional)
   - Skip

7. **TTL:** (opcional)
   - Default (sin fecha de expiración)

8. Click **"Continue to summary"**

9. Click **"Create Token"**

10. **GUARDAR EL TOKEN** - Cloudflare solo lo muestra una vez

## Usar el Token

Una vez que tengas el token, ejecútalo así:

```powershell
$env:PATH = "$env:APPDATA\npm;$env:PATH"
$env:CLOUDFLARE_API_TOKEN = "TU_NUEVO_TOKEN_AQUI"
$env:CLOUDFLARE_ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
cd "C:\Desarrollos\api REM\worker"
wrangler deploy
```

## Alternativa: Usar Email + API Key (Más Simple)

Si prefieres no crear más tokens, puedes usar tu **Global API Key**:

1. Ve a: https://dash.cloudflare.com/profile/api-tokens
2. Busca **"Global API Key"** y click en **"View"**
3. Copia la API Key
4. Ejecútalo así:

```powershell
$env:PATH = "$env:APPDATA\npm;$env:PATH"
$env:CLOUDFLARE_EMAIL = "facujallia@gmail.com"
$env:CLOUDFLARE_API_KEY = "TU_GLOBAL_API_KEY_AQUI"
$env:CLOUDFLARE_ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
cd "C:\Desarrollos\api REM\worker"
wrangler deploy
```

⚠️ **Nota de seguridad:** La Global API Key tiene acceso completo a tu cuenta. Es más seguro usar tokens con permisos específicos, pero más fácil para empezar.

## ¿Qué Token Usar?

| Token | Para qué | Permisos |
|-------|----------|----------|
| **R2 REM Pipeline** (actual) | Subir archivos a R2 | Solo R2 bucket rem-data |
| **Worker Deploy Token** (nuevo) | Desplegar el Worker | Workers + R2 (binding) |

Ambos tokens son necesarios:
- El primero se usa en GitHub Actions para subir datos
- El segundo se usa una vez para desplegar el Worker

Una vez desplegado el Worker, solo necesitas el token R2 para las actualizaciones diarias.
