<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ habilitada: boolean; pensando: boolean }>()
const emit = defineEmits<{ enviar: [texto: string] }>()

const texto = ref('')

function enviar() {
  const limpio = texto.value.trim()
  if (!limpio) return
  emit('enviar', limpio)
  texto.value = ''
}
</script>

<template>
  <form class="entrada" @submit.prevent="enviar">
    <label class="sr-solo" for="dijo-cliente">Escriba lo que dijo el cliente</label>
    <input
      id="dijo-cliente"
      v-model="texto"
      type="text"
      autocomplete="off"
      :disabled="!habilitada || pensando"
      :placeholder="
        habilitada ? 'Escriba lo que dijo el cliente…' : 'Inicie la gestión para escribir'
      "
    />
    <button type="submit" class="micro" :disabled="!habilitada || pensando || !texto.trim()">
      {{ pensando ? 'Consultando' : 'Consultar' }}
    </button>
  </form>
</template>

<style scoped>
.entrada {
  display: flex;
  gap: var(--gap-sm);
  padding: var(--gap-sm) var(--gap);
  border-top: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

input {
  flex: 1;
  min-width: 0;
  padding: 8px 11px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-base);
}

input:disabled {
  background: var(--superficie-tenue);
  color: var(--tinta-suave);
}

button {
  padding: 0 16px;
  border: 1px solid var(--movistar-noche);
  border-radius: var(--r);
  background: var(--movistar-noche);
  color: var(--tinta-inversa);
  white-space: nowrap;
}

button:disabled {
  border-color: var(--linea);
  background: var(--superficie);
  color: var(--tinta-suave);
  cursor: not-allowed;
}
</style>
