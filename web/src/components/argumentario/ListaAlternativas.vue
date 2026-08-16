<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Recomendacion } from '@/api/tipos'

defineProps<{
  alternativas: Recomendacion[]
  descartadas: Recomendacion[]
  alternativaActiva: Recomendacion | null
}>()
defineEmits<{ seleccionar: [oferta: Recomendacion]; volver: [] }>()
</script>

<template>
  <section v-if="alternativas.length || descartadas.length" class="bloque tarjeta-suelta">
    <TituloPanel
      texto="Alternativas"
      acento="ninguno"
      :contador="alternativas.length + descartadas.length"
    />
    <button v-if="alternativaActiva" class="volver" type="button" @click="$emit('volver')">
      ← Mejor plan
    </button>
    <ul>
      <button v-for="alt in alternativas" :key="alt.oferta" class="fila seleccionable" type="button" @click="$emit('seleccionar', alt)">
        <span class="nombre" :title="alt.oferta">{{ alt.oferta }}</span>
        <span class="barra" aria-hidden="true">
          <span class="relleno" :style="{ width: `${alt.probabilidad}%` }"></span>
        </span>
        <span class="cifra pct">{{ alt.probabilidad }}%</span>
        <p v-if="alt.nota" class="nota">{{ alt.nota }}</p>
      </button>

      <!-- Descartadas al final: mostrar por qué el motor NO recomendó algo
           vale tanto como mostrar por qué sí. -->
      <li v-for="alt in descartadas" :key="alt.oferta" class="fila descartada">
        <span class="nombre tachado" :title="alt.oferta">{{ alt.oferta }}</span>
        <span class="barra" aria-hidden="true">
          <span class="relleno" :style="{ width: `${alt.probabilidad}%` }"></span>
        </span>
        <span class="cifra pct">{{ alt.probabilidad }}%</span>
        <p class="motivo">{{ alt.descartada }}</p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.bloque {
  overflow: hidden;
}

.volver {
  width: calc(100% - 24px);
  margin: 8px 12px 0;
  padding: 7px 10px;
  border: 1px solid var(--movistar-azul);
  border-radius: var(--r-chico);
  background: var(--info-fondo);
  color: var(--movistar-azul-hondo);
  font-size: var(--t-xs);
  font-weight: 700;
  text-align: left;
}

.fila {
  display: grid;
  grid-template-columns: 1fr 56px 38px;
  align-items: center;
  gap: var(--gap-sm);
  padding: 8px var(--gap-lg);
  border-bottom: 1px solid var(--superficie-tenue);
  font-size: var(--t-sm);
}

.seleccionable {
  width: 100%;
  border: 0;
  border-bottom: 1px solid var(--superficie-tenue);
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.seleccionable:hover {
  background: var(--info-fondo);
}

.fila:last-child {
  border-bottom: 0;
}

.nombre {
  color: var(--tinta-media);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.barra {
  height: 4px;
  background: var(--gris-canvas);
  border-radius: 2px;
  overflow: hidden;
}

.relleno {
  display: block;
  height: 100%;
  background: var(--tinta-suave);
}

.pct {
  font-size: var(--t-xs);
  text-align: right;
  color: var(--tinta-media);
}

.nota,
.motivo {
  grid-column: 1 / -1;
  margin-top: 2px;
  font-size: var(--t-micro);
  line-height: 1.35;
  color: var(--tinta-suave);
}

.descartada {
  background: var(--superficie-tenue);
}

.descartada .nombre,
.descartada .pct {
  color: var(--tinta-suave);
}

.tachado {
  text-decoration: line-through;
}

.descartada .relleno {
  background: var(--linea);
}

.motivo {
  color: var(--tinta-media);
}
</style>
