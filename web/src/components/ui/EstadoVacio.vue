<script setup lang="ts">
import { computed } from 'vue'

defineProps<{ error: string | null; cargando: boolean }>()
const emit = defineEmits<{ probar: [dni: string] }>()

type ClientePrioridad = {
  dni: string
  clienteId: string
  nombre: string
  tipo: string
  contexto: string
  probabilidad: number
  resultado: string
}

/** Bandeja inicial de la demo. En producción esta lista vendrá del motor de priorización. */
const CLIENTES_PRIORIZADOS: ClientePrioridad[] = [
  {
    dni: '45789123',
    clienteId: 'CLI-0084213',
    nombre: 'Luis Ramírez Ccahuana',
    tipo: 'Antiguo',
    contexto: 'Alto consumo · Movistar Total',
    probabilidad: 78,
    resultado: 'Venta sugerida',
  },
  {
    dni: '08954412',
    clienteId: 'CLI-0037710',
    nombre: 'Rosa Quispe Mamani',
    tipo: 'Antiguo',
    contexto: 'Riesgo de baja · Retención',
    probabilidad: 66,
    resultado: 'Venta sugerida',
  },
  {
    dni: '76340219',
    clienteId: 'CLI-0224187',
    nombre: 'Kevin Huamán Ríos',
    tipo: 'Nuevo',
    contexto: 'Portabilidad digital · 45 GB + equipo',
    probabilidad: 48,
    resultado: 'Venta sugerida',
  },
  {
    dni: '70112384',
    clienteId: 'CLI-0219944',
    nombre: 'Andrea Salazar Pinto',
    tipo: 'Nuevo',
    contexto: 'Sin historial · Plan de entrada',
    probabilidad: 42,
    resultado: 'Requiere contacto',
  },
]

const clientes = computed(() => [...CLIENTES_PRIORIZADOS].sort((a, b) => b.probabilidad - a.probabilidad))
</script>

<template>
  <main class="inicio" aria-labelledby="titulo-inicio">
    <section class="cabecera-inicio">
      <div>
        <p class="micro eyebrow">Bandeja comercial</p>
        <h1 id="titulo-inicio">Clientes priorizados</h1>
        <p class="subtitulo">
          Seleccione un cliente para abrir su recomendación y comenzar la gestión.
        </p>
      </div>
      <div class="resumen">
        <span class="cifra total">{{ clientes.length }}</span>
        <span class="micro">clientes disponibles</span>
      </div>
    </section>

    <div v-if="cargando" class="estado-carga" role="status">Consultando clientes…</div>
    <div v-else>
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <div class="tabla-wrap">
        <div class="fila encabezado" aria-hidden="true">
          <span>Cliente</span>
          <span>ID cliente</span>
          <span>DNI</span>
          <span>Perfil comercial</span>
          <span>Probabilidad</span>
          <span></span>
        </div>

        <button
          v-for="cliente in clientes"
          :key="cliente.dni"
          class="fila cliente"
          type="button"
          @click="emit('probar', cliente.dni)"
        >
          <span class="identidad">
            <strong>{{ cliente.nombre }}</strong>
            <small>{{ cliente.tipo }}</small>
          </span>
          <span class="cifra dato">{{ cliente.clienteId }}</span>
          <span class="cifra dni">{{ cliente.dni }}</span>
          <span class="perfil">
            <span>{{ cliente.contexto }}</span>
            <small>{{ cliente.resultado }}</small>
          </span>
          <span class="probabilidad">
            <span class="barra"><span :style="{ width: `${cliente.probabilidad}%` }"></span></span>
            <strong class="cifra">{{ cliente.probabilidad }}%</strong>
          </span>
          <span class="abrir" aria-hidden="true">Abrir <span>→</span></span>
        </button>
      </div>
    </div>
  </main>
</template>

