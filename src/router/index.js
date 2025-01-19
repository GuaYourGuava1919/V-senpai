import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/SignInView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/SignUpView.vue'),
    }
  ],
})

// 加入守衛
router.beforeEach((to) => {
  const isAuthenticated = localStorage.getItem('token')
  if (to.name !== 'login' && !isAuthenticated) {
    return { name: 'login' }
  }
})

export default router
