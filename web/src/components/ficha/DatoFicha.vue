<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  etiqueta: string
  /** null se dibuja como raya: un 0 se leería como dato real y sería falso. */
  valor: string | number | null
  tono?: 'normal' | 'alerta' | 'ok' | 'aviso'
  /** 0–100: dibuja una barra bajo la cifra. */
  barra?: number | null
  destacado?: boolean
}>()

// La raya también llega como texto desde los datos: se trata igual que un nulo.
const vacio = computed(
  () => props.valor === null || props.valor === undefined || props.valor === '—',
)

const tono = computed(() => (vacio.value ? 'vacio' : (props.tono ?? 'normal')))
</script>

<template>
  <div class="tarjeta" :class="[tono, { destacado }]">
    <span class="micro etiqueta">{{ etiqueta }}</span>
    <span class="cifra valor">{{ vacio ? '—' : valor }}</span>
    <span v-if="!vacio && barra != null" class="riel" aria-hidden="true">
      <span class="relleno" :style="{ width: `${Math.min(100, Math.max(0, barra))}%` }"></span>
    </span>
  </div>
</template>

<style scoped>
.tarjeta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 84px;
  padding: 7px 11px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  white-space: nowrap;
}

.etiqueta {
  color: var(--tinta-suave);
}

.valor {
  font-size: var(--t-md);
  font-weight: 600;
  line-height: 1.2;
  color: var(--tinta);
}

.riel {
  height: 3px;
  margin-top: 3px;
  border-radius: 2px;
  background: var(--gris-canvas);
  overflow: hidden;
}

.relleno {
  display: block;
  height: 100%;
  background: currentColor;
}

/* El color solo aparece cuando el dato pide una decisión. */
.alerta {
  border-color: var(--alarma);
  background: var(--risk-fondo);
  color: var(--alarma);
}
.alerta .valor,
.alerta .etiqueta {
  color: var(--alarma);
}

.aviso {
  border-color: var(--ambar);
  background: var(--warn-fondo);
  color: var(--ambar);
}
.aviso .valor,
.aviso .etiqueta {
  color: var(--ambar);
}

.ok {
  border-color: var(--verde);
  color: var(--verde);
}
.ok .valor {
  color: var(--verde);
}

.vacio {
  background: var(--superficie-tenue);
}
.vacio .valor {
  color: var(--tinta-suave);
}

/* Realce breve cuando el campo se llena con un dato revelado en la llamada. */
.destacado {
  animation: capturado 900ms ease-out;
}

@keyframes capturado {
  0%,
  35% {
    border-color: var(--movistar-azul);
    background: var(--movistar-cielo);
  }
}

@media (prefers-reduced-motion: reduce) {
  .destacado {
    animation: none;
    border-color: var(--movistar-azul);
    background: var(--movistar-cielo);
  }
}
</style>
