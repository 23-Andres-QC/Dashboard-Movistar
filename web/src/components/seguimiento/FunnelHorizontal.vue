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

/** El último paso toma el nombre del desenlace una vez registrado. */
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
        v-for="paso_ in pasos"
        :key="paso_.numero"
        class="paso"
        :class="{ hecho: paso_.hecho, actual: paso_.actual, desenlace: paso_.final && !!resultado }"
      >
        <span class="marca" aria-hidden="true">
          <span v-if="paso_.hecho" class="tilde">✓</span>
          <span v-else class="cifra">{{ paso_.numero }}</span>
        </span>
        <span class="nombre">{{ paso_.nombre }}</span>
        <span v-if="paso_.final && hora" class="cifra hora">{{ hora }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.funnel {
  padding: 10px var(--gap-lg);
  background: var(--superficie);
  border-bottom: 1px solid var(--linea);
}

ol {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--gap-sm);
}

.paso {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  min-width: 0;
}

/* Hilo que une los pasos; se tiñe cuando el tramo ya se recorrió. */
.paso:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 26px;
  right: -8px;
  top: 12px;
  height: 2px;
  background: var(--linea);
  z-index: 0;
}

.paso.hecho:not(:last-child)::after {
  background: var(--verde);
}

.marca {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  flex: none;
  border: 2px solid var(--linea);
  border-radius: 50%;
  background: var(--superficie);
  font-size: 11px;
  color: var(--tinta-suave);
}

.hecho .marca {
  border-color: var(--verde);
  background: var(--verde);
  color: var(--tinta-inversa);
}

.tilde {
  font-size: 13px;
  line-height: 1;
}

.actual .marca {
  border-color: var(--movistar-azul);
  color: var(--movistar-azul);
}

.nombre {
  font-family: var(--fuente-micro);
  font-size: var(--t-xs);
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--tinta-suave);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* El desenlace tiñe el último paso. */
.desenlace .nombre {
  color: var(--verde);
}

.rechazado .desenlace .marca,
.sin_contacto .desenlace .marca {
  border-color: var(--alarma);
  background: var(--alarma);
}

.rechazado .desenlace .nombre,
.sin_contacto .desenlace .nombre {
  color: var(--alarma);
}

.sin_contacto .desenlace .marca {
  border-color: var(--tinta-media);
  background: var(--tinta-media);
}

.sin_contacto .desenlace .nombre {
  color: var(--tinta-media);
}

@media (max-width: 900px) {
  ol {
    grid-template-columns: repeat(5, auto);
    overflow-x: auto;
  }

  .nombre {
    display: none;
  }

  .paso:not(:last-child)::after {
    right: -8px;
    left: 26px;
  }
}
</style>
