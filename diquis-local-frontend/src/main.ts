import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Capacitor } from '@capacitor/core'
import App from './App.vue'
import router from './router'
import { initBackButtonHandler } from './composables/useBackButton'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')

if (Capacitor.isNativePlatform()) {
  initBackButtonHandler(router);
}