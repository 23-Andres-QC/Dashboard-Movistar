<script setup lang="ts">
defineProps<{ quien: 'cliente' | 'asesor'; texto: string; etiqueta?: string }>()
</script>

<template>
  <li class="fila" :class="quien">
    <div class="burbuja">
      <span v-if="etiqueta" class="micro etiqueta">{{ etiqueta }}</span>
      <p class="texto">{{ texto }}</p>
    </div>
  </li>
</template>

<style scoped>
.fila {
  display: flex;
  margin-bottom: var(--gap-sm);
}

.cliente {
  justify-content: flex-start;
}

.asesor {
  justify-content: flex-end;
}

.burbuja {
  max-width: 82%;
  padding: 8px 11px;
  border-radius: var(--r);
  font-size: var(--t-base);
  line-height: 1.45;
}

.cliente .burbuja {
  background: var(--gris-canvas);
  border: 1px solid var(--linea);
  border-top-left-radius: 2px;
}

.asesor .burbuja {
  background: var(--movistar-azul);
  border: 1px solid var(--movistar-azul);
  color: var(--tinta-inversa);
  border-top-right-radius: 2px;
}

.etiqueta {
  display: block;
  margin-bottom: 2px;
  color: var(--tinta-suave);
}

.asesor .etiqueta {
  color: rgba(255, 255, 255, 0.7);
}

.texto {
  margin: 0;
}
</style>
