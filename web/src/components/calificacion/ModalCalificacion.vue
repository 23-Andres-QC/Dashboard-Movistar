<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { ETIQUETA_RESULTADO } from '@/api/etiquetas'
import type { CalificacionEnvio, MedioProbatorio, Motivo, Resultado } from '@/api/tipos'

defineProps<{
  resultado: Exclude<Resultado, 'en_curso'>
  motivoInicial: Motivo | null
  sugerida: { facilidad_venta: number; oferta_fue_pertinente: boolean } | null
}>()

const emit = defineEmits<{
  enviar: [datos: CalificacionEnvio, motivo: Motivo | null, medio: MedioProbatorio | null]
  omitir: []
}>()

const facilidad = ref<number | null>(null)
const recomendaria = ref<number | null>(null)
const enviando = ref(false)
const dialogo = ref<HTMLElement | null>(null)

const completo = () => facilidad.value !== null && recomendaria.value !== null

function enviar() {
  if (!completo() || enviando.value) return
  enviando.value = true
  emit(
    'enviar',
    {
      facilidad_venta: facilidad.value!,
      // Compatibilidad con el campo histórico: 7–10 se considera pertinente.
      oferta_fue_pertinente: recomendaria.value! >= 7,
      nps_declarado: recomendaria.value!,
      comentario: null,
    },
    null,
    null,
  )
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
        <span class="micro eyebrow">Encuesta rápida</span>
        <h2 id="titulo-calificacion" class="titulo">Calificar la gestión</h2>
        <p class="ayuda">
          Resultado:
          <span class="resultado" :class="resultado">{{ ETIQUETA_RESULTADO[resultado] }}</span>
        </p>
      </header>

      <fieldset class="campo">
        <legend>¿Qué tan fácil fue usar la consola?</legend>
        <div class="escala">
          <button
            v-for="n in 10"
            :key="n"
            type="button"
            class="cifra grado"
            :class="{ activo: facilidad === n }"
            :aria-label="`${n} de 10`"
            :aria-pressed="facilidad === n"
            @click="facilidad = n"
          >
            {{ n }}
          </button>
        </div>
        <p class="pie-escala"><span>1 · muy difícil</span><span>10 · muy fácil</span></p>
      </fieldset>

      <fieldset class="campo">
        <legend>¿Recomendaría esta oferta?</legend>
        <div class="escala">
          <button
            v-for="n in 10"
            :key="n"
            type="button"
            class="cifra grado"
            :class="{ activo: recomendaria === n }"
            :aria-label="`${n} de 10`"
            :aria-pressed="recomendaria === n"
            @click="recomendaria = n"
          >
            {{ n }}
          </button>
        </div>
        <p class="pie-escala"><span>1 · nada probable</span><span>10 · totalmente probable</span></p>
      </fieldset>

      <footer class="acciones">
        <button type="button" class="secundario" @click="emit('omitir')">Omitir</button>
        <button type="button" class="primario" :disabled="!completo() || enviando" @click="enviar">
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
  width: min(500px, 100%);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.cabecera {
  padding-bottom: 14px;
  border-bottom: 1px solid var(--linea);
}

.eyebrow {
  color: var(--movistar-azul-hondo);
}

.titulo {
  margin-top: 4px;
  font-size: 21px;
  font-weight: 700;
}

.ayuda {
  margin-top: 4px;
  color: var(--tinta-suave);
  font-size: var(--t-sm);
}

.resultado {
  font-weight: 700;
}

.resultado.vendido { color: var(--verde); }
.resultado.rechazado { color: var(--alarma); }

.campo {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin: 0;
  padding: 0;
  border: 0;
}

legend {
  padding: 0;
  color: var(--tinta);
  font-size: var(--t-base);
  font-weight: 600;
}

.escala {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 5px;
}

.grado {
  padding: 10px 0;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  font-size: var(--t-sm);
}

.grado:hover,
.grado.activo {
  border-color: var(--movistar-azul);
  background: var(--movistar-azul);
  color: var(--tinta-inversa);
}

.pie-escala {
  display: flex;
  justify-content: space-between;
  color: var(--tinta-suave);
  font-size: var(--t-xs);
}

.acciones {
  display: flex;
  gap: var(--gap-sm);
  padding-top: 14px;
  border-top: 1px solid var(--linea);
}

.secundario,
.primario {
  flex: 1;
  padding: 10px;
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

@media (max-width: 520px) {
  .dialogo { padding: 18px; gap: 18px; }
  .escala { gap: 3px; }
  .grado { padding: 9px 0; }
}
</style>
