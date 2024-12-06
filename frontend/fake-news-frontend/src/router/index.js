import { createRouter, createWebHistory } from 'vue-router';

import UserLogin from '../components/UserLogin.vue';
import UserRegister from '../components/UserRegister.vue';
import MainPage from '../components/MainPage.vue';
import Visualization from '../components/Visualization.vue';
import TextDetect from '../components/TextDetect.vue';
import NewsPage from '../components/NewsPage.vue';
import AIAssist from '../components/AIAssist.vue';
import AboutUs from '../components/AboutUs.vue';
import Profile from '../components/Profile.vue';
import Settings from '../components/Settings.vue';


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
      { path: 'about', component: AboutUs },
      { path: 'visualization', component: Visualization },
      { path: 'textdetect', component: TextDetect },
      { path: 'newspage', component: NewsPage },
      { path: 'aiassist', component: AIAssist }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});


export default router;