<template>
  <div class="system-settings">
    <div class="settings-header">
      <h3>其他设置</h3>
    </div>
    <div class="theme-buttons">
      div
      <h3 class="main-title">系统外观</h3>
      <h5 class="sub-title">根据偏好选择系统的外观。</h5>
      <el-button
        :class="['theme-button', { 'active': !darkTheme }]"
        @click="switchTheme(false)"
      >
        <i class="el-icon-sunny"></i>
        浅色主题
        <p>Light Mode</p>
      </el-button>
      <el-button
        :class="['theme-button', { 'active': darkTheme }]"
        @click="switchTheme(true)"
      >
        <i class="el-icon-moon"></i>
        深色主题
        <p>Dark Mode</p>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const darkTheme = ref(localStorage.getItem('theme') === 'dark')

const switchTheme = (val) => {
  const theme = val ? 'dark' : 'light'
  localStorage.setItem('theme', theme)
  document.documentElement.setAttribute('data-theme', theme)
  darkTheme.value = val
}

onMounted(() => {
  switchTheme(darkTheme.value)
})
</script>

<style scoped lang="scss">
// 引入主题配置文件
@use "@/assets/styles/_themes.scss" as *;
#app {
  height: 100vh;
  text-align: center;
  background-color: var(--bg-color);
  color: var(--font-color);

  .fun{
    width: 100%;
    display: flex;
    justify-content: flex-end;
    padding: 5px;
    box-sizing: border-box;
  }
}

.system-settings{
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  margin-bottom: 20px;
  border-bottom: 1px solid #eeeeee;
  padding-bottom: 10px;

  h3 {
    margin: 0;
    font-size: 18px;
    margin-bottom: 10px;
    text-align: left;
    color:var(--font-color);
  }

  h5 {
    margin: 0;
    font-size: 14px;
    font-weight: 400;
    text-align: left;
    margin-bottom: 10px;
    color:var(--font-color);
  }
}

h3 {
  margin: 0;
  font-size: 18px;
  margin-bottom: 10px;
  text-align: left;
  color:var(--font-color);
}

h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 400;
  text-align: left;
  margin-bottom: 10px;
  color:var(--font-color);
}

:deep(.system-settings){
  color: var(--text-primary)!important;
}

.theme-buttons {
  display: flex;
  justify-content: space-between;
  width: 50%;
}

.theme-button {
  width: 48%;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;

  i {
    font-size: 24px;
    margin-bottom: 10px;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: #999999;
  }

  &.active {
    border-color: #409eff;
    background-color: #ecf5ff;

    i {
      color: #409eff;
    }

    p {
      color: #409eff;
    }
  }
}

:deep(.el-button){
  color:var(--font-color)!important;
  background: var(--bg-color);
}
.theme-button.active{
  color:var(--font-color)!important;
  background: var(--bg-color);
}
.el-button:hover{
  background-color: #489dff9b;
}

</style>
