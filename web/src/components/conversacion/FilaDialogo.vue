<script setup lang="ts">
import { computed } from 'vue'

import { ETIQUETA_MOTIVO } from '@/api/etiquetas'
import type { Intercambio, Motivo } from '@/api/tipos'

const props = defineProps<{ intercambio: Intercambio; actual: boolean }>()

const objecion = computed(() => {
  const cat = props.intercambio.guia?.objecion_categoria
  if (!cat || cat === 'otro') return null
  return ETIQUETA_MOTIVO[cat as Motivo] ?? cat
})

const confianza = computed(() => {
  const c = props.intercambio.guia?.objecion_confianza
  return c === null || c === undefined ? null : Math.round(c * 100)
})

const inseguro = computed(() => {
  const g = props.intercambio.guia
  return g !== null && (!g.grounded || g.requiere_revision)
})

/** Cuando el copiloto solo puede pedir aclaración y hay línea de guion, manda
 *  el guion: repetir «cuénteme más» en cada turno no ayuda al asesor. */
const usaRespaldo = computed(() => {
  const g = props.intercambio.guia
  if (!g || !props.intercambio.respaldo) return false
  // El motor devuelve `otro` cuando no reconoce la objeción, no null.
  const sinObjecion = !g.objecion_categoria || g.objecion_categoria === 'otro'
  return g.recommended_action === 'ASK_CLARIFYING_QUESTION' && sinObjecion
})

const queDecir = computed(() =>
  usaRespaldo.value ? props.intercambio.respaldo! : (props.intercambio.guia?.que_decir ?? ''),
)
</script>

<template>
  <li class="fila" :class="{ actual }">
    <!-- Izquierda: lo que dice el cliente, literal. -->
    <div class="lado cliente">
      <span class="micro etiqueta">{{ intercambio.etiqueta }}</span>
      <p class="dicho">{{ intercambio.dijo }}</p>
      <p v-if="objecion" class="objecion">
        <span class="micro">{{ objecion }}</span>
        <span v-if="confianza !== null" class="cifra confianza">{{ confianza }}%</span>
      </p>
    </div>

    <!-- Derecha: lo que el asesor debe responder. -->
    <div class="lado asesor">
      <p v-if="intercambio.pendiente" class="pensando">
        <span class="punto" aria-hidden="true"></span>
        El copiloto está redactando la respuesta…
      </p>

      <p v-else-if="intercambio.error" class="fallo">{{ intercambio.error }}</p>

      <template v-else-if="intercambio.guia">
        <p v-if="inseguro" class="fallo">
          {{ intercambio.guia.resumen || 'Sin conocimiento autorizado: no improvise.' }}
        </p>
        <template v-else>
          <p class="responder">{{ queDecir }}</p>
          <p v-if="!usaRespaldo && intercambio.guia.pregunta_seguimiento" class="pregunta">
            {{ intercambio.guia.pregunta_seguimiento }}
          </p>
          <p class="porque">
            <span class="micro fuente">{{ usaRespaldo ? 'Guion base' : 'Copiloto' }}</span>
            <template v-if="!usaRespaldo && intercambio.guia.resumen">
              {{ intercambio.guia.resumen }}
            </template>
          </p>
        </template>
      </template>
    </div>
  </li>
</template>

<style scoped>
.fila {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px solid var(--linea);
}

.lado {
  padding: 11px var(--gap);
}

.cliente {
  border-right: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

.etiqueta {
  display: block;
  margin-bottom: 3px;
}

.dicho {
  font-size: var(--t-base);
  line-height: 1.45;
  color: var(--tinta-media);
}

.objecion {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 6px;
}

.objecion .micro {
  padding: 2px 7px;
  border: 1px solid var(--ambar);
  border-radius: 3px;
  color: var(--ambar);
  background: var(--superficie);
}

.confianza {
  font-size: var(--t-micro);
  color: var(--tinta-suave);
}

.responder {
  font-size: var(--t-base);
  line-height: 1.45;
  color: var(--tinta);
}

.pregunta {
  margin-top: 6px;
  padding-left: 9px;
  border-left: 2px solid var(--movistar-azul);
  font-size: var(--t-sm);
  line-height: 1.4;
  color: var(--movistar-noche);
}

.porque {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 7px;
  font-size: var(--t-xs);
  line-height: 1.4;
  color: var(--tinta-suave);
}

.fuente {
  padding: 1px 6px;
  border: 1px solid var(--linea);
  border-radius: 3px;
  white-space: nowrap;
}

.pensando {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}

.punto {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--movistar-azul);
  animation: latido 1.1s ease-in-out infinite;
}

@keyframes latido {
  50% {
    opacity: 0.25;
  }
}

.fallo {
  font-size: var(--t-sm);
  line-height: 1.4;
  color: var(--alarma);
}

/* El turno vivo manda; los anteriores quedan de contexto. */
.fila:not(.actual) .dicho,
.fila:not(.actual) .responder {
  color: var(--tinta-suave);
}

.fila:not(.actual) .responder {
  font-size: var(--t-sm);
}

.fila:not(.actual) .pregunta,
.fila:not(.actual) .porque {
  display: none;
}

.actual .responder {
  font-weight: 500;
}

@media (max-width: 640px) {
  .fila {
    grid-template-columns: 1fr;
  }

  .cliente {
    border-right: 0;
    border-bottom: 1px solid var(--linea);
  }
}
</style>
