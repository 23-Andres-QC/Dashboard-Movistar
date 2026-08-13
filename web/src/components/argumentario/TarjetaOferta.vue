<script setup lang="ts">
import { computed } from 'vue'

import { ETIQUETA_CANAL } from '@/api/etiquetas'
import type { Canal, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  oferta: Recomendacion
  /** Probabilidad del canal que el asesor está mirando. */
  probabilidad: number
  canalActivo: Canal | null
}>()

const canal = computed(() => (props.canalActivo ? ETIQUETA_CANAL[props.canalActivo] : null))

const esOtroCanal = computed(
  () => props.canalActivo !== null && props.canalActivo !== props.oferta.canal_sugerido,
)

/** La escala es fija 0–100: la barra se llena, no se reescala. */
const relleno = computed(() => Math.min(100, Math.max(0, props.probabilidad)))
const anchoMargen = computed(() => Math.min(100 - relleno.value, props.oferta.margen))
</script>

<template>
  <article class="tarjeta">
    <header class="cabecera">
      <span class="micro rango">Oferta recomendada</span>
      <span class="micro sello" :class="oferta.confianza">Confianza {{ oferta.confianza }}</span>
    </header>

    <h2 class="nombre">{{ oferta.oferta }}</h2>

    <div class="tasa">
      <div class="lectura">
        <span class="cifra prob">{{ probabilidad }}<span class="pct">%</span></span>
        <span v-if="oferta.margen > 0" class="cifra margen">±{{ oferta.margen }}</span>
        <span class="micro leyenda">
          Probabilidad de aceptación<template v-if="canal"> · {{ canal }}</template>
        </span>
      </div>

      <div
        class="riel"
        role="meter"
        :aria-valuenow="oferta.probabilidad"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-label="`Probabilidad de aceptación ${oferta.probabilidad} de 100`"
      >
        <span class="lleno" :style="{ width: `${relleno}%` }"></span>
        <span
          v-if="anchoMargen > 0"
          class="incierto"
          :style="{ left: `${relleno}%`, width: `${anchoMargen}%` }"
        ></span>
      </div>

      <p class="micro procedencia">
        {{ oferta.origen === 'lookalike' ? 'Clientes similares' : 'Historial propio' }}
        <span v-if="oferta.margen > 0">· el tramo claro es el margen</span>
      </p>
    </div>

    <dl v-if="oferta.ahorro != null || oferta.instalacion != null" class="cifras">
      <div v-if="oferta.ahorro != null" class="celda">
        <dt class="micro">Ahorro / mes</dt>
        <dd class="cifra monto">S/ {{ oferta.ahorro }}</dd>
      </div>
      <div v-if="oferta.instalacion != null" class="celda">
        <dt class="micro">Instalación</dt>
        <dd class="cifra monto neutro">S/ {{ oferta.instalacion }}</dd>
      </div>
    </dl>

    <p v-if="oferta.franja_sugerida" class="contacto">
      <span class="micro chip" :class="{ alterno: esOtroCanal }">
        {{ esOtroCanal ? 'Fuera del canal recomendado' : 'Canal recomendado' }}
      </span>
      <span>{{ oferta.franja_sugerida }}</span>
    </p>
  </article>
</template>

<style scoped>
.tarjeta {
  padding: var(--gap) var(--gap-lg) var(--gap-lg);
  border-bottom: 1px solid var(--linea);
  border-left: 3px solid var(--movistar-azul);
  background: var(--movistar-cielo);
}

.cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--gap-sm);
}

.rango {
  color: var(--movistar-noche);
}

.sello {
  padding: 2px 7px;
  border: 1px solid var(--linea);
  border-radius: 3px;
  background: var(--superficie);
  color: var(--tinta-media);
}

.sello.alta {
  border-color: var(--verde);
  color: var(--verde);
}

.sello.baja {
  border-color: var(--ambar);
  color: var(--ambar);
}

.nombre {
  margin-top: 6px;
  font-size: var(--t-lg);
  font-weight: 600;
  line-height: 1.25;
  color: var(--movistar-noche);
}

.tasa {
  margin-top: var(--gap);
}

.lectura {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.prob {
  font-size: var(--t-xxl);
  font-weight: 600;
  line-height: 1;
  color: var(--movistar-noche);
}

.pct {
  font-size: var(--t-md);
  margin-left: 1px;
}

.margen {
  font-size: var(--t-sm);
  color: var(--tinta-media);
}

.leyenda {
  margin-left: auto;
  color: var(--tinta-media);
}

.procedencia {
  margin-top: 5px;
  color: var(--tinta-suave);
  letter-spacing: 0.06em;
}

/* Escala fija 0–100: se llena, no se reescala. */
.riel {
  position: relative;
  margin-top: 7px;
  height: 8px;
  border-radius: 4px;
  background: var(--superficie);
  border: 1px solid var(--linea);
  overflow: hidden;
}

.lleno {
  position: absolute;
  inset: 0 auto 0 0;
  background: var(--movistar-azul);
  transition: width 280ms ease;
}

/* Tramo de incertidumbre: hasta dónde podría llegar el estimado. */
.incierto {
  position: absolute;
  top: 0;
  bottom: 0;
  background: var(--movistar-azul);
  opacity: 0.28;
  border-left: 1px solid var(--superficie);
}

.cifras {
  display: flex;
  gap: var(--gap-xl);
  margin-top: var(--gap);
  padding-top: var(--gap);
  border-top: 1px solid var(--linea);
}

.celda {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.monto {
  font-size: var(--t-lg);
  font-weight: 600;
  color: var(--verde);
}

.monto.neutro {
  color: var(--tinta-media);
}

.contacto {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  margin-top: var(--gap);
  font-size: var(--t-sm);
  color: var(--tinta-media);
}

.chip {
  padding: 3px 8px;
  border: 1px solid var(--verde);
  border-radius: 3px;
  color: var(--verde);
  background: var(--superficie);
  white-space: nowrap;
}

.chip.alterno {
  border-color: var(--ambar);
  color: var(--ambar);
}
</style>
