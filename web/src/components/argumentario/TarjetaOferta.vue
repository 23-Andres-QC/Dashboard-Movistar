<script setup lang="ts">
import { computed } from 'vue'

import AnilloProbabilidad from '@/components/ui/AnilloProbabilidad.vue'
import type { Canal, Recomendacion } from '@/api/tipos'

const props = withDefaults(defineProps<{
  oferta: Recomendacion
  /** Probabilidad del canal que el asesor está mirando. */
  probabilidad: number
  canalActivo: Canal | null
  esMejorOpcion?: boolean
}>(), { esMejorOpcion: true })

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
        <span v-if="esMejorOpcion" class="micro sello mejor-opcion">Mejor opción</span>
      </div>
      <button class="contraste" type="button" @click.stop="$emit('detalle')">
        Ver contraste <span aria-hidden="true">↗</span>
      </button>
      <div class="probabilidad-cabecera">
        <AnilloProbabilidad
          :valor="probabilidad"
          :margen="oferta.margen"
          :tamano="62"
          :acento="esMejorOpcion ? 'ambar' : 'auto'"
        />
      </div>
    </header>

    <p v-if="oferta.franja_sugerida" class="pie">
      <span class="micro chip" :class="{ alterno: esOtroCanal }">
        {{ esOtroCanal ? 'Fuera del recomendado' : 'Canal recomendado' }}
      </span>
      <span class="franja">{{ oferta.franja_sugerida }}</span>
    </p>
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
  position: relative;
  min-height: 110px;
  padding: 7px 96px 8px var(--gap-lg);
  background: var(--movistar-noche-fondo);
  color: var(--tinta-inversa);
}

.probabilidad-cabecera {
  --linea: rgba(255, 255, 255, 0.28);
  --tinta-suave: rgba(255, 255, 255, 0.72);
  position: absolute;
  top: 7px;
  right: 18px;
  pointer-events: none;
}

.contraste {
  position: absolute;
  right: var(--gap-lg);
  bottom: 9px;
  padding: 0;
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.88);
  font-size: var(--t-xs);
  font-weight: 700;
  z-index: 1;
}

.contraste:hover {
  color: var(--movistar-azul);
  text-decoration: underline;
}

.rango {
  color: rgba(255, 255, 255, 0.62);
}

.nombre {
  margin-top: 3px;
  font-size: var(--t-md);
  font-weight: 600;
  line-height: 1.25;
}

.sellos {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
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

.sello.mejor-opcion {
  border-color: var(--verde-vivo);
  background: var(--verde-vivo);
  color: #06381f;
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
  padding: 8px var(--gap-lg);
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

</style>
