<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Angulo } from '@/api/tipos'

defineProps<{ angulos: Angulo[] }>()
</script>

<template>
  <section v-if="angulos.length" class="bloque tarjeta-suelta">
    <TituloPanel texto="Ángulos de convencimiento" acento="azul" :contador="angulos.length" />
    <ul>
      <li v-for="(angulo, i) in angulos" :key="angulo.titulo" class="angulo">
        <span class="cifra orden" aria-hidden="true">{{ i + 1 }}</span>
        <div class="cuerpo">
          <span class="micro titulo">{{ angulo.titulo }}</span>
          <p class="texto">{{ angulo.texto }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.bloque {
  overflow: hidden;
}

.angulo {
  display: flex;
  gap: var(--gap);
  padding: 11px var(--gap-lg);
  border-bottom: 1px solid var(--superficie-tenue);
}

.angulo:last-child {
  border-bottom: 0;
}

.orden {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  flex: none;
  margin-top: 1px;
  border: 1px solid var(--linea);
  border-radius: 50%;
  font-size: 10.5px;
  color: var(--tinta-suave);
}

.cuerpo {
  min-width: 0;
}

.titulo {
  color: var(--movistar-noche);
}

.texto {
  margin-top: 2px;
  font-size: var(--t-base);
  color: var(--tinta);
  line-height: 1.45;
}
</style>
