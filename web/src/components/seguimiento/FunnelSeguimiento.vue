<script setup lang="ts">
import { computed } from 'vue'

import TituloPanel from '@/components/ui/TituloPanel.vue'
import { ETIQUETA_RESULTADO } from '@/api/etiquetas'
import { PASOS_FUNNEL } from '@/stores/gestion'
import type { Resultado } from '@/api/tipos'

const props = defineProps<{
  paso: number
  resultado: Resultado | null
  hora: string | null
}>()

/** El último paso toma el nombre del desenlace una vez registrado. */
const nombres = computed(() =>
  PASOS_FUNNEL.map((nombre, i) =>
    i === PASOS_FUNNEL.length - 1 && props.resultado
      ? `${nombre} · ${ETIQUETA_RESULTADO[props.resultado]}`
      : nombre,
  ),
)
</script>

<template>
  <section class="bloque">
    <TituloPanel
      texto="Seguimiento"
      acento="verde"
      :contador="`${Math.min(paso, PASOS_FUNNEL.length)}/${PASOS_FUNNEL.length}`"
    />
    <ol class="funnel">
      <li
        v-for="(nombre, i) in nombres"
        :key="i"
        class="paso"
        :class="{
          hecho: paso > i + 1,
          actual: paso === i + 1,
          final: i === nombres.length - 1 && !!resultado,
          [resultado ?? '']: i === nombres.length - 1 && !!resultado,
        }"
      >
        <span class="marca" aria-hidden="true">
          <span class="cifra numero">{{ i + 1 }}</span>
        </span>
        <span class="nombre">{{ nombre }}</span>
        <span v-if="i === nombres.length - 1 && hora" class="cifra hora">{{ hora }}</span>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.bloque {
  border-bottom: 1px solid var(--linea);
}

.funnel {
  padding: var(--gap-sm) var(--gap) var(--gap);
}

.paso {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 5px 0;
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}

/* Hilo vertical que une los pasos. */
.paso:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 9px;
  top: 24px;
  width: 1px;
  height: calc(100% - 14px);
  background: var(--linea);
}

.paso.hecho:not(:last-child)::before {
  background: var(--verde);
}

.marca {
  display: grid;
  place-items: center;
  width: 19px;
  height: 19px;
  flex: none;
  border: 1px solid var(--linea);
  border-radius: 50%;
  background: var(--superficie);
  z-index: 1;
}

.numero {
  font-size: 9.5px;
  color: var(--tinta-suave);
}

.hecho {
  color: var(--tinta-media);
}

.hecho .marca {
  border-color: var(--verde);
  background: var(--verde);
}

.hecho .numero {
  color: var(--tinta-inversa);
}

.actual {
  color: var(--tinta);
  font-weight: 600;
}

.actual .marca {
  border-color: var(--movistar-azul);
  border-width: 2px;
}

.actual .numero {
  color: var(--movistar-azul);
}

.hora {
  margin-left: auto;
  font-size: var(--t-micro);
  color: var(--tinta-suave);
}

/* El desenlace tiñe el último paso: vendido en verde, rechazo en rojo. */
.final.vendido {
  color: var(--verde);
}

.final.rechazado {
  color: var(--alarma);
}

.final.rechazado .marca,
.final.sin_contacto .marca {
  border-color: currentColor;
  background: var(--superficie);
}

.final.rechazado .numero,
.final.sin_contacto .numero {
  color: currentColor;
}
</style>
