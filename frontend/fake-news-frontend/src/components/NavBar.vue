<template>
  <nav class="navbar">
    <ul class="nav-links">
      <li><router-link to="/mainPage/visualization">可视化</router-link></li>
      <li><router-link to="/mainPage/textdetect">文本检测</router-link></li>
      <li><router-link to="/mainPage/newspage">新闻</router-link></li>
      <li><router-link to="/mainPage/aiassist">AI助手</router-link></li>
      <li><router-link to="/mainPage/profile">个人资料</router-link></li>
      <li><router-link to="/mainPage/settings">设置</router-link></li>
      <li><router-link to="/mainPage/about">关于</router-link></li>
      <li><a @click="logout">登出</a></li>
    </ul>
  </nav>
</template>

<script>
export default {
  methods: {
    logout() {
      localStorage.removeItem('user');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.navbar {
  background-color: #4CAF50;
  color: white;
  padding: 10px;
}

.nav-links {
  list-style-type: none;
  display: flex;
  gap: 15px;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.nav-links a:hover {
  text-decoration: underline;
}
</style>