<script setup lang="ts">
import type { Recomendacion } from '@/api/tipos'

defineProps<{ oferta: Recomendacion; planActual: string | null; facturacion: number | null }>()
</script>

<template>
  <section class="detalle tarjeta-suelta" aria-label="Detalle de la oferta">
    <header class="cabecera">
      <span class="micro">Detalle del plan</span>
      <span class="micro confianza">Datos para sustentar la oferta</span>
    </header>

    <div class="comparacion">
      <div class="antes">
        <span class="micro">Antes · tiene hoy</span>
        <strong>{{ planActual ?? 'Sin plan registrado' }}</strong>
        <span>{{ facturacion !== null ? `S/ ${facturacion} al mes` : 'Sin factura registrada' }}</span>
      </div>
      <span class="flecha" aria-hidden="true">→</span>
      <div class="ahora">
        <span class="micro">Ahora · oferta sugerida</span>
        <strong>{{ oferta.oferta }}</strong>
        <span>{{ oferta.precio_mensual !== null ? `S/ ${oferta.precio_mensual} al mes` : 'Consultar precio' }}</span>
      </div>
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
  </section>
</template>

<style scoped>
.detalle { overflow: hidden; }
.cabecera {
  display: flex;
  justify-content: space-between;
  gap: var(--gap);
  padding: 10px var(--gap-lg);
  border-bottom: 1px solid var(--linea);
  background: var(--superficie-tenue);
}
.confianza { color: var(--verde); }
.comparacion { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 8px; padding: 10px var(--gap-lg) 0; }
.antes, .ahora { display: flex; flex-direction: column; gap: 3px; min-width: 0; padding: 8px 9px; border-radius: var(--r-chico); }
.antes { background: var(--superficie-tenue); color: var(--tinta-media); }
.ahora { border: 1px solid rgba(29, 107, 69, 0.35); background: var(--good-fondo); color: var(--verde); }
.antes strong, .ahora strong { overflow: hidden; color: var(--tinta); font-size: var(--t-xs); text-overflow: ellipsis; white-space: nowrap; }
.ahora strong { color: var(--verde); }
.antes span:last-child, .ahora span:last-child { font-size: var(--t-xs); }
.flecha { color: var(--movistar-azul-hondo); font-size: 20px; font-weight: 700; }
.metricas { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; padding: 10px var(--gap-lg); }
.metricas div { display: flex; flex-direction: column; gap: 2px; padding: 7px; border: 1px solid var(--linea); border-radius: var(--r-chico); background: var(--superficie); }
.metricas strong { color: var(--movistar-noche); font-size: var(--t-sm); }
.explicacion { display: grid; gap: 4px; padding: 0 var(--gap-lg) 9px; color: var(--tinta-media); font-size: var(--t-xs); }
.explicacion li::before { content: '✓'; margin-right: 6px; color: var(--verde); font-weight: 700; }
.angulos { display: grid; gap: 4px; padding: 9px var(--gap-lg) 11px; border-top: 1px solid var(--linea-suave); color: var(--tinta-media); font-size: var(--t-xs); }
.angulos p { line-height: 1.35; }
.angulos strong { color: var(--movistar-noche); }
</style>
