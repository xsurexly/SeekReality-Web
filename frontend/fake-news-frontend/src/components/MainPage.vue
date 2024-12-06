<template>
  <div class="main-page">
    <NavBar />
    <div class="content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import NavBar from './NavBar.vue';

export default {
  components: {
    NavBar
  }
};
</script>

<style>
.main-container {
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