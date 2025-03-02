<template>
  <div class="security-settings">
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
        />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input
          v-model="form.newPassword"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          show-password
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">
          修改密码
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

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

const submitForm = () => {
  formRef.value.validate(valid => {
    if (valid) {
      // 这里应该调用修改密码的API
      ElMessage.success('密码修改成功')
      formRef.value.resetFields()
    }
  })
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;
:deep(.el-form-item__label){
  color:var(--font-color)!important;
}
</style>
