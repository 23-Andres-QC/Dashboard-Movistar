<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import DatoFicha from './DatoFicha.vue'
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
        <h1 class="nombre">{{ cliente.nombre }}</h1>
        <span v-if="cliente.es_nuevo" class="micro sin-historial">Sin historial</span>
      </div>
      <div class="sub">
        <span class="cifra id">{{ cliente.id_cliente }}</span>
        <span class="punto" aria-hidden="true">·</span>
        <span>{{ cliente.distrito }}</span>
        <span class="punto" aria-hidden="true">·</span>
        <span class="cifra">DNI {{ cliente.dni }}</span>
      </div>
    </div>

    <div class="datos">
      <DatoFicha etiqueta="Antigüedad" :valor="antiguedad" />
      <DatoFicha
        etiqueta="ARPU"
        :valor="cliente.arpu === null ? null : `S/ ${cliente.arpu}`"
        :destacado="seRealza('arpu')"
      />
      <DatoFicha etiqueta="Productos" :valor="cliente.productos" />
      <DatoFicha etiqueta="Riesgo de baja" :valor="cliente.riesgo_baja" :tono="tonoRiesgo" />
      <DatoFicha
        etiqueta="Consumo datos"
        :valor="cliente.pct_consumo_datos === null ? null : `${cliente.pct_consumo_datos}%`"
        :tono="tonoConsumo"
        :destacado="seRealza('pct_consumo_datos')"
      />
      <DatoFicha
        etiqueta="Líneas domicilio"
        :valor="cliente.lineas_domicilio || null"
        :destacado="seRealza('lineas_domicilio')"
      />
      <DatoFicha
        etiqueta="Fibra"
        :valor="cliente.cobertura_fibra ? 'Sí' : 'No'"
        :tono="cliente.cobertura_fibra ? 'ok' : 'normal'"
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

.sin-historial {
  padding: 2px 7px;
  border: 1px solid var(--linea);
  border-radius: 3px;
  background: var(--superficie-tenue);
  color: var(--tinta-media);
  white-space: nowrap;
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
