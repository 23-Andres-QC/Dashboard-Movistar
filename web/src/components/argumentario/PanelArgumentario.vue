<script setup lang="ts">
import ListaAlternativas from './ListaAlternativas.vue'
import ListaAngulos from './ListaAngulos.vue'
import ListaRebates from './ListaRebates.vue'
import SelectorCanal from './SelectorCanal.vue'
import TarjetaOferta from './TarjetaOferta.vue'
import BloquePorQue from '@/components/seguimiento/BloquePorQue.vue'
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Canal, Motivo, Recomendacion } from '@/api/tipos'

defineProps<{
  oferta: Recomendacion | null
  alternativas: Recomendacion[]
  descartadas: Recomendacion[]
  objecionActiva: Motivo | null
  probabilidad: number
  canalSeleccionado: Canal | null
  mejorCanal: Canal | null
  probChurn: number | null
  /** Con la gestión abierta el canal ya no se cambia. */
  hayGestion: boolean
  /** Hay gestión abierta y viva: lo que se recomienda cambia turno a turno. */
  enCurso: boolean
}>()

defineEmits<{ seleccionarCanal: [canal: Canal] }>()
</script>

<template>
  <aside class="panel columna" aria-label="Argumentario">
    <TituloPanel texto="Qué decirle ahora" acento="azul" :vivo="enCurso" />
    <template v-if="oferta">
      <TarjetaOferta
        :oferta="oferta"
        :probabilidad="probabilidad"
        :canal-activo="canalSeleccionado"
      />
      <SelectorCanal
        :prob-por-canal="oferta.prob_por_canal"
        :mejor-canal="mejorCanal"
        :seleccionado="canalSeleccionado"
        :bloqueado="hayGestion"
        @seleccionar="$emit('seleccionarCanal', $event)"
      />
      <ListaAlternativas :alternativas="alternativas" :descartadas="descartadas" />
      <ListaAngulos :angulos="oferta.angulos" />
      <ListaRebates :rebates="oferta.rebates" :objecion-activa="objecionActiva" />
      <BloquePorQue :explicacion="oferta.explicacion" :prob-churn="probChurn" />
    </template>
    <p v-else class="vacio">Calculando recomendaciones…</p>
  </aside>
</template>

<style scoped>
.columna {
  overflow-y: auto;
  align-self: start;
  max-height: 100%;
}

.vacio {
  padding: var(--gap);
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}
</style>
