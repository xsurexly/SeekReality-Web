<template>
  <div class="aboutUs-container">
    <!-- Navbar组件将在这里渲染 -->
    <Navbar/>

    <div class="content">
      <!-- 路由视图，用于显示匹配的组件 -->
      <router-view></router-view>
    </div>

    <h1>这里是关于我们</h1>
    <p>欢迎！！！！</p>
  </div>
</template>

<script>
import Navbar from './NavBar.vue'; // 确保路径正确

export default {
  components: {
    Navbar
  },
  name: 'AboutUs'
};
</script>

<style>
.aboutUs-container {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  display: flex; /* 使用Flexbox布局 */
  min-height: 100vh; /* 使容器高度占满整个视口高度 */
}

.content {
  flex-grow: 1; /* 使内容区域占据剩余空间 */
  padding: 20px;
  text-align: center;
}
</style>