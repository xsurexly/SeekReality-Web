<template>
  <div id="app" :class="isLoggedIn ? 'main-layout' : 'container'">
    <!-- 未登录时显示登录或注册界面 -->
    <div v-if="!isLoggedIn" class="auth-container">
      <div class="left-section">
        <img :src="require('@/assets/pic.jpg')" alt="Welcome" class="welcome-image" />
      </div>
      <div class="right-section">
        <h1>欢迎来到虚假新闻检测系统</h1>
        <router-view></router-view>
        <div class="links">
          <router-link
            to="/userRegister"
            v-if="$route.path === '/'"
            class="register-link"
          >
            注册
          </router-link>
        </div>
      </div>
    </div>

    <!-- 登录后显示主页面 -->
    <div v-else class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('user');
    }
  }
};
</script>

<style scoped>
/* 全局布局 */
.container {
  display: flex;
  height: 100vh;
  margin: 0;
}

/* 左侧区域样式 */
.left-section {
  flex: 3; /* 左侧区域占大部分空间 */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  overflow: hidden; /* 确保超出内容隐藏 */
}

.welcome-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 确保图片填满并保持比例 */
  border-radius: 0; /* 可根据需要调整边框圆角 */
}

/* 右侧区域样式 */
.right-section {
  flex: 1; /* 右侧区域占较小部分空间 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  padding: 20px;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
}

/* 标题样式 */
h1 {
  font-size: 2rem;
  margin-bottom: 20px;
  color: #333;
}

/* 注册链接样式 */
.links {
  margin-top: 0px;
}

.register-link {
  color: #4caf50;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}

.register-link:hover {
  text-decoration: underline;
}

/* 可选：更好适配移动设备 */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }

  .left-section {
    flex: 1;
  }

  .right-section {
    flex: 1;
    width: 100%;
  }
}
</style>
