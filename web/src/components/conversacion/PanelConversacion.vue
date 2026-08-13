<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

import BurbujaTurno from './BurbujaTurno.vue'
import PilaSugerencias from './PilaSugerencias.vue'
import TermometroReceptividad from './TermometroReceptividad.vue'
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Sugerencia, TurnoGuion } from '@/api/tipos'

const props = defineProps<{
  turnos: TurnoGuion[]
  temperatura: number
  estado: string
  sugerencias: Sugerencia[]
  quedanTurnos: boolean
  cerrada: boolean
  hayGestion: boolean
  cargando: boolean
}>()

defineEmits<{ siguiente: []; iniciar: [] }>()

const hilo = ref<HTMLElement | null>(null)

watch(
  () => props.turnos.length,
  async () => {
    await nextTick()
    hilo.value?.scrollTo({ top: hilo.value.scrollHeight, behavior: 'smooth' })
  },
)
</script>

<template>
  <section class="panel columna" aria-label="Conversación">
    <TituloPanel texto="Conversación" acento="ninguno" :contador="`${turnos.length} turnos`" />

    <TermometroReceptividad :temperatura="temperatura" :estado="estado" />

    <div ref="hilo" class="hilo">
      <ul v-if="turnos.length">
        <template v-for="(turno, i) in turnos" :key="i">
          <BurbujaTurno quien="cliente" :texto="turno.cliente" :etiqueta="turno.etiqueta" />
          <BurbujaTurno quien="asesor" :texto="turno.asesor" />
        </template>
      </ul>
      <p v-else-if="!hayGestion" class="vacio">Inicie la gestión para registrar la llamada.</p>
      <p v-else class="vacio">
        La conversación aparece aquí. Pulse «Siguiente turno» para recorrer el guion.
      </p>
    </div>

    <div class="pie">
      <button
        v-if="!hayGestion"
        class="boton"
        type="button"
        :disabled="cargando"
        @click="$emit('iniciar')"
      >
        {{ cargando ? 'Abriendo…' : 'Iniciar gestión' }}
      </button>
      <button
        v-else
        class="boton"
        type="button"
        :disabled="!quedanTurnos || cerrada"
        @click="$emit('siguiente')"
      >
        {{ quedanTurnos ? 'Siguiente turno' : 'Guion completo' }}
      </button>
    </div>

    <PilaSugerencias :sugerencias="sugerencias" :en-curso="hayGestion && !cerrada" />
  </section>
</template>

<style scoped>
.columna {
  display: grid;
  grid-template-rows: auto auto minmax(160px, 1fr) auto minmax(0, 0.9fr);
  min-height: 0;
  overflow: hidden;
}

.hilo {
  overflow-y: auto;
  padding: var(--gap) var(--gap) 4px;
  min-height: 0;
}

.vacio {
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}

.pie {
  padding: var(--gap-sm) var(--gap);
  border-top: 1px solid var(--linea);
}

.boton {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--movistar-azul);
  border-radius: var(--r);
  background: var(--movistar-azul);
  color: var(--tinta-inversa);
  font-size: var(--t-sm);
  font-weight: 600;
}

.boton:disabled {
  background: var(--superficie);
  border-color: var(--linea);
  color: var(--tinta-suave);
  cursor: not-allowed;
}

@media (max-width: 1180px) {
  .columna {
    grid-template-rows: auto auto auto auto auto;
    overflow: visible;
  }

  .hilo {
    max-height: 340px;
  }
}
</style>
