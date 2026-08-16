<script setup lang="ts">
import TituloPanel from '@/components/ui/TituloPanel.vue'
import { ETIQUETA_MOTIVO } from '@/api/etiquetas'
import type { Motivo, Rebate } from '@/api/tipos'

defineProps<{ rebates: Rebate[]; objecionActiva: Motivo | null }>()
</script>

<template>
  <section v-if="rebates.length" class="bloque tarjeta-suelta">
    <TituloPanel
      texto="Objeciones previstas"
      acento="ambar"
      :vivo="objecionActiva !== null"
      :contador="rebates.length"
    />
    <!-- Solo el nombre de la objeción: la respuesta la redacta el copiloto en
         vivo, así que repetir aquí un texto fijo sobraba. -->
    <ul class="chips">
      <li
        v-for="rebate in rebates"
        :key="rebate.objecion"
        class="chip"
        :class="{ activo: rebate.objecion === objecionActiva }"
      >
        <span class="punto" aria-hidden="true"></span>
        {{ ETIQUETA_MOTIVO[rebate.objecion] }}
      </li>
    </ul>
    <p v-if="objecionActiva" class="nota">
      Detectada en la llamada. La respuesta está en «Usted debe decir».
    </p>
  </section>
</template>

<style scoped>
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding: var(--gap) var(--gap-lg);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px;
  border: 1px solid var(--linea);
  border-radius: 999px;
  background: var(--superficie-tenue);
  font-size: var(--t-sm);
  color: var(--tinta-media);
  transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease;
}

.punto {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--linea);
}

.activo {
  border-color: rgba(143, 74, 11, 0.45);
  background: var(--warn-fondo);
  color: var(--ambar);
  font-weight: 600;
}

.activo .punto {
  background: var(--ambar);
}

.nota {
  padding: 0 var(--gap-lg) var(--gap);
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}
</style>
