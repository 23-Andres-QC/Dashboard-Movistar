<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import FranjaFicha from '@/components/ficha/FranjaFicha.vue'
import FormularioClienteNuevo from '@/components/ficha/FormularioClienteNuevo.vue'
import ModalCalificacion from '@/components/calificacion/ModalCalificacion.vue'
import PanelArgumentario from '@/components/argumentario/PanelArgumentario.vue'
import PanelConversacion from '@/components/conversacion/PanelConversacion.vue'
import FunnelHorizontal from '@/components/seguimiento/FunnelHorizontal.vue'
import PanelCierre from '@/components/seguimiento/PanelCierre.vue'
import RailSuperior from '@/components/rail/RailSuperior.vue'
import AvisoDiscreto from '@/components/ui/AvisoDiscreto.vue'
import EstadoVacio from '@/components/ui/EstadoVacio.vue'

import { ID_ASESOR, NOMBRE_ASESOR, useGestionStore } from '@/stores/gestion'
import type { CalificacionEnvio, CierreEnvio, MedioProbatorio, Motivo } from '@/api/tipos'

const route = useRoute()
const router = useRouter()
const store = useGestionStore()

const {
  cliente,
  clienteVista,
  perfilNuevoCompleto,
  ofertaPrincipal,
  alternativas,
  descartadas,
  desenlace,
  speechInicial,
  intercambios,
  copilotoPensando,
  objecionActiva,
  ultimaCaptura,
  pasoFunnel,
  canalSeleccionado,
  mejorCanal,
  probInicial,
  probActual,
  temperatura,
  estadoCliente,
  quedanTurnos,
  rumboRechazo,
  cerrada,
  cierre,
  horaCierre,
  calificada,
  cargando,
  abriendoGestion,
  error,
  aviso,
  idGestion,
  hayGestion,
  inicioLlamada,
} = storeToRefs(store)

/** Cierre elegido en el panel, pendiente de confirmar en el modal. */
const cierrePendiente = ref<CierreEnvio | null>(null)
const mostrarDetalleOferta = ref(false)

const dniRuta = computed(() => (route.params.dni as string | undefined) ?? '')

async function buscar(dni: string) {
  mostrarDetalleOferta.value = false
  if (dni !== dniRuta.value) await router.push({ name: 'asesor', params: { dni } })
  await store.buscar(dni)
}

/** El panel de cierre no escribe todavía: primero se confirma el motivo. */
async function pedirCierre(datos: CierreEnvio) {
  // Sin contacto no hay interacción que evaluar: se registra y termina sin encuesta.
  if (datos.resultado === 'sin_contacto') {
    await store.cerrarGestion(datos)
    return
  }
  cierrePendiente.value = datos
}

async function confirmarCierre(
  calificacion: CalificacionEnvio,
  motivo: Motivo | null,
  medio: MedioProbatorio | null,
) {
  if (!cierrePendiente.value) return
  await store.cerrarGestion({
    ...cierrePendiente.value,
    motivo_real: motivo,
    medio_probatorio: medio,
  })
  await store.calificar(calificacion)
  cierrePendiente.value = null
}

/** Omitir la calificación no puede perder el resultado: se cierra igual. */
async function omitirCalificacion() {
  if (!cierrePendiente.value) return
  await store.cerrarGestion(cierrePendiente.value)
  cierrePendiente.value = null
}

onMounted(() => {
  if (dniRuta.value) store.buscar(dniRuta.value)
})

watch(dniRuta, (nuevo, anterior) => {
  if (nuevo && nuevo !== anterior && nuevo !== cliente.value?.dni) store.buscar(nuevo)
})
</script>

