<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'
import type { Sugerencia } from '@/api/tipos'

defineProps<{ sugerencias: Sugerencia[]; enCurso: boolean }>()
</script>

<template>
  <section class="pila">
    <TituloPanel
      texto="Sugerencias clave"
      acento="azul"
      :vivo="enCurso"
      :contador="sugerencias.length"
    />
    <ul v-if="sugerencias.length" class="lista">
      <!-- La más reciente arriba: el asesor lee de arriba hacia abajo. -->
      <li v-for="(s, i) in sugerencias" :key="`${s.titulo}-${i}`" class="sugerencia" :class="s.tipo">
        <span class="micro titulo">{{ s.titulo }}</span>
        <p class="texto">{{ s.texto }}</p>
      </li>
    </ul>
    <p v-else class="vacio">Avance el guion para recibir sugerencias.</p>
  </section>
</template>

<style scoped>
.pila {
  border-top: 1px solid var(--linea);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.lista {
  overflow-y: auto;
  padding: var(--gap-sm) var(--gap);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sugerencia {
  padding: 7px 9px;
  border-left: 3px solid var(--linea);
  border-radius: 0 var(--r) var(--r) 0;
  background: var(--superficie-tenue);
}

.info {
  border-left-color: var(--estado-info);
  background: var(--info-fondo);
}
.warn {
  border-left-color: var(--estado-warn);
  background: var(--warn-fondo);
}
.risk {
  border-left-color: var(--estado-risk);
  background: var(--risk-fondo);
}
.good {
  border-left-color: var(--estado-good);
  background: var(--good-fondo);
}

.info .titulo {
  color: var(--movistar-noche);
}
.warn .titulo {
  color: var(--ambar);
}
.risk .titulo {
  color: var(--alarma);
}
.good .titulo {
  color: var(--verde);
}

.texto {
  margin-top: 2px;
  font-size: var(--t-sm);
  line-height: 1.4;
}

.vacio {
  padding: var(--gap);
  font-size: var(--t-sm);
  color: var(--tinta-suave);
}
</style>
