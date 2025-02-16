<template>
  <div class="navbar-container">
    <!-- 使用 el-menu 重构导航栏 -->
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :collapse="isNavbarCollapsed"
      :collapse-transition="false"
      background-color="#EBF5F4"
      text-color="#000"
      active-text-color="#000"
    >
      <!-- Logo 区域 -->
      <router-link to="/home">
        <div class="logo-container">
          <img
            :class="{ 'collapsed-logo': isNavbarCollapsed }"
            src="../assets/logo.png"
            alt="Logo"
          />
        </div>
      </router-link>

      <!-- 折叠按钮 -->
      <div class="hamburger-container">
        <el-icon
          :size="24"
          class="collapse-icon"
          @click="toggleNavbar"
          style="margin-right: 140px;"
        >
          <component :is="isNavbarCollapsed ? Expand : Fold" />
        </el-icon>
      </div>

      <!-- 导航菜单 -->
      <el-menu-item index="/home" @click="navigateTo('/home')">
        <el-icon><svg-icon icon-name="icon-shouye" /></el-icon>
        <template #title>
          <span>首页</span>
        </template>
      </el-menu-item>

      <el-menu-item index="/visualization" @click="navigateTo('/visualization')">
        <el-icon><svg-icon icon-name="icon-shuju" /></el-icon>
        <template #title>
          <span>可视化</span>
        </template>
      </el-menu-item>

      <el-menu-item index="/textdetect" @click="navigateTo('/textdetect')">
        <el-icon><svg-icon icon-name="icon-jilu" /></el-icon>
        <template #title>
          <span>新闻检测</span>
        </template>
      </el-menu-item>

      <el-menu-item index="/newspage" @click="navigateTo('/newspage')">
        <el-icon><svg-icon icon-name="icon-pinlei" /></el-icon>
        <template #title>
          <span>新闻阅读</span>
        </template>
      </el-menu-item>

      <!-- 用户信息区域 -->
      <div class="user-info">
        <el-dropdown trigger="click" @visible-change="handleDropdownVisible">
          <div class="user-content">
            <el-avatar :size="40" :src="avatar" />
            <span v-show="!isNavbarCollapsed" class="username">{{ user.username }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToProfile">
                <el-icon><svg-icon icon-name="icon-wode" /></el-icon>
                个人主页
              </el-dropdown-item>
              <el-dropdown-item @click="goToAboutUs">
                <el-icon><svg-icon icon-name="icon-guanyuwomen" /></el-icon>
                关于我们
              </el-dropdown-item>
              <el-dropdown-item divided @click="logout">
                <el-icon><svg-icon icon-name="icon-tuichu" /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Fold, Expand } from '@element-plus/icons-vue'

const { isNavbarCollapsed } = defineProps({
  isNavbarCollapsed: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['toggle-menu'])

const router = useRouter()
const route = useRoute()

// 计算当前激活菜单
const activeMenu = computed(() => route.path)

const getStoredUser = () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user'))
    return userData || { username: '未登录' }
  } catch {
    return { username: '未登录' }
  }
}

const user = ref(getStoredUser())
const avatar = ref(localStorage.getItem('avatar') || 'avatar.png')

// 导航跳转
const navigateTo = (path) => {
  router.push(path)
}

// 切换菜单折叠
const toggleNavbar = () => {
  emit('toggle-menu')
}

// 用户操作
const goToProfile = () => {
  router.push('/profile')
}

const goToAboutUs = () => {
  router.push('/about')
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}

</script>

<style scoped lang="scss">
.navbar-container {
  height: 100vh;
  position: fixed;
  z-index: 1000;
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
  
  &:not(.el-menu--collapse) {
    width: 200px;
  }

  .logo-container {
    padding: 10px 0;
    text-align: center;
    
    img {
      width: 160px;
      transition: all 0.3s;
      
      &.collapsed-logo {
        width: 40px;
        height: 45px;
        object-fit: cover;
        object-position: 0 100%;
      }
    }
  }

  .hamburger-container {
    padding: 10px;
    text-align: center;
    
    .collapse-icon {
      cursor: pointer;
      transition: transform 0.3s;
      margin-left: 10px;
      
      &:hover {
        color: var(--el-color-primary);
      }
    }
  }

  .user-info {
    position: absolute;
    bottom: 20px;
    width: 100%;
    padding: 0 10px;
    
    .user-content {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .username {
        margin-left: 10px;
        font-size: 14px;
      }
    }
  }
}

/* 覆盖 Element 默认样式 */
.el-menu-item {
  height: 50px;
  line-height: 50px;
  
  &:hover {
    background-color: #86D9D4 !important;
    transform: scale(1.03);
    border-radius: 10px;
  }
  
  &.is-active {
    background-color: #BEEBE7 !important;
  }
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  
  .el-icon {
    margin-right: 8px;
  }
  
  &:hover {
    background-color: #86D9D4 !important;
    transform: scale(1.03);
    border-radius: 10px;
  }
}

.el-dropdown-menu{
  background-color: #EBF5F4;
  color: #000;
}
.el-dropdown__popper {
    --el-dropdown-menu-box-shadow: var(--el-box-shadow-light);
    --el-dropdown-menuItem-hover-fill: #000;
    --el-dropdown-menuItem-hover-color: #4ebfb9;
    --el-dropdown-menu-index: 10;
}
</style>