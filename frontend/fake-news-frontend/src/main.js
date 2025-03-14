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
