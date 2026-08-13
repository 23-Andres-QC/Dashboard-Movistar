/** Espejo del contrato de la API (api/app/schemas.py).
 *  En la fase 2 cambia quien produce estos datos, no su forma. */

export type Canal = 'tienda' | 'call_in' | 'call_out' | 'digital'

export type Resultado = 'en_curso' | 'vendido' | 'rechazado' | 'sin_contacto'

export type Motivo =
  | 'precio'
  | 'permanencia'
  | 'no_entiende_beneficio'
  | 'ya_tiene_proveedor'
  | 'pide_tiempo'
  | 'sin_interes'

export type TipoSugerencia = 'info' | 'warn' | 'risk' | 'good'

export type Confianza = 'alta' | 'media' | 'baja'

export type Origen = 'historial' | 'lookalike'

export interface Cliente {
  dni: string
  id_cliente: string
  es_nuevo: boolean
  nombre: string
  distrito: string
  antiguedad_meses: number
  /** null en clientes nuevos: no hay historial. Nunca 0. */
  arpu: number | null
  productos: string
  riesgo_baja: string | null
  prob_churn: number | null
  pct_consumo_datos: number | null
  lineas_domicilio: number
  cobertura_fibra: boolean
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
  oferta: string
  probabilidad: number
  /** Incertidumbre en puntos porcentuales. 0 cuando la confianza es alta. */
  margen: number
  confianza: Confianza
  origen: Origen
  ahorro: number | null
  instalacion: number | null
  explicacion: string[]
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
  /** Se estrecha turno a turno cuando el cliente revela información. */
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
  calificacion_sugerida: { facilidad_venta: number; oferta_fue_pertinente: boolean } | null
}

export interface Gestion {
  id_gestion: string
  id_cliente: string
  oferta_recomendada: string
  canal: string
  id_asesor: string
  inicio: string
  fin: string | null
  prob_inicial: number
  prob_final: number | null
  resultado: Resultado
  motivo_real: Motivo | null
  medio_probatorio: string | null
  objeciones_detectadas: Motivo[]
}

export interface CalificacionEnvio {
  facilidad_venta: number
  oferta_fue_pertinente: boolean
  nps_declarado: number | null
  comentario: string | null
}

export interface CierreEnvio {
  resultado: Exclude<Resultado, 'en_curso'>
  motivo_real: Motivo | null
  prob_final: number | null
  medio_probatorio: string | null
}
