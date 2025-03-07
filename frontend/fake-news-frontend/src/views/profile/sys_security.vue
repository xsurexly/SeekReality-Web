<template>
  <div class="security-settings">
    <div class="settings-header">
      <h3>账户安全</h3>
      <h5>通过修改密码等方式，增加账户安全性</h5>
    </div>
    <el-form
      :model="form"
      label-width="120px"
      :rules="rules"
      ref="formRef"
    >
      <el-form-item label="当前密码" prop="currentPassword">
        <el-input
          v-model="form.currentPassword"
          type="password"
          show-password
          :disabled="!isEditingPassword"
          placeholder="请输入当前密码"
        />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input
          v-model="form.newPassword"
          type="password"
          show-password
          :disabled="!isEditingPassword"
          placeholder="请输入新密码"
        />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          show-password
          :disabled="!isEditingPassword"
          placeholder="请确认新密码"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleEditPassword"
          v-if="!isEditingPassword"
        >
          修改
        </el-button>
        <el-button
          type="success"
          @click="submitForm"
          v-else
        >
          保存
        </el-button>
        <el-button
          @click="handleCancelPassword"
          v-if="isEditingPassword"
        >
          取消
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const isEditingPassword = ref(false)
const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const formRef = ref(null)

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能小于6位'))
  } else {
    if (form.confirmPassword !== '') {
      formRef.value.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive({
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPass, trigger: 'blur' }
  ]
})

const handleEditPassword = () => {
  isEditingPassword.value = true
}

const submitForm = () => {
  formRef.value.validate(valid => {
    if (valid) {
      // 这里应该调用修改密码的API
      ElMessage.success('密码修改成功')
      formRef.value.resetFields()
      isEditingPassword.value = false
    }
  })
}

const handleCancelPassword = () => {
  formRef.value.resetFields()
  isEditingPassword.value = false
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

.security-settings {
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

:deep(.el-form-item__label) {
  color: var(--font-color) !important;
}
</style>
