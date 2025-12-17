// worker.js - Cloudflare Worker para API REM BCRA
// Deploy: wrangler deploy

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
    nombre: 'API REM - BCRA',
    descripcion: 'Relevamiento de Expectativas de Mercado del Banco Central de la República Argentina',
    version: '1.0',
    endpoints: {
      metadata: '/api/metadata - Información sobre última actualización',
      bloques: '/api/bloques - Archivo maestro con todas las tablas',
      tabla: '/api/{tabla} - Tabla específica (ej: /api/tipo_cambio)',
    },
    tablas_disponibles: [
      'ipc_general',
      'ipc_nucleo',
      'tasa_interes',
      'tipo_cambio',
      'exportaciones',
      'importaciones',
      'resultado_primario',
      'desocupacion',
      'pbi',
      'ipc_general_top10',
      'ipc_nucleo_top10',
      'tasa_interes_top10',
      'tipo_cambio_top10',
      'exportaciones_top10',
      'importaciones_top10',
      'resultado_primario_top10',
      'desocupacion_top10',
      'pbi_top10',
    ],
    ejemplos: {
      tipo_cambio: '/api/tipo_cambio',
      inflacion: '/api/ipc_general',
      pbi: '/api/pbi',
    },
    documentacion: 'https://github.com/facundoallia/carry-trade-analyzer',
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
