<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { ETIQUETA_MEDIO, ETIQUETA_MOTIVO, ETIQUETA_RESULTADO, MEDIOS, MOTIVOS } from '@/api/etiquetas'
import type { CalificacionEnvio, MedioProbatorio, Motivo, Resultado } from '@/api/tipos'

const props = defineProps<{
  resultado: Exclude<Resultado, 'en_curso'>
  motivoInicial: Motivo | null
  sugerida: { facilidad_venta: number; oferta_fue_pertinente: boolean } | null
}>()

const emit = defineEmits<{
  enviar: [datos: CalificacionEnvio, motivo: Motivo | null, medio: MedioProbatorio | null]
  omitir: []
}>()

const medio = ref<MedioProbatorio | ''>('')

const facilidad = ref<number | null>(props.sugerida?.facilidad_venta ?? null)
const pertinente = ref<boolean | null>(props.sugerida?.oferta_fue_pertinente ?? null)
const motivo = ref<Motivo | ''>(props.motivoInicial ?? '')
const nps = ref<number | null>(null)
const comentario = ref('')
const enviando = ref(false)

const dialogo = ref<HTMLElement | null>(null)

/** Sin venta, el motivo real es obligatorio: es el campo que da valor a la
 *  base de datos. Con venta, no aplica y queda deshabilitado. */
const requiereMotivo = computed(() => props.resultado !== 'vendido')

const completo = computed(
  () =>
    facilidad.value !== null &&
    pertinente.value !== null &&
    (!requiereMotivo.value || motivo.value !== ''),
)

async function enviar() {
  if (!completo.value || enviando.value) return
  enviando.value = true
  try {
    emit(
      'enviar',
      {
        facilidad_venta: facilidad.value!,
        oferta_fue_pertinente: pertinente.value!,
        nps_declarado: nps.value,
        comentario: comentario.value.trim() || null,
      },
      motivo.value === '' ? null : motivo.value,
      medio.value === '' ? null : medio.value,
    )
  } finally {
    enviando.value = false
  }
}

function alPulsarTecla(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('omitir')
}

onMounted(async () => {
  document.addEventListener('keydown', alPulsarTecla)
  await nextTick()
  dialogo.value?.querySelector('button')?.focus()
})

onBeforeUnmount(() => document.removeEventListener('keydown', alPulsarTecla))
</script>

