<template>
  <!-- 顶部的 Header -->
  <header class="header">
    <router-link to="/home">
      <div class="logo">
        <img src="../assets/logo.png" alt="" style="width: 160px;padding-top: 10px;margin-left: 5px;">
      </div>
    </router-link>

    <!-- 用户信息部分 -->
    <div class="user-info" @click="toggleMenu">
      <span class="username">{{ user.username }}</span>
      <img :src="avatar" alt="用户头像" class="user-avatar" />
    </div>

    <div v-show="isMenuOpen" class="avatar-menu">
      <div class="menu-item" @click="goToProfile">
        <SvgIcon iconName="icon-gerenzhuye1" style="width: 18px;height: 18px;margin-top: 8px;margin-right: 8px;"></SvgIcon>个人主页
      </div>
      <div class="menu-item" @click="logout">
        <SvgIcon iconName="icon-tuichu" style="width: 18px;height: 18px;margin-top: 8px;margin-right: 8px;"></SvgIcon>退出登录
      </div>
    </div>
  </header>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();
    
    // 用户信息和头像管理
    const user = reactive({
      username: '', // 从 localStorage 或 Vuex 获取
    });
    const avatar = ref(''); // 头像地址
    const isMenuOpen = ref(false); // 控制菜单是否打开

    // 打开/关闭头像菜单
    function toggleMenu() {
      isMenuOpen.value = !isMenuOpen.value;
    }

    // 跳转到个人主页
    function goToProfile() {
      isMenuOpen.value = false; // 关闭菜单
      router.push('/profile'); // 使用 Vue Router 来跳转
    }

    // 退出登录
    function logout() {
      isMenuOpen.value = false; // 关闭菜单
      localStorage.removeItem('user');
      localStorage.removeItem('avatar');
      router.push('/login'); // 使用 Vue Router 来跳转
    }

    // 获取本地存储的用户信息和头像
    onMounted(() => {
      const savedUser = JSON.parse(localStorage.getItem('user'));
      const savedAvatar = localStorage.getItem('avatar');

      if (savedUser) {
        user.username = savedUser.username; // 从 localStorage 获取用户名
      } else {
        user.username = '未登录'; // 如果没有找到用户名，设置为“未登录”
      }

      if (savedAvatar) {
        avatar.value = savedAvatar; // 从 localStorage 获取头像
      } else {
        avatar.value = 'default-avatar.png'; // 默认头像路径
      }
    });

    return {
      user,
      avatar,
      isMenuOpen,
      toggleMenu,
      goToProfile,
      logout,
    };
  },
};
</script>

<style scoped>
/* 顶部 Header 样式 */
.header {
  display: flex;
  position: fixed;
  justify-content: space-between; /* 左右两边对齐 */
  align-items: center;
  padding: 10px 20px;
  background-color: #EBF5F4;
  color: black;
  height: 40px;
  width: 100%;
  z-index: 10;
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  border-radius: 50%;
  margin-left: 10px;
  margin-right: 25px;
  width: 40px;
  height: 40px;
}

/* 头像菜单样式 */
.avatar-menu {
  position: absolute;
  top: 65px; /* 菜单的顶部位置，确保不会遮挡头像 */
  right: 35px; /* 菜单的右侧位置 */
  background-color: #EBF5F4;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 150px;
  z-index: 1000;
}

.avatar-menu .menu-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.avatar-menu .menu-item:hover {
  transition: background-color 0.3s ease, padding-left 0.2s ease;
  border-radius: 6px;
  background-color: #86D9D4;
  padding-left: 20px;
  transform: scale(1.03);
}
</style>
