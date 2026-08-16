<script setup lang="ts">
import { computed } from 'vue'

defineProps<{ plan: string | null; facturacion: number | null }>()

/** Cuadro propio, separado de la oferta: el contraste entre lo que tiene y lo
 *  que se le ofrece se lee de un vistazo. */
const flecha = computed(() => '↓')
</script>

<template>
  <section class="actual tarjeta-suelta">
    <div class="linea">
      <span class="micro etiqueta">Tiene hoy</span>
      <span class="plan">{{ plan ?? 'Sin plan contratado' }}</span>
      <span v-if="facturacion !== null" class="cifra monto">S/ {{ facturacion }}</span>
    </div>
    <span class="flecha" aria-hidden="true">{{ flecha }}</span>
  </section>
</template>

<style scoped>
.actual {
  position: relative;
  padding: 10px var(--gap-lg) 14px;
  background: var(--superficie-tenue);
}

.linea {
  display: flex;
  align-items: baseline;
  gap: var(--gap-sm);
}

.etiqueta {
  color: var(--tinta-suave);
  white-space: nowrap;
}

/* Tachado: es lo que deja de tener si acepta. */
.plan {
  flex: 1;
  min-width: 0;
  font-size: var(--t-base);
  color: var(--tinta-suave);
  text-decoration: line-through;
  text-decoration-color: var(--tinta-suave);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monto {
  font-size: var(--t-sm);
  color: var(--tinta-suave);
  text-decoration: line-through;
  white-space: nowrap;
}

.flecha {
  position: absolute;
  left: 50%;
  bottom: -11px;
  transform: translateX(-50%);
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border: 1px solid var(--linea);
  border-radius: 50%;
  background: var(--superficie);
  color: var(--movistar-azul-hondo);
  font-size: 12px;
  line-height: 1;
  z-index: 1;
}
</style>
