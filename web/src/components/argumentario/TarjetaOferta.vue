<script setup lang="ts">
import { computed } from 'vue'

import AnilloProbabilidad from '@/components/ui/AnilloProbabilidad.vue'
import type { Canal, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  oferta: Recomendacion
  /** Probabilidad del canal que el asesor está mirando. */
  probabilidad: number
  canalActivo: Canal | null
}>()

defineEmits<{ detalle: [] }>()

const esOtroCanal = computed(
  () => props.canalActivo !== null && props.canalActivo !== props.oferta.canal_sugerido,
)

</script>

<template>
  <article
    class="tarjeta tarjeta-suelta"
    role="button"
    tabindex="0"
    aria-label="Ver detalles de la oferta"
    @click="$emit('detalle')"
    @keydown.enter="$emit('detalle')"
    @keydown.space.prevent="$emit('detalle')"
  >
    <header class="cabecera">
      <span class="micro rango">Oferta recomendada</span>
      <h2 class="nombre">{{ oferta.oferta }}</h2>
      <div class="sellos">
        <span class="micro sello" :class="oferta.confianza">
          Confianza {{ oferta.confianza }}
        </span>
        <span v-if="oferta.es_movistar_total" class="micro sello mt">Movistar Total</span>
      </div>
    </header>

    <div class="cuerpo">
      <AnilloProbabilidad :valor="probabilidad" :margen="oferta.margen" :tamano="118" />
      <p class="resumen">Oferta seleccionada para este cliente</p>
    </div>

    <p v-if="oferta.franja_sugerida" class="pie">
      <span class="micro chip" :class="{ alterno: esOtroCanal }">
        {{ esOtroCanal ? 'Fuera del recomendado' : 'Canal recomendado' }}
      </span>
      <span class="franja">{{ oferta.franja_sugerida }}</span>
    </p>
    <div class="acciones-detalle">
      <button type="button" @click.stop="$emit('detalle')">Ver contraste <span aria-hidden="true">↗</span></button>
    </div>
  </article>
</template>

<style scoped>
.tarjeta {
  box-shadow: var(--sombra-2);
  flex: 0 0 auto;
  cursor: pointer;
  transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.tarjeta:hover,
.tarjeta:focus-visible {
  border-color: var(--movistar-azul);
  box-shadow: var(--sombra-2), 0 0 0 3px var(--movistar-cielo);
  transform: translateY(-1px);
}

/* Cabecera sobria en azul noche: da jerarquía sin recurrir al color vivo. */
.cabecera {
  padding: 11px var(--gap-lg) 13px;
  background: var(--movistar-noche-fondo);
  color: var(--tinta-inversa);
}

.rango {
  color: rgba(255, 255, 255, 0.62);
}

.nombre {
  margin-top: 3px;
  font-size: var(--t-lg);
  font-weight: 600;
  line-height: 1.25;
}

.sellos {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

/* Chips con tinte, no bloques: el color se insinúa. */
.sello {
  padding: 3px 9px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.9);
}

.sello.alta {
  border-color: rgba(47, 163, 107, 0.7);
  background: rgba(47, 163, 107, 0.18);
}

.sello.baja {
  border-color: rgba(224, 150, 60, 0.7);
  background: rgba(224, 150, 60, 0.18);
}

.sello.mt {
  border-color: rgba(1, 157, 244, 0.75);
  background: rgba(1, 157, 244, 0.2);
}

.cuerpo {
  display: flex;
  align-items: center;
  gap: var(--gap-lg);
  min-height: 150px;
  padding: 16px;
}

.resumen {
  color: var(--tinta-suave);
  font-size: var(--t-xs);
}

/* Filas apiladas: cada etiqueta y su valor en una línea, sin truncarse. */
.cifras {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.fila {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gap);
  padding: 7px 0;
  border-bottom: 1px solid var(--linea-suave);
}

.fila:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.fila:first-child {
  padding-top: 0;
}

.etiqueta {
  color: var(--tinta-suave);
  white-space: nowrap;
}

.valor {
  font-size: var(--t-md);
  font-weight: 700;
  line-height: 1.2;
  text-align: right;
  white-space: nowrap;
}

.valor.verde {
  color: var(--verde);
}
.valor.noche {
  color: var(--movistar-noche);
}
.valor.azul {
  color: var(--movistar-azul-hondo);
}
.valor.ambar {
  color: var(--ambar);
}

.pie {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 10px var(--gap-lg);
  border-top: 1px solid var(--linea);
  background: var(--superficie-tenue);
  font-size: var(--t-sm);
  color: var(--tinta-media);
}

.chip {
  padding: 3px 9px;
  border: 1px solid rgba(29, 107, 69, 0.35);
  border-radius: 999px;
  background: var(--good-fondo);
  color: var(--verde);
  white-space: nowrap;
}

.chip.alterno {
  border-color: rgba(143, 74, 11, 0.35);
  background: var(--warn-fondo);
  color: var(--ambar);
}

.franja {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.acciones-detalle {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 8px var(--gap-lg);
  border-top: 1px solid var(--linea);
}

.acciones-detalle button {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--movistar-azul-hondo);
  font-size: var(--t-xs);
  font-weight: 700;
}

.acciones-detalle button:hover {
  text-decoration: underline;
}
</style>
