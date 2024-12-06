<template>
  <nav class="navbar">
    <ul class="nav-links">
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
  background-color: #333;
  min-height: 100vh; /* 使navbar高度占满整个视口高度 */
}

.nav-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column; /* 垂直排列链接 */
  align-items: flex-start; /* 靠左对齐 */
}

.nav-links li {
  padding: 14px;
}

.nav-links li a {
  text-decoration: none;
  color: white;
  display: block;
}

.nav-links li a:hover {
  background-color: #ddd;
  color: black;
}
</style>