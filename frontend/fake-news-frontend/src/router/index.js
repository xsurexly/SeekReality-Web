import { createRouter, createWebHistory } from 'vue-router';

import UserLogin from '../components/UserLogin.vue';
import UserRegister from '../components/UserRegister.vue';
import MainPage from '../components/MainPage.vue';
import AboutUs from '../components/AboutUs.vue';
import Profile from '../components/Profile.vue'; // 新增组件
import Settings from '../components/Settings.vue'; // 新增组件


const routes = [
  {
    path: '/',
    component: UserLogin
  },
  {
    path: '/userRegister',
    component: UserRegister
  },
   {
    path: '/MainPage',
    component: MainPage,
    children: [
      { path: 'profile', component: Profile },
      { path: 'settings', component: Settings },
      { path: 'about', component: AboutUs }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});


export default router;