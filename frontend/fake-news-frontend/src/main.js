import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import SvgIcon from '@/components/SvgIcon.vue';
import '@/assets/iconfont.js'

createApp(App)
  .use(ElementPlus)
  .use(router)
  .component('SvgIcon', SvgIcon)
  .mount('#app');