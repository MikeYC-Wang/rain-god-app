import { createApp } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faCloudRain,
  faRoute,
  faMapLocationDot,
  faLocationDot,
  faCircleInfo,
  faBars,
  faXmark,
  faTriangleExclamation,
  faSun,
  faCloudSun,
  faCloud,
  faDroplet,
  faMagnifyingGlass,
  faHouse,
  faGear,
  faFlag,
  faRotateLeft,
  faCheck,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons'

import './style.css'
import App from './App.vue'

library.add(
  faCloudRain,
  faRoute,
  faMapLocationDot,
  faLocationDot,
  faCircleInfo,
  faBars,
  faXmark,
  faTriangleExclamation,
  faSun,
  faCloudSun,
  faCloud,
  faDroplet,
  faMagnifyingGlass,
  faHouse,
  faGear,
  faFlag,
  faRotateLeft,
  faCheck,
  faSpinner,
)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app')
