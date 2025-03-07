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
import Navbar from '@/components/NavBar.vue'
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

window.ResizeObserver = class ResizeObserver extends window.ResizeObserver {
  constructor(callback) {
    let timer = null;
    const debouncedCallback = function () {
      let context = this;
      let args = arguments;
      clearTimeout(timer);
      timer = setTimeout(function () {
        callback.apply(context, args);
      }, 16);
    };
    super(debouncedCallback);
  }
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

#app {
  height: 100vh;
  color: var(--font-color);
}

.main-container {
  display: flex; /* 使用 flex 布局 */
  height: 100vh;
  background-color: var(--bg-color);
}

.el-main {
  flex-grow: 1; /* 内容区域自动扩展，占据剩余空间 */
  padding: 20px;
  transition: margin-left 0.3s ease; /* 内容区的过渡效果 */
  background-color: var(--bg-color);
}


/* 左侧导航栏 */
.el-aside {
  color: var(--font-color);
  transition: width 0.3s ease;
  /* 默认宽度为200px，收起时为94px */
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
