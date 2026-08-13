import type { Canal, Motivo, Resultado } from './tipos'

export const ETIQUETA_MOTIVO: Record<Motivo, string> = {
  precio: 'Precio',
  permanencia: 'Permanencia',
  no_entiende_beneficio: 'No entiende el beneficio',
  ya_tiene_proveedor: 'Ya tiene proveedor',
  pide_tiempo: 'Pide tiempo',
  sin_interes: 'Sin interés',
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

export const MOTIVOS: Motivo[] = [
  'precio',
  'permanencia',
  'no_entiende_beneficio',
  'ya_tiene_proveedor',
  'pide_tiempo',
  'sin_interes',
]
