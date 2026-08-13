<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ valorInicial?: string; cargando?: boolean }>()
const emit = defineEmits<{ buscar: [dni: string] }>()

const dni = ref(props.valorInicial ?? '')

watch(
  () => props.valorInicial,
  (nuevo) => {
    if (nuevo) dni.value = nuevo
  },
)

function enviar() {
  const limpio = dni.value.trim()
  if (limpio) emit('buscar', limpio)
}
</script>

<template>
  <form class="buscador" role="search" @submit.prevent="enviar">
    <label class="sr-solo" for="dni">DNI del cliente</label>
    <input
      id="dni"
      v-model="dni"
      class="cifra campo"
      type="text"
      inputmode="numeric"
      autocomplete="off"
      maxlength="12"
      placeholder="DNI del cliente"
    />
    <button class="micro boton" type="submit" :disabled="cargando">
      {{ cargando ? 'Buscando' : 'Buscar' }}
    </button>
  </form>
</template>

<style scoped>
.buscador {
  display: flex;
  align-items: stretch;
  border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: var(--r);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.06);
}

.campo {
  width: 190px;
  padding: 6px 10px;
  border: 0;
  background: transparent;
  color: var(--tinta-inversa);
  font-size: var(--t-sm);
  letter-spacing: 0.06em;
}

.campo::placeholder {
  color: rgba(255, 255, 255, 0.45);
  font-family: var(--fuente-cuerpo);
  letter-spacing: 0;
}

.campo:focus {
  outline: none;
}

.buscador:focus-within {
  border-color: var(--movistar-azul);
}

.boton {
  padding: 0 14px;
  border: 0;
  border-left: 1px solid rgba(255, 255, 255, 0.24);
  background: var(--movistar-azul);
  color: var(--tinta-inversa);
}

.boton:disabled {
  opacity: 0.6;
  cursor: progress;
}
</style>
