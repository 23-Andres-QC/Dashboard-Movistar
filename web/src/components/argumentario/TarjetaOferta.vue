<script setup lang="ts">
import { computed } from 'vue'

import AnilloProbabilidad from '@/components/ui/AnilloProbabilidad.vue'
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
</script>

<template>
  <article class="tarjeta">
    <header class="cabecera">
      <span class="micro rango">Oferta recomendada</span>
      <span class="micro sello" :class="oferta.confianza">Confianza {{ oferta.confianza }}</span>
    </header>

    <h2 class="nombre">{{ oferta.oferta }}</h2>

    <div class="tasa">
      <AnilloProbabilidad :valor="probabilidad" :margen="oferta.margen" :tamano="104" />

      <dl class="cifras">
        <div v-if="oferta.ahorro != null" class="celda">
          <dt class="micro">Ahorro / mes</dt>
          <dd class="cifra monto">S/ {{ oferta.ahorro }}</dd>
        </div>
        <div v-if="oferta.precio_mensual != null" class="celda">
          <dt class="micro">Cuota</dt>
          <dd class="cifra monto neutro">S/ {{ oferta.precio_mensual }}</dd>
        </div>
        <div class="celda">
          <dt class="micro">Aceptación por</dt>
          <dd class="canal-valor">{{ canal ?? '—' }}</dd>
        </div>
      </dl>
    </div>

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
  display: flex;
  align-items: center;
  gap: var(--gap-lg);
  margin-top: var(--gap);
  padding-top: var(--gap);
  border-top: 1px solid var(--borde-cielo);
}

.cifras {
  display: flex;
  flex-direction: column;
  gap: 9px;
  min-width: 0;
}

.celda {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.monto {
  font-size: var(--t-lg);
  font-weight: 700;
  line-height: 1.1;
  color: var(--verde);
}

.monto.neutro {
  color: var(--movistar-noche);
}

.canal-valor {
  font-size: var(--t-base);
  font-weight: 600;
  color: var(--movistar-azul);
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
