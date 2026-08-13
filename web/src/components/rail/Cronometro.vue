<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps<{ inicio: number | null; detenido?: boolean }>()

const ahora = ref(Date.now())
let temporizador: number | undefined

function detener() {
  if (temporizador !== undefined) {
    clearInterval(temporizador)
    temporizador = undefined
  }
}

watch(
  () => [props.inicio, props.detenido] as const,
  ([inicio, detenidoAhora]) => {
    detener()
    if (inicio === null || detenidoAhora) return
    ahora.value = Date.now()
    temporizador = window.setInterval(() => (ahora.value = Date.now()), 1000)
  },
  { immediate: true },
)

onBeforeUnmount(detener)

const transcurrido = computed(() => {
  if (props.inicio === null) return '00:00'
  const segundos = Math.max(0, Math.floor((ahora.value - props.inicio) / 1000))
  const mm = String(Math.floor(segundos / 60)).padStart(2, '0')
  const ss = String(segundos % 60).padStart(2, '0')
  return `${mm}:${ss}`
})

/** Menos de un minuto por llamada: pasado ese punto la cifra se marca. */
const excedido = computed(
  () => props.inicio !== null && ahora.value - props.inicio > 60_000,
)
</script>

<template>
  <div class="cronometro" :class="{ excedido }">
    <span class="micro etiqueta">Llamada</span>
    <time class="cifra valor">{{ transcurrido }}</time>
  </div>
</template>

<style scoped>
.cronometro {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
}

.etiqueta {
  color: rgba(255, 255, 255, 0.5);
}

.valor {
  font-size: var(--t-md);
  color: var(--tinta-inversa);
}

.excedido .valor {
  color: #ff9a90;
}
</style>
