<script setup lang="ts">
import logoUrl from '@/assets/logo-movistar.png'

defineProps<{ error: string | null; cargando: boolean }>()
const emit = defineEmits<{ probar: [dni: string] }>()

/** Matriz de la demo: tipo de cliente × desenlace. */
const EJEMPLOS = [
  { dni: '45789123', pista: 'Antiguo, alto consumo · Movistar Total · vendido' },
  { dni: '70112384', pista: 'Nuevo, sin historial · plan de entrada · rechazado' },
  { dni: '08954412', pista: 'Antiguo en riesgo · retención, no MT · vendido tras rebate' },
  { dni: '76340219', pista: 'Nuevo, portabilidad digital · 45 GB + equipo · vendido' },
]
</script>

<template>
  <section class="vacio panel">
    <img :src="logoUrl" alt="Movistar" class="simbolo" />
    <p v-if="cargando" class="mensaje">Consultando…</p>
    <template v-else>
      <p v-if="error" class="error">{{ error }}</p>
      <p class="mensaje">Busque un DNI para abrir la gestión.</p>
      <ul class="ejemplos">
        <li v-for="e in EJEMPLOS" :key="e.dni">
          <button class="cifra dni" type="button" @click="emit('probar', e.dni)">
            {{ e.dni }}
          </button>
          <span class="pista">{{ e.pista }}</span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.vacio {
  margin: var(--gap-lg);
  padding: var(--gap-xl);
  text-align: center;
}

.simbolo {
  height: 46px;
  width: auto;
  margin: 0 auto var(--gap-lg);
  display: block;
}

.mensaje {
  font-size: var(--t-md);
  color: var(--tinta-media);
}

.error {
  margin-bottom: var(--gap-sm);
  padding: 7px var(--gap);
  display: inline-block;
  border: 1px solid var(--alarma);
  border-radius: var(--r);
  background: var(--risk-fondo);
  color: var(--alarma);
  font-size: var(--t-sm);
}

.ejemplos {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-top: var(--gap-lg);
}

.ejemplos li {
  display: grid;
  grid-template-columns: 96px 1fr;
  align-items: center;
  gap: var(--gap-sm);
  text-align: left;
}

.dni {
  padding: 4px 9px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
  color: var(--movistar-azul);
}

.pista {
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}
</style>
