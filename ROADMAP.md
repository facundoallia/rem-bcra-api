# 🗺️ Roadmap API REM - BCRA

## 📍 Estado Actual: Parser Funcional

### ✅ Completado (Fase 0)

1. **Script de descarga** (`download REM`)
   - ✅ Detección automática de URL más reciente
   - ✅ Descarga a `data/` con nombre con fecha
   - ✅ Manejo de SSL y timeouts

2. **Parser robusto** (`read REM.py`)
   - ✅ Procesa 2 hojas del Excel
   - ✅ Genera 18 tablas JSON (9 + 9 TOP10)
   - ✅ Normalización de columnas
   - ✅ Conversión de fechas y números
   - ✅ Estructura JSON consistente

3. **Validación básica** (`verificar_tablas.py`)
   - ✅ Cuenta y lista tablas
   - ✅ Muestra resumen de filas

4. **Validación avanzada** (`validate_output.py`)
   - ✅ Detecta fechas inválidas
   - ✅ Valida tipos de datos
   - ✅ Verifica rangos numéricos
   - ✅ Estructura JSON
   - ⚠️  **ENCONTRÓ PROBLEMAS** → Necesita ajustes en parser

---

## 🚧 Fase 1: Corrección y Estabilización (PRÓXIMO)

### 🔴 Prioridad Alta - Correcciones Inmediatas

1. **Mejorar parser para períodos especiales**
   - [ ] Detectar y manejar "próx. 12 meses", "próx. 24 meses"
   - [ ] Convertir "Trim. III-25" a formato manejable
   - [ ] Filtrar filas de "Fuente:" que se colaron en datos
   - [ ] Opciones:
     - Dejar como string descriptivo
     - Convertir a fecha estimada (ej: "próx. 12 meses" → fecha +12m)
     - Agregar campo `tipo_periodo` (fecha | relativo | trimestre)

2. **Ajustar validaciones**
   - [ ] Hacer validación de fecha más flexible
   - [ ] Ajustar rango de exportaciones/importaciones (permitir > 50K)
   - [ ] Distinguir entre errores críticos y advertencias

3. **Mejorar estructura de datos**
   ```json
   {
     "período": "2025-12-31",
     "período_tipo": "fecha",  // nuevo
     "período_descripción": null,  // nuevo
     "referencia": "$/USD",
     "datos": {...}
   }
   ```

### 🟡 Prioridad Media - Mejoras

4. **Testing**
   - [ ] Tests unitarios para parser
   - [ ] Tests para validador
   - [ ] Fixtures con datos de ejemplo

5. **Documentación**
   - [ ] Documentar formato de cada tabla
   - [ ] Ejemplos de uso
   - [ ] Esquemas JSON (JSON Schema)

---

## 🚀 Fase 2: Automatización (1-2 semanas)

### GitHub Actions

1. **Workflow de actualización**
   - [x] Crear `.github/workflows/update-rem.yml`
   - [ ] Probar ejecución manual
   - [ ] Configurar cron semanal
   - [ ] Alertas por email/Slack en fallos

2. **Estrategia de publicación**

   **Opción A: Commit al repo (Simple)**
   ```
   ✅ Pros: Simple, versionado automático con Git
   ❌ Contras: Commits automáticos, crece repo
   ```
   
   **Opción B: Cloudflare R2 + KV (Recomendada)**
   ```
   ✅ Pros: No ensucia repo, CDN gratis, rápido
   ✅ Mejor separación: código vs datos
   ❌ Contras: Requiere cuenta Cloudflare
   ```

3. **Implementación Cloudflare**
   - [ ] Crear cuenta/proyecto Cloudflare
   - [ ] Configurar R2 bucket para JSONs
   - [ ] Configurar KV para metadata
   - [ ] Secrets en GitHub Actions (API tokens)
   - [ ] Script de deploy en workflow

---

## 🌐 Fase 3: API REST (2-3 semanas)

### Cloudflare Worker

1. **Endpoints básicos**
   ```
   GET /api/rem                    → Índice
   GET /api/rem/bloques            → Maestro completo
   GET /api/rem/{tabla}            → Tabla específica
   GET /api/rem/{tabla}/latest     → Último valor
   ```

2. **Filtros y consultas**
   ```
   GET /api/rem/tipo_cambio?desde=2025-01&hasta=2025-12
   GET /api/rem/ipc_general?referencia=var%25mensual
   GET /api/rem/pbi?trim=IV-25
   ```

3. **Features adicionales**
   - [ ] CORS para uso en frontend
   - [ ] Rate limiting (via Cloudflare)
   - [ ] Cache headers
   - [ ] Compresión (gzip/brotli)
   - [ ] Métricas de uso

4. **Documentación API**
   - [ ] OpenAPI/Swagger spec
   - [ ] Página de docs interactiva
   - [ ] Ejemplos en múltiples lenguajes
   - [ ] Status page público

---

## 📊 Fase 4: Dashboard y Visualización (Opcional)

### Frontend Simple

1. **Landing page**
   - [ ] Descripción del proyecto
   - [ ] Enlaces a documentación
   - [ ] Ejemplos de uso
   - [ ] Últimos datos disponibles

