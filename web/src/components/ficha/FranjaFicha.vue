<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import DatoFicha from './DatoFicha.vue'
import { ETIQUETA_CANAL } from '@/api/etiquetas'
import type { Cliente } from '@/api/tipos'

const props = defineProps<{ cliente: Cliente; ultimaCaptura: string[] }>()

const antiguedad = computed(() => {
  if (props.cliente.es_nuevo || props.cliente.antiguedad_meses === 0) return null
  const años = Math.floor(props.cliente.antiguedad_meses / 12)
  const meses = props.cliente.antiguedad_meses % 12
  return años ? `${años}a ${meses}m` : `${meses}m`
})

const tonoRiesgo = computed(() =>
  props.cliente.riesgo_baja === 'alto'
    ? 'alerta'
    : props.cliente.riesgo_baja === 'bajo'
      ? 'ok'
      : 'normal',
)

const tonoConsumo = computed(() =>
  (props.cliente.pct_consumo_datos ?? 0) >= 85 ? 'alerta' : 'normal',
)

/** Qué servicios tiene hoy, que es lo que define si le falta algo para MT. */
const productos = computed(() => {
  const partes: string[] = []
  if (props.cliente.tiene_movil) partes.push('Móvil')
  if (props.cliente.tiene_internet_hogar) partes.push('Internet')
  else if (props.cliente.tiene_hogar) partes.push('Hogar')
  return partes.length ? partes.join(' + ') : null
})

const mora = computed(() =>
  props.cliente.meses_moroso === null ? null : `${props.cliente.meses_moroso}/6 meses`,
)

const tonoMora = computed(() => ((props.cliente.meses_moroso ?? 0) > 0 ? 'alerta' : 'ok'))

/** Etiqueta de segmento MT: es el eje del desafío, va junto al nombre. */
const sello = computed(() => {
  if (props.cliente.es_movistar_total) return { texto: 'Ya tiene MT', tono: 'ok' as const }
  if (props.cliente.elegible_mt) return { texto: 'Elegible MT', tono: 'foco' as const }
  return { texto: 'No elegible MT', tono: 'neutro' as const }
})

/** Campos que acaban de llenarse: se realzan un instante y vuelven a la calma. */
const realzados = ref<string[]>([])
let temporizador: number | undefined

watch(
  () => props.ultimaCaptura,
  (campos) => {
    clearTimeout(temporizador)
    realzados.value = campos ?? []
    if (realzados.value.length) {
      temporizador = window.setTimeout(() => (realzados.value = []), 1000)
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => clearTimeout(temporizador))

const seRealza = (campo: string) => realzados.value.includes(campo)
</script>

<template>
  <section class="franja" aria-label="Ficha del cliente">
    <div class="identidad">
      <div class="linea-nombre">
        <h1 class="nombre">{{ cliente.nombre ?? cliente.cliente_id }}</h1>
        <span class="micro sello" :class="sello.tono">{{ sello.texto }}</span>
        <span v-if="cliente.es_nuevo" class="micro sello neutro">Sin historial</span>
      </div>
      <div class="sub">
        <span class="cifra id">{{ cliente.cliente_id }}</span>
        <span class="punto" aria-hidden="true">·</span>
        <span>{{ cliente.ubicacion_departamento }}</span>
        <template v-if="cliente.edad_rango">
          <span class="punto" aria-hidden="true">·</span>
          <span class="cifra">{{ cliente.edad_rango }}</span>
        </template>
        <template v-if="cliente.tipo_cliente">
          <span class="punto" aria-hidden="true">·</span>
          <span>{{ cliente.tipo_cliente }}</span>
        </template>
      </div>
    </div>

    <div class="datos">
      <DatoFicha etiqueta="Antigüedad" :valor="antiguedad" />
      <DatoFicha
        etiqueta="Facturación"
        :valor="
          cliente.monto_facturado_prom === null ? null : `S/ ${cliente.monto_facturado_prom}`
        "
        :destacado="seRealza('monto_facturado_prom')"
      />
      <DatoFicha etiqueta="Servicios" :valor="productos" />
      <DatoFicha etiqueta="Riesgo de baja" :valor="cliente.riesgo_baja" :tono="tonoRiesgo" />
      <DatoFicha
        etiqueta="Consumo datos"
        :valor="cliente.pct_consumo_datos === null ? null : `${cliente.pct_consumo_datos}%`"
        :tono="tonoConsumo"
        :destacado="seRealza('pct_consumo_datos') || seRealza('consumo_datos_gb_prom')"
      />
      <DatoFicha etiqueta="Mora" :valor="mora" :tono="tonoMora" />
      <DatoFicha etiqueta="Reclamos" :valor="cliente.n_reclamos" />
      <DatoFicha
        etiqueta="Canal habitual"
        :valor="cliente.canal_mas_usado ? ETIQUETA_CANAL[cliente.canal_mas_usado] : null"
      />
      <DatoFicha
        etiqueta="Usa la app"
        :valor="cliente.es_usuario_app ? 'Sí' : 'No'"
        :tono="cliente.es_usuario_app ? 'ok' : 'normal'"
      />
    </div>
  </section>
</template>

<style scoped>
.franja {
  display: flex;
  align-items: center;
  gap: var(--gap-xl);
  padding: 10px var(--gap-lg);
  background: var(--superficie);
  border-bottom: 1px solid var(--linea);
  overflow-x: auto;
}

.linea-nombre {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
}

.nombre {
  font-size: var(--t-lg);
  font-weight: 600;
  line-height: 1.15;
  white-space: nowrap;
}

.sello {
  padding: 2px 7px;
  border: 1px solid var(--linea);
  border-radius: 3px;
  background: var(--superficie-tenue);
  color: var(--tinta-media);
  white-space: nowrap;
}

/* Elegible MT es el segmento prioritario del reto: se marca en azul. */
.sello.foco {
  border-color: var(--movistar-azul);
  background: var(--movistar-cielo);
  color: var(--movistar-noche);
}

.sello.ok {
  border-color: var(--verde);
  color: var(--verde);
}

.sub {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--t-xs);
  color: var(--tinta-media);
  white-space: nowrap;
}

.punto {
  color: var(--tinta-suave);
}

.datos {
  display: flex;
  align-items: center;
  margin-left: auto;
}

@media (max-width: 1180px) {
  .franja {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--gap);
  }

  .datos {
    margin-left: 0;
    flex-wrap: wrap;
    gap: var(--gap-sm) 0;
  }
}
</style>
