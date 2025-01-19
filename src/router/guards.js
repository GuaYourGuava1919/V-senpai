// src/router/guards.js
export function authGuard(to, from, next) {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'

    if (to.meta.requiresAuth && !isLoggedIn) {
        next('/signin') // 導向登入頁
    } else {
        next() // 繼續導航
    }
}
