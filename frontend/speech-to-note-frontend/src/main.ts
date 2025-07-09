import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import ConfirmationService from 'primevue/confirmationservice'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import './assets/style.scss'
import Tooltip from 'primevue/tooltip'
import ConfirmPopup from 'primevue/confirmpopup'

const app = createApp(App)
app.use(ConfirmationService)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
})
app.use(createPinia())
app.directive('tooltip', Tooltip)
app.component('ConfirmPopup', ConfirmPopup)

app.mount('#app')
