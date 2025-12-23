// worker.js - Cloudflare Worker para API REM BCRA
// Deploy: wrangler deploy

// Configuración de límites
const RATE_LIMIT = {
  REQUESTS_PER_MINUTE: 1,
  MONTHLY_LIMIT: 100000,
  WINDOW_MS: 10000, // 1O segundos en milisegundos
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Content-Type': 'application/json; charset=utf-8',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Solo GET permitido
    if (request.method !== 'GET') {
      return new Response(
        JSON.stringify({ error: 'Método no permitido' }),
        { status: 405, headers: corsHeaders }
      );
    }

    try {
      // Aplicar rate limiting
      const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
      const rateLimitResult = await checkRateLimit(env, clientIP);
      
      if (!rateLimitResult.allowed) {
        return new Response(
          JSON.stringify({ 
            error: 'Límite de peticiones excedido',
            mensaje: rateLimitResult.message,
            retry_after: rateLimitResult.retryAfter
          }),
          { 
            status: 429,
            headers: {
              ...corsHeaders,
              'Retry-After': rateLimitResult.retryAfter.toString()
            }
          }
        );
      }

      // Router
      if (path === '/' || path === '/api') {
        return handleIndex(corsHeaders);
      }
      
      if (path === '/api/metadata' || path === '/metadata') {
        return handleMetadata(env, corsHeaders);
      }
      
      if (path === '/api/bloques' || path === '/bloques') {
        return handleBloques(env, corsHeaders);
      }
      
      if (path === '/api/stats' || path === '/stats') {
        return handleStats(env, corsHeaders);
      }
      
      // Endpoint para tabla específica: /api/{tabla}
      // Soporta query params: ?periodo=2025-11 o ?year=2025&month=11
      const match = path.match(/^\/api\/([a-z_0-9]+)$/);
      if (match) {
        const tabla = match[1];
        const searchParams = url.searchParams;
        const periodo = searchParams.get('periodo');
        const year = searchParams.get('year');
        const month = searchParams.get('month');
        
        return handleTabla(env, tabla, periodo, year, month, corsHeaders);
      }

      // 404
      return new Response(
        JSON.stringify({ error: 'Endpoint no encontrado' }),
        { status: 404, headers: corsHeaders }
      );

    } catch (error) {
      console.error('Error:', error);
      return new Response(
        JSON.stringify({ error: 'Error interno del servidor' }),
        { status: 500, headers: corsHeaders }
      );
    }
  }
};

// Handler: Índice de la API
function handleIndex(headers) {
  const info = {
    nombre: 'API REM BCRA',
    descripcion: 'API del Relevamiento de Expectativas de Mercado del Banco Central de la República Argentina',
    version: '1.0.0',
    documentacion: 'https://github.com/facundoallia/rem-bcra-api',
    fuente_datos: 'https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp',
    
    rate_limits: {
      por_ip: '1 petición por minuto',
      mensual_global: '100,000 peticiones por mes',
      nota: 'Ver /api/stats para estadísticas de uso actual'
    },
    
    endpoints: {
      raiz: {
        ruta: '/',
        descripcion: 'Este endpoint - documentación de la API',
        metodo: 'GET'
      },
      metadata: {
        ruta: '/api/metadata',
        descripcion: 'Información sobre la última actualización de datos',
        metodo: 'GET',
        ejemplo: '/api/metadata'
      },
      stats: {
        ruta: '/api/stats',
        descripcion: 'Estadísticas de uso y límites de rate limiting',
        metodo: 'GET',
        ejemplo: '/api/stats'
      },
      bloques: {
        ruta: '/api/bloques',
        descripcion: 'Archivo maestro con todas las tablas disponibles',
        metodo: 'GET',
        ejemplo: '/api/bloques'
      },
      tabla: {
        ruta: '/api/{tabla}',
        descripcion: 'Obtener datos de una tabla específica',
        metodo: 'GET',
        parametros: {
          tabla: 'Nombre de la tabla (ver lista abajo)',
          periodo: 'Opcional. Formato YYYY-MM (ej: 2025-11)',
          year: 'Opcional. Año (usar con month)',
          month: 'Opcional. Mes (usar con year)'
        },
        ejemplos: {
          actual: '/api/tipo_cambio',
          historico: '/api/tipo_cambio?periodo=2025-11',
          historico_alt: '/api/ipc_general?year=2025&month=11'
        }
      }
    },
    
    tablas_disponibles: {
      principales: [
        {
          id: 'ipc_general',
          nombre: 'IPC Nivel General',
          descripcion: 'Precios minoristas - IPC nivel general (Nacional, INDEC)',
          endpoint: '/api/ipc_general'
        },
        {
          id: 'ipc_nucleo',
          nombre: 'IPC Núcleo',
          descripcion: 'Precios minoristas - IPC núcleo (Nacional, INDEC)',
          endpoint: '/api/ipc_nucleo'
        },
        {
          id: 'tasa_interes',
          nombre: 'Tasa de Interés TAMAR',
          descripcion: 'Tasa de Interés de Referencia',
          endpoint: '/api/tasa_interes'
        },
        {
          id: 'tipo_cambio',
          nombre: 'Tipo de Cambio Nominal',
          descripcion: 'Tipo de cambio USD/ARS',
          endpoint: '/api/tipo_cambio'
        },
        {
          id: 'exportaciones',
          nombre: 'Exportaciones',
          descripcion: 'Exportaciones en millones de USD',
          endpoint: '/api/exportaciones'
        },
        {
          id: 'importaciones',
          nombre: 'Importaciones',
          descripcion: 'Importaciones en millones de USD',
          endpoint: '/api/importaciones'
        },
        {
          id: 'resultado_primario',
          nombre: 'Resultado Primario SPNF',
          descripcion: 'Resultado Primario del Sector Público No Financiero',
          endpoint: '/api/resultado_primario'
        },
        {
          id: 'desocupacion',
          nombre: 'Desocupación Abierta',
          descripcion: 'Tasa de desocupación',
          endpoint: '/api/desocupacion'
        },
        {
          id: 'pbi',
          nombre: 'PIB',
          descripcion: 'PIB a precios constantes',
          endpoint: '/api/pbi'
        }
      ],
      top10: [
        'ipc_general_top10', 'ipc_nucleo_top10', 'tasa_interes_top10',
        'tipo_cambio_top10', 'exportaciones_top10', 'importaciones_top10',
        'resultado_primario_top10', 'desocupacion_top10', 'pbi_top10'
      ]
    },
    
    formato_respuesta: {
      exito: {
        descripcion: 'Datos en formato JSON',
        content_type: 'application/json',
        cache: 'Cache-Control: public, max-age=3600 (1 hora)'
      },
      error: {
        campos: ['error', 'mensaje', 'sugerencia'],
        codigos: {
          400: 'Petición incorrecta',
          404: 'Recurso no encontrado',
          429: 'Límite de peticiones excedido',
          500: 'Error interno del servidor'
        }
      }
    },
    
    cors: {
      habilitado: true,
      origen: '*',
      metodos: ['GET', 'OPTIONS']
    }
  };

  return new Response(JSON.stringify(info, null, 2), { headers });
}

