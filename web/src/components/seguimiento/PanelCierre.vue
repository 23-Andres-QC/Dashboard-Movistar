<script setup lang="ts">
import { computed, ref } from 'vue'

import { ETIQUETA_MEDIO, ETIQUETA_MOTIVO, ETIQUETA_RESULTADO, MEDIOS, MOTIVOS } from '@/api/etiquetas'
import type { CierreEnvio, MedioProbatorio, Motivo, Resultado } from '@/api/tipos'

const props = defineProps<{
  cerrada: boolean
  resultadoCerrado: Resultado | null
  idGestion: string | null
  probActual: number
  objecionActiva: Motivo | null
  motivoSugerido: Motivo | null
  /** La conversación va hacia el rechazo: se marca para no insistir. */
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
  if (motivo.value === '') motivo.value = props.motivoSugerido ?? props.objecionActiva ?? ''
}

function confirmar() {
  if (!seleccion.value || !puedeCerrar.value) return
  emit('cerrar', {
    resultado: seleccion.value,
    motivo_real: motivo.value === '' ? null : motivo.value,
    prob_final: props.probActual,
    contactabilidad: seleccion.value === 'sin_contacto' ? 'no_contactado' : 'contactado',
    es_rebate: props.objecionActiva !== null,
    medio_probatorio: medio.value === '' ? null : medio.value,
  })
}
</script>

<template>
  <section class="cierre" :class="{ registrado: cerrada }">
    <!-- Cerrada: una sola línea con el desenlace. -->
    <div v-if="cerrada" class="resuelto" :class="resultadoCerrado ?? ''">
      <span class="icono" aria-hidden="true">{{ resultadoCerrado === 'vendido' ? '✓' : '—' }}</span>
      <span class="valor">{{ resultadoCerrado ? ETIQUETA_RESULTADO[resultadoCerrado] : '' }}</span>
      <span class="cifra id">{{ idGestion }}</span>
    </div>

    <template v-else>
      <div class="botones" role="group" aria-label="Resultado de la gestión">
        <button
          v-for="r in RESULTADOS"
          :key="r"
          type="button"
          class="opcion"
          :class="[r, { activa: seleccion === r, sugerida: resaltarRechazo && r === 'rechazado' }]"
          :aria-pressed="seleccion === r"
          :disabled="!idGestion"
          @click="elegir(r)"
        >
          <span class="icono" aria-hidden="true">{{ r === 'vendido' ? '✓' : r === 'rechazado' ? '✕' : '—' }}</span>
          <span class="micro">{{ ETIQUETA_RESULTADO[r] }}</span>
        </button>
      </div>

      <div v-if="seleccion" class="detalle">
        <label class="campo">
          <span class="micro">
            Motivo real
            <span v-if="requiereMotivo" class="obligatorio">obligatorio</span>
          </span>
          <select v-model="motivo" :disabled="seleccion === 'vendido'">
            <option value="">Sin especificar</option>
            <option v-for="m in MOTIVOS" :key="m" :value="m">{{ ETIQUETA_MOTIVO[m] }}</option>
          </select>
        </label>

        <label class="campo">
          <span class="micro">Medio probatorio</span>
          <select v-model="medio">
            <option value="">Sin registrar</option>
            <option v-for="m in MEDIOS" :key="m" :value="m">{{ ETIQUETA_MEDIO[m] }}</option>
          </select>
        </label>

        <button class="confirmar" type="button" :disabled="!puedeCerrar" @click="confirmar">
          Cerrar gestión
        </button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.cierre {
  padding: var(--gap-sm) var(--gap);
  border-top: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

.botones {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.opcion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 4px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  transition: border-color 140ms ease, background-color 140ms ease;
}

.icono {
  font-size: 13px;
  line-height: 1;
}

.opcion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* Rumbo al rechazo: se marca para que el asesor deje de insistir. */
.opcion.sugerida:not(.activa) {
  border-color: var(--alarma);
  border-width: 2px;
  color: var(--alarma);
}

.detalle {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: end;
  gap: var(--gap-sm);
  margin-top: var(--gap-sm);
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

select {
  padding: 7px 8px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
}

select:disabled {
  background: var(--superficie-tenue);
  color: var(--tinta-suave);
}

.obligatorio {
  color: var(--alarma);
}

.confirmar {
  padding: 8px 18px;
  border: 1px solid var(--movistar-noche);
  border-radius: var(--r);
  background: var(--movistar-noche);
  color: var(--tinta-inversa);
  font-size: var(--t-sm);
  font-weight: 600;
  white-space: nowrap;
}

.confirmar:disabled {
  border-color: var(--linea);
  background: var(--superficie);
  color: var(--tinta-suave);
  cursor: not-allowed;
}

.resuelto {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 6px 2px;
}

.resuelto .valor {
  font-size: var(--t-md);
  font-weight: 600;
}

.resuelto .id {
  margin-left: auto;
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}

.resuelto.vendido {
  color: var(--verde);
}
.resuelto.rechazado {
  color: var(--alarma);
}
.resuelto.sin_contacto {
  color: var(--tinta-media);
}

@media (max-width: 700px) {
  .detalle {
    grid-template-columns: 1fr;
  }
}
</style>