2. **Explorador de datos**
   - [ ] Tabla interactiva con filtros
   - [ ] Gráficos básicos (Chart.js/Plotly)
   - [ ] Comparación de tablas
   - [ ] Descarga de CSV/Excel

3. **Hosting**
   - [ ] Cloudflare Pages (mismo proyecto)
   - [ ] Dominio personalizado (opcional)

---

## 🔧 Fase 5: Mejoras Avanzadas (Futuro)

### Features Avanzadas

1. **Histórico completo**
   - [ ] Guardar todos los releases mensuales
   - [ ] API de series temporales
   - [ ] Endpoint de diferencias entre releases
   - [ ] Revisiones y correcciones del BCRA

2. **Análisis automático**
   - [ ] Detección de cambios significativos
   - [ ] Alertas de volatilidad
   - [ ] Resumen ejecutivo generado
   - [ ] Comparación con releases anteriores

3. **Integración con otras fuentes**
   - [ ] Datos del INDEC
   - [ ] Bloomberg/Reuters (si disponible)
   - [ ] Normalización cruzada

4. **ML/Predicciones (muy futuro)**
   - [ ] Modelos de forecast basados en histórico
   - [ ] Detección de anomalías
   - [ ] Intervalos de confianza

---

## ⏱️ Timeline Sugerido

### Sprint 1 (Esta semana)
- ✅ Parser funcional
- 🔄 Corregir problemas detectados por validador
- ✅ Validación robusta
- 🔄 Tests básicos

### Sprint 2 (Próxima semana)
- [ ] GitHub Actions funcionando
- [ ] Decisión: Opción A o B para deploy
- [ ] Implementar deploy automático
- [ ] Monitoreo básico

### Sprint 3 (Semana 3)
- [ ] Cloudflare Worker básico
- [ ] 4-5 endpoints principales
- [ ] CORS y cache
- [ ] Documentación básica

### Sprint 4 (Semana 4)
- [ ] Filtros y búsqueda
- [ ] OpenAPI completo
- [ ] Landing page simple
- [ ] Status monitoring

---

## 🎯 KPIs de Éxito

### Técnicos
- ✅ 18 tablas parseadas correctamente
- ⏳ 0 errores en validación (actualmente 48)
- ⏳ < 2min tiempo de procesamiento total
- ⏳ 99.5% uptime del workflow
- ⏳ < 500ms respuesta API (p95)

### Funcionales
- ⏳ Actualización automática semanal
- ⏳ Datos disponibles < 2h después del release BCRA
- ⏳ Documentación completa para usuarios
- ⏳ 0 intervenciones manuales por mes

---

## 🤝 Decisiones Pendientes

### Alta Prioridad
1. **¿Cómo manejar períodos relativos?**
   - Opción 1: Dejar como string ("próx. 12 meses")
   - Opción 2: Calcular fecha estimada
   - Opción 3: Campo tipo + descripción
   - **Recomendación**: Opción 3 (más flexible)

2. **¿Dónde hostear los datos?**
   - Opción A: Git repo (simple, versionado)
   - Opción B: Cloudflare R2 (profesional, escalable)
   - **Recomendación**: Opción B para producción

### Media Prioridad
3. **¿Guardar histórico completo?**
   - Sí: Más valioso, análisis temporal
   - No: Más simple, solo última versión
   - **Recomendación**: Empezar simple, agregar después

4. **¿Frontend necesario?**
   - Sí: Más accesible para no-técnicos
   - No: Solo API para developers
   - **Recomendación**: Landing + docs básico

---

## 📞 Próximos Pasos INMEDIATOS

### Para HOY/MAÑANA

1. **Corregir parser** (2-3 horas)
   - Agregar detección de períodos especiales
   - Filtrar filas "Fuente:"
   - Ajustar tipo de datos en columna período

2. **Ajustar validador** (1 hora)
   - Hacer validación de fechas más permisiva
   - Separar errores críticos de warnings
   - Ajustar rangos de exportaciones

3. **Decisión de arquitectura** (30 min)
   - ¿Opción A o B para datos?
   - ¿Usar Cloudflare o alternativa?
   - Documentar decisión

4. **Configurar GitHub Actions** (1-2 horas)
   - Crear secrets necesarios
   - Probar workflow manualmente
   - Configurar alertas

**Total estimado Fase 1**: 4-7 horas de trabajo

---

## 🎓 Recursos Necesarios

### Cuentas/Servicios
- [x] GitHub repo
- [ ] Cloudflare account (free tier suficiente)
- [ ] (Opcional) Dominio personalizado

### Skills Requeridos
- [x] Python (básico-intermedio)
- [x] GitHub Actions (básico)
- [ ] Cloudflare Workers (básico) - aprendible en 1-2h
- [ ] REST API design (básico)

### Herramientas
- [x] VS Code / editor
- [x] Python 3.11+
- [x] Git
- [ ] Wrangler CLI (Cloudflare)

---

**¿Por dónde seguimos?** → Corregir problemas del parser detectados por validador
