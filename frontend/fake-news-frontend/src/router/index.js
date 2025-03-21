import { createRouter, createWebHistory } from 'vue-router';  // 使用 Vue 3 的路由方法
import Login from '../views/login.vue';
import Register from '../views/register.vue';
import Home from '../views/Home.vue'
import About from '../views/about_us/index.vue';
import Profile from '../views/profile/index.vue';
import Textdetect from '../views/text_detect/index.vue'
import Visualization from '../views/visualization/index.vue'
import Newspage from '../views/news_page/index.vue'
import Password_modify from '@/views/password_modify.vue';
import History from '../views/detect_history/index.vue';
import ReadHistory from '../views/read_history/index.vue';
import HomePage from '@/views/HomePage.vue';



const routes = [
  {
    path: '/',
    name: 'start',
    component: HomePage,
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
    path: '/password_modify',
    name: 'password_modify',
    component: Password_modify,
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
    name:'Home',
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
  },
  {
  path:'/visualization',
  name:'visualization',
  component: Visualization,
  meta: {
    keepAlive: true
    }
  },
  {
    path:'/newspage',
    name:'news',
    component: Newspage,
    meta: {
      keepAlive: true
    },
    props: (route) => ({
      newsId: route.query.newsId,
      autoOpen: route.query.autoOpen
    })
  },
  {
    path:'/detecthistory',
    name:'detecthistory',
    component: History,
    meta: {
      keepAlive: true
      }
  },
  {
    path:'/read_history',
    name:'read_history',
    component: ReadHistory,
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
