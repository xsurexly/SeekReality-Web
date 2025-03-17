import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import SvgIcon from '@/components/SvgIcon.vue';
import '@/assets/styles/_themes.scss'
import '@/assets/iconfont.js'
import axios from "axios";
import { createPinia } from 'pinia'

const app = createApp(App);
const pinia = createPinia()
app.use(pinia)
app.config.globalProperties.$axios = axios;
app.use(ElementPlus).use(router).component('SvgIcon', SvgIcon).mount('#app');

const initializeTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
  } else {
    const systemDarkTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.setAttribute('data-theme', systemDarkTheme ? 'dark' : 'light')
  }
}

initializeTheme()