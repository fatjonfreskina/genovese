import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAnalytics, trackPageview } from './utils/analytics'

const savedTheme = localStorage.getItem('equa-theme')
const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
document.documentElement.classList.toggle('dark', savedTheme ? savedTheme === 'dark' : prefersDark)

const app = createApp(App)
app.use(createPinia())
app.use(router)
initAnalytics()
router.afterEach((to) => trackPageview(to.path.startsWith('/group/') ? '/group' : '/'))
app.mount('#app')
