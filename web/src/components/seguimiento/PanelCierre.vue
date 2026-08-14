<script setup lang="ts">
import { ETIQUETA_RESULTADO } from '@/api/etiquetas'
import type { CierreEnvio, Motivo, Resultado } from '@/api/tipos'

const props = defineProps<{
  cerrada: boolean
  resultadoCerrado: Resultado | null
  idGestion: string | null
  probActual: number
  objecionActiva: Motivo | null
  /** La conversación va hacia el rechazo: se marca para no insistir. */
  resaltarRechazo: boolean
}>()

const emit = defineEmits<{ cerrar: [datos: CierreEnvio] }>()

const RESULTADOS: Exclude<Resultado, 'en_curso'>[] = ['vendido', 'rechazado', 'sin_contacto']
const ICONO: Record<string, string> = { vendido: '✓', rechazado: '✕', sin_contacto: '—' }

/** El botón es la acción: el motivo y el medio se piden en el modal. */
function registrar(resultado: Exclude<Resultado, 'en_curso'>) {
  if (!props.idGestion || props.cerrada) return
  emit('cerrar', {
    resultado,
    motivo_real: null,
    prob_final: props.probActual,
    contactabilidad: resultado === 'sin_contacto' ? 'no_contactado' : 'contactado',
    es_rebate: props.objecionActiva !== null,
    medio_probatorio: null,
  })
}
</script>

<template>
  <section class="cierre">
    <div v-if="cerrada" class="resuelto" :class="resultadoCerrado ?? ''">
      <span class="icono" aria-hidden="true">
        {{ resultadoCerrado ? ICONO[resultadoCerrado] : '' }}
      </span>
      <span class="valor">{{ resultadoCerrado ? ETIQUETA_RESULTADO[resultadoCerrado] : '' }}</span>
      <span class="cifra id">{{ idGestion }}</span>
    </div>

    <div v-else class="botones" role="group" aria-label="Resultado de la gestión">
      <button
        v-for="r in RESULTADOS"
        :key="r"
        type="button"
        class="opcion"
        :class="[r, { sugerida: resaltarRechazo && r === 'rechazado' }]"
        :disabled="!idGestion"
        @click="registrar(r)"
      >
        <span class="icono" aria-hidden="true">{{ ICONO[r] }}</span>
        <span class="texto">{{ ETIQUETA_RESULTADO[r] }}</span>
      </button>
    </div>
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
  gap: 8px;
}

.opcion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  padding: 12px 4px;
  border: 2px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  font-size: var(--t-base);
  font-weight: 600;
  transition: border-color 140ms ease, background-color 140ms ease, color 140ms ease;
}

.icono {
  font-size: 15px;
  line-height: 1;
}

.opcion:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Cada resultado toma su color al pasar por encima: la decisión se ve venir. */
.opcion.vendido:not(:disabled):hover {
  border-color: var(--verde);
  background: var(--verde);
  color: var(--tinta-inversa);
}

.opcion.rechazado:not(:disabled):hover {
  border-color: var(--alarma);
  background: var(--alarma);
  color: var(--tinta-inversa);
}

.opcion.sin_contacto:not(:disabled):hover {
  border-color: var(--tinta-media);
  background: var(--tinta-media);
  color: var(--tinta-inversa);
}

/* Rumbo al rechazo: se marca para que el asesor deje de insistir. */
.opcion.sugerida:not(:disabled) {
  border-color: var(--alarma);
  color: var(--alarma);
}

.resuelto {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 8px 2px;
}

.resuelto .valor {
  font-size: var(--t-md);
  font-weight: 700;
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
</style>
