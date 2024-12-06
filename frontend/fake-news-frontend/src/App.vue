<template>
  <div id="app" :class="isLoggedIn ? 'main-layout' : 'container'">
    <!-- 未登录时显示登录或注册界面 -->
    <div v-if="!isLoggedIn" class="auth-container">
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

    <!-- 登录后显示主页面 -->
    <div v-else class="main-content">
        <h1>主界面</h1>
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


