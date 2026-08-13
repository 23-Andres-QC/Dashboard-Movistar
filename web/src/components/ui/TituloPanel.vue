<script setup lang="ts">
defineProps<{
  texto: string
  contador?: string | number
  /** Acento de color a la izquierda del rótulo, para jerarquizar secciones. */
  acento?: 'azul' | 'ambar' | 'verde' | 'ninguno'
  /** Esto sí cambia durante la llamada: se marca como en vivo. */
  vivo?: boolean
}>()
</script>

<template>
  <header class="titulo">
    <span v-if="acento && acento !== 'ninguno'" class="tick" :class="acento" aria-hidden="true" />
    <span class="micro rotulo">{{ texto }}</span>
    <span v-if="vivo" class="micro insignia">
      <span class="punto" aria-hidden="true"></span>
      En vivo
    </span>
    <span v-if="contador !== undefined" class="cifra contador">{{ contador }}</span>
  </header>
</template>

<style scoped>
.titulo {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 10px var(--gap-lg) 9px;
  border-bottom: 1px solid var(--linea);
  background: var(--superficie-tenue);
}

.tick {
  width: 3px;
  height: 12px;
  border-radius: 2px;
  flex: none;
}

.tick.azul {
  background: var(--movistar-azul);
}
.tick.ambar {
  background: var(--ambar);
}
.tick.verde {
  background: var(--verde);
}

.rotulo {
  color: var(--tinta-media);
}

.insignia {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 1px 6px;
  border: 1px solid var(--verde);
  border-radius: 3px;
  color: var(--verde);
  letter-spacing: 0.08em;
}

.punto {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--verde);
  animation: latido 2s ease-in-out infinite;
}

@keyframes latido {
  50% {
    opacity: 0.3;
  }
}

.contador {
  margin-left: auto;
  font-size: var(--t-xs);
  color: var(--tinta-suave);
}
</style>
