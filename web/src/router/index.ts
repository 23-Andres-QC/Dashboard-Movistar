import { createRouter, createWebHistory } from 'vue-router'

import ConsolaAsesor from '@/views/ConsolaAsesor.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/asesor/:dni?', name: 'asesor', component: ConsolaAsesor, props: true },
    { path: '/', name: 'inicio', component: ConsolaAsesor },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
