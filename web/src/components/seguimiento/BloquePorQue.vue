<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'

defineProps<{ explicacion: string[]; probChurn: number | null }>()
</script>

<template>
  <section class="bloque">
    <TituloPanel texto="Por qué esta oferta" acento="ninguno" />
    <ul class="razones">
      <li v-for="razon in explicacion" :key="razon" class="razon">
        <span class="vineta" aria-hidden="true"></span>
        <span>{{ razon }}</span>
      </li>
    </ul>
    <p class="nota">
      Riesgo de baja estimado
      <span class="cifra">{{ probChurn === null ? '—' : `${Math.round(probChurn * 100)}%` }}</span>
      <span v-if="probChurn === null" class="sin-dato">sin historial</span>
    </p>
  </section>
</template>

<style scoped>
.bloque {
  border-top: 1px solid var(--linea);
}

.razones {
  padding: var(--gap-sm) var(--gap) 0;
}

.razon {
  display: flex;
  gap: var(--gap-sm);
  padding: 3px 0;
  font-size: var(--t-sm);
  color: var(--tinta-media);
  line-height: 1.4;
}

.vineta {
  width: 4px;
  height: 4px;
  margin-top: 7px;
  flex: none;
  border-radius: 50%;
  background: var(--movistar-azul);
}

.nota {
  padding: var(--gap-sm) var(--gap) var(--gap);
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}

.sin-dato {
  margin-left: 4px;
  font-style: italic;
}
</style>
