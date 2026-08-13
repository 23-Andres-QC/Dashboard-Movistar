import type {
  CalificacionEnvio,
  Canal,
  CierreEnvio,
  Cliente,
  Desenlace,
  Gestion,
  GuiaCopiloto,
  Motivo,
  Recomendacion,
  TurnoGuion,
} from './tipos'

const BASE = '/api'

export class ErrorApi extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
    this.name = 'ErrorApi'
  }
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let respuesta: Response
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ErrorApi('No se pudo contactar con la API', 0)
  }

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null)
    throw new ErrorApi(cuerpo?.detail ?? `Error ${respuesta.status}`, respuesta.status)
  }
  return (await respuesta.json()) as T
}

export const api = {
  buscarCliente: (dni: string) =>
    pedir<Cliente>(`/clientes/buscar?dni=${encodeURIComponent(dni)}`),

  recomendaciones: (idCliente: string) =>
    pedir<Recomendacion[]>(`/clientes/${encodeURIComponent(idCliente)}/recomendaciones`),

  guion: (idCliente: string) =>
    pedir<TurnoGuion[]>(`/clientes/${encodeURIComponent(idCliente)}/guion`),

  desenlace: (idCliente: string) =>
    pedir<Desenlace>(`/clientes/${encodeURIComponent(idCliente)}/desenlace`),

  abrirGestion: (cuerpo: {
    id_cliente: string
    oferta_id: string
    oferta_recomendada: string
    oferta_es_mt: boolean
    segmento_objetivo: string
    canal: Canal
    id_asesor: string
    prob_inicial: number
  }) => pedir<Gestion>('/gestiones', { method: 'POST', body: JSON.stringify(cuerpo) }),

  marcarObjecion: (idGestion: string, objecion: Motivo) =>
    pedir<Gestion>(`/gestiones/${idGestion}/objecion`, {
      method: 'PATCH',
      body: JSON.stringify({ objecion }),
    }),

  cerrarGestion: (idGestion: string, cuerpo: CierreEnvio) =>
    pedir<Gestion>(`/gestiones/${idGestion}/cerrar`, {
      method: 'POST',
      body: JSON.stringify(cuerpo),
    }),

  iniciarCopiloto: (idGestion: string, canal: Canal | null) =>
    pedir<GuiaCopiloto>(`/gestiones/${idGestion}/copiloto/iniciar`, {
      method: 'POST',
      body: JSON.stringify({ canal }),
    }),

  turnoCopiloto: (idGestion: string, conversationId: string, texto: string) =>
    pedir<GuiaCopiloto>(`/gestiones/${idGestion}/copiloto/turno`, {
      method: 'POST',
      body: JSON.stringify({ conversation_id: conversationId, texto }),
    }),

  calificar: (idGestion: string, cuerpo: CalificacionEnvio) =>
    pedir<unknown>(`/gestiones/${idGestion}/calificacion`, {
      method: 'POST',
      body: JSON.stringify(cuerpo),
    }),
}
