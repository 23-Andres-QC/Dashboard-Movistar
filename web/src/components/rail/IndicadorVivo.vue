<script setup lang="ts">
defineProps<{ activo: boolean }>()
</script>

<template>
  <div class="vivo" :class="{ activo }">
    <span class="punto" aria-hidden="true"></span>
    <span class="micro">{{ activo ? 'En llamada' : 'Sin llamada' }}</span>
  </div>
</template>

<style scoped>
.vivo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.vivo .micro {
  color: rgba(255, 255, 255, 0.5);
}

.punto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
}

.activo .micro {
  color: var(--tinta-inversa);
}

.activo .punto {
  background: #4ad991;
  animation: latido 2s ease-in-out infinite;
}

@keyframes latido {
  50% {
    opacity: 0.35;
  }
}
</style>
