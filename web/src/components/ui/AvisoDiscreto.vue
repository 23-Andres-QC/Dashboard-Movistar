<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'

const props = withDefaults(defineProps<{ texto: string; ms?: number }>(), { ms: 4000 })
const emit = defineEmits<{ cerrar: [] }>()

let temporizador: number | undefined

onMounted(() => {
  temporizador = window.setTimeout(() => emit('cerrar'), props.ms)
})

onBeforeUnmount(() => clearTimeout(temporizador))
</script>

<template>
  <div class="aviso" role="status" aria-live="polite">
    <span class="punto" aria-hidden="true"></span>
    <span class="texto">{{ texto }}</span>
    <button class="cerrar" type="button" aria-label="Cerrar aviso" @click="emit('cerrar')">
      ×
    </button>
  </div>
</template>

<style scoped>
.aviso {
  position: fixed;
  right: var(--gap-lg);
  bottom: var(--gap-lg);
  z-index: 60;
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 8px 10px 8px 12px;
  border: 1px solid var(--linea);
  border-left: 3px solid var(--verde);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
}

.punto {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--verde);
}

.texto {
  color: var(--tinta);
}

.cerrar {
  border: 0;
  background: none;
  color: var(--tinta-suave);
  font-size: 15px;
  line-height: 1;
  padding: 0 2px;
}
</style>
