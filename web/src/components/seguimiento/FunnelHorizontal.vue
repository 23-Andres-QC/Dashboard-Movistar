<script setup lang="ts">
import { computed } from 'vue'

import { ETIQUETA_RESULTADO } from '@/api/etiquetas'
import { PASOS_FUNNEL } from '@/stores/gestion'
import type { Resultado } from '@/api/tipos'

const props = defineProps<{
  paso: number
  resultado: Resultado | null
  hora: string | null
}>()

const pasos = computed(() =>
  PASOS_FUNNEL.map((nombre, i) => ({
    numero: i + 1,
    nombre:
      i === PASOS_FUNNEL.length - 1 && props.resultado
        ? ETIQUETA_RESULTADO[props.resultado]
        : nombre,
    hecho: props.paso > i + 1,
    actual: props.paso === i + 1,
    final: i === PASOS_FUNNEL.length - 1,
  })),
)

const tono = computed(() => props.resultado ?? '')
</script>

<template>
  <nav class="funnel" :class="tono" aria-label="Seguimiento del ofrecimiento">
    <ol>
      <li
        v-for="p in pasos"
        :key="p.numero"
        class="paso"
        :class="{ hecho: p.hecho, actual: p.actual, desenlace: p.final && !!resultado }"
      >
        <!-- Los conectores viven en su propia fila: nunca cruzan el texto. -->
        <span class="rieles" aria-hidden="true">
          <span class="riel izq"></span>
          <span class="marca">
            <span v-if="p.hecho" class="tilde">✓</span>
            <span v-else class="cifra">{{ p.numero }}</span>
          </span>
          <span class="riel der"></span>
        </span>
        <span class="nombre">{{ p.nombre }}</span>
        <span v-if="p.final && hora" class="cifra hora">{{ hora }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.funnel {
  padding: 12px var(--gap-lg) 10px;
  background: var(--superficie);
  border-bottom: 1px solid var(--linea);
}

ol {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}

.paso {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  min-width: 0;
}

.rieles {
  display: flex;
  align-items: center;
  width: 100%;
}

.riel {
  flex: 1;
  height: 3px;
  border-radius: 2px;
  background: var(--linea);
}

.paso:first-child .izq,
.paso:last-child .der {
  visibility: hidden;
}

/* El tramo de entrada se tiñe cuando el paso ya se alcanzó. */
.hecho .izq,
.hecho .der,
.actual .izq {
  background: var(--verde);
}

.marca {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex: none;
  margin: 0 6px;
  border: 2px solid var(--linea);
  border-radius: 50%;
  background: var(--superficie);
  font-size: 12px;
  color: var(--tinta-suave);
  transition: background-color 200ms ease, border-color 200ms ease;
}

.hecho .marca {
  border-color: var(--verde);
  background: var(--verde);
  color: var(--tinta-inversa);
}

.tilde {
  font-size: 15px;
  line-height: 1;
}

.actual .marca {
  border-color: var(--movistar-azul);
  background: var(--movistar-cielo);
  color: var(--movistar-azul);
  box-shadow: 0 0 0 4px var(--movistar-cielo);
}

.nombre {
  font-family: var(--fuente-micro);
  font-size: var(--t-xs);
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--tinta-suave);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.hecho .nombre {
  color: var(--tinta-media);
}

.actual .nombre {
  color: var(--movistar-noche);
}

.hora {
  font-size: var(--t-micro);
  color: var(--tinta-suave);
}

.desenlace .nombre {
  color: var(--verde);
}

.rechazado .desenlace .marca {
  border-color: var(--alarma);
  background: var(--alarma);
  color: var(--tinta-inversa);
}
.rechazado .desenlace .nombre {
  color: var(--alarma);
}

.sin_contacto .desenlace .marca {
  border-color: var(--tinta-media);
  background: var(--tinta-media);
  color: var(--tinta-inversa);
}
.sin_contacto .desenlace .nombre {
  color: var(--tinta-media);
}

@media (max-width: 760px) {
  .nombre {
    display: none;
  }
}
</style>
