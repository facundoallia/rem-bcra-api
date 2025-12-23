# 🔒 Seguridad y Mejores Prácticas

## ✅ Implementaciones de Seguridad

### 1. Credenciales Protegidas

**❌ ANTES** (INSEGURO):
```python
API_TOKEN = "Cm8qe2j5U9GW5qncg-z6iGc7LAV58DYlve1Iyd_T"  # Hardcoded
ACCOUNT_ID = "b716491d6afe361dba0e016519df6cb3"
```

**✅ AHORA** (SEGURO):
```python
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
```

**Archivos afectados:**
- ✅ [deploy_with_wrangler.py](deploy_with_wrangler.py)
- ✅ [get_account_info.py](get_account_info.py)

### 2. Rate Limiting Implementado

**Protecciones activas:**
- 🚦 1 petición por minuto por IP
- 📊 100,000 peticiones mensuales global
- 🔄 Respuesta 429 con header `Retry-After`
- 📈 Endpoint `/api/stats` para monitoreo

**Implementación:** [worker.js](worker/worker.js)

### 3. URL Profesional

**❌ ANTES**: 
```
https://rem-bcra-api.facujallia.workers.dev
```

**✅ AHORA**:
```
https://bcra-rem-api.<TU_SUBDOMINIO>.workers.dev
```

Sin datos personales en la URL pública.

### 4. Archivo .gitignore Actualizado

Protege:
- ✅ `.env` y variables de entorno
- ✅ Archivos temporales con credenciales
- ✅ Logs con información sensible
- ✅ Datos generados localmente

## 🔐 Checklist de Seguridad

### Antes de Hacer Push

- [ ] No hay tokens en el código
- [ ] `.env` está en `.gitignore`
- [ ] Variables de entorno configuradas localmente
- [ ] GitHub Secrets configurados para CI/CD
- [ ] No hay Account IDs públicos innecesarios

### Verificación Rápida

```bash
# Buscar posibles credenciales
grep -r "token\|password\|secret\|api_key" --include="*.py" --include="*.js"

# Verificar .gitignore
cat .gitignore | grep -E "\.env|token|secret"
```

## 📝 Variables de Entorno Requeridas

### Desarrollo Local

```powershell
# PowerShell
$env:CLOUDFLARE_API_TOKEN = "tu_token"
$env:CLOUDFLARE_ACCOUNT_ID = "tu_account_id"
```

```bash
# Bash/Linux/Mac
export CLOUDFLARE_API_TOKEN="tu_token"
export CLOUDFLARE_ACCOUNT_ID="tu_account_id"
```

### GitHub Actions

Configurar en: **Settings > Secrets and variables > Actions**

Secretos necesarios:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Ver: [.github/workflows/update-rem.yml](.github/workflows/update-rem.yml)

## 🛡️ Recomendaciones Adicionales

### 1. Rotar Tokens Regularmente

1. Crear nuevo token en Cloudflare
2. Actualizar en GitHub Secrets
3. Actualizar localmente
4. Revocar token anterior

### 2. Limitar Permisos del Token

El token debe tener **solo** estos permisos:
- ✅ Workers Scripts - Edit
- ✅ Workers R2 Storage - Edit
- ✅ Workers KV Storage - Edit
- ❌ Todo lo demás - NO

### 3. Monitorear Uso

```bash
# Ver estadísticas de la API
curl https://bcra-rem-api.<TU_SUBDOMINIO>.workers.dev/api/stats

# Ver logs del worker
wrangler tail
```

### 4. Cloudflare Dashboard

Revisar regularmente:
- Analytics > Requests
- Security > Errors (especialmente 429)
- Workers KV > Browse (verificar rate limits)

## 🚨 Qué Hacer si las Credenciales se Exponen

### 1. Inmediatamente

```bash
# Revocar token en Cloudflare
# Dashboard > API Tokens > Revoke
```

### 2. Crear Nuevo Token

```bash
# Seguir: CLOUDFLARE_TOKENS.md
```

### 3. Actualizar Repositorio

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch archivo_con_credenciales.py" \
  --prune-empty --tag-name-filter cat -- --all
```

### 4. Force Push

```bash
git push origin --force --all
```

### 5. Contactar Cloudflare

Si no puedes revocar el token, contacta soporte.

## 📚 Referencias

- [Cloudflare API Tokens](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [GitHub Secrets](https://docs.github.com/es/actions/security-guides/encrypted-secrets)
- [Rate Limiting Best Practices](https://www.cloudflare.com/learning/bots/what-is-rate-limiting/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

## ✅ Estado Actual

| Aspecto | Estado | Notas |
|---------|--------|-------|
| Credenciales hardcodeadas | ✅ Eliminadas | Usar variables de entorno |
| Rate limiting | ✅ Implementado | 1 req/min, 100k/mes |
| URL profesional | ✅ Configurado | Sin datos personales |
| .gitignore | ✅ Actualizado | Protege .env y secrets |
| Documentación | ✅ Completa | README, SECURITY.md |
| Monitoreo | ✅ Disponible | /api/stats endpoint |
