<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ valor: number; margen?: number; tamano?: number; etiqueta?: string }>(),
  { margen: 0, tamano: 104, etiqueta: '' },
)

const RADIO = 44
const GROSOR = 11
const CIRCUNFERENCIA = 2 * Math.PI * RADIO

const acotado = computed(() => Math.min(100, Math.max(0, props.valor)))

/** El arco se llena sobre una escala fija 0–100. */
const relleno = computed(() => (acotado.value / 100) * CIRCUNFERENCIA)

/** Tramo de incertidumbre: hasta dónde podría llegar el estimado. */
const arcoMargen = computed(() =>
  Math.min(100 - acotado.value, props.margen) / 100 * CIRCUNFERENCIA,
)

const color = computed(() =>
  acotado.value >= 75
    ? 'var(--verde)'
    : acotado.value >= 65
      ? 'var(--movistar-azul)'
      : 'var(--alarma)',
)
</script>

<template>
  <figure
    class="anillo"
    :style="{ width: `${tamano}px`, height: `${tamano}px` }"
    role="img"
    :aria-label="`Probabilidad de aceptación ${valor} por ciento`"
  >
    <svg viewBox="0 0 110 110">
      <!-- Riel -->
      <circle cx="55" cy="55" :r="RADIO" fill="none" stroke="var(--linea)" :stroke-width="GROSOR" />

      <!-- Margen de incertidumbre, a continuación del relleno -->
      <circle
        v-if="arcoMargen > 0"
        cx="55"
        cy="55"
        :r="RADIO"
        fill="none"
        :stroke="color"
        :stroke-width="GROSOR"
        opacity="0.3"
        :stroke-dasharray="`${arcoMargen} ${CIRCUNFERENCIA}`"
        :stroke-dashoffset="-relleno"
        transform="rotate(-90 55 55)"
      />

      <!-- Valor -->
      <circle
        cx="55"
        cy="55"
        :r="RADIO"
        fill="none"
        :stroke="color"
        :stroke-width="GROSOR"
        stroke-linecap="round"
        :stroke-dasharray="`${relleno} ${CIRCUNFERENCIA}`"
        transform="rotate(-90 55 55)"
        class="arco"
      />

      <text x="55" y="58" class="cifra numero" :fill="color">{{ acotado }}</text>
      <text x="55" y="73" class="pct">%</text>
    </svg>
    <figcaption v-if="etiqueta || margen > 0" class="micro pie">
      <span v-if="margen > 0" class="cifra">±{{ margen }}</span>
      <span v-else>{{ etiqueta }}</span>
    </figcaption>
  </figure>
</template>

<style scoped>
.anillo {
  position: relative;
  flex: none;
}

svg {
  width: 100%;
  height: 100%;
  display: block;
}

.arco {
  transition: stroke-dasharray 420ms ease, stroke 260ms ease;
}

.numero {
  font-size: 32px;
  font-weight: 700;
  text-anchor: middle;
}

.pct {
  font-size: 11px;
  text-anchor: middle;
  fill: var(--tinta-suave);
  font-family: var(--fuente-micro);
  letter-spacing: 0.1em;
}

.pie {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -2px;
  text-align: center;
  color: var(--tinta-suave);
}

@media (prefers-reduced-motion: reduce) {
  .arco {
    transition: none;
  }
}
</style>
