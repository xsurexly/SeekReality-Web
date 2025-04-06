<template>
  <div class="common-layout" id="app">
    <el-container class="main-container">
      <el-container>
        <!-- 桌面端侧边导航栏 -->
        <el-aside 
          v-if="!isMobile && $route.meta.keepAlive" 
          :style="{ width: isNavbarCollapsed ? '75px' : '200px' }"
        >
          <Navbar @toggle-menu="toggleNavbar" :isNavbarCollapsed="isNavbarCollapsed" />
        </el-aside>

        <!-- 主要内容区 -->
        <el-main :class="{ 
          'isNavbarCollapsed': isNavbarCollapsed,
          'has-bottom-navbar': isMobile 
        }">
          <div class="content">
            <router-view />
          </div>
          <div class="aihelper" v-if="$route.meta.keepAlive">
            <AIhelper></AIhelper>
          </div>
        </el-main>

        <!-- 移动端底部导航栏 -->
        <div v-if="isMobile && $route.meta.keepAlive" class="mobile-navbar">
          <Navbar @toggle-menu="toggleNavbar" :isNavbarCollapsed="isNavbarCollapsed" />
        </div>
      </el-container>
    </el-container>
  </div>
</template>


<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Navbar from '@/components/NavBar.vue'
import AIhelper from './views/ai_helper/index.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    AIhelper
  },
  setup() {
    const isNavbarCollapsed = ref(false)
    const isMobile = ref(false)

    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    const toggleNavbar = () => {
      isNavbarCollapsed.value = !isNavbarCollapsed.value
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      isNavbarCollapsed,
      isMobile,
      toggleNavbar
    }
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

.mobile-navbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.el-main {
  &.has-bottom-navbar {
    padding-bottom: 90px; // 为底部导航栏留出空间
  }
}



</style>
