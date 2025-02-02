<template>
  <div class="navbar-container">
    <!-- 左侧导航栏 -->
    <nav :class="['navbar', { 'collapsed': isNavbarCollapsed }]">
      <div class="hamburger-container">
        <hamburger @toggle-menu="toggleNavbar" />
      </div>
      <ul class="nav-links">
        <li>
          <router-link to="/home" active-class="active-nav-item">
            <SvgIcon iconName="icon-shouye2" style="margin-right: 5px;"></SvgIcon>
            <i class="fa fa-chart-bar"></i> <span v-if="!isNavbarCollapsed">首页</span>
          </router-link>
        </li>
        <li>
          <router-link to="/visualization" active-class="active-nav-item">
            <SvgIcon iconName="icon-a-091_shuju" style="margin-right: 5px;"></SvgIcon>
            <i class="fa fa-chart-bar"></i> <span v-if="!isNavbarCollapsed">可视化</span>
          </router-link>
        </li>
        <li>
          <router-link to="/textdetect" active-class="active-nav-item">
            <SvgIcon iconName="icon-a-091_wendang-12" style="margin-right: 5px;"></SvgIcon>
            <i class="fa fa-font"></i> <span v-if="!isNavbarCollapsed">文本检测</span>
          </router-link>
        </li>
        <li>
          <router-link to="/newspage" active-class="active-nav-item">
            <SvgIcon iconName="icon-a-091_zhuanlan" style="margin-right: 5px;"></SvgIcon>
            <i class="fa fa-newspaper"></i> <span v-if="!isNavbarCollapsed">新闻阅读</span>
          </router-link>
        </li>
        <li>
          <router-link to="/about" active-class="active-nav-item">
            <SvgIcon iconName="icon-a-091_xinjian" style="margin-right: 5px;"></SvgIcon>
            <i class="fa fa-info-circle"></i> <span v-if="!isNavbarCollapsed">关于我们</span>
          </router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import Hamburger from './Hamburger.vue';
//import { ref } from 'vue';

export default {
  components: {
    Hamburger,
  },
  props: {
    // 接收父组件传递的 isNavbarCollapsed
    isNavbarCollapsed: {
      type: Boolean,
      required: true
    },
  },
  methods: {
    // 发出事件通知父组件切换导航栏收起状态
    toggleNavbar() {
      this.$emit('toggle-menu');
    },
  },
};
</script>

<style scoped>
.navbar-container {
  display: flex;
  position: fixed;
  flex-direction: column;
  width: 100%;
  height: 100vh;
}

.hamburger-container {
  display: flex;
  align-items: center;
  padding-left: 23px;
  padding-top: 15px;
  z-index: 9999;
}

.navbar {
  background-color: #EBF5F4;
  color: black;
  width: 200px;
  height: calc(100% - 60px); 
  position: fixed;
  top: 60px;
  left: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: all 0.3s ease;
  /*box-shadow:-20px -2px 15px -25px #00000067 inset;*/
}

.navbar.collapsed  {
  width: 94px;
}

.nav-links {
  list-style-type: none;
  padding: 0;
  width: 100%;
  margin-top: 10px;
}

.nav-links li {
  width: 100%;
  margin: 10px 0;
}

.nav-links a {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: black;
  text-decoration: none;
  font-size: 1.1rem;
  border-radius: 6px;
  transition: background-color 0.3s ease, padding-left 0.2s ease;
}

.nav-links a:hover {
  background-color: #86D9D4;
  padding-left: 30px;
}

.nav-links i {
  margin-right: 15px;
  font-size: 1.5rem;
  transition: transform 0.2s ease;
}

.nav-links a:hover i {
  transform: scale(1.1);
}


.active-nav-item {
  background-color: #BEEBE7; 
  padding-left: 30px; 
  border-radius: 6px;

}

</style>
