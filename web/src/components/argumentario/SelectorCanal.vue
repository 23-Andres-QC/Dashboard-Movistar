<script setup lang="ts">
import { computed } from 'vue'

import { CANALES, ETIQUETA_CANAL } from '@/api/etiquetas'
import type { Canal } from '@/api/tipos'

const props = defineProps<{
  probPorCanal: Partial<Record<Canal, number>>
  /** El canal que el motor recomienda: siempre queda marcado. */
  mejorCanal: Canal | null
  seleccionado: Canal | null
  /** Con la gestión abierta el canal ya quedó registrado. */
  bloqueado: boolean
}>()

const emit = defineEmits<{ seleccionar: [canal: Canal] }>()

/** Solo los canales con estimación, ordenados de mejor a peor. */
const canales = computed(() =>
  CANALES.filter((c) => props.probPorCanal[c] !== undefined)
    .map((c) => ({ canal: c, prob: props.probPorCanal[c]! }))
    .sort((a, b) => b.prob - a.prob),
)

const probMejor = computed(() =>
  props.mejorCanal ? (props.probPorCanal[props.mejorCanal] ?? null) : null,
)

/** Cuánto se pierde por atender fuera del canal recomendado. */
const caida = computed(() => {
  if (!props.seleccionado || !props.mejorCanal || props.seleccionado === props.mejorCanal) return 0
  const actual = props.probPorCanal[props.seleccionado]
  if (actual === undefined || probMejor.value === null) return 0
  return probMejor.value - actual
})
</script>

<template>
  <section v-if="canales.length" class="selector tarjeta-suelta">
    <header class="cabecera">
      <span class="micro">Probabilidad por canal</span>
      <span v-if="mejorCanal" class="micro mejor">
        Mejor: {{ ETIQUETA_CANAL[mejorCanal] }} · {{ probMejor }}%
      </span>
    </header>

    <div class="botones" role="group" aria-label="Canal de atención">
      <button
        v-for="c in canales"
        :key="c.canal"
        type="button"
        class="canal"
        :class="{ activo: seleccionado === c.canal, recomendado: c.canal === mejorCanal }"
        :aria-pressed="seleccionado === c.canal"
        :disabled="bloqueado"
        @click="emit('seleccionar', c.canal)"
      >
        <span class="micro nombre">{{ ETIQUETA_CANAL[c.canal] }}</span>
        <span class="cifra prob">{{ c.prob }}%</span>
        <span v-if="c.canal === mejorCanal" class="estrella" aria-hidden="true">●</span>
      </button>
    </div>

    <p v-if="bloqueado" class="nota">Canal registrado al abrir la gestión.</p>
    <p v-else-if="caida > 0" class="aviso">
      Por este canal pierde <span class="cifra">{{ caida }}</span> puntos frente a
      {{ mejorCanal ? ETIQUETA_CANAL[mejorCanal] : '' }}.
    </p>
  </section>
</template>

<style scoped>
.selector {
  padding: var(--gap) var(--gap-lg);
}

.cabecera {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gap-sm);
  margin-bottom: 6px;
}

.mejor {
  color: var(--verde);
  letter-spacing: 0.06em;
}

.botones {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 5px;
}

.canal {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 7px 2px 6px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  transition: border-color 140ms ease, background-color 140ms ease;
}

.nombre {
  color: inherit;
  white-space: nowrap;
}

.prob {
  font-size: var(--t-md);
  font-weight: 600;
  line-height: 1;
  color: var(--tinta);
}

/* El recomendado se distingue aunque el asesor esté mirando otro. */
.recomendado {
  border-color: var(--verde);
}

.recomendado .prob {
  color: var(--verde);
}

.estrella {
  position: absolute;
  top: 3px;
  right: 4px;
  font-size: 7px;
  color: var(--verde);
}

.activo {
  border-width: 2px;
  border-color: var(--movistar-noche);
  background: var(--superficie-tenue);
}

.activo:not(.recomendado) .prob {
  color: var(--movistar-noche);
}

.canal:disabled {
  cursor: default;
}

.canal:disabled:not(.activo):not(.recomendado) {
  opacity: 0.55;
}

.aviso {
  margin-top: 7px;
  font-size: var(--t-xs);
  color: var(--ambar);
}

.nota {
  margin-top: 7px;
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}
</style>
