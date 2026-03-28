import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },
  {
    path: '/route',
    name: 'route',
    component: () => import('../views/RoutePage.vue'),
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
