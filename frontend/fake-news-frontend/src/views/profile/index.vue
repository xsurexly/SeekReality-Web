<template>
  <div class="profile-container">
    <h3 class="main-title">账户设置</h3>
    <h5 class="sub-title">管理您的个人信息以及系统设置</h5>
    <div class="tab-container">
      <el-tabs tab-position="left" class="tabs">
        <el-tab-pane label="基本信息">
          <self_intro/>
        </el-tab-pane>

        <el-tab-pane label="账户安全">
          <security/>
        </el-tab-pane>

        <el-tab-pane label="其他设置">
          <setting/>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import self_intro from './self_info.vue'
import setting from './setting.vue'
import security from './sys_security.vue'

export default {
  components: {
    self_intro,
    setting,
    security
  }
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

.profile-container {
  max-width: 1400px;
  margin: 0 auto;
  color: var(--font-color);
}

.tab-container {
  background-color: var(--card-bg);
  padding: 40px;
  border-radius: 10px;
  box-shadow: var(--shadow-color);
  min-height: 250px;
}

.main-title {
  margin-top: 10px;
  text-align: left;
  margin-bottom: 10px;
  color: var(--font-color);
  font-size: 24px;
}

.sub-title{

  text-align: left;
  margin-bottom: 10px;
  color: var(--font-color);
  font-size: 14px;
  font-weight: 400;
}

.el-tabs {
  height: 100%;
  color: var(--font-color);
}

.el-tabs--left .el-tabs__content {
  padding-left: 30px;
}

:deep(.el-tabs__item){
  color: var(--font-color);
}
</style>
