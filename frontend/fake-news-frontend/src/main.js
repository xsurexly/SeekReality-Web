import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import SvgIcon from '@/components/SvgIcon.vue';
import '@/assets/iconfont.js'

createApp(App)
  .use(router)
  .component('SvgIcon', SvgIcon)
  .mount('#app');