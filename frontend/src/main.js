import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap-icons/font/bootstrap-icons.css"

import * as Vue from 'vue' // in Vue 3
import axios from 'axios'
import VueAxios from 'vue-axios'

axios.defaults.baseURL = "/api/"

createApp(App)
    .use(store)
    .use(router)
    .use(VueAxios, axios)
    .mount('#app')
