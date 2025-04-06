<template>
  <div class="findpassword-container">
    <img src="../assets/logo.png" alt="Logo" style="width: 250px; margin-bottom: 50px;"/>

    <el-form
      :model="form"
      label-width="120px"
      :rules="rules"
      ref="formRef"
    >
      <el-form-item  prop="email" class="my-el-form">
        <el-input
          v-model="form.email"
          type="text"
          placeholder="请输入注册邮箱"
        />
      </el-form-item>
      <el-form-item  prop="newPassword" class="my-el-form">
        <el-input
          v-model="form.newPassword"
          type="password"
          show-password
          placeholder="请输入新密码"
        />
      </el-form-item>
      <el-form-item  prop="confirmPassword" class="my-el-form">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          show-password
          placeholder="请确认新密码"
        />
      </el-form-item>
      <el-form-item class="my-el-form">
        <el-button
          type="primary"
          @click="submitForm"
        >
          找回密码
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
          <el-button type="primary" @click="confirmPasswordChange">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <p class="mt-3">
      <router-link to="/login" class="login-link">前往登录</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const dialogVisible = ref(false)
const cooldown = ref(0)
const form = reactive({
  email:"",
  newPassword: '',
  confirmPassword: '',
})

const verificationForm = reactive({
  email: '',
  verificationCode: '',
})

const formRef = ref(null)
const verificationFormRef = ref(null)

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
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
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
      dialogVisible.value = true,
      verificationForm.email = form.email
    }
  })
}


const sendVerificationCode = async () => {
  try {
    // 基础验证
    if (!form.email) {
      ElMessage.warning('请先填写邮箱和用户名')
      return
    }

    const response = await fetch('/apis/auth/request-verification-code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: form.email,
      })
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('验证码已发送')
      cooldown.value = 60
      const timer = setInterval(() => {
        cooldown.value--
        if (cooldown.value <= 0) clearInterval(timer)
      }, 1000)
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    ElMessage.error('发送验证码失败')
  }
}

const confirmPasswordChange = async () => {
  try {
    // 表单验证
    await formRef.value.validate()

    const response = await fetch('/apis/auth/find-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: verificationForm.email,
        newPassword: form.newPassword,
        verificationCode: verificationForm.verificationCode
      })
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('密码修改成功')
      formRef.value.resetFields()
      // 清除验证码输入
      form.verificationCode = ''
    } else {
      ElMessage.error(data.message)
    }
  } catch (error) {
    if (error.name !== 'Error') {
      ElMessage.error('表单验证未通过')
    }
  }
}
</script>

<style scoped>
.findpassword-container {
  width: 400px;
  margin: 0 auto;
  margin-top: 80px;
  padding: 60px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #b5b5b5;
  text-align: center;
  align-items: center;
}


:deep(.el-input__wrapper){

  width: 100%;
  padding: 10px;
  margin-top: 25px;
  border: 1px solid #b5b5b5;
  border-radius: 5px;
  font-size: 1rem;
  box-sizing: border-box;
}

.el-form-item.my-el-form >:last-child {
   margin-left:0px !important;
}

.el-input:focus{
  outline: none;
  border-color: #409EFF;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
}

:deep(.el-button){
  background-color: #409EFF;
  color: white;
  padding: 12px;
  width: 100%;
  height: 40px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 15px;
}

:deep(.el-button:hover) {
  background-color: rgb(121.3, 187.1, 255); /* 悬停时按钮变深绿色 */
}
:deep(.el-button:active) {
  background-color: rgb(121.3, 187.1, 255);
}

.login-link {
  color: #409eff;
  text-decoration: none;
  float: right;
}

.login-link:hover {
  text-decoration: underline;
}

.mt-3 {
  margin-top: 15px;
}
</style>
