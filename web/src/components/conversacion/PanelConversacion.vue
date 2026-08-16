<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

import EntradaCliente from './EntradaCliente.vue'
import FilaDialogo from './FilaDialogo.vue'
import SpeechRecomendado from './SpeechRecomendado.vue'
import TermometroReceptividad from './TermometroReceptividad.vue'
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { GuiaCopiloto, Intercambio, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  oferta: Recomendacion | null
  speechInicial: GuiaCopiloto | null
  intercambios: Intercambio[]
  copilotoPensando: boolean
  temperatura: number
  estado: string
  quedanTurnos: boolean
  cerrada: boolean
  hayGestion: boolean
  cargando: boolean
}>()

defineEmits<{ siguiente: []; iniciar: []; decir: [texto: string] }>()

const hilo = ref<HTMLElement | null>(null)

watch(
  () => props.intercambios.length,
  async () => {
    await nextTick()
    hilo.value?.scrollTo({ top: hilo.value.scrollHeight, behavior: 'smooth' })
  },
)
</script>

<template>
  <section class="columna" aria-label="Conversación">
    <!-- Arriba: cómo convencerlo. -->
    <SpeechRecomendado
      :guia="speechInicial"
      :oferta="oferta"
      :en-curso="hayGestion && !cerrada"
    />

    <TermometroReceptividad :temperatura="temperatura" :estado="estado" />

    <!-- Abajo: lo que dice el cliente y lo que hay que responderle. -->
    <TituloPanel
      texto="Diálogo"
      acento="ninguno"
      :contador="`${intercambios.length} turnos`"
    />

    <div class="encabezados" aria-hidden="true">
      <span class="micro">El cliente dice</span>
      <span class="micro destacado">Usted debe decir</span>
    </div>

    <div ref="hilo" class="hilo">
      <ul v-if="intercambios.length">
        <FilaDialogo
          v-for="(intercambio, i) in intercambios"
          :key="i"
          :intercambio="intercambio"
          :actual="i === intercambios.length - 1"
        />
      </ul>
      <div v-else class="vacio">
        <span class="marca-vacio" aria-hidden="true">‹ ›</span>
        <p class="titulo-vacio">
          {{ hayGestion ? 'Escuchando al cliente' : 'Llamada sin iniciar' }}
        </p>
        <p class="pista">
          {{
            hayGestion
              ? 'Escriba abajo lo que dice el cliente y el copiloto le dirá qué responder.'
              : 'Pulse «Iniciar gestión» para abrir la llamada y recibir el speech.'
          }}
        </p>
      </div>
    </div>

    <EntradaCliente
      :habilitada="hayGestion && !cerrada"
      :pensando="copilotoPensando"
      @enviar="$emit('decir', $event)"
    />

    <div class="pie">
      <button
        v-if="!hayGestion"
        class="boton primario"
        type="button"
        :disabled="cargando"
        @click="$emit('iniciar')"
      >
        {{ cargando ? 'Abriendo…' : 'Iniciar gestión' }}
      </button>
      <button
        v-else
        class="boton"
        type="button"
        :disabled="!quedanTurnos || cerrada || copilotoPensando"
        @click="$emit('siguiente')"
      >
        {{ quedanTurnos ? 'Siguiente turno del guion' : 'Guion completo' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.columna {
  display: grid;
  grid-template-rows: auto auto auto auto minmax(0, 1fr) auto auto;
  min-height: 0;
  overflow: hidden;
  background: var(--superficie);
}

.encabezados {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px solid var(--linea);
}

.encabezados span {
  padding: 6px var(--gap);
}

.encabezados span:first-child {
  border-right: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

.destacado {
  color: var(--movistar-noche);
}

.hilo {
  overflow-y: auto;
  min-height: 0;
}

/* El hilo vacío ocupa mucho: se llena con la instrucción, centrada. */
.vacio {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 100%;
  min-height: 220px;
  padding: var(--gap-xl) var(--gap);
  text-align: center;
}

.marca-vacio {
  font-family: var(--fuente-cifra);
  font-size: 30px;
  color: var(--borde-cielo);
  letter-spacing: -0.08em;
}

.titulo-vacio {
  font-size: var(--t-md);
  font-weight: 600;
  color: var(--tinta-media);
}

.pista {
  max-width: 340px;
  font-size: var(--t-sm);
  line-height: 1.45;
  color: var(--tinta-suave);
}

.pie {
  padding: 10px var(--gap);
  border-top: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

.boton {
  width: 100%;
  padding: 9px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  font-size: var(--t-base);
  font-weight: 600;
}

.boton.primario {
  border-color: #008edb;
  background: linear-gradient(180deg, #08a5ef 0%, #0196df 100%);
  color: var(--tinta-inversa);
  box-shadow: 0 3px 8px rgba(1, 157, 244, 0.22);
}

.boton:not(:disabled):hover {
  border-color: var(--movistar-azul-hondo);
  background: var(--superficie-tenue);
}

.boton.primario:not(:disabled):hover {
  border-color: var(--movistar-azul);
  background: #008edb;
}

.boton:disabled {
  background: var(--superficie);
  border-color: var(--linea);
  color: var(--tinta-suave);
  cursor: not-allowed;
}

@media (max-width: 1180px) {
  .columna {
    grid-template-rows: none;
    display: flex;
    flex-direction: column;
    overflow: visible;
  }

  .hilo {
    max-height: 420px;
  }
}

@media (max-width: 640px) {
  .encabezados {
    display: none;
  }
}
</style>
