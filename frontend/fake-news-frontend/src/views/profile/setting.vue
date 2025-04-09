<template>
  <div class="system-settings">
    <div class="settings-header">
      <h3>其他设置</h3>
    </div>
    <div class="setting-top">
      <h3 class="main-title">系统外观</h3>
      <h5 class="sub-title">根据偏好选择系统的外观。</h5>
    </div>
    <div class="theme-buttons">
      <el-button
        :class="['theme-button', { 'active': !darkTheme }]"
        @click="switchTheme(false)"
      >
        <el-icon><svg-icon icon-name="icon-mingliangmoshi" /></el-icon>
        <i class="el-icon-sunny"></i>
        浅色主题
        <p>Light Mode</p>
      </el-button>
      <el-button
        :class="['theme-button', { 'active': darkTheme }]"
        @click="switchTheme(true)"
      >
        <el-icon><svg-icon icon-name="icon-anheimoshi" /></el-icon>
        <i class="el-icon-moon"></i>
        深色主题
        <p>Dark Mode</p>
      </el-button>
    </div>

    <!-- 模型选择部分 -->
    <div class="model-selection">
      <h3 class="main-title">模型选择</h3>
      <h5 class="sub-title">选择偏好的模型。</h5>
      <div class="radio-group">
        <el-radio-group v-model="selectedModel" class="model-radio-group">
          <el-radio label="model1">Model 1(Based on Bert)</el-radio>
          <el-radio label="model2">Model 2</el-radio>
          <el-radio label="model3">Model 3</el-radio>
        </el-radio-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const darkTheme = ref(localStorage.getItem('theme') === 'dark')
const selectedModel = ref('model1') // 默认选择 model1

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

.system-settings {
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
    color: var(--font-color);
  }

  h5 {
    margin: 0;
    font-size: 14px;
    font-weight: 400;
    text-align: left;
    margin-bottom: 10px;
    color: var(--font-color);
  }
}

.setting-top {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  margin-bottom: 20px;
  padding-bottom: 10px;

  h3 {
    margin: 0;
    font-size: 18px;
    margin-bottom: 10px;
    text-align: left;
    color: var(--font-color);
  }

  h5 {
    margin: 0;
    font-size: 14px;
    font-weight: 400;
    text-align: left;
    color: var(--font-color);
  }
}

.theme-buttons {
  display: flex;
  justify-content: space-between;
  width: 50%;
}

.theme-button {
  width: 60%;
  height: 150%;
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

  .el-icon {
    margin-bottom: 0;
    margin-right: 10px;
  }
}

.model-selection {
  margin-top: 20px;

  .main-title {
    margin: 0;
    font-size: 18px;
    margin-bottom: 10px;
    text-align: left;
    color: var(--font-color);
  }

  .sub-title {
    margin: 0;
    font-size: 14px;
    font-weight: 400;
    text-align: left;
    color: var(--font-color);
  }

  .radio-group {
    display: flex;
    justify-content: flex-start; /* 靠左对齐 */
    width: 100%;
  }

  .model-radio-group {
    display: flex;
    flex-direction: row; /* 横向排列 */
    gap: 20px; /* 单选按钮之间的间距 */
  }

  :deep(.el-radio) {
    margin-right: 0; /* 移除默认的右边距 */
    text-align: left; /* 文本靠左对齐 */
  }
}

:deep(.el-button) {
  color: var(--font-color) !important;
  background-color: var(--navbar-bg);
}

.theme-button.active {
  color: var(--font-color) !important;
  background-color: var(--navbar-bg);
}

.el-button:hover {
  background-color: #489dff9b;
}

@media (max-width: 768px) {
  .theme-buttons {
    flex-direction: column;
    width: 100%;
    gap: 10px;
  }

  .theme-button {
    width: 100%;
  }
  :deep(.el-button+.el-button){
    margin-left: 0;
    margin-top: 5px;
  }
}

</style>
