<template>
  <div class="system-settings">
    <el-form label-width="160px">
      <el-form-item label="主题设置">
        <el-switch
          v-model="darkTheme"
          :active-value="true"
          :inactive-value="false"
          active-text="暗黑模式"
          inactive-text="明亮模式"
          @change="switchChange"
          class="custom-switch"
        />
      </el-form-item>
      <el-form-item label="消息通知">
        <el-switch v-model="notificationEnabled" />
      </el-form-item>
      <el-form-item label="自动保存间隔">
        <el-slider
          v-model="saveInterval"
          :step="5"
          :min="5"
          :max="60"
          show-input
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const darkTheme = ref(localStorage.getItem('theme') === 'dark')
const notificationEnabled = ref(localStorage.getItem('notification') === 'true')
const saveInterval = ref(Number(localStorage.getItem('saveInterval')) || 15)

// 主题切换处理
const switchChange = (val) => {
  const theme = val ? 'dark' : 'light'
  localStorage.setItem('theme', theme)
  document.documentElement.setAttribute('data-theme', theme)
}

// 组件挂载时初始化主题
onMounted(() => {
  switchChange(darkTheme.value)
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

:deep(.system-settings){
  color: var(--text-primary)!important;
}

.custom-switch .el-switch__core {
  width: 50px; /* 调整开关宽度 */
  height: 25px; /* 调整开关高度 */
}

.custom-switch .el-switch__core::after {
  width: 25px; /* 调整滑块宽度 */
  height: 25px; /* 调整滑块高度 */
  margin-left: -25px; /* 调整滑块位置 */
  border-radius: 50%; /* 使滑块圆形 */
  background-color: #ffffff; /* 滑块背景颜色 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); /* 添加阴影 */
  transition: all 0.3s; /* 添加过渡效果 */
}

.custom-switch .el-switch__core.is-checked::after {
  margin-left: 25px; /* 调整滑块位置 */
  background-color: #000000; /* 滑块背景颜色（激活状态） */
}

.custom-switch .el-switch__label {
  font-size: 14px; /* 字体大小 */
  color: #333333; /* 字体颜色 */
}

.custom-switch .el-switch__label.is-active {
  color: #409EFF; /* 激活状态下的字体颜色 */
}


:deep(.el-switch__label){
  color:var(--font-color)!important;
}

:deep(.el-form-item__label){
  color:var(--font-color)!important;
}
</style>
