<script setup lang="ts">
import BuscadorDni from './BuscadorDni.vue'
import Cronometro from './Cronometro.vue'
import IndicadorVivo from './IndicadorVivo.vue'
import logoUrl from '@/assets/logo-movistar.png'

defineProps<{
  dniInicial?: string
  cargando?: boolean
  inicioLlamada: number | null
  llamadaCerrada: boolean
  nombreAsesor: string
  idAsesor: string
}>()

defineEmits<{ buscar: [dni: string] }>()
</script>

<template>
  <header class="rail">
    <div class="marca">
      <img :src="logoUrl" alt="Movistar" class="simbolo" />
      <span class="nombre-marca">movistar</span>
      <span class="filete" aria-hidden="true"></span>
      <span class="micro producto">Next Best Offer · Consola del asesor</span>
    </div>

    <BuscadorDni
      :valor-inicial="dniInicial"
      :cargando="cargando"
      @buscar="$emit('buscar', $event)"
    />

    <div class="derecha">
      <Cronometro :inicio="inicioLlamada" :detenido="llamadaCerrada" />
      <span class="separador" aria-hidden="true"></span>
      <div class="asesor">
        <span class="nombre">{{ nombreAsesor }}</span>
        <span class="cifra id">{{ idAsesor }}</span>
      </div>
      <span class="separador" aria-hidden="true"></span>
      <IndicadorVivo :activo="inicioLlamada !== null && !llamadaCerrada" />
    </div>
  </header>
</template>

<style scoped>
.rail {
  display: flex;
  align-items: center;
  gap: var(--gap-lg);
  height: var(--rail-alto);
  padding: 0 var(--gap-lg);
  background: linear-gradient(105deg, #082536 0%, var(--movistar-noche) 54%, #0e3348 100%);
  color: var(--tinta-inversa);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 10px rgba(11, 39, 57, 0.16);
}

.marca {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  min-width: 0;
}

/* Símbolo oficial; el nombre va como texto, no como imitación del lettering. */
.simbolo {
  height: 26px;
  width: auto;
  display: block;
}

.nombre-marca {
  font-size: 20px;
  font-weight: 500;
  letter-spacing: -0.005em;
  line-height: 1;
  color: var(--tinta-inversa);
}

.filete {
  width: 1px;
  height: 20px;
  margin: 0 4px;
  background: rgba(255, 255, 255, 0.2);
}

.producto {
  color: rgba(255, 255, 255, 0.55);
  white-space: nowrap;
  font-size: 10px;
}

.derecha {
  display: flex;
  align-items: center;
  gap: var(--gap);
  margin-left: auto;
}

.separador {
  width: 1px;
  height: 22px;
  background: rgba(255, 255, 255, 0.16);
}

.asesor {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.nombre {
  font-size: var(--t-sm);
}

.id {
  font-size: var(--t-micro);
  color: rgba(255, 255, 255, 0.5);
}

@media (max-width: 1180px) {
  .producto {
    display: none;
  }
}

@media (max-width: 768px) {
  .rail {
    height: auto;
    flex-wrap: wrap;
    gap: var(--gap-sm);
    padding: var(--gap-sm) var(--gap);
  }

  .derecha {
    width: 100%;
    margin-left: 0;
  }
}
</style>
