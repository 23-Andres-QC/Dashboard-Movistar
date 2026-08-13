import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api, ErrorApi } from '@/api/client'
import type {
  CalificacionEnvio,
  Canal,
  CierreEnvio,
  Cliente,
  Desenlace,
  Motivo,
  Recomendacion,
  Sugerencia,
  TurnoGuion,
} from '@/api/tipos'

export const ID_ASESOR = 'ASE-001'
export const NOMBRE_ASESOR = 'M. Delgado'

/** Pasos del funnel de seguimiento, en orden. */
export const PASOS_FUNNEL = [
  'Clasificado',
  'Contactado',
  'Oferta presentada',
  'Objeción y rebate',
  'Resultado',
] as const

export const SIN_RESULTADOS =
  'Sin resultados para ese DNI. Pruebe con 45789123, 70112384 u 08954412.'

export const useGestionStore = defineStore('gestion', () => {
  // --- Estado ------------------------------------------------------------
  const cliente = ref<Cliente | null>(null)
  const recomendaciones = ref<Recomendacion[]>([])
  const guion = ref<TurnoGuion[]>([])
  const desenlace = ref<Desenlace | null>(null)

  const indiceTurno = ref(-1)
  const idGestion = ref<string | null>(null)
  const inicioLlamada = ref<number | null>(null)

  const objecionActiva = ref<Motivo | null>(null)
  const objecionesDetectadas = ref<Motivo[]>([])
  const sugerencias = ref<Sugerencia[]>([])
  const pasoFunnel = ref(0)

  /** Datos que el cliente reveló durante la llamada, por campo de ficha. */
  const datosCapturados = ref<Record<string, number>>({})
  const ultimaCaptura = ref<string[]>([])

  const cerrada = ref(false)
  const cierre = ref<CierreEnvio | null>(null)
  const horaCierre = ref<string | null>(null)
  const calificada = ref(false)

  const cargando = ref(false)
  const abriendoGestion = ref(false)
  const error = ref<string | null>(null)
  const aviso = ref<string | null>(null)

  // --- Derivados ---------------------------------------------------------
  const ofertaPrincipal = computed(() => recomendaciones.value[0] ?? null)

  /** Las descartadas van al final: primero lo que sí se puede ofrecer. */
  const alternativas = computed(() =>
    recomendaciones.value.slice(1).filter((r) => !r.descartada),
  )
  const descartadas = computed(() => recomendaciones.value.filter((r) => !!r.descartada))

  const turnosVisibles = computed(() => guion.value.slice(0, indiceTurno.value + 1))
  const turnoActual = computed(() => guion.value[indiceTurno.value] ?? null)
  const quedanTurnos = computed(() => indiceTurno.value < guion.value.length - 1)

  const esNuevo = computed(() => cliente.value?.es_nuevo ?? false)

  /** Ficha con los datos capturados en vivo sobreescribiendo los vacíos. */
  const clienteVista = computed<Cliente | null>(() =>
    cliente.value ? { ...cliente.value, ...datosCapturados.value } : null,
  )

  const probInicial = computed(() => ofertaPrincipal.value?.probabilidad ?? 0)

  /** Solo se usa para registrar `prob_final` al cerrar: no se muestra en pantalla. */
  const probActual = computed(() =>
    turnoActual.value ? turnoActual.value.probabilidad : probInicial.value,
  )

  const temperatura = computed(() => turnoActual.value?.temperatura ?? 50)

  const estadoCliente = computed(() => turnoActual.value?.estado ?? 'Sin contacto')

  const hayGestion = computed(() => idGestion.value !== null)

  /** La última sugerencia es de riesgo: la conversación va hacia el rechazo. */
  const rumboRechazo = computed(() => sugerencias.value[0]?.tipo === 'risk')

  // --- Acciones ----------------------------------------------------------
  function reiniciar() {
    cliente.value = null
    recomendaciones.value = []
    guion.value = []
    desenlace.value = null
    indiceTurno.value = -1
    idGestion.value = null
    inicioLlamada.value = null
    objecionActiva.value = null
    objecionesDetectadas.value = []
    sugerencias.value = []
    pasoFunnel.value = 0
    datosCapturados.value = {}
    ultimaCaptura.value = []
    cerrada.value = false
    cierre.value = null
    horaCierre.value = null
    calificada.value = false
    error.value = null
    aviso.value = null
  }

  /** El funnel solo avanza: nunca retrocede al recalcularse. */
  function avanzarFunnel(paso: number) {
    if (paso > pasoFunnel.value) pasoFunnel.value = paso
  }

  async function buscar(dni: string) {
    const limpio = dni.trim()
    if (!limpio) return

    reiniciar()
    cargando.value = true
    try {
      const ficha = await api.buscarCliente(limpio)
      cliente.value = ficha
      avanzarFunnel(1) // clasificado

      const [recos, turnos] = await Promise.all([
        api.recomendaciones(ficha.id_cliente),
        api.guion(ficha.id_cliente),
      ])
      recomendaciones.value = recos
      guion.value = turnos

      // El desenlace es opcional: si falta, la demo sigue funcionando.
      desenlace.value = await api.desenlace(ficha.id_cliente).catch(() => null)
    } catch (e) {
      error.value =
        e instanceof ErrorApi
          ? e.status === 404
            ? SIN_RESULTADOS
            : e.message
          : 'Error inesperado'
      cliente.value = null
    } finally {
      cargando.value = false
    }
  }

  /** Abre la gestión en la base. Hasta aquí no se ha escrito nada real. */
  async function iniciarGestion() {
    const oferta = ofertaPrincipal.value
    if (!cliente.value || !oferta || idGestion.value) return

    abriendoGestion.value = true
    try {
      const gestion = await api.abrirGestion({
        id_cliente: cliente.value.id_cliente,
        oferta_recomendada: oferta.oferta,
        canal: (oferta.canal_sugerido ?? 'call_out') as Canal,
        id_asesor: ID_ASESOR,
        prob_inicial: oferta.probabilidad,
      })
      idGestion.value = gestion.id_gestion
      inicioLlamada.value = Date.now()
      avanzarFunnel(2) // contactado
    } catch (e) {
      error.value = e instanceof ErrorApi ? e.message : 'No se pudo abrir la gestión'
    } finally {
      abriendoGestion.value = false
    }
  }

  async function siguienteTurno() {
    if (!hayGestion.value || !quedanTurnos.value || cerrada.value) return
    indiceTurno.value += 1
    const turno = turnoActual.value
    if (!turno) return

    if (turno.sugerencia) sugerencias.value.unshift(turno.sugerencia)

    avanzarFunnel(3) // oferta presentada
    if (turno.paso_funnel) avanzarFunnel(turno.paso_funnel)

    // Cada dato revelado llena un campo vacío de la ficha y estrecha el margen.
    if (turno.datos_capturados) {
      datosCapturados.value = { ...datosCapturados.value, ...turno.datos_capturados }
      ultimaCaptura.value = Object.keys(turno.datos_capturados)
    } else {
      ultimaCaptura.value = []
    }

    if (turno.objecion) {
      objecionActiva.value = turno.objecion
      avanzarFunnel(4) // objeción y rebate
      if (!objecionesDetectadas.value.includes(turno.objecion)) {
        objecionesDetectadas.value.push(turno.objecion)
        if (idGestion.value) {
          try {
            await api.marcarObjecion(idGestion.value, turno.objecion)
          } catch {
            aviso.value = 'No se pudo registrar la objeción'
          }
        }
      }
    }
  }

  async function cerrarGestion(datos: CierreEnvio) {
    if (!idGestion.value || cerrada.value) return
    cargando.value = true
    try {
      await api.cerrarGestion(idGestion.value, {
        ...datos,
        prob_final: datos.prob_final ?? probActual.value,
      })
      cerrada.value = true
      cierre.value = datos
      horaCierre.value = new Date().toLocaleTimeString('es-PE', {
        hour: '2-digit',
        minute: '2-digit',
      })
      avanzarFunnel(5) // resultado
    } catch (e) {
      error.value = e instanceof ErrorApi ? e.message : 'No se pudo cerrar la gestión'
      throw e
    } finally {
      cargando.value = false
    }
  }

  async function calificar(datos: CalificacionEnvio) {
    if (!idGestion.value) return
    await api.calificar(idGestion.value, datos)
    calificada.value = true
    aviso.value = `Calificación registrada en ${idGestion.value}`
  }

  function limpiarAviso() {
    aviso.value = null
  }

  return {
    cliente,
    clienteVista,
    recomendaciones,
    guion,
    desenlace,
    indiceTurno,
    idGestion,
    inicioLlamada,
    objecionActiva,
    objecionesDetectadas,
    sugerencias,
    pasoFunnel,
    datosCapturados,
    ultimaCaptura,
    cerrada,
    cierre,
    horaCierre,
    calificada,
    cargando,
    abriendoGestion,
    error,
    aviso,

    ofertaPrincipal,
    alternativas,
    descartadas,
    turnosVisibles,
    turnoActual,
    quedanTurnos,
    esNuevo,
    probInicial,
    probActual,
    temperatura,
    estadoCliente,
    hayGestion,
    rumboRechazo,

    buscar,
    iniciarGestion,
    siguienteTurno,
    cerrarGestion,
    calificar,
    reiniciar,
    limpiarAviso,
  }
})
