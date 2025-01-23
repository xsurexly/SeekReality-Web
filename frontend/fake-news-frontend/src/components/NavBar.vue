<template>
  <nav class="navbar">
  
    <ul class="nav-links">
      <!-- 个人资料菜单 -->
      <li class="profile">
        <router-link to="/profile">
          <SvgIcon  iconName="icon-gerenzhuye1" style="margin-right: 5px;"></SvgIcon >
          <i class="fa fa-user"></i> 个人资料
        </router-link>
      </li>
      <li>
        <router-link to="/visualization">
          <SvgIcon iconName="icon-a-091_shuju" style="margin-right: 5px;"></SvgIcon>
          <i class="fa fa-chart-bar"></i> 可视化
        </router-link>
      </li>
      <li>
        <router-link to="/textdetect">
          <SvgIcon iconName="icon-a-091_wendang-12" style="margin-right: 5px;"></SvgIcon>
          <i class="fa fa-font"></i> 文本检测
        </router-link>
      </li>
      <li>
        <router-link to="/newspage">
          <SvgIcon iconName="icon-a-091_zhuanlan" style="margin-right: 5px;"></SvgIcon>
          <i class="fa fa-newspaper"></i> 新闻
        </router-link>
      </li>
      <li>
        <router-link to="/about">
          <SvgIcon iconName="icon-a-091_xinjian" style="margin-right: 5px;"></SvgIcon>
          <i class="fa fa-info-circle"></i> 关于我们
        </router-link>
      </li>
      <li v-if="isLoggedIn">
        <a href="#" @click="logout">退出登录</a>
      </li>
    </ul>
  </nav>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const isLoggedIn = ref(false); // 这里应该用 Vuex 或其他状态管理工具来管理

    function logout() {
      // 退出登录逻辑
      isLoggedIn.value = false;
    }

    return {
      isLoggedIn,
      logout,
    };
  },
};
</script>
<style lang="scss" scoped>
.navbar {
  background-color: white; /* 更深的绿色，给人更稳重的感觉 */
  color: black;
  width: 220px;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* 左对齐 */
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.3); /* 增加阴影效果 */
  border-radius: 10px;
  transition: all 0.3s ease;
}

/* 设置导航链接的样式 */
.nav-links {
  list-style-type: none;
  padding: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: calc(100% - 80px); /* 留出底部空间放个人资料 */
  margin-top: 20px; /* 上方留点间距 */
}

.nav-links li {
  width: 100%;
  margin: 10px 0;
}

.nav-links a {
  display: flex;
  align-items: center;
  padding: 12px 20px; /* 让按钮宽度一致，左右增加间距 */
  color: black;
  text-decoration: none;
  font-size: 1.1rem;
  border-radius: 6px;
  transition: background-color 0.3s ease, padding-left 0.2s ease; /* 添加缓慢的背景色变化和内边距 */
}

.nav-links a:hover {
  background-color: #B0E4C8; /* 按钮悬停背景色变为绿色 */
  padding-left: 30px; /* 悬停时左侧内边距增加，给用户更好的交互反馈 */
}

/* 图标样式 */
.nav-links i {
  margin-right: 15px; /* 图标和文字之间更大的间距 */
  font-size: 1.5rem; /* 增大图标 */
  transition: transform 0.2s ease; /* 增加图标放大效果 */
}

.nav-links a:hover i {
  transform: scale(1.1); /* 图标在悬停时微微放大 */
}

/* 添加专门的登出链接样式 */
.logout-link {
  display: block;
  padding: 12px 20px;
  color: white;
  text-decoration: none;
  font-size: 1.1rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}
</style>