<template>
  <div class="velo" @click.self="emit('omitir')">
    <div
      ref="dialogo"
      class="dialogo panel"
      role="dialog"
      aria-modal="true"
      aria-labelledby="titulo-calificacion"
    >
      <header class="cabecera">
        <h2 id="titulo-calificacion" class="titulo">Calificar la gestión</h2>
        <p class="ayuda">
          Resultado
          <span class="resultado" :class="resultado">{{ ETIQUETA_RESULTADO[resultado] }}</span>
          · treinta segundos, alimenta la calidad del servicio.
        </p>
      </header>

      <label class="campo">
        <span class="micro">
          Motivo real
          <span v-if="requiereMotivo" class="obligatorio">obligatorio</span>
          <span v-else class="opcional">no aplica en venta</span>
        </span>
        <select v-model="motivo" :disabled="!requiereMotivo">
          <option value="">Seleccione un motivo</option>
          <option v-for="m in MOTIVOS" :key="m" :value="m">{{ ETIQUETA_MOTIVO[m] }}</option>
        </select>
      </label>

      <fieldset class="campo">
        <legend class="micro">Facilidad de venta</legend>
        <div class="escala">
          <button
            v-for="n in 5"
            :key="n"
            type="button"
            class="cifra grado"
            :class="{ activo: facilidad === n }"
            :aria-pressed="facilidad === n"
            @click="facilidad = n"
          >
            {{ n }}
          </button>
        </div>
        <p class="pie-escala">
          <span>1 · muy difícil</span>
          <span>5 · muy fácil</span>
        </p>
      </fieldset>

      <fieldset class="campo">
        <legend class="micro">¿La oferta fue pertinente?</legend>
        <div class="binario">
          <button
            type="button"
            class="opcion"
            :class="{ activo: pertinente === true, si: true }"
            :aria-pressed="pertinente === true"
            @click="pertinente = true"
          >
            Sí
          </button>
          <button
            type="button"
            class="opcion"
            :class="{ activo: pertinente === false, no: true }"
            :aria-pressed="pertinente === false"
            @click="pertinente = false"
          >
            No
          </button>
        </div>
      </fieldset>

      <fieldset class="campo">
        <legend class="micro">NPS declarado por el cliente (opcional)</legend>
        <div class="nps">
          <button
            v-for="n in 11"
            :key="n - 1"
            type="button"
            class="cifra celda-nps"
            :class="{ activo: nps === n - 1 }"
            :aria-pressed="nps === n - 1"
            @click="nps = nps === n - 1 ? null : n - 1"
          >
            {{ n - 1 }}
          </button>
        </div>
      </fieldset>

      <label class="campo">
        <span class="micro">Medio probatorio</span>
        <select v-model="medio">
          <option value="">Sin registrar</option>
          <option v-for="m in MEDIOS" :key="m" :value="m">{{ ETIQUETA_MEDIO[m] }}</option>
        </select>
      </label>

      <label class="campo">
        <span class="micro">Comentario (opcional)</span>
        <textarea v-model="comentario" rows="2" placeholder="Qué faltó, qué funcionó…"></textarea>
      </label>

      <footer class="acciones">
        <button type="button" class="secundario" @click="emit('omitir')">Omitir</button>
        <button type="button" class="primario" :disabled="!completo || enviando" @click="enviar">
          {{ enviando ? 'Enviando…' : 'Enviar calificación' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.velo {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: var(--gap);
  background: rgba(11, 39, 57, 0.55);
}

.dialogo {
  width: min(420px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  padding: var(--gap-lg);
  display: flex;
  flex-direction: column;
  gap: var(--gap);
}

.cabecera {
  border-bottom: 1px solid var(--linea);
  padding-bottom: var(--gap-sm);
}

.titulo {
  font-size: var(--t-md);
  font-weight: 600;
}

.ayuda {
  margin-top: 2px;
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 5px;
  border: 0;
  padding: 0;
  margin: 0;
}

.escala,
.binario {
  display: grid;
  gap: 5px;
}

.escala {
  grid-template-columns: repeat(5, 1fr);
}

.binario {
  grid-template-columns: repeat(2, 1fr);
}

.grado,
.opcion {
  padding: 8px 0;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
  color: var(--tinta-media);
}

.grado.activo,
.opcion.si.activo {
  border-color: var(--movistar-azul);
  background: var(--movistar-azul);
  color: var(--tinta-inversa);
}

.opcion.no.activo {
  border-color: var(--alarma);
  background: var(--alarma);
  color: var(--tinta-inversa);
}

.pie-escala {
  display: flex;
  justify-content: space-between;
  font-size: var(--t-micro);
  color: var(--tinta-suave);
}

.nps {
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  gap: 3px;
}

.celda-nps {
  padding: 6px 0;
  border: 1px solid var(--linea);
  border-radius: 3px;
  background: var(--superficie);
  font-size: var(--t-xs);
  color: var(--tinta-media);
}

.celda-nps.activo {
  border-color: var(--movistar-noche);
  background: var(--movistar-noche);
  color: var(--tinta-inversa);
}

textarea,
select {
  padding: 7px 9px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
  resize: vertical;
}

select:disabled {
  background: var(--superficie-tenue);
  color: var(--tinta-suave);
}

.resultado {
  font-weight: 600;
}

.resultado.vendido {
  color: var(--verde);
}
.resultado.rechazado {
  color: var(--alarma);
}
.resultado.sin_contacto {
  color: var(--tinta-media);
}

.obligatorio {
  color: var(--alarma);
  letter-spacing: 0.09em;
}

.opcional {
  color: var(--tinta-suave);
  letter-spacing: 0.09em;
}

.acciones {
  display: flex;
  gap: var(--gap-sm);
  padding-top: var(--gap-sm);
  border-top: 1px solid var(--linea);
}

.secundario,
.primario {
  flex: 1;
  padding: 9px;
  border-radius: var(--r);
  font-size: var(--t-sm);
  font-weight: 600;
}

.secundario {
  border: 1px solid var(--linea);
  background: var(--superficie);
  color: var(--tinta-media);
}

.primario {
  border: 1px solid var(--movistar-noche);
  background: var(--movistar-noche);
  color: var(--tinta-inversa);
}

.primario:disabled {
  border-color: var(--linea);
  background: var(--superficie);
  color: var(--tinta-suave);
  cursor: not-allowed;
}
</style>
