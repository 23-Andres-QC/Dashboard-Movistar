<script setup lang="ts">
export type PerfilNuevo = {
  tipo_cliente: 'prepago' | 'postpago'
  consumo_datos_gb_prom: number
  consumo_voz_min_prom: number
  tiene_internet_hogar: boolean
  necesidad: 'movil' | 'hogar' | 'ambos'
  presupuesto: number
}

const emit = defineEmits<{ calcular: [perfil: PerfilNuevo] }>()

const perfil: PerfilNuevo = {
  tipo_cliente: 'postpago',
  consumo_datos_gb_prom: 10,
  consumo_voz_min_prom: 300,
  tiene_internet_hogar: false,
  necesidad: 'movil',
  presupuesto: 59,
}

function calcular() {
  emit('calcular', { ...perfil })
}
</script>

<template>
  <section class="formulario panel" aria-labelledby="titulo-perfil">
    <header class="encabezado">
      <div>
        <span class="micro eyebrow">Perfil incompleto · cliente nuevo</span>
        <h2 id="titulo-perfil">Conozcamos mejor al cliente</h2>
        <p>
          No hay historial suficiente. Complete estos datos para recalcular la mejor oferta.
        </p>
      </div>
      <span class="paso cifra">1 <small>/ 5</small></span>
    </header>

    <div class="campos">
      <label class="campo">
        <span class="micro">Tipo de línea</span>
        <select v-model="perfil.tipo_cliente">
          <option value="postpago">Postpago</option>
          <option value="prepago">Prepago</option>
        </select>
      </label>

      <label class="campo">
        <span class="micro">Consumo estimado de datos</span>
        <select v-model.number="perfil.consumo_datos_gb_prom">
          <option :value="3">Hasta 5 GB</option>
          <option :value="10">Entre 5 y 15 GB</option>
          <option :value="25">Entre 15 y 30 GB</option>
          <option :value="45">Más de 30 GB</option>
        </select>
      </label>

      <label class="campo">
        <span class="micro">Minutos de voz al mes</span>
        <select v-model.number="perfil.consumo_voz_min_prom">
          <option :value="100">Menos de 200 min</option>
          <option :value="300">Entre 200 y 500 min</option>
          <option :value="700">Más de 500 min</option>
        </select>
      </label>

      <label class="campo">
        <span class="micro">Presupuesto mensual</span>
        <select v-model.number="perfil.presupuesto">
          <option :value="39">Hasta S/ 39</option>
          <option :value="59">S/ 40 – 69</option>
          <option :value="89">S/ 70 – 99</option>
          <option :value="129">Más de S/ 100</option>
        </select>
      </label>

      <label class="campo amplio">
        <span class="micro">¿Qué necesita principalmente?</span>
        <div class="opciones" role="group" aria-label="Necesidad principal">
          <button type="button" :class="{ activo: perfil.necesidad === 'movil' }" @click="perfil.necesidad = 'movil'">
            Solo móvil
          </button>
          <button type="button" :class="{ activo: perfil.necesidad === 'hogar' }" @click="perfil.necesidad = 'hogar'">
            Internet hogar
          </button>
          <button type="button" :class="{ activo: perfil.necesidad === 'ambos' }" @click="perfil.necesidad = 'ambos'">
            Móvil + hogar
          </button>
        </div>
      </label>

      <label class="check amplio">
        <input v-model="perfil.tiene_internet_hogar" type="checkbox" />
        <span>Ya tiene internet hogar con otro operador</span>
      </label>
    </div>

    <footer class="pie">
      <span class="pista"><strong>Tip:</strong> pregunte primero por consumo y presupuesto.</span>
      <button type="button" class="primario" @click="calcular">Calcular mejor plan <span>→</span></button>
    </footer>
  </section>
</template>

<style scoped>
.formulario {
  margin: var(--gap) 0 0;
  padding: 22px 24px;
  border-top: 3px solid var(--movistar-azul);
}

.encabezado {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--gap-lg);
  padding-bottom: 18px;
  border-bottom: 1px solid var(--linea);
}

.eyebrow { color: var(--movistar-azul-hondo); }
h2 { margin-top: 5px; color: var(--movistar-noche); font-size: 21px; }
.encabezado p { margin-top: 5px; color: var(--tinta-suave); font-size: var(--t-sm); }
.paso { color: var(--movistar-azul-hondo); font-size: 21px; }
.paso small { color: var(--tinta-suave); font-size: var(--t-xs); }

.campos {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 18px 0;
}

.campo { display: flex; flex-direction: column; gap: 7px; min-width: 0; }
.campo select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  font-size: var(--t-sm);
}
.amplio { grid-column: span 2; }
.opciones { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.opciones button {
  padding: 9px 7px;
  border: 1px solid var(--linea);
  border-radius: var(--r);
  background: var(--superficie);
  color: var(--tinta-media);
  font-size: var(--t-sm);
}
.opciones button.activo { border-color: var(--movistar-azul); background: var(--info-fondo); color: var(--movistar-noche); font-weight: 600; }
.check { display: flex; align-items: center; gap: 8px; align-self: end; min-height: 38px; color: var(--tinta-media); font-size: var(--t-sm); }
.check input { width: 16px; height: 16px; accent-color: var(--movistar-azul); }

.pie { display: flex; align-items: center; justify-content: space-between; gap: var(--gap-lg); padding-top: 16px; border-top: 1px solid var(--linea); }
.pista { color: var(--tinta-suave); font-size: var(--t-xs); }
.primario { padding: 10px 16px; border: 0; border-radius: var(--r); background: var(--movistar-azul); color: var(--tinta-inversa); font-size: var(--t-sm); font-weight: 700; }
.primario span { margin-left: 6px; font-size: 17px; }

@media (max-width: 900px) {
  .campos { grid-template-columns: repeat(2, 1fr); }
  .amplio { grid-column: span 2; }
}
@media (max-width: 580px) {
  .formulario { padding: 18px; }
  .campos { grid-template-columns: 1fr; }
  .amplio { grid-column: auto; }
  .pie { align-items: stretch; flex-direction: column; }
}
</style>
