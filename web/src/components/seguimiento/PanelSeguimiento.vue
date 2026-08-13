<script setup lang="ts">
import BloquePorQue from './BloquePorQue.vue'
import FunnelSeguimiento from './FunnelSeguimiento.vue'
import PanelCierre from './PanelCierre.vue'
import type { CierreEnvio, Motivo, Recomendacion, Resultado } from '@/api/tipos'

defineProps<{
  paso: number
  cerrada: boolean
  resultadoCerrado: Resultado | null
  horaCierre: string | null
  idGestion: string | null
  probActual: number
  objecionActiva: Motivo | null
  motivoSugerido: Motivo | null
  resaltarRechazo: boolean
  oferta: Recomendacion | null
  probChurn: number | null
}>()

defineEmits<{ cerrar: [datos: CierreEnvio] }>()
</script>

<template>
  <aside class="panel columna" aria-label="Seguimiento">
    <FunnelSeguimiento :paso="paso" :resultado="resultadoCerrado" :hora="horaCierre" />

    <PanelCierre
      :cerrada="cerrada"
      :resultado-cerrado="resultadoCerrado"
      :id-gestion="idGestion"
      :prob-actual="probActual"
      :objecion-activa="objecionActiva"
      :motivo-sugerido="motivoSugerido"
      :resaltar-rechazo="resaltarRechazo"
      @cerrar="$emit('cerrar', $event)"
    />

    <BloquePorQue v-if="oferta" :explicacion="oferta.explicacion" :prob-churn="probChurn" />
  </aside>
</template>

<style scoped>
.columna {
  overflow-y: auto;
  align-self: start;
  max-height: 100%;
}
</style>