<template>
  <div class="consola">
    <RailSuperior
      :dni-inicial="dniRuta"
      :cargando="cargando"
      :inicio-llamada="inicioLlamada"
      :llamada-cerrada="cerrada"
      :nombre-asesor="NOMBRE_ASESOR"
      :id-asesor="ID_ASESOR"
      @buscar="buscar"
    />

    <template v-if="clienteVista">
      <div class="marco">
        <FranjaFicha :cliente="clienteVista" :ultima-captura="ultimaCaptura" />
      </div>

      <div v-if="clienteVista.es_nuevo && !perfilNuevoCompleto" class="marco">
        <FormularioClienteNuevo @calcular="store.completarPerfil($event)" />
      </div>

      <div v-else class="columnas marco">
        <PanelArgumentario
          :oferta="ofertaPrincipal"
          :alternativas="alternativas"
          :descartadas="descartadas"
          :objecion-activa="objecionActiva"
          :probabilidad="probInicial"
          :canal-seleccionado="canalSeleccionado"
          :mejor-canal="mejorCanal"
          :plan-actual="clienteVista.plan_actual"
          :facturacion="clienteVista.monto_facturado_prom"
          :hay-gestion="hayGestion"
          :en-curso="hayGestion && !cerrada"
          :mostrar-detalle="mostrarDetalleOferta"
          @seleccionar-canal="store.seleccionarCanal($event)"
          @ver-detalle="mostrarDetalleOferta = !mostrarDetalleOferta"
        />

        <div class="centro panel">
          <FunnelHorizontal
            :paso="pasoFunnel"
            :resultado="cierre?.resultado ?? null"
            :hora="horaCierre"
          />

          <PanelConversacion
            :oferta="ofertaPrincipal"
            :speech-inicial="speechInicial"
            :intercambios="intercambios"
            :copiloto-pensando="copilotoPensando"
            :temperatura="temperatura"
            :estado="estadoCliente"
            :quedan-turnos="quedanTurnos"
            :cerrada="cerrada"
            :hay-gestion="hayGestion"
            :cargando="abriendoGestion"
            @iniciar="store.iniciarGestion()"
            @siguiente="store.siguienteTurno()"
            @decir="store.decirCliente($event)"
          />

          <!-- El resultado se registra al final de la llamada, bajo el chat. -->
          <PanelCierre
            :cerrada="cerrada"
            :resultado-cerrado="cierre?.resultado ?? null"
            :id-gestion="idGestion"
            :prob-actual="probActual"
            :objecion-activa="objecionActiva"
            :resaltar-rechazo="rumboRechazo"
            @cerrar="pedirCierre"
          />
        </div>
      </div>
    </template>

    <EstadoVacio v-else :error="error" :cargando="cargando" @probar="buscar" />

    <ModalCalificacion
      v-if="cierrePendiente && !calificada"
      :resultado="cierrePendiente.resultado"
      :motivo-inicial="cierrePendiente.motivo_real"
      :sugerida="desenlace?.calificacion_sugerida ?? null"
      @enviar="confirmarCierre"
      @omitir="omitirCalificacion"
    />

    <AvisoDiscreto v-if="aviso" :texto="aviso" @cerrar="store.limpiarAviso()" />
  </div>
</template>

<style scoped>
.consola {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  background: linear-gradient(180deg, #edf3f7 0%, var(--gris-canvas) 34%, var(--gris-canvas) 100%);
}

/* El contenido no se pega a los bordes en pantallas anchas. */
.marco {
  width: 100%;
  max-width: var(--ancho-max);
  margin: 0 auto;
  padding: 0 var(--gap);
}

.marco + .marco {
  margin-top: var(--gap);
}

.marco:first-of-type {
  margin-top: var(--gap);
}

.columnas {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
  gap: var(--gap);
  padding: var(--gap);
  flex: 1;
  min-height: 0;
}

/* La columna central apila copiloto y cierre dentro de un solo panel. */
.centro {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-height: 0;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: var(--sombra-2);
}

@media (max-width: 1180px) {
  .consola {
    height: auto;
  }

  .columnas {
    grid-template-columns: 1fr;
  }

  .centro {
    grid-template-rows: none;
    overflow: visible;
  }
}

@media (max-width: 768px) {
  .marco {
    padding-inline: var(--gap-sm);
  }

  .columnas {
    padding: var(--gap-sm);
    gap: var(--gap-sm);
  }
}
</style>
