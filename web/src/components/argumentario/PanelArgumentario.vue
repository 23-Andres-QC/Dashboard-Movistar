<script setup lang="ts">
import ListaAlternativas from './ListaAlternativas.vue'
import PlanActual from './PlanActual.vue'
import SelectorCanal from './SelectorCanal.vue'
import TarjetaOferta from './TarjetaOferta.vue'
import type { Canal, Motivo, Recomendacion } from '@/api/tipos'

defineProps<{
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
}>()

defineEmits<{ seleccionarCanal: [canal: Canal]; verDetalle: [] }>()
</script>

<template>
  <!-- Sin fondo propio: la columna se funde con el gris de la página y solo
       las tarjetas destacan en blanco. Así no quedan parches sueltos. -->
  <aside class="columna" aria-label="Argumentario">
    <template v-if="oferta">
      <PlanActual :plan="planActual" :facturacion="facturacion" />

      <TarjetaOferta
        :oferta="oferta"
        :probabilidad="probabilidad"
        :canal-activo="canalSeleccionado"
        @detalle="$emit('verDetalle')"
      />

      <SelectorCanal
        :prob-por-canal="oferta.prob_por_canal"
        :mejor-canal="mejorCanal"
        :seleccionado="canalSeleccionado"
        :bloqueado="hayGestion"
        @seleccionar="$emit('seleccionarCanal', $event)"
      />

      <ListaAlternativas :alternativas="alternativas" :descartadas="descartadas" />
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
