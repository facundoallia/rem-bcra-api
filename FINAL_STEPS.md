# 🚀 GUÍA FINAL: Subir Archivos a R2 via Dashboard

## ❌ Problema Detectado

Los archivos NO están en R2 remoto. Wrangler por defecto usa modo "local" (simulador).

## ✅ Solución: Usar Dashboard Web de Cloudflare

### Opción 1: Dashboard Web (Más Simple - 5 minutos)

1. **Ve al Dashboard de R2:**
   https://dash.cloudflare.com/b716491d6afe361dba0e016519df6cb3/r2/buckets/rem-data

2. **Click en "Upload"** (botón azul arriba a la derecha)

3. **Selecciona "Upload Files"**

4. **Arrastra todos los archivos JSON desde:**
   ```
   C:\Desarrollos\api REM\data\rem_*.json
   ```
   
   Deberías subir 19 archivos:
   - rem_bloques.json
   - rem_ipc_general.json
   - rem_ipc_nucleo.json
   - rem_tasa_interes.json
   - rem_tipo_cambio.json
   - rem_exportaciones.json
   - rem_importaciones.json
   - rem_resultado_primario.json
   - rem_desocupacion.json
   - rem_pbi.json
   - Y sus versiones _top10

5. **IMPORTANTE:** Crea una carpeta "data" primero:
   - Click en "Create folder"
   - Nombre: `data`
   - Luego entra a esa carpeta
   - Sube todos los archivos DENTRO de la carpeta `data/`

6. **Verifica:** Los archivos deben estar en:
   - `data/rem_bloques.json`
   - `data/rem_tipo_cambio.json`
   - etc.

### Opción 2: Wrangler CLI con configuración correcta

Si prefieres CLI, necesitas autenticar wrangler correctamente:

```powershell
# 1. Limpiar configuración local
Remove-Item -Path "$env:USERPROFILE\.wrangler" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Autenticar (abre navegador)
wrangler login

# 3. Luego sube archivo por archivo
$files = Get-ChildItem "C:\Desarrollos\api REM\data\rem_*.json"
foreach ($file in $files) {
    wrangler r2 object put "rem-data/data/$($file.Name)" `
        --file="$($file.FullName)"
    Write-Host "Subido: $($file.Name)"
}
```

## 🧪 Verificar que Funcionó

Después de subir, prueba la API:

```powershell
cd "C:\Desarrollos\api REM"
C:/Desarrollos/.venv/Scripts/python.exe -c "import requests, json; r = requests.get('https://rem-bcra-api.facujallia.workers.dev/api/tipo_cambio', verify=False); print('Status:', r.status_code); data = r.json(); print('Registros:', len(data) if isinstance(data, list) else 'Error'); print(json.dumps(data[:2] if isinstance(data, list) else data, indent=2, ensure_ascii=False))"
```

**Output esperado:**
```
Status: 200
Registros: 36
[
  {
    "Período": "Dic-24",
    "Referencia": "Mediana",
    "IPC nivel general": "1138.20"
  },
  ...
]
```

## 📋 Checklist Final

- [ ] Abrir dashboard de R2
- [ ] Crear carpeta "data" en el bucket rem-data
- [ ] Subir 19 archivos JSON dentro de data/
- [ ] Verificar que los archivos están en data/rem_*.json
- [ ] Probar la API con curl/Python
- [ ] Configurar GitHub Secrets:
  - CLOUDFLARE_API_TOKEN = `Cm8qe2j5U9GW5qncg-z6iGc7LAV58DYlve1Iyd_T`
  - CLOUDFLARE_ACCOUNT_ID = `b716491d6afe361dba0e016519df6cb3`

## ⏱️ Tiempo Estimado

- Dashboard Web: **5 minutos**
- Wrangler CLI: **10 minutos** (si tienes problemas de proxy)

## 🎯 URLs Importantes

- **R2 Dashboard:** https://dash.cloudflare.com/b716491d6afe361dba0e016519df6cb3/r2/buckets/rem-data
- **API desplegada:** https://rem-bcra-api.facujallia.workers.dev/api
- **GitHub repo:** https://github.com/facundoallia/carry-trade-analyzer

---

Una vez que subas los archivos, la API funcionará inmediatamente. El Worker ya está desplegado y configurado correctamente, solo faltan los datos en R2.
