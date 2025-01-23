<template>
  <div class="aboutUs-container">
    <div class="content">
      <!-- 路由视图，用于显示匹配的组件 -->
      <router-view></router-view>
    </div>

    <h1>这里是设置</h1>
    <p>欢迎！！！！</p>
  </div>
</template>

<script>


export default {
  components: {

  },
  name: 'Settings'
};
</script>

<style>
.aboutUs-container {
  font-family: Arial, sans-serif;
  background-color: white;
  display: flex; /* 使用Flexbox布局 */
  min-height: 100vh; /* 使容器高度占满整个视口高度 */
}

.content {
  flex-grow: 1; /* 使内容区域占据剩余空间 */
  padding: 20px;
  text-align: center;
}
</style>
