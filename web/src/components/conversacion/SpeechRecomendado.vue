<script setup lang="ts">
import { computed } from 'vue'

import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { GuiaCopiloto, Recomendacion } from '@/api/tipos'

const props = defineProps<{
  /** Speech vivo del copiloto; manda sobre el estático de la oferta. */
  guia: GuiaCopiloto | null
  oferta: Recomendacion | null
  enCurso: boolean
  mostrarDetalle: boolean
}>()

const texto = computed(() => props.guia?.que_decir || props.oferta?.speech || '')

const pregunta = computed(() => props.guia?.pregunta_seguimiento ?? null)

/** El motor se abstuvo o no pudo fundamentar: no se presenta como speech. */
const inseguro = computed(
  () => props.guia !== null && (!props.guia.grounded || props.guia.requiere_revision),
)

const origen = computed(() => (props.guia ? 'Copiloto' : ''))
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

      <div v-if="mostrarDetalle && oferta" class="detalle">
        <div class="detalle-cabecera">
          <span class="micro">Detalle del plan</span>
          <span class="micro confianza">Datos para sustentar la oferta</span>
        </div>
        <div class="metricas">
          <div><span class="micro">Precio mensual</span><strong>S/ {{ oferta.precio_mensual ?? '—' }}</strong></div>
          <div><span class="micro">Datos incluidos</span><strong>{{ oferta.gb_incluidos ? `${oferta.gb_incluidos} GB` : '—' }}</strong></div>
          <div><span class="micro">Ahorro</span><strong>S/ {{ oferta.ahorro ?? '—' }}</strong></div>
          <div><span class="micro">Instalación</span><strong>S/ {{ oferta.instalacion ?? 0 }}</strong></div>
        </div>
        <ul v-if="oferta.explicacion?.length" class="explicacion">
          <li v-for="item in oferta.explicacion" :key="item">{{ item }}</li>
        </ul>
        <div v-if="oferta.angulos?.length" class="angulos">
          <span class="micro">Ángulos de conversación</span>
          <p v-for="angulo in oferta.angulos" :key="angulo.titulo"><strong>{{ angulo.titulo }}:</strong> {{ angulo.texto }}</p>
        </div>
      </div>
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

.detalle {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--borde-cielo);
}

.detalle-cabecera {
  display: flex;
  justify-content: space-between;
  gap: var(--gap);
  color: var(--movistar-noche);
}

.confianza {
  color: var(--verde);
}

.metricas {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 9px;
}

.metricas div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 7px 9px;
  border: 1px solid var(--borde-cielo);
  border-radius: var(--r-chico);
  background: rgba(255, 255, 255, 0.56);
}

.metricas strong {
  color: var(--movistar-noche);
  font-size: var(--t-base);
}

.explicacion {
  display: grid;
  gap: 4px;
  margin-top: 10px;
  color: var(--tinta-media);
  font-size: var(--t-sm);
}

.explicacion li::before {
  content: '✓';
  margin-right: 7px;
  color: var(--verde);
  font-weight: 700;
}

.angulos {
  display: grid;
  gap: 4px;
  margin-top: 10px;
  color: var(--tinta-media);
  font-size: var(--t-sm);
}

.angulos p {
  line-height: 1.35;
}

.angulos strong {
  color: var(--movistar-noche);
}

.etiqueta {
  display: block;
  color: var(--movistar-azul-hondo);
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

@media (max-width: 760px) {
  .metricas {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
