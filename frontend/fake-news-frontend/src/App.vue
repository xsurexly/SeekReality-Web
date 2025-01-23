<template>
  <div id="app">
    <Navbar v-if="$route.meta.keepAlive"></Navbar>
    <router-view></router-view>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default  {
  name:  'App',
  components: {
    Navbar
    },
    metaInfo() {
        return {
            title: "虚假新闻检测系统",
            titleTemplate: "虚假新闻检测系统"
        }
    },
}
</script>

<style>
.app-container {
  display: flex;
  flex-direction: row; /* 左右排列 */
  height: 100vh; /* 使用视口高度 */
}
.router-view {
  flex: 1; /* 让路由视图占满剩余空间 */
  padding: 20px;
  text-align: center;
}

</style>