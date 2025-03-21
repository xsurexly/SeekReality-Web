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

    <el-dialog
      v-model="dialogVisible"
      title="验证身份"
      width="40%"
    >
      <el-form :model="verificationForm" :rules="verificationRules" ref="verificationFormRef">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="verificationForm.email" disabled />
        </el-form-item>
        <el-form-item label="验证码" prop="verificationCode">
          <div style="display: flex; gap: 10px;">
            <el-input v-model="verificationForm.verificationCode" placeholder="请输入验证码" />
            <el-button type="primary" @click="sendVerificationCode" :disabled="cooldown > 0">
              {{ cooldown > 0 ? `${cooldown}秒后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmPasswordChange">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive,onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const isEditingPassword = ref(false)
const dialogVisible = ref(false)
const cooldown = ref(0)
const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const verificationForm = reactive({
  email: '',
  verificationCode: '',
  username:'',
})

onMounted(() => {
  verificationForm.email = localStorage.getItem('email') || '';  // 确保获取邮箱
  verificationForm.username =  localStorage.getItem('username');
  console.log('获取到的邮箱:', verificationForm.email);  // 调试输出
  console.log('获取到的用户名:', verificationForm.username);  // 调试输出

})

const formRef = ref(null)
const verificationFormRef = ref(null)

// 验证规则
const verificationRules = {
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, max: 6, message: '验证码长度应为6位', trigger: 'blur' }
  ]
}

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
      dialogVisible.value = true
    }
  })
}

// 发送验证码
const sendVerificationCode = async () => {
  try {
    const response = await fetch('/apis/auth/request-verification-code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: verificationForm.email,
      })
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('验证码已发送')
      // 开始倒计时
      cooldown.value = 60
      const timer = setInterval(() => {
        cooldown.value--
        if (cooldown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('发送验证码失败')
  }
}

// 确认修改密码
const confirmPasswordChange = async () => {
  try {
    console.log('准备修改密码请求')
    console.log('请求数据:', {
      email: verificationForm.email,
      username: verificationForm.username,
      currentPassword: form.currentPassword,
      newPassword: form.newPassword,
      verificationCode: verificationForm.verificationCode
    })

    const response = await fetch('/apis/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: verificationForm.email,
        username: localStorage.getItem('username'),
        currentPassword: form.currentPassword,
        newPassword: form.newPassword,
        verificationCode: verificationForm.verificationCode
      })
    })

    const data = await response.json()
    console.log('修改密码响应:', data)

    if (data.success) {
      ElMessage.success('密码修改成功')
      dialogVisible.value = false
      isEditingPassword.value = false
      formRef.value.resetFields()
      verificationFormRef.value.resetFields()
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('修改密码失败')
  }
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
