/** Espejo del contrato de la API (api/app/schemas.py).
 *  Los nombres siguen el diccionario de datos del desafío: en la fase 2 cambia
 *  quién produce estos datos, no su forma. */

export type Canal = 'tienda' | 'call_in' | 'call_out' | 'digital'

export type Resultado = 'en_curso' | 'vendido' | 'rechazado' | 'sin_contacto'

/** Taxonomía de `historial_campanias.motivo_rechazo`. */
export type Motivo =
  | 'precio'
  | 'no_necesita'
  | 'ya_tiene_similar'
  | 'mal_momento'
  | 'no_confia'
  | 'otro'

export type MedioProbatorio = 'registro_plataforma' | 'audio_llamada' | 'chat_log'

export type Contactabilidad = 'contactado' | 'no_contactado'

export type TipoOferta =
  | 'plan_movil'
  | 'plan_hogar'
  | 'upgrade'
  | 'equipo'
  | 'paquete_adicional'
  | 'movistar_total'

export type SegmentoObjetivo = 'movil' | 'hogar' | 'ambos'

export type TipoCliente = 'prepago' | 'postpago'

export type TipoSugerencia = 'info' | 'warn' | 'risk' | 'good'

export type Confianza = 'alta' | 'media' | 'baja'

export type Origen = 'historial' | 'lookalike'

export interface Cliente {
  // Identidad. El dataset real es anónimo: dni y nombre son solo de demo.
  cliente_id: string
  dni: string | null
  nombre: string | null

  // Perfil y relación comercial
  tipo_cliente: TipoCliente | null
  antiguedad_meses: number
  tiene_movil: boolean
  tiene_hogar: boolean
  tiene_internet_hogar: boolean
  es_movistar_total: boolean
  /** Segmento prioritario del desafío. */
  elegible_mt: boolean
  plan_actual: string | null
  monto_facturado_prom: number | null
  edad_rango: string | null
  ubicacion_departamento: string
  es_usuario_app: boolean

  // Comportamiento de los últimos 6 meses
  consumo_datos_gb_prom: number | null
  consumo_voz_min_prom: number | null
  dias_mora_prom: number | null
  meses_moroso: number | null
  n_reclamos: number | null
  n_actividad_canal: number | null
  canal_mas_usado: Canal | null

  // Derivados por el modelo
  es_nuevo: boolean
  pct_consumo_datos: number | null
  prob_churn: number | null
  riesgo_baja: string | null
}

export interface Angulo {
  titulo: string
  texto: string
}

export interface Rebate {
  objecion: Motivo
  cita: string
  texto: string
}

export interface Recomendacion {
  // Catálogo
  oferta_id: string
  oferta: string
  tipo_oferta: TipoOferta
  segmento_objetivo: SegmentoObjetivo
  es_movistar_total: boolean
  precio_mensual: number | null
  ahorro_pct: number | null
  gb_incluidos: number | null

  // Score del motor
  probabilidad: number
  /** Incertidumbre en puntos porcentuales. 0 cuando la confianza es alta. */
  margen: number
  confianza: Confianza
  origen: Origen
  /** Motivo de rechazo más probable para esta oferta y este cliente. */
  riesgo_principal: Motivo | null
  ahorro: number | null
  instalacion: number | null
  /** Speech base de la oferta; el copiloto lo reemplaza cuando responde. */
  speech: string | null
  explicacion: string[]
  /** Probabilidad estimada por canal; `canal_sugerido` es el máximo. */
  prob_por_canal: Partial<Record<Canal, number>>
  canal_sugerido: Canal | null
  franja_sugerida: string | null
  angulos: Angulo[]
  rebates: Rebate[]
  /** Por qué el motor NO recomendó esta oferta. */
  descartada: string | null
  nota: string | null
}

export interface Sugerencia {
  tipo: TipoSugerencia
  titulo: string
  texto: string
}

export interface TurnoGuion {
  cliente: string
  asesor: string
  probabilidad: number
  margen: number | null
  temperatura: number
  estado: string
  etiqueta: string
  objecion: Motivo | null
  paso_funnel: number | null
  datos_capturados: Record<string, number> | null
  sugerencia: Sugerencia | null
}

export interface Desenlace {
  resultado: Resultado
  motivo_real: Motivo | null
  prob_final: number
  contactabilidad: Contactabilidad
  es_rebate: boolean
  medio_probatorio: MedioProbatorio | null
  calificacion_sugerida: { facilidad_venta: number; oferta_fue_pertinente: boolean } | null
}

export interface Gestion {
  id_gestion: string
  id_cliente: string
  oferta_id: string | null
  oferta_recomendada: string
  oferta_es_mt: boolean
  segmento_objetivo: string
  canal: string
  id_asesor: string
  inicio: string
  fin: string | null
  prob_inicial: number
  prob_final: number | null
  resultado: Resultado
  motivo_real: Motivo | null
  contactabilidad: Contactabilidad | null
  es_rebate: boolean
  medio_probatorio: MedioProbatorio | null
  objeciones_detectadas: Motivo[]
}

export interface CalificacionEnvio {
  facilidad_venta: number
  oferta_fue_pertinente: boolean
  nps_declarado: number | null
  comentario: string | null
}

/** Guía del AI Engine (contrato Dashboard 0.1) para un turno. */
export interface GuiaCopiloto {
  conversation_id: string
  response_type: string
  conversation_stage: string
  recommended_action: string
  resumen: string | null
  que_decir: string
  pregunta_seguimiento: string | null
  oferta_alternativa: string | null
  objecion_categoria: string | null
  objecion_confianza: number | null
  grounded: boolean
  requiere_revision: boolean
  flags: string[]
}

/** Un intercambio del diálogo: lo que dijo el cliente y qué responderle. */
export interface Intercambio {
  dijo: string
  etiqueta: string
  guia: GuiaCopiloto | null
  /** Línea del guion base, por si el copiloto solo puede pedir aclaración. */
  respaldo: string | null
  pendiente: boolean
  error: string | null
}

export interface CierreEnvio {
  resultado: Exclude<Resultado, 'en_curso'>
  motivo_real: Motivo | null
  prob_final: number | null
  contactabilidad: Contactabilidad
  es_rebate: boolean
  medio_probatorio: MedioProbatorio | null
}
