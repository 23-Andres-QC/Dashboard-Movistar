import type {
  Canal,
  Contactabilidad,
  MedioProbatorio,
  Motivo,
  Resultado,
  TipoOferta,
} from './tipos'

/** Taxonomía del diccionario de datos, con su lectura en español de asesor. */
export const ETIQUETA_MOTIVO: Record<Motivo, string> = {
  precio: 'Precio',
  no_necesita: 'No lo necesita',
  ya_tiene_similar: 'Ya tiene algo similar',
  mal_momento: 'Mal momento',
  no_confia: 'No confía',
  otro: 'Otro',
}

export const ETIQUETA_CANAL: Record<Canal, string> = {
  tienda: 'Tienda',
  call_in: 'Call in',
  call_out: 'Call out',
  digital: 'Digital',
}

export const ETIQUETA_RESULTADO: Record<Resultado, string> = {
  en_curso: 'En curso',
  vendido: 'Vendido',
  rechazado: 'Rechazado',
  sin_contacto: 'Sin contacto',
}

export const ETIQUETA_MEDIO: Record<MedioProbatorio, string> = {
  registro_plataforma: 'Registro de plataforma',
  audio_llamada: 'Audio de la llamada',
  chat_log: 'Log de chat',
}

export const ETIQUETA_CONTACTABILIDAD: Record<Contactabilidad, string> = {
  contactado: 'Contactado',
  no_contactado: 'No contactado',
}

export const ETIQUETA_TIPO_OFERTA: Record<TipoOferta, string> = {
  plan_movil: 'Plan móvil',
  plan_hogar: 'Plan hogar',
  upgrade: 'Upgrade',
  equipo: 'Equipo',
  paquete_adicional: 'Paquete adicional',
  movistar_total: 'Movistar Total',
}

export const MOTIVOS: Motivo[] = [
  'precio',
  'no_necesita',
  'ya_tiene_similar',
  'mal_momento',
  'no_confia',
  'otro',
]

export const CANALES: Canal[] = ['tienda', 'call_in', 'call_out', 'digital']

export const MEDIOS: MedioProbatorio[] = ['registro_plataforma', 'audio_llamada', 'chat_log']