<style scoped>
.inicio {
  width: min(calc(100% - 48px), var(--ancho-max));
  margin: 16px auto 0;
  padding: 26px 28px 28px;
  background: var(--superficie);
  border: 1px solid var(--linea);
  border-radius: 12px;
  box-shadow: var(--sombra-2);
}

.cabecera-inicio {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--gap-lg);
  padding-bottom: 22px;
  border-bottom: 1px solid var(--linea);
}

.eyebrow {
  margin-bottom: 6px;
  color: var(--movistar-azul-hondo);
}

h1 {
  color: var(--movistar-noche);
  font-size: 26px;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.subtitulo {
  margin-top: 8px;
  color: var(--tinta-suave);
  font-size: var(--t-base);
}

.resumen {
  display: flex;
  align-items: baseline;
  gap: 7px;
  color: var(--tinta-suave);
  white-space: nowrap;
}

.total {
  color: var(--movistar-noche);
  font-size: 26px;
  font-weight: 700;
}

.tabla-wrap {
  padding-top: 10px;
}

.fila {
  display: grid;
  grid-template-columns: minmax(190px, 1.2fr) 145px 120px minmax(245px, 1.5fr) 190px 72px;
  align-items: center;
  column-gap: var(--gap-lg);
  width: 100%;
}

.encabezado {
  min-height: 34px;
  padding: 0 14px;
  color: var(--tinta-suave);
  font-family: var(--fuente-micro);
  font-size: var(--t-micro);
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.cliente {
  min-height: 76px;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-top-color: var(--linea-suave);
  background: var(--superficie);
  text-align: left;
  transition: background-color 140ms ease, border-color 140ms ease, transform 140ms ease;
}

.cliente:hover {
  z-index: 1;
  border-color: var(--borde-cielo);
  background: var(--info-fondo);
  transform: translateY(-1px);
}

.identidad,
.perfil {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 3px;
}

.identidad strong {
  overflow: hidden;
  color: var(--tinta);
  font-size: var(--t-base);
  text-overflow: ellipsis;
  white-space: nowrap;
}

small {
  color: var(--tinta-suave);
  font-size: var(--t-xs);
}

.dato,
.dni {
  color: var(--tinta-media);
  font-size: var(--t-sm);
}

.dni {
  color: var(--movistar-azul-hondo);
}

.perfil span {
  overflow: hidden;
  color: var(--tinta-media);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.perfil small {
  color: var(--verde);
}

.probabilidad {
  display: flex;
  align-items: center;
  gap: 9px;
}

.barra {
  flex: 1;
  height: 6px;
  overflow: hidden;
  border-radius: 99px;
  background: var(--linea-suave);
}

.barra span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--verde-vivo);
}

.probabilidad strong {
  min-width: 38px;
  color: var(--verde);
  font-size: var(--t-sm);
  text-align: right;
}

.abrir {
  color: var(--movistar-azul-hondo);
  font-size: var(--t-xs);
  font-weight: 600;
  text-align: right;
  white-space: nowrap;
}

.abrir span {
  margin-left: 3px;
  font-size: 16px;
}

.error {
  margin: 14px 0 4px;
  padding: 8px 12px;
  border: 1px solid var(--alarma);
  border-radius: var(--r);
  background: var(--risk-fondo);
  color: var(--alarma);
  font-size: var(--t-sm);
}

.estado-carga {
  padding: 30px 0 10px;
  color: var(--tinta-suave);
  text-align: center;
}

@media (max-width: 1100px) {
  .inicio {
    width: calc(100% - 32px);
    padding: 22px 18px;
    overflow-x: auto;
  }

  .fila {
    min-width: 980px;
  }
}

@media (max-width: 640px) {
  .inicio {
    width: calc(100% - 16px);
    margin-top: 8px;
    padding: 18px 12px;
  }

  .cabecera-inicio {
    align-items: flex-start;
    flex-direction: column;
    padding-bottom: 16px;
  }
}
</style>
