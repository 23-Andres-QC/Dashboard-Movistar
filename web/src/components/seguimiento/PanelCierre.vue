<script setup lang="ts">
import { computed, ref } from 'vue'

import TituloPanel from '@/components/ui/TituloPanel.vue'
import { ETIQUETA_MEDIO, ETIQUETA_MOTIVO, ETIQUETA_RESULTADO, MEDIOS, MOTIVOS } from '@/api/etiquetas'
import type { CierreEnvio, MedioProbatorio, Motivo, Resultado } from '@/api/tipos'

const props = defineProps<{
  cerrada: boolean
  resultadoCerrado: Resultado | null
  idGestion: string | null
  probActual: number
  objecionActiva: Motivo | null
  motivoSugerido: Motivo | null
  /** La conversación va hacia el rechazo: se marca el botón para no insistir. */
  resaltarRechazo: boolean
}>()

const emit = defineEmits<{ cerrar: [datos: CierreEnvio] }>()

const RESULTADOS: Exclude<Resultado, 'en_curso'>[] = ['vendido', 'rechazado', 'sin_contacto']

const seleccion = ref<Exclude<Resultado, 'en_curso'> | null>(null)
const motivo = ref<Motivo | ''>('')
const medio = ref<MedioProbatorio | ''>('')

/** Una venta no necesita motivo de rechazo; el resto sí lo pide. */
const requiereMotivo = computed(() => seleccion.value !== null && seleccion.value !== 'vendido')
const puedeCerrar = computed(
  () => seleccion.value !== null && (!requiereMotivo.value || motivo.value !== ''),
)

function elegir(resultado: Exclude<Resultado, 'en_curso'>) {
  seleccion.value = resultado
  if (resultado === 'vendido') {
    motivo.value = ''
    return
  }
  // Lo más probable ya está en pantalla: la objeción viva o el motivo del caso.
  if (motivo.value === '') motivo.value = props.motivoSugerido ?? props.objecionActiva ?? ''
}

function confirmar() {
  if (!seleccion.value || !puedeCerrar.value) return
  emit('cerrar', {
    resultado: seleccion.value,
    motivo_real: motivo.value === '' ? null : motivo.value,
    prob_final: props.probActual,
    // Sin contacto no hubo contactabilidad real: es el `pendiente` del dataset.
    contactabilidad: seleccion.value === 'sin_contacto' ? 'no_contactado' : 'contactado',
    es_rebate: props.objecionActiva !== null,
    medio_probatorio: medio.value === '' ? null : medio.value,
  })
}
</script>

<template>
  <section class="bloque">
    <TituloPanel texto="Cierre de la gestión" acento="ninguno" :contador="idGestion ?? '—'" />

    <div v-if="cerrada" class="cerrada">
      <span class="micro">Resultado registrado</span>
      <span class="valor" :class="resultadoCerrado ?? ''">
        {{ resultadoCerrado ? ETIQUETA_RESULTADO[resultadoCerrado] : '' }}
      </span>
    </div>

    <div v-else class="formulario">
      <div class="botones" role="group" aria-label="Resultado de la gestión">
        <button
          v-for="r in RESULTADOS"
          :key="r"
          type="button"
          class="micro opcion"
          :class="[
            r,
            { activa: seleccion === r, sugerida: resaltarRechazo && r === 'rechazado' },
          ]"
          :aria-pressed="seleccion === r"
          :disabled="!idGestion"
          @click="elegir(r)"
        >
          {{ ETIQUETA_RESULTADO[r] }}
        </button>
      </div>

      <label class="campo">
        <span class="micro">Motivo real {{ requiereMotivo ? '' : '(opcional)' }}</span>
        <select v-model="motivo" :disabled="!seleccion || seleccion === 'vendido'">
          <option value="">Sin especificar</option>
          <option v-for="m in MOTIVOS" :key="m" :value="m">{{ ETIQUETA_MOTIVO[m] }}</option>
        </select>
      </label>

      <label class="campo">
        <span class="micro">Medio probatorio</span>
        <select v-model="medio" :disabled="!seleccion">
          <option value="">Sin registrar</option>
          <option v-for="m in MEDIOS" :key="m" :value="m">{{ ETIQUETA_MEDIO[m] }}</option>
        </select>
      </label>

      <button class="confirmar" type="button" :disabled="!puedeCerrar" @click="confirmar">
        Cerrar gestión
      </button>
    </div>
  </section>
</template>

<style scoped>
.bloque {
  border-bottom: 1px solid var(--linea);
}

.formulario {
  padding: var(--gap-sm) var(--gap) var(--gap);
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.botones {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
}

.opcion {
  padding: 7px 3px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
}

.opcion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Rumbo al rechazo: se resalta el botón para que el asesor deje de insistir. */
.opcion.sugerida:not(.activa) {
  border-color: var(--alarma);
  border-width: 2px;
  color: var(--alarma);
}

.opcion.activa.vendido {
  border-color: var(--verde);
  background: var(--verde);
  color: var(--tinta-inversa);
}

.opcion.activa.rechazado {
  border-color: var(--alarma);
  background: var(--alarma);
  color: var(--tinta-inversa);
}

.opcion.activa.sin_contacto {
  border-color: var(--tinta-media);
  background: var(--tinta-media);
  color: var(--tinta-inversa);
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

select,
input {
  padding: 6px 8px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
}

select:disabled,
input:disabled {
  background: var(--superficie-tenue);
  color: var(--tinta-suave);
}

.confirmar {
  margin-top: 2px;
  padding: 8px;
  border: 1px solid var(--movistar-noche);
  border-radius: var(--r);
  background: var(--movistar-noche);
  color: var(--tinta-inversa);
  font-size: var(--t-sm);
  font-weight: 600;
}

.confirmar:disabled {
  border-color: var(--linea);
  background: var(--superficie);
  color: var(--tinta-suave);
  cursor: not-allowed;
}

.cerrada {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gap-sm);
  padding: var(--gap);
}

.valor {
  font-size: var(--t-md);
  font-weight: 600;
}

.valor.vendido {
  color: var(--verde);
}
.valor.rechazado {
  color: var(--alarma);
}
.valor.sin_contacto {
  color: var(--tinta-media);
}
</style>
