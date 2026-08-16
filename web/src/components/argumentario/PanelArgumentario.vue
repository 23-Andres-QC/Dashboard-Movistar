<script setup lang="ts">
import ListaAlternativas from './ListaAlternativas.vue'
import DetalleOferta from './DetalleOferta.vue'
import SelectorCanal from './SelectorCanal.vue'
import TarjetaOferta from './TarjetaOferta.vue'
import { computed, ref, watch } from 'vue'
import type { Canal, Motivo, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  oferta: Recomendacion | null
  alternativas: Recomendacion[]
  descartadas: Recomendacion[]
  objecionActiva: Motivo | null
  probabilidad: number
  canalSeleccionado: Canal | null
  mejorCanal: Canal | null
  planActual: string | null
  facturacion: number | null
  /** Con la gestión abierta el canal ya no se cambia. */
  hayGestion: boolean
  /** Hay gestión abierta y viva: lo que se recomienda cambia turno a turno. */
  enCurso: boolean
  mostrarDetalle: boolean
}>()

const alternativaActiva = ref<Recomendacion | null>(null)
const ofertaVista = computed(() => alternativaActiva.value ?? props.oferta!)
const probabilidadVista = computed(() => {
  const oferta = ofertaVista.value
  if (!oferta) return 0
  return props.canalSeleccionado && oferta.prob_por_canal[props.canalSeleccionado] !== undefined
    ? oferta.prob_por_canal[props.canalSeleccionado]!
    : oferta.probabilidad
})

watch(() => props.oferta?.oferta_id, () => { alternativaActiva.value = null })

defineEmits<{ seleccionarCanal: [canal: Canal]; verDetalle: [] }>()
</script>

<template>
  <!-- Sin fondo propio: la columna se funde con el gris de la página y solo
       las tarjetas destacan en blanco. Así no quedan parches sueltos. -->
  <aside class="columna" aria-label="Argumentario">
    <template v-if="oferta">
      <SelectorCanal
        :prob-por-canal="ofertaVista?.prob_por_canal ?? {}"
        :mejor-canal="ofertaVista?.canal_sugerido ?? null"
        :seleccionado="canalSeleccionado"
        :bloqueado="hayGestion"
        @seleccionar="$emit('seleccionarCanal', $event)"
      />

      <ListaAlternativas
        :alternativas="alternativas"
        :descartadas="descartadas"
        :alternativa-activa="alternativaActiva"
        @seleccionar="alternativaActiva = $event"
        @volver="alternativaActiva = null"
      />

      <TarjetaOferta
        :oferta="ofertaVista"
        :probabilidad="probabilidadVista"
        :canal-activo="canalSeleccionado"
        :es-mejor-opcion="!alternativaActiva"
        @detalle="$emit('verDetalle')"
      />

      <DetalleOferta
        v-if="mostrarDetalle"
        :oferta="ofertaVista"
        :plan-actual="planActual"
        :facturacion="facturacion"
      />

    </template>

    <p v-else class="vacio tarjeta-suelta">Calculando recomendaciones…</p>
  </aside>
</template>

<style scoped>
.columna {
  display: flex;
  flex-direction: column;
  gap: var(--gap);
  overflow-y: auto;
  align-self: stretch;
  min-height: 0;
  padding-right: 2px;
}

/* La columna tiene scroll propio: cada tarjeta conserva su contenido completo
   y nunca se comprime para intentar caber en el alto del panel. */
.columna > * {
  flex: 0 0 auto;
}

.vacio {
  padding: var(--gap-lg);
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}
</style>
