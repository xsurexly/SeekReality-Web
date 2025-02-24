<template>
  <div class="common-layout" id="app">
    <el-container class="main-container">
      <el-container>
        <!-- 左侧导航栏，动态宽度 -->
        <el-aside :style="{ width: isNavbarCollapsed ? '75px' : '200px' }" v-if="$route.meta.keepAlive">
          <Navbar @toggle-menu="toggleNavbar" :isNavbarCollapsed="isNavbarCollapsed" />
        </el-aside>

        <!-- 右侧内容区 -->
        <el-main :class="{ 'isNavbarCollapsed': isNavbarCollapsed }">
          <div class="content">
            <router-view />
          </div>
          <div class="aihelper" v-if="$route.meta.keepAlive">
            <AIhelper></AIhelper>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import AIhelper from'./views/ai_helper/index.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    AIhelper
  },
  data() {
    return {
      isNavbarCollapsed: false,
    };
  },
  methods: {
    // 切换导航栏收起状态
    toggleNavbar() {
      this.isNavbarCollapsed = !this.isNavbarCollapsed;
    },
  }
};
</script>

<style scoped>
/* Flex 布局容器 */
.main-container {
  display: flex; /* 使用 flex 布局 */
  height: 100vh;
}

/* 左侧导航栏 */
.el-aside {
  color: black;
  transition: width 0.3s ease;
  /* 默认宽度为200px，收起时为94px */
}

/* 右侧内容区域 */
.el-main {
  flex-grow: 1; /* 内容区域自动扩展，占据剩余空间 */
  padding: 20px;
  transition: margin-left 0.3s ease; /* 内容区的过渡效果 */
  background-color:rgba(226, 226, 226, 0.259);
}

/* 收起导航栏时，右侧内容区向左移动 */
.el-main.isNavbarCollapsed {
  margin-left: 0px; /* 当导航栏收缩时，内容区域宽度自适应 */
}

.content {
  overflow-y: auto; /* 如果内容超出，允许滚动 */
  text-align: center;
}


.aihelper{
  z-index: 999;
}

</style>