<script setup lang="ts">
import ListaAlternativas from './ListaAlternativas.vue'
import ListaAngulos from './ListaAngulos.vue'
import ListaRebates from './ListaRebates.vue'
import TarjetaOferta from './TarjetaOferta.vue'
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Motivo, Recomendacion } from '@/api/tipos'

defineProps<{
  oferta: Recomendacion | null
  alternativas: Recomendacion[]
  descartadas: Recomendacion[]
  objecionActiva: Motivo | null
  /** Hay gestión abierta: lo que se recomienda cambia turno a turno. */
  enCurso: boolean
}>()
</script>

<template>
  <aside class="panel columna" aria-label="Argumentario">
    <TituloPanel texto="Qué decirle ahora" acento="azul" :vivo="enCurso" />
    <template v-if="oferta">
      <TarjetaOferta :oferta="oferta" />
      <ListaAlternativas :alternativas="alternativas" :descartadas="descartadas" />
      <ListaAngulos :angulos="oferta.angulos" />
      <ListaRebates :rebates="oferta.rebates" :objecion-activa="objecionActiva" />
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
