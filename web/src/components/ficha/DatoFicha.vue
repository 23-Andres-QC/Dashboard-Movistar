<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  etiqueta: string
  /** null se dibuja como raya: un 0 se leería como dato real y sería falso. */
  valor: string | number | null
  tono?: 'normal' | 'alerta' | 'ok'
  destacado?: boolean
}>()

// La raya también llega como texto desde los datos: se trata igual que un nulo.
const vacio = computed(
  () => props.valor === null || props.valor === undefined || props.valor === '—',
)
</script>

<template>
  <div class="dato" :class="{ destacado }">
    <span class="micro">{{ etiqueta }}</span>
    <span class="cifra valor" :class="[vacio ? 'vacio' : (tono ?? 'normal')]">
      {{ vacio ? '—' : valor }}
    </span>
  </div>
</template>

<style scoped>
.dato {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 0 var(--gap-lg);
  border-left: 1px solid var(--linea);
  white-space: nowrap;
}

.dato:first-child {
  border-left: 0;
  padding-left: 0;
}

.valor {
  font-size: var(--t-md);
  line-height: 1.25;
}

.alerta {
  color: var(--alarma);
}

.ok {
  color: var(--verde);
}

.vacio {
  color: var(--tinta-suave);
}

/* Realce breve cuando el campo se llena con un dato revelado en la llamada. */
.destacado {
  animation: capturado 900ms ease-out;
}

@keyframes capturado {
  0%,
  35% {
    background: var(--movistar-cielo);
  }
  100% {
    background: transparent;
  }
}

@media (prefers-reduced-motion: reduce) {
  .destacado {
    animation: none;
    background: var(--movistar-cielo);
  }
}

@media (max-width: 768px) {
  .dato {
    padding: 0 var(--gap);
  }
}
</style>
