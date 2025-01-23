import { createRouter, createWebHistory } from 'vue-router';  // 使用 Vue 3 的路由方法
import Login from '../views/login.vue';
import Register from '../views/register.vue';
import Home from '../views/Home.vue'
import About from '../views/about_us/index.vue';
import Profile from '../views/profile/index.vue';
import Textdetect from '../views/text_detect/index.vue'

const routes = [
  {
    path: '/',
    name: 'start',
    component: Login,
    meta: {
      keepAlive: false
      }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      keepAlive: false
      }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: {
      keepAlive: false
      }
  },
  {
    path:'/home',
    name:'home',
    component: Home,
    meta: {
      keepAlive: true
      }
  },
  {
    path:'/about',
    name:'about',
    component: About,
    meta: {
      keepAlive: true
      }
  },
  {
    path:'/profile',
    name:'profile',
    component: Profile,
    meta: {
      keepAlive: true
      }
  },
  {
    path:'/textdetect',
    name:'textdetect',
    component: Textdetect,
    meta: {
      keepAlive: true
      }
  }
];

const router = createRouter({
  history: createWebHistory(),  // 使用 WebHistory 模式
  routes
});

export default router;