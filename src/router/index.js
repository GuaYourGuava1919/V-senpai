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
// 這個守衛會在每次路由切換前檢查是否有 token，如果沒有就導向登入頁面或是註冊頁面
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'login' && to.name !== 'register' && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
