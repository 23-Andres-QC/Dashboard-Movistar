<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ temperatura: number; estado: string }>()

const color = computed(() =>
  props.temperatura >= 65
    ? 'var(--verde)'
    : props.temperatura >= 40
      ? 'var(--movistar-azul)'
      : 'var(--alarma)',
)
</script>

<template>
  <div class="termometro">
    <div class="cabecera">
      <span class="micro">Receptividad</span>
      <span class="estado">{{ estado }}</span>
      <span class="cifra grados" :style="{ color }">{{ temperatura }}°</span>
    </div>
    <div
      class="riel"
      role="meter"
      :aria-valuenow="temperatura"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`Receptividad ${temperatura} de 100`"
    >
      <div class="mercurio" :style="{ width: `${temperatura}%`, background: color }"></div>
    </div>
  </div>
</template>

<style scoped>
.termometro {
  padding: 8px var(--gap) 10px;
  border-bottom: 1px solid var(--linea);
}

.cabecera {
  display: flex;
  align-items: baseline;
  gap: var(--gap-sm);
  margin-bottom: 5px;
}

.estado {
  font-size: var(--t-xs);
  color: var(--tinta-media);
  margin-left: auto;
}

.grados {
  font-size: var(--t-sm);
  font-weight: 600;
}

.riel {
  height: 5px;
  background: var(--gris-canvas);
  border-radius: 3px;
  overflow: hidden;
}

.mercurio {
  height: 100%;
  transition: width 260ms ease, background-color 260ms ease;
}
</style>
