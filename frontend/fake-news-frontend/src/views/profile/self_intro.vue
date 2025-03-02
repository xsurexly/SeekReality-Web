<template>
  <div class="user-info">
    <el-form :model="form" label-width="100px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" :disabled="!isEditing" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" :disabled="!isEditing" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.phone" :disabled="!isEditing" />
      </el-form-item>
      <el-form-item label="个人简介">
        <el-input
          v-model="form.bio"
          type="textarea"
          :rows="4"
          :disabled="!isEditing"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleEdit"
          v-if="!isEditing"
        >
          编辑信息
        </el-button>
        <el-button
          type="success"
          @click="handleSave"
          v-else
        >
          保存修改
        </el-button>
        <el-button @click="handleCancel" v-if="isEditing">
          取消
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const isEditing = ref(false)
const originalData = {
  username: localStorage.getItem('username') || '用户123',
  email: localStorage.getItem('email') || 'user@example.com',
  phone: localStorage.getItem('phone') || '13800138000',
  bio: localStorage.getItem('bio') || '这个人很懒，什么都没留下'
}

const form = reactive({ ...originalData })

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = () => {
  Object.keys(form).forEach(key => {
    localStorage.setItem(key, form[key])
  })
  ElMessage.success('信息保存成功')
  isEditing.value = false
}

const handleCancel = () => {
  Object.assign(form, originalData)
  isEditing.value = false
}

</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;
:deep(.el-form-item__label){
  color:var(--font-color)!important;
}

</style>
