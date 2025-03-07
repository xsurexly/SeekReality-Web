<template>
  <div class="user-info">
    <div class="info-header">
      <h3>基本信息</h3>
      <h5>请及时更新信息以便找回密码，在第一次登陆后请注意填写邮箱！</h5>
    </div>
    <el-row :gutter="20" class="info-content">
      <el-col :span="6" class="avatar-section">
        <div class="avatar-card">
          <el-avatar
            :size="100"
            :src="avatarUrl"
            class="user-avatar"
          >
            <img
              src="https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png"
              alt="默认头像"
            />
          </el-avatar>
          <div class="user-info-text">
            <p>{{ form.username }}</p>
            <p>{{ form.userId }}</p>
            <p>Level: {{ form.level }}</p>
          </div>
        </div>
      </el-col>
      <el-col :span="18" class="form-section">
        <el-form :model="form" label-width="100px">
          <el-form-item label="邮箱">
            <el-input
              v-model="form.email"
              :disabled="!isEditing"
              placeholder="请输入邮箱"
            />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input
              v-model="form.nickname"
              :disabled="!isEditing"
              placeholder="请输入昵称"
            />
          </el-form-item>
          <el-form-item label="性别">
            <el-select
              v-model="form.gender"
              :disabled="!isEditing"
              placeholder="请选择性别"
            >
              <el-option
                v-for="(gender, index) in genders"
                :key="index"
                :label="gender"
                :value="gender"
              />
            </el-select>
          </el-form-item>
          <el-form-item v-if="!isEditing">
            <el-button
              type="primary"
              @click="handleEdit"
              class="update-button"
            >
              编辑
            </el-button>
          </el-form-item>
          <el-form-item v-else>
            <el-button type="success" @click="handleSave" class="update-button">
              保存
            </el-button>
            <el-button @click="handleCancel">取消</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const isEditing = ref(false)
const avatarUrl = ref(localStorage.getItem('avatar') || '')

const form = reactive({
  username: localStorage.getItem('username') || '王小二',
  userId: localStorage.getItem('userId') || '0000001',
  level: localStorage.getItem('level') || '0',
  email: localStorage.getItem('email') || '',
  nickname: localStorage.getItem('nickname') || '',
  gender: localStorage.getItem('gender') || '男'
})

const genders =([' ref男', '女', '其他'])

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = () => {
  // 保存逻辑
  Object.keys(form).forEach(key => {
    localStorage.setItem(key, form[key])
  })
  ElMessage.success('信息保存成功')
  isEditing.value = false
}

const handleCancel = () => {
  // 恢复原始数据
  form.username = localStorage.getItem('username') || '王小二'
  form.email = localStorage.getItem('email') || ''
  form.nickname = localStorage.getItem('nickname') || ''
  form.gender = localStorage.getItem('gender') || '男'
  isEditing.value = false
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

.user-info {
  padding: 20px;
  
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.info-header {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  margin-bottom: 20px;
  border-bottom: 1px solid #eeeeee;
  padding-bottom: 10px;

  h3 {
    margin: 0;
    text-align: left;
    font-size: 18px;
    margin-bottom: 10px;
    color:var(--font-color);
  }

  h5 {
    margin: 0;
    text-align: left;
    font-size: 14px;
    font-weight: 400;
    margin-bottom: 10px;
    color:var(--font-color);
  }
}

.info-content {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-right: 1px solid #eeeeee;

  .avatar-card {
    text-align: center;
  }

  .user-info-text {
    margin-top: 10px;

    p {
      margin: 5px 0;
      font-size: 16px;
      color:var(--font-color)
    }
  }
}

.form-section {
  flex: 1;
  padding: 0 20px;

  .el-form {
    width: 100%;
  }
}

.update-button {
  margin-left: 0 !important;
}

:deep(.el-form-item__label) {
  font-weight: bold;
  color:var(--font-color)
}
</style>
