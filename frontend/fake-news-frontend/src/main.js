import { createApp } from 'vue';

import App from './App.vue';
import router from './router/index';
import axios from 'axios';

const app = createApp(App);
app.use(router);

// 添加 axios 到 Vue 原型
app.config.globalProperties.$http = axios;

app.mount('#app');