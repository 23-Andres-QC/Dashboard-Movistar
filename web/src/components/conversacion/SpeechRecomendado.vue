<script setup lang="ts">
import { computed } from 'vue'

import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { GuiaCopiloto, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  /** Speech vivo del copiloto; manda sobre el estático de la oferta. */
  guia: GuiaCopiloto | null
  oferta: Recomendacion | null
  enCurso: boolean
}>()

const texto = computed(() => props.guia?.que_decir || props.oferta?.speech || '')

const pregunta = computed(() => props.guia?.pregunta_seguimiento ?? null)

/** El motor se abstuvo o no pudo fundamentar: no se presenta como speech. */
const inseguro = computed(
  () => props.guia !== null && (!props.guia.grounded || props.guia.requiere_revision),
)

const origen = computed(() => (props.guia ? 'Copiloto' : 'Guion base'))
</script>

<template>
  <section class="speech">
    <TituloPanel texto="Cómo convencerlo" acento="azul" :vivo="enCurso" :contador="origen" />

    <div v-if="inseguro" class="alerta">
      <span class="micro titulo">Revisión humana</span>
      <p>{{ guia?.resumen || 'El copiloto no encontró conocimiento autorizado para responder.' }}</p>
    </div>

    <div v-else-if="texto" class="cuerpo">
      <p class="texto">{{ texto }}</p>
      <p v-if="pregunta" class="pregunta">
        <span class="micro etiqueta">Y pregunte</span>
        {{ pregunta }}
      </p>
    </div>

    <p v-else class="vacio">Inicie la gestión para recibir el speech personalizado.</p>
  </section>
</template>

<style scoped>
.speech {
  border-bottom: 1px solid var(--linea);
}

.cuerpo {
  padding: var(--gap) var(--gap-lg) var(--gap);
  border-left: 3px solid var(--movistar-azul);
  background: var(--movistar-cielo);
}

.texto {
  font-size: var(--t-md);
  line-height: 1.5;
  color: var(--movistar-noche);
}

.pregunta {
  margin-top: var(--gap-sm);
  padding-top: var(--gap-sm);
  border-top: 1px solid var(--borde-cielo);
  font-size: var(--t-base);
  line-height: 1.45;
  color: var(--tinta-media);
}

.etiqueta {
  display: block;
  color: var(--movistar-azul);
}

.alerta {
  padding: var(--gap) var(--gap-lg);
  border-left: 3px solid var(--alarma);
  background: var(--risk-fondo);
  font-size: var(--t-base);
  line-height: 1.45;
}

.alerta .titulo {
  display: block;
  color: var(--alarma);
}

.vacio {
  padding: var(--gap) var(--gap-lg);
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}
</style>
