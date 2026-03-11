<div align="center">

# REM BCRA API

**Open-source REST API for Argentina's Market Expectations Survey**

Automated data pipeline that fetches, normalizes, and distributes macroeconomic forecasts from the Central Bank of Argentina (BCRA).

[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://bcra-rem-api.facujallia.workers.dev/api/metadata)
[![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen)](https://bcra-rem-api.facujallia.workers.dev)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-black?logo=github-actions)](https://github.com/features/actions)
[![Cloudflare Workers](https://img.shields.io/badge/runtime-Cloudflare%20Workers-orange?logo=cloudflare)](https://workers.cloudflare.com/)

**Base URL:** `https://bcra-rem-api.facujallia.workers.dev`

[Endpoints](#endpoints) · [Quick Start](#quick-start) · [Response Format](#response-format) · [Examples](#code-examples) · [Data Pipeline](#data-pipeline)

</div>

---

## Overview

The **REM (Relevamiento de Expectativas de Mercado)** is a monthly survey published by the [Central Bank of Argentina (BCRA)](https://www.bcra.gob.ar/) consolidating macroeconomic forecasts from approximately **45 economists and research firms**.

This API automates the entire data pipeline — from downloading the official Excel file to serving structured JSON — making REM data programmatically accessible with no authentication required.

**Key highlights:**

- ✅ No authentication required — fully public
- ✅ Global edge delivery via Cloudflare Workers
- ✅ Updated automatically between the 1st–15th of each month
- ✅ Includes both consensus (median) data and top-10 individual forecasts
- ✅ 1-hour cache for fast, consistent responses

---

## Quick Start

```bash
# Get inflation forecast
curl https://bcra-rem-api.facujallia.workers.dev/api/ipc_general

# Get exchange rate forecast
curl https://bcra-rem-api.facujallia.workers.dev/api/tipo_cambio

# Check last update
curl https://bcra-rem-api.facujallia.workers.dev/api/metadata
```

---

## Endpoints

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metadata` | Last update timestamp and data version info |
| `GET` | `/api/bloques` | Master index of all available tables |

### Macroeconomic Forecasts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ipc_general` | General CPI — monthly inflation rate |
| `GET` | `/api/ipc_nucleo` | Core CPI — excluding volatile items |
| `GET` | `/api/tipo_cambio` | Nominal exchange rate (USD/ARS) |
| `GET` | `/api/tasa_interes` | Interest rate (TAMAR) |
| `GET` | `/api/pbi` | GDP at constant prices |
| `GET` | `/api/exportaciones` | Total exports |
| `GET` | `/api/importaciones` | Total imports |
| `GET` | `/api/desocupacion` | Unemployment rate |
| `GET` | `/api/resultado_primario` | Primary fiscal balance (SPNF) |

### Top-10 Forecasters

Every forecast endpoint above has a corresponding `_top10` variant returning individual projections from the 10 best-performing forecasters in the survey.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ipc_general_top10` | General CPI — top 10 individual forecasts |
| `GET` | `/api/ipc_nucleo_top10` | Core CPI — top 10 individual forecasts |
| `GET` | `/api/tipo_cambio_top10` | Exchange rate — top 10 individual forecasts |
| `GET` | `/api/tasa_interes_top10` | Interest rate — top 10 individual forecasts |
| `GET` | `/api/pbi_top10` | GDP — top 10 individual forecasts |
| `GET` | `/api/exportaciones_top10` | Exports — top 10 individual forecasts |
| `GET` | `/api/importaciones_top10` | Imports — top 10 individual forecasts |
| `GET` | `/api/desocupacion_top10` | Unemployment — top 10 individual forecasts |
| `GET` | `/api/resultado_primario_top10` | Fiscal balance — top 10 individual forecasts |

---

## Response Format

All endpoints return a consistent JSON envelope:

```json
{
  "endpoint": "ipc_general",
  "ultima_actualizacion": "2025-05-12T10:30:00Z",
  "datos": [
    {
      "periodo": "2025-05",
      "mediana": 3.2,
      "percentil_25": 2.9,
      "percentil_75": 3.5
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `string` | Identifier of the requested dataset |
| `ultima_actualizacion` | `string` | ISO 8601 timestamp of the last data update |
| `datos` | `array` | Array of forecast objects |
| `datos[].periodo` | `string` | Forecast period in `YYYY-MM` format |
| `datos[].mediana` | `number` | Median forecast across all surveyed economists |
| `datos[].percentil_25` | `number` | 25th percentile — lower bound of consensus range |
| `datos[].percentil_75` | `number` | 75th percentile — upper bound of consensus range |

> **Top-10 endpoints** return the same envelope but each object in `datos` also includes `pronosticador` (forecaster identifier) and `valor` (individual forecast value) instead of percentile fields.

---

## Code Examples

### Python

```python
import requests

BASE_URL = "https://bcra-rem-api.facujallia.workers.dev"

# Fetch general CPI forecast
response = requests.get(f"{BASE_URL}/api/ipc_general")
response.raise_for_status()

data = response.json()
forecasts = data["datos"]

for row in forecasts:
    print(f"{row['periodo']}: {row['mediana']}% (median)")
```

```python
import requests
import pandas as pd

BASE_URL = "https://bcra-rem-api.facujallia.workers.dev"

def get_rem(endpoint: str) -> pd.DataFrame:
    """Fetch a REM endpoint and return a DataFrame."""
    response = requests.get(f"{BASE_URL}/api/{endpoint}")
    response.raise_for_status()
    return pd.DataFrame(response.json()["datos"])

# Load inflation and exchange rate forecasts
ipc = get_rem("ipc_general")
usd = get_rem("tipo_cambio")

print(ipc.head())
print(usd.head())
```

### JavaScript / TypeScript

```typescript
const BASE_URL = "https://bcra-rem-api.facujallia.workers.dev";

async function getREM(endpoint: string) {
  const res = await fetch(`${BASE_URL}/api/${endpoint}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Fetch CPI forecast
const { datos } = await getREM("ipc_general");
console.log(datos);
```

### R

```r
library(httr2)
library(jsonlite)

base_url <- "https://bcra-rem-api.facujallia.workers.dev"

get_rem <- function(endpoint) {
  req <- request(paste0(base_url, "/api/", endpoint))
  resp <- req_perform(req)
  fromJSON(resp_body_string(resp))$datos
}

ipc <- get_rem("ipc_general")
head(ipc)
```

---

## Rate Limits & Caching

| Limit | Value |
|-------|-------|
| Rate limit | 1 request / minute per IP |
| Cache TTL | 1 hour (Cloudflare edge) |
| Data freshness | Updated monthly (days 1–15) |

Responses include standard cache headers. For high-frequency use cases, cache responses on your end using the `ultima_actualizacion` field to detect stale data.

---

## Data Pipeline

```
BCRA (bcra.gob.ar)
       │
       │  Excel download (days 1–15/month)
       ▼
GitHub Actions
       │
       │  Triggers processing workflow
       ▼
Python + Pandas
       │
       │  Parses, normalizes → 19 JSON tables
       ▼
Cloudflare R2
       │
       │  Object storage (persistent)
       ▼
Cloudflare Workers
       │
       │  Serverless API · Global edge · 1h cache
       ▼
  REST API  ──►  Your application
```

**Stack:** GitHub Actions · Python · Pandas · Cloudflare R2 · Cloudflare Workers

---

## Data Source

All data originates from the official **Relevamiento de Expectativas de Mercado** published by the [Banco Central de la República Argentina (BCRA)](https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp).

This project is not affiliated with or endorsed by the BCRA. It is an independent open-source tool that redistributes publicly available data in a developer-friendly format.

---

## Contributing

Contributions are welcome. If you find a parsing error, want to add a new table, or improve the pipeline, please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push and open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built by [Facundo Allia](https://github.com/facundoallia) · Data sourced from [BCRA](https://www.bcra.gob.ar/)

</div>
