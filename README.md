API REM - BCRA (Datos Abiertos)
Los datos de inflación proyectada provienen de la API REM - BCRA, un proyecto open-source que automatiza la lectura, normalización y distribución del Relevamiento de Expectativas de Mercado del Banco Central.

Pipeline de datos
1
Descarga automática
GitHub Actions descarga el archivo Excel del REM desde bcra.gob.ar (días 1-15 de cada mes)

2
Procesamiento
Python + Pandas parsea, normaliza y estructura 19 tablas JSON con medianas, percentiles y proyecciones de ~45 economistas

3
Distribución
Los datos se almacenan en Cloudflare R2 y se sirven globalmente via Cloudflare Workers con cache de 1 hora

Endpoints disponibles
Endpoint	Descripción
/api/metadata	Información sobre última actualización
/api/ipc_general	Inflación general (IPC)
/api/ipc_nucleo	Inflación núcleo
/api/tipo_cambio	Tipo de cambio nominal (USD/ARS)
/api/tasa_interes	Tasa de interés (TAMAR)
/api/pbi	PIB a precios constantes
/api/exportaciones	Exportaciones
/api/importaciones	Importaciones
/api/desocupacion	Tasa de desocupación
/api/resultado_primario	Resultado primario SPNF
/api/bloques	Índice maestro de todas las tablas
Cada tabla tiene además su versión _top10 con los pronósticos individuales de los 10 mejores pronosticadores.

Ejemplo de uso
// JavaScript
fetch('https://bcra-rem-api.facujallia.workers.dev/api/ipc_general')
  .then(r => r.json())
  .then(data => console.log(data.datos));

# Python
import requests
data = requests.get('https://bcra-rem-api.facujallia.workers.dev/api/tipo_cambio').json()
Tecnologías
GitHub Actions (orquestación) → Python + Pandas (parsing) → Cloudflare R2 (almacenamiento) → Cloudflare Workers (API serverless)

Base URL: https://bcra-rem-api.facujallia.workers.dev
Código fuente: github.com/facundoallia/rem-bcra-api
Acceso: API pública, sin autenticación. Rate limit: 1 req/min por IP.
