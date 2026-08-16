import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api, ErrorApi } from '@/api/client'
import type {
  CalificacionEnvio,
  Canal,
  CierreEnvio,
  Cliente,
  Desenlace,
  GuiaCopiloto,
  Intercambio,
  Motivo,
  Recomendacion,
  Sugerencia,
  TurnoGuion,
} from '@/api/tipos'
import type { PerfilNuevo } from '@/components/ficha/FormularioClienteNuevo.vue'

const MOTIVOS_VALIDOS: Motivo[] = [
  'precio',
  'no_necesita',
  'ya_tiene_similar',
  'mal_momento',
  'no_confia',
  'otro',
]

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

  /** Canal por el que se atiende. Arranca en el que recomienda el motor, pero
   *  el asesor puede mirar los otros: el mejor nunca se oculta. */
  const canalSeleccionado = ref<Canal | null>(null)

  const objecionActiva = ref<Motivo | null>(null)
  const objecionesDetectadas = ref<Motivo[]>([])
  const sugerencias = ref<Sugerencia[]>([])
  const pasoFunnel = ref(0)

  // --- Copiloto conversacional (AI Engine) -----------------------------
  const conversationId = ref<string | null>(null)
  const speechInicial = ref<GuiaCopiloto | null>(null)
  const intercambios = ref<Intercambio[]>([])
  const copilotoPensando = ref(false)

  /** Datos que el cliente reveló durante la llamada, por campo de ficha. */
  const datosCapturados = ref<Partial<Cliente>>({})
  const perfilNuevoCompleto = ref(false)
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

  const mejorCanal = computed(() => ofertaPrincipal.value?.canal_sugerido ?? null)

  /** Probabilidad de la oferta por el canal que se está mirando. */
  const probInicial = computed(() => {
    const oferta = ofertaPrincipal.value
    if (!oferta) return 0
    const canal = canalSeleccionado.value
    if (canal && oferta.prob_por_canal[canal] !== undefined) {
      return oferta.prob_por_canal[canal]!
    }
    return oferta.probabilidad
  })

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
    canalSeleccionado.value = null
    conversationId.value = null
    speechInicial.value = null
    intercambios.value = []
    copilotoPensando.value = false
    objecionActiva.value = null
    objecionesDetectadas.value = []
    sugerencias.value = []
    pasoFunnel.value = 0
    datosCapturados.value = {}
    perfilNuevoCompleto.value = false
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
        api.recomendaciones(ficha.cliente_id),
        api.guion(ficha.cliente_id),
      ])
      recomendaciones.value = recos
      guion.value = turnos
      canalSeleccionado.value = recos[0]?.canal_sugerido ?? null

      // El desenlace es opcional: si falta, la demo sigue funcionando.
      desenlace.value = await api.desenlace(ficha.cliente_id).catch(() => null)
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
        id_cliente: cliente.value.cliente_id,
        oferta_id: oferta.oferta_id,
        oferta_recomendada: oferta.oferta,
        oferta_es_mt: oferta.es_movistar_total,
        segmento_objetivo: oferta.segmento_objetivo,
        // Se registra el canal por el que se atiende de verdad, no el sugerido.
        canal: (canalSeleccionado.value ?? oferta.canal_sugerido ?? 'call_out') as Canal,
        id_asesor: ID_ASESOR,
        prob_inicial: probInicial.value,
      })
      idGestion.value = gestion.id_gestion
      inicioLlamada.value = Date.now()
      avanzarFunnel(2) // contactado

      // El copiloto abre la conversación y entrega el speech inicial.
      try {
        const guia = await api.iniciarCopiloto(gestion.id_gestion, canalSeleccionado.value)
        conversationId.value = guia.conversation_id
        speechInicial.value = guia
      } catch (e) {
        aviso.value =
          e instanceof ErrorApi ? `Copiloto: ${e.message}` : 'El copiloto no respondió'
      }
    } catch (e) {
      error.value = e instanceof ErrorApi ? e.message : 'No se pudo abrir la gestión'
    } finally {
      abriendoGestion.value = false
    }
  }

  /** Completa el perfil de un cliente nuevo y recalcula el ranking local de ofertas. */
  function completarPerfil(perfil: PerfilNuevo) {
    if (!cliente.value?.es_nuevo) return

    datosCapturados.value = {
      ...datosCapturados.value,
      tipo_cliente: perfil.tipo_cliente,
      consumo_datos_gb_prom: perfil.consumo_datos_gb_prom,
      consumo_voz_min_prom: perfil.consumo_voz_min_prom,
      tiene_internet_hogar: perfil.tiene_internet_hogar,
      tiene_hogar: perfil.necesidad !== 'movil',
      tiene_movil: true,
      monto_facturado_prom: perfil.presupuesto,
      pct_consumo_datos: Math.min(99, Math.round((perfil.consumo_datos_gb_prom / 50) * 100)),
    }

    const puntuaciones = recomendaciones.value.map((oferta) => {
      let score = 35
      if (oferta.tipo_oferta === 'plan_movil') {
        score += perfil.necesidad !== 'hogar' ? 25 : 0
        score += perfil.consumo_datos_gb_prom >= 25 ? 15 : perfil.consumo_datos_gb_prom >= 10 ? 8 : 2
        score += perfil.presupuesto >= (oferta.precio_mensual ?? 0) ? 12 : -8
      }
      if (oferta.tipo_oferta === 'plan_hogar') {
        score += perfil.necesidad !== 'movil' ? 28 : 0
        score += perfil.presupuesto >= (oferta.precio_mensual ?? 0) ? 12 : -10
        score += perfil.tiene_internet_hogar ? -8 : 8
      }
      if (oferta.tipo_oferta === 'movistar_total') {
        score += perfil.necesidad === 'ambos' ? 25 : 0
        score += perfil.tiene_internet_hogar ? 20 : 0
        score += perfil.presupuesto >= (oferta.precio_mensual ?? 0) ? 12 : -15
      }
      const probabilidad = Math.min(92, Math.max(8, score))
      return {
        ...oferta,
        probabilidad,
        margen: Math.max(4, Math.round(oferta.margen * 0.55)),
        confianza: 'media' as const,
        nota: 'Calculado con los datos declarados por el cliente',
      }
    })

    recomendaciones.value = puntuaciones.sort((a, b) => b.probabilidad - a.probabilidad)
    canalSeleccionado.value = recomendaciones.value[0]?.canal_sugerido ?? null
    perfilNuevoCompleto.value = true
    aviso.value = `Perfil completo: ${recomendaciones.value[0]?.oferta ?? 'recomendación actualizada'}`
  }

  /** Manda al copiloto lo que dijo el cliente y guarda qué responderle. */
  async function decirCliente(texto: string, etiqueta = 'Turno', respaldo: string | null = null) {
    const limpio = texto.trim()
    if (!limpio || !idGestion.value || !conversationId.value || cerrada.value) return

    const intercambio: Intercambio = {
      dijo: limpio,
      etiqueta,
      guia: null,
      respaldo,
      pendiente: true,
      error: null,
    }
    intercambios.value.push(intercambio)
    copilotoPensando.value = true
    avanzarFunnel(3) // oferta presentada

    // Las líneas del guion demo son respuestas validadas: se muestran de
    // inmediato y no quedan bloqueadas esperando al servicio externo.
    if (respaldo) {
      intercambio.guia = {
        conversation_id: conversationId.value,
        response_type: 'demo_fallback',
        conversation_stage: 'guion_demo',
        recommended_action: 'RESPOND_WITH_SCRIPT',
        resumen: 'Respuesta validada para este escenario de demostración.',
        que_decir: respaldo,
        pregunta_seguimiento: null,
        oferta_alternativa: null,
        objecion_categoria: null,
        objecion_confianza: null,
        grounded: true,
        requiere_revision: false,
        flags: ['demo_fallback'],
      }
      intercambio.pendiente = false
      copilotoPensando.value = false
      return
    }

    try {
      const guia = await api.turnoCopiloto(idGestion.value, conversationId.value, limpio)
      intercambio.guia = guia
      await registrarObjecion(guia.objecion_categoria)
    } catch (e) {
      // En la demo, la línea validada del guion mantiene la conversación fluida
      // aunque el servicio de copiloto no responda a tiempo.
      if (respaldo) {
        intercambio.guia = {
          conversation_id: conversationId.value,
          response_type: 'demo_fallback',
          conversation_stage: 'guion_demo',
          recommended_action: 'RESPOND_WITH_SCRIPT',
          resumen: 'Respuesta validada para este escenario de demostración.',
          que_decir: respaldo,
          pregunta_seguimiento: null,
          oferta_alternativa: null,
          objecion_categoria: null,
          objecion_confianza: null,
          grounded: true,
          requiere_revision: false,
          flags: ['demo_fallback'],
        }
      } else {
        intercambio.error = e instanceof ErrorApi ? e.message : 'El copiloto no respondió'
      }
    } finally {
      intercambio.pendiente = false
      copilotoPensando.value = false
    }
  }

  /** La objeción la clasifica el copiloto; aquí solo se registra. */
  async function registrarObjecion(categoria: string | null) {
    if (!categoria || categoria === 'otro') return
    const motivo = MOTIVOS_VALIDOS.find((m) => m === categoria)
    if (!motivo) return

    objecionActiva.value = motivo
    avanzarFunnel(4) // objeción y rebate
    if (objecionesDetectadas.value.includes(motivo) || !idGestion.value) return

    objecionesDetectadas.value.push(motivo)
    try {
      await api.marcarObjecion(idGestion.value, motivo)
    } catch {
      aviso.value = 'No se pudo registrar la objeción'
    }
  }

  /** Avanza el guion de demo: toma lo que dice el cliente y se lo pasa al
   *  copiloto, que es quien decide la respuesta. El guion aporta el contexto
   *  de ML (probabilidad, temperatura, datos revelados), no el texto a decir. */
  async function siguienteTurno() {
    if (!hayGestion.value || !quedanTurnos.value || cerrada.value) return
    indiceTurno.value += 1
    const turno = turnoActual.value
    if (!turno) return

    if (turno.sugerencia) sugerencias.value.unshift(turno.sugerencia)
    if (turno.paso_funnel) avanzarFunnel(turno.paso_funnel)

    // Cada dato revelado llena un campo vacío de la ficha y estrecha el margen.
    if (turno.datos_capturados) {
      datosCapturados.value = { ...datosCapturados.value, ...turno.datos_capturados }
      ultimaCaptura.value = Object.keys(turno.datos_capturados)
    } else {
      ultimaCaptura.value = []
    }

    await decirCliente(turno.cliente, turno.etiqueta, turno.asesor)
    if (turno.objecion) await registrarObjecion(turno.objecion)
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

  function seleccionarCanal(canal: Canal) {
    // Una vez abierta la gestión el canal ya quedó registrado: no se cambia.
    if (hayGestion.value) return
    canalSeleccionado.value = canal
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
    canalSeleccionado,
    conversationId,
    speechInicial,
    intercambios,
    copilotoPensando,
    objecionActiva,
    objecionesDetectadas,
    sugerencias,
    pasoFunnel,
    datosCapturados,
    perfilNuevoCompleto,
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
    mejorCanal,
    probInicial,
    probActual,
    temperatura,
    estadoCliente,
    hayGestion,
    rumboRechazo,

    buscar,
    seleccionarCanal,
    iniciarGestion,
    decirCliente,
    siguienteTurno,
    cerrarGestion,
    calificar,
    completarPerfil,
    reiniciar,
    limpiarAviso,
  }
})
