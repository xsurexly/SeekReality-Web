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
  min-height: 100vh; /* 确保占满整个视口 */
  background: white; /* 主界面背景颜色 */
  padding: 20px;
  box-sizing: border-box;
}

.content {
  flex-grow: 1; /* 使内容区域占据剩余空间 */
  padding: 20px;
  text-align: center;
}
</style>