// Handler: Metadata
async function handleMetadata(env, headers) {
  try {
    const object = await env.R2_BUCKET.get('data/latest/_metadata.json');
    
    if (!object) {
      return new Response(
        JSON.stringify({ error: 'Metadata no encontrado' }),
        { status: 404, headers }
      );
    }

    const data = await object.json();
    return new Response(JSON.stringify(data, null, 2), { headers });

  } catch (error) {
    console.error('Error leyendo metadata:', error);
    return new Response(
      JSON.stringify({ error: 'Error leyendo metadata' }),
      { status: 500, headers }
    );
  }
}

// Handler: Bloques (archivo maestro)
async function handleBloques(env, headers) {
  try {
    // Siempre buscar en latest/
    const object = await env.R2_BUCKET.get('data/latest/rem_bloques.json');
    
    if (!object) {
      return new Response(
        JSON.stringify({ error: 'Archivo maestro no encontrado' }),
        { status: 404, headers }
      );
    }

    const data = await object.json();
    
    // Agregar headers de cache
    const headersWithCache = {
      ...headers,
      'Cache-Control': 'public, max-age=3600', // Cache 1 hora
    };

    return new Response(JSON.stringify(data, null, 2), { headers: headersWithCache });

  } catch (error) {
    console.error('Error leyendo bloques:', error);
    return new Response(
      JSON.stringify({ error: 'Error leyendo archivo maestro' }),
      { status: 500, headers }
    );
  }
}

// Handler: Tabla específica
async function handleTabla(env, tabla, periodo, year, month, headers) {
  try {
    // Determinar ruta según parámetros
    let basePath = 'data/latest';
    
    if (periodo) {
      // Formato: 2025-11
      const [y, m] = periodo.split('-');
      basePath = `data/${y}/${m}`;
    } else if (year && month) {
      basePath = `data/${year}/${month}`;
    }
    
    // Construir nombre de archivo
    const fileName = `${basePath}/rem_${tabla}.json`;
    
    console.log(`Intentando obtener: ${fileName}`);
    console.log(`Binding R2_BUCKET:`, env.R2_BUCKET ? 'OK' : 'MISSING');
    
    const object = await env.R2_BUCKET.get(fileName);
    
    console.log(`Objeto obtenido:`, object ? 'SI' : 'NO');
    
    if (!object) {
      // Intentar listar objetos para debug
      const list = await env.R2_BUCKET.list({ prefix: 'data/latest/', limit: 5 });
      console.log(`Archivos encontrados con prefix data/latest/:`, list.objects.map(o => o.key));
      
      return new Response(
        JSON.stringify({ 
          error: 'Tabla no encontrada',
          tabla: tabla,
          buscando: fileName,
          periodo_solicitado: periodo || `${year}-${month}` || 'latest',
          archivos_encontrados: list.objects.map(o => o.key),
          sugerencia: 'Ver /api para lista de tablas disponibles. Usa ?periodo=2025-11 para períodos específicos'
        }),
        { status: 404, headers }
      );
    }

    const data = await object.json();
    
    // Agregar headers de cache
    const headersWithCache = {
      ...headers,
      'Cache-Control': 'public, max-age=3600', // Cache 1 hora
    };

    return new Response(JSON.stringify(data, null, 2), { headers: headersWithCache });

  } catch (error) {
    console.error(`Error leyendo tabla ${tabla}:`, error);
    return new Response(
      JSON.stringify({ error: 'Error leyendo tabla', details: error.message }),
      { status: 500, headers }
    );
  }
}

