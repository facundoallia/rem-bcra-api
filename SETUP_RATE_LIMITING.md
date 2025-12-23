# 🔧 Configurar Rate Limiting

La API ahora incluye protección contra abuso con:
- ✅ Límite de 1 petición por minuto por IP
- ✅ Límite global de 100,000 peticiones mensuales
- ✅ Endpoint `/api/stats` para monitorear uso

## Pasos de Configuración

### 1. Crear KV Namespace

Ejecuta en PowerShell desde la carpeta `worker`:

```powershell
cd "c:\Quant projects\rem-bcra-api\worker"
wrangler kv:namespace create "RATE_LIMIT_KV"
```

Esto mostrará algo como:

```
✨ Success!
Add the following to your configuration file in your kv_namespaces array:
{ binding = "RATE_LIMIT_KV", id = "abc123def456..." }
```

### 2. Actualizar wrangler.toml

Copia el ID generado y reemplaza en [wrangler.toml](worker/wrangler.toml):

```toml
[[kv_namespaces]]
binding = "RATE_LIMIT_KV"
id = "TU_ID_AQUI"  # Reemplaza con el ID real
```

### 3. Deploy

```powershell
$env:CLOUDFLARE_API_TOKEN = "TU_TOKEN"
$env:CLOUDFLARE_ACCOUNT_ID = "TU_ACCOUNT_ID"
wrangler deploy
```

## Verificar Funcionamiento

### Probar Rate Limiting

```bash
# Primera petición - debe funcionar
curl https://bcra-rem-api.<TU_SUBDOMINIO>.workers.dev/api/tipo_cambio

# Segunda petición inmediata - debe retornar 429
curl https://bcra-rem-api.<TU_SUBDOMINIO>.workers.dev/api/tipo_cambio
```

### Ver Estadísticas

```bash
curl https://bcra-rem-api.<TU_SUBDOMINIO>.workers.dev/api/stats
```

Respuesta esperada:

```json
{
  "periodo": "2025-12",
  "requests_realizadas": 42,
  "limite_mensual": 100000,
  "porcentaje_uso": "0.04%",
  "requests_restantes": 99958,
  "rate_limit": "1 petición por minuto",
  "segundos_hasta_reset_mensual": 1036800
}
```

## Configuración Opcional

### Ajustar Límites

Edita en [worker.js](worker/worker.js):

```javascript
const RATE_LIMIT = {
  REQUESTS_PER_MINUTE: 1,     // Cambiar a 2, 5, 10, etc.
  MONTHLY_LIMIT: 100000,       // Cambiar según necesidad
  WINDOW_MS: 60000,            // Ventana de tiempo (1 min)
};
```

### Deshabilitar Temporalmente

Si no has creado el KV namespace aún, la API funcionará igual pero **sin protección**. El código verifica la existencia de `env.RATE_LIMIT_KV` antes de aplicar límites.

## Monitoreo

### Dashboard de Cloudflare

1. Ve a Workers & Pages
2. Selecciona `bcra-rem-api`
3. Tab "Analytics"
4. Ver:
   - Requests por minuto
   - Errores 429 (rate limited)
   - Uso de KV

### Logs en Tiempo Real

```powershell
wrangler tail
```

## Troubleshooting

### Error: "KV binding not found"

El KV namespace no está configurado. Sigue los pasos 1-2 arriba.

### Rate limiting no funciona

Verifica en logs:

```powershell
wrangler tail
```

Busca mensajes como: `Error en rate limiting: ...`

### Resetear contadores

```powershell
# Listar todas las keys
wrangler kv:key list --namespace-id=TU_KV_ID

# Eliminar key específica
wrangler kv:key delete "monthly:2025-12" --namespace-id=TU_KV_ID
```
