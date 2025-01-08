// import './assets/scss/all.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 引入 Element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'     // 引入 Element-plus 的 CSS 樣式

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(ElementPlus)
app.use(createPinia())
app.use(router)

app.mount('#app')