// ============================================================================
// RATE LIMITING & USAGE TRACKING
// ============================================================================

/**
 * Verifica y aplica límites de rate limiting
 * @param {object} env - Cloudflare Worker environment
 * @param {string} clientIP - IP del cliente
 * @returns {object} { allowed: boolean, message: string, retryAfter: number }
 */
async function checkRateLimit(env, clientIP) {
  const now = Date.now();
  const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
  
  // Key para rate limiting por IP (1 request/minuto)
  const rateLimitKey = `ratelimit:${clientIP}`;
  
  // Key para contador mensual global
  const monthlyKey = `monthly:${currentMonth}`;
  
  try {
    // Verificar rate limit por IP (1 req/min) usando KV
    if (env.RATE_LIMIT_KV) {
      const lastRequest = await env.RATE_LIMIT_KV.get(rateLimitKey);
      
      if (lastRequest) {
        const lastRequestTime = parseInt(lastRequest);
        const timeSinceLastRequest = now - lastRequestTime;
        
        if (timeSinceLastRequest < RATE_LIMIT.WINDOW_MS) {
          const retryAfter = Math.ceil((RATE_LIMIT.WINDOW_MS - timeSinceLastRequest) / 1000);
          return {
            allowed: false,
            message: `Solo se permite 1 petición por minuto. Espera ${retryAfter} segundos.`,
            retryAfter
          };
        }
      }
      
      // Actualizar timestamp de última petición (expira en 2 minutos)
      await env.RATE_LIMIT_KV.put(rateLimitKey, now.toString(), { expirationTtl: 120 });
    }
    
    // Verificar límite mensual global
    if (env.RATE_LIMIT_KV) {
      const monthlyCount = await env.RATE_LIMIT_KV.get(monthlyKey);
      const currentCount = monthlyCount ? parseInt(monthlyCount) : 0;
      
      if (currentCount >= RATE_LIMIT.MONTHLY_LIMIT) {
        return {
          allowed: false,
          message: `Límite mensual de ${RATE_LIMIT.MONTHLY_LIMIT.toLocaleString()} peticiones alcanzado. Intenta el próximo mes.`,
          retryAfter: getSecondsUntilNextMonth()
        };
      }
      
      // Incrementar contador mensual (expira al final del mes)
      const ttl = getSecondsUntilNextMonth();
      await env.RATE_LIMIT_KV.put(monthlyKey, (currentCount + 1).toString(), { expirationTtl: ttl });
    }
    
    return { allowed: true, message: 'OK', retryAfter: 0 };
    
  } catch (error) {
    console.error('Error en rate limiting:', error);
    // En caso de error, permitir la petición (fail open)
    return { allowed: true, message: 'OK', retryAfter: 0 };
  }
}

/**
 * Obtiene segundos hasta el próximo mes
 */
function getSecondsUntilNextMonth() {
  const now = new Date();
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return Math.ceil((nextMonth - now) / 1000);
}

// Handler: Estadísticas de uso
async function handleStats(env, headers) {
  try {
    const currentMonth = new Date().toISOString().slice(0, 7);
    const monthlyKey = `monthly:${currentMonth}`;
    
    let currentCount = 0;
    if (env.RATE_LIMIT_KV) {
      const monthlyCount = await env.RATE_LIMIT_KV.get(monthlyKey);
      currentCount = monthlyCount ? parseInt(monthlyCount) : 0;
    }
    
    const stats = {
      periodo: currentMonth,
      requests_realizadas: currentCount,
      limite_mensual: RATE_LIMIT.MONTHLY_LIMIT,
      porcentaje_uso: ((currentCount / RATE_LIMIT.MONTHLY_LIMIT) * 100).toFixed(2) + '%',
      requests_restantes: RATE_LIMIT.MONTHLY_LIMIT - currentCount,
      rate_limit: `${RATE_LIMIT.REQUESTS_PER_MINUTE} petición por minuto`,
      segundos_hasta_reset_mensual: getSecondsUntilNextMonth()
    };
    
    return new Response(JSON.stringify(stats, null, 2), { headers });
    
  } catch (error) {
    console.error('Error obteniendo stats:', error);
    return new Response(
      JSON.stringify({ error: 'Error obteniendo estadísticas' }),
      { status: 500, headers }
    );
  }
}
