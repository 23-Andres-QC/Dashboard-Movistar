<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'
import { ETIQUETA_MOTIVO } from '@/api/etiquetas'
import type { Motivo, Rebate } from '@/api/tipos'

defineProps<{ rebates: Rebate[]; objecionActiva: Motivo | null }>()
</script>

<template>
  <section v-if="rebates.length" class="bloque">
    <TituloPanel
      texto="Rebates por objeción"
      acento="ambar"
      :vivo="objecionActiva !== null"
      :contador="rebates.length"
    />
    <ul>
      <li
        v-for="rebate in rebates"
        :key="rebate.objecion"
        class="rebate"
        :class="{ activo: rebate.objecion === objecionActiva }"
      >
        <div class="cabecera">
          <span class="micro objecion">{{ ETIQUETA_MOTIVO[rebate.objecion] }}</span>
          <span v-if="rebate.objecion === objecionActiva" class="micro marca">Detectada</span>
        </div>
        <p class="cita">«{{ rebate.cita }}»</p>
        <p class="texto">{{ rebate.texto }}</p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.bloque {
  border-bottom: 1px solid var(--linea);
}

.rebate {
  padding: 11px var(--gap-lg) 12px;
  border-bottom: 1px solid var(--superficie-tenue);
  /* La barra ámbar existe siempre, transparente: al llegar la objeción cambia
     de color en lugar de empujar el contenido. */
  border-left: 3px solid transparent;
  transition: background-color 160ms ease, border-color 160ms ease;
}

.rebate:last-child {
  border-bottom: 0;
}

.activo {
  border-left-color: var(--ambar);
  background: var(--warn-fondo);
}

.cabecera {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gap-sm);
}

.objecion {
  color: var(--tinta-media);
}

.activo .objecion {
  color: var(--ambar);
}

.marca {
  padding: 1px 6px;
  border: 1px solid var(--ambar);
  border-radius: 3px;
  color: var(--ambar);
  letter-spacing: 0.1em;
}

.cita {
  margin-top: 3px;
  font-size: var(--t-sm);
  font-style: italic;
  color: var(--tinta-suave);
}

.texto {
  margin-top: 5px;
  font-size: var(--t-base);
  line-height: 1.45;
  color: var(--tinta);
}

/* Lo que hay que decir ahora se lee un punto más fuerte. */
.activo .texto {
  font-weight: 500;
  color: var(--movistar-noche);
}
</style>
