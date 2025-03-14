<template>
  <div class="navbar-container">
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :collapse="isNavbarCollapsed"
      :collapse-transition="true"
      text-color="var(--text-primary)"
      active-text-color="var(--el-color-primary)"
      background-color= "var(--navbar-bg)"

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

      <el-sub-menu index="/textdetect">
          <template #title>
            <el-icon><svg-icon icon-name="icon-jilu" /></el-icon>
            <span>新闻检测</span>
          </template>
            <el-menu-item index="/textdetect" @click="navigateTo('/textdetect')">新闻检测</el-menu-item>
            <el-menu-item index="/detecthistory" @click="navigateTo('/detecthistory')">检测历史</el-menu-item>
        </el-sub-menu>


      <el-sub-menu index="/newspage">
          <template #title>
            <el-icon><svg-icon icon-name="icon-pinlei" /></el-icon>
            <span>新闻阅读</span>
          </template>
            <el-menu-item index="/newspage" @click="navigateTo('/newspage')">新闻阅读</el-menu-item>
            <el-menu-item index="/readhistory" @click="navigateTo('/read_history')">阅读历史</el-menu-item>
        </el-sub-menu>

      <el-menu-item index="/profile" @click="navigateTo('/profile')">
        <el-icon><svg-icon icon-name="icon-wode"/></el-icon>
        <template #title>
          <span>个人主页</span>
        </template>
      </el-menu-item>

      <el-menu-item index="/about" @click="navigateTo('/about')">
        <el-icon><svg-icon icon-name="icon-guanyuwomen" /></el-icon>
        <template #title>
          <span>关于我们</span>
        </template>
      </el-menu-item>

      <el-menu-item index="/logout" @click="logout">
        <el-icon><svg-icon icon-name="icon-tuichu" /></el-icon>
        <template #title>
          <span>退出登录</span>
        </template>
      </el-menu-item>

      <!-- 用户信息区域 -->
      <div class="user-info">
        <el-dropdown trigger="click" @visible-change="handleDropdownVisible">
          <div class="user-content">
            <el-avatar
              :size="45"
              :src="avatarUrl"
              style="margin-left: 10px;margin-right: 10px;"
              class="custom-avatar"
            >
              <img src="https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png" />
            </el-avatar>
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
import { ref, computed, onMounted } from 'vue'
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
    return {
      username: localStorage.getItem('username') || '未登录',
      userid: localStorage.getItem('userid') || '',
      gender: localStorage.getItem('gender') || '男'
    }
  } catch {
    return { username: '未登录', userid: '', gender: '男' }
  }
}

const user = ref(getStoredUser())
const avatar = ref(localStorage.getItem('avatar') || '')

// 计算头像URL
const avatarUrl = computed(() => {
  if (!avatar.value) {
    return 'https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png'
  }

  if (avatar.value.startsWith('http')) {
    return avatar.value
  }

  return `http://localhost:5000${avatar.value}`
})

// 在组件挂载时更新用户信息
onMounted(() => {
  const userData = getStoredUser()
  user.value = userData
  avatar.value = localStorage.getItem('avatar') || ''
})

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
  user.value = { username: '未登录', userid: '', gender: '男' }
  avatar.value = ''
  router.push('/login')
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

  .logo-container {
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
        color: #409EFF;
      }
    }
  }


  .custom-avatar {
  border: none !important;
  background-color: transparent !important;
}

.user-info {

  .user-content {
    display: flex;
    align-items: center;
    cursor: pointer;
    color: var(--text-primary);

    .username {
      margin-left: 10x;
      font-size: 14px;
    }
  }
}

.navbar-container {
  height: 100vh;
  position: fixed;
  z-index: 1000;
  background-color: var(--navbar-bg);
  color: var(--text-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}


.el-menu-vertical {
  height: 100%;
  border-right: none;
  background-color: var(--navbar-bg);


  &:not(.el-menu--collapse) {
    width: 200px;
  }

  .logo-container {
    padding: 10px 0;
    text-align: center;
    background-color: var(--navbar-bg);
  }

  .user-info {
    position: absolute;
    bottom: 20px;
    width: 100%;
    padding: 0 0px;
    margin-left: 0px;
  }
}

.el-menu-item:hover {
  background-color: var(--hover-nav);
}

:deep(.el-sub-menu__title) {
  &:hover {
    background-color: var(--hover-nav) !important;
  }
}

.el-dropdown-menu {
  background-color: var(--navbar-bg);
  color: var(--text-primary);
}

:deep(.el-dropdown-menu__item) {
  color: var(--text-primary);
  
  &:hover {
    background-color: var(--hover-nav) !important;
  }
}
</style>
