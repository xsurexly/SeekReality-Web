<template>
  <div :class="isLoginPage ? 'login-background' : ''">
    <router-view /> <!-- 根据路由动态加载页面 -->
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoginPage() {
      // 判断当前路由是否为登录页或注册页
      return this.$route.path === '/' || this.$route.path === '/userRegister';
    }
  }
};
</script>

<style>
/* 全局样式重置 */
body {
  margin: 0;
  font-family: Arial, sans-serif;
}

/* 登录页的背景样式 */
.login-background {
  padding-top:200px;
  height: 100vh;
  background: url('@/assets/pic.jpg') no-repeat center center fixed;
  background-size: cover;
}
</style>

