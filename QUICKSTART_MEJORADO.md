# 🚀 Inicio Rápido - API REM BCRA

> **Versión mejorada con seguridad y rate limiting**

## ⚡ Deploy en 5 Pasos

### 1️⃣ Configurar Variables de Entorno

```powershell
# PowerShell - Windows
$env:CLOUDFLARE_API_TOKEN = "tu_token_aqui"
$env:CLOUDFLARE_ACCOUNT_ID = "tu_account_id_aqui"
```

🔑 **Obtener credenciales**: https://dash.cloudflare.com/profile/api-tokens

---

### 2️⃣ Crear KV Namespace (Rate Limiting)

```powershell
cd worker
wrangler kv:namespace create "RATE_LIMIT_KV"
```

📋 **Copiar el ID generado** y pegarlo en `worker/wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "RATE_LIMIT_KV"
id = "PEGAR_ID_AQUI"  # ← Reemplazar
```

---

### 3️⃣ Deploy del Worker

```powershell
cd worker
wrangler deploy
```

📝 **Anota tu URL**: `https://bcra-rem-api.XXXXX.workers.dev`

---

### 4️⃣ Verificar Configuración

```powershell
cd ..
python verify_setup.py
```

✅ Debe mostrar **5/6 checks pasados** (las variables de entorno se verifican localmente)

---

### 5️⃣ Probar API

```powershell
# Ver documentación
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/

# Ver estadísticas
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/api/stats

# Obtener tipo de cambio
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/api/tipo_cambio
```

---

## 🎯 Verificar Rate Limiting

```bash
# Primera petición (debe funcionar)
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/api/tipo_cambio

# Segunda petición inmediata (debe retornar 429)
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/api/tipo_cambio
```

**Respuesta esperada** (segunda petición):
```json
{
  "error": "Límite de peticiones excedido",
  "mensaje": "Solo se permite 1 petición por minuto. Espera 60 segundos.",
  "retry_after": 60
}
```

---

## 📊 Monitorear Uso

```bash
curl https://bcra-rem-api.TU_SUBDOMINIO.workers.dev/api/stats
```

**Respuesta**:
```json
{
  "periodo": "2025-12",
  "requests_realizadas": 142,
  "limite_mensual": 100000,
  "porcentaje_uso": "0.14%",
  "requests_restantes": 99858,
  "rate_limit": "1 petición por minuto",
  "segundos_hasta_reset_mensual": 1036800
}
```

---

## 🔧 GitHub Actions (Opcional)

### Configurar Secrets

1. Ve a tu repo: **Settings > Secrets and variables > Actions**
2. Agrega:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`

### Verificar Workflow

El workflow se ejecuta automáticamente los primeros 7 días del mes a las 12:00 UTC.

**Manual trigger**:
- Ve a **Actions > Actualizar REM BCRA > Run workflow**

---

## 📚 Documentación Completa

- 📖 [README.md](README.md) - Documentación general
- 🔒 [SECURITY.md](SECURITY.md) - Guía de seguridad
- 🚦 [SETUP_RATE_LIMITING.md](SETUP_RATE_LIMITING.md) - Rate limiting detallado
- 📝 [CHANGELOG.md](CHANGELOG.md) - Resumen de cambios

---

## 🐛 Troubleshooting

### Error: "wrangler not found"

```powershell
npm install -g wrangler
$env:PATH = "$env:APPDATA\npm;$env:PATH"
```

### Error: "KV binding not found"

El KV namespace no está creado o el ID en `wrangler.toml` es incorrecto.

**Solución**: Repetir paso 2️⃣

### Rate limiting no funciona

```powershell
# Ver logs en tiempo real
wrangler tail
```

Buscar mensajes de error relacionados con KV.

---

## ✅ Checklist Completo

- [ ] Variables de entorno configuradas
- [ ] KV namespace creado
- [ ] ID del KV en wrangler.toml
- [ ] Worker deployado exitosamente
- [ ] verify_setup.py pasa 5/6 checks
- [ ] Rate limiting probado (429 en segunda petición)
- [ ] /api/stats funciona
- [ ] GitHub Secrets configurados (opcional)

---

## 🎉 Todo Listo!

Tu API está:
- ✅ Segura (sin credenciales expuestas)
- ✅ Protegida (rate limiting activo)
- ✅ Monitoreada (endpoint /stats)
- ✅ Documentada (endpoints descriptivos)
- ✅ Profesional (URL sin datos personales)

**URL pública**: `https://bcra-rem-api.TU_SUBDOMINIO.workers.dev`

---

## 📞 Soporte

- 📖 Ver documentación completa en [README.md](README.md)
- 🔍 Ejecutar `python verify_setup.py` para diagnosticar problemas
- 📊 Revisar logs: `wrangler tail`
