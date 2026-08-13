import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// El destino del proxy cambia segun donde corra: dentro de compose es el
// servicio `api`, fuera es localhost.
const destinoApi = process.env.VITE_API_PROXY ?? 'http://localhost:8000'

// Vite rechaza peticiones cuyo Host no reconoce. Al servir desde un servidor
// hay que declararlo: `VITE_ALLOWED_HOSTS=34.176.22.197` o varios separados por
// coma. Sin la variable solo se sirve en local.
const hostsPermitidos = (process.env.VITE_ALLOWED_HOSTS ?? '')
  .split(',')
  .map((h) => h.trim())
  .filter(Boolean)

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: hostsPermitidos.length ? hostsPermitidos : undefined,
    proxy: {
      '/api': { target: destinoApi, changeOrigin: true },
    },
  },
})
