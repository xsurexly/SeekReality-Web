<template>
  <nav class="navbar">
    <ul class="nav-links">
      <li><router-link to="/mainPage/visualization">可视化</router-link></li>
      <li><router-link to="/mainPage/textdetect">文本检测</router-link></li>
      <li><router-link to="/mainPage/newspage">新闻</router-link></li>
      <li><router-link to="/mainPage/aiassist">AI助手</router-link></li>
      <li><router-link to="/mainPage/profile">个人资料</router-link></li>
      <li><router-link to="/mainPage/settings">设置</router-link></li>
      <li><router-link to="/mainPage/about">关于我们</router-link></li>
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
/* 设置导航栏固定在左侧 */
.navbar {
  background-color: #2e7d32;
  color: white;
  width: 200px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 2px 0px 10px rgba(0, 0, 0, 0.1);
}

/* 设置导航链接的样式 */
.nav-links {
  list-style-type: none;
  padding: 0;
  width: 100%;
}

.nav-links li {
  width: 100%;
  text-align: center;
  margin: 10px 0;
}

.nav-links a {
  display: block;
  padding: 12px;
  color: white;
  text-decoration: none;
  font-size: 1.1rem;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.nav-links a:hover {
  background-color: #81c784; /* 背景色变化 */
}

</style>
