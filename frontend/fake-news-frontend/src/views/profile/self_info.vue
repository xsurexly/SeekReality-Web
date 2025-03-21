<template>
  <div class="user-info">
    <div class="info-header">
      <h3>基本信息</h3>
      <h5>请及时更新信息以便找回密码！</h5>
    </div>
    <el-row :gutter="20" class="info-content">
      <el-col :span="6" class="avatar-section">
        <div class="avatar-card">
          <el-upload
            class="avatar-uploader"
            :action="`http://localhost:5000/profile/upload-avatar`"
            :headers="uploadHeaders"
            :data="uploadData"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :on-error="handleAvatarError"
            :before-upload="beforeAvatarUpload"
            :disabled="!isEditing"
          >
            <el-avatar
              :size="150"
              :src="avatarUrl"
              class="user-avatar"
            >
              <img src="https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png" />
            </el-avatar>
            <el-button
              type="primary"
              :disabled="!isEditing"
              class="upload-button"
            >
            <el-icon><svg-icon icon-name="icon-xiugai" /></el-icon>
            </el-button>
          </el-upload>
          <div class="user-info-text">
            <p>{{ user.username }}</p>
            <p>{{ user.userid }}</p>
          </div>
        </div>
      </el-col>
      <el-col :span="18" class="form-section">
        <el-form :model="user" label-width="100px">
          <el-form-item label="用户名">
            <el-input
              v-model="user.username"
              :disabled="!isEditing"
              placeholder="请输入用户名"
            />
          </el-form-item>
          <el-form-item label="性别">
            <el-select
              v-model="user.gender"
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

const getStoredUser = () => {
  try {
    // 从localStorage获取完整的用户信息
    const storedUsername = localStorage.getItem('username')
    const storedUserid = localStorage.getItem('userid')
    const storedGender = localStorage.getItem('gender')

    // 如果没有用户信息，返回默认值
    if (!storedUsername || !storedUserid) {
      return { username: '未登录', userid: '', gender: '男' }
    }

    return {
      username: storedUsername,
      userid: storedUserid,
      gender: storedGender || '男'
    }
  } catch {
    return { username: '未登录', userid: '', gender: '男' }
  }
}

const isEditing = ref(false)
const user = ref(getStoredUser())
const avatar = ref(localStorage.getItem('avatar') || 'avatar.png')

const genders = ['男', '女', '其他']

onMounted(() => {
  // 重新获取用户信息
  const userData = getStoredUser()
  user.value = userData

  // 如果没有用户信息，可以考虑重定向到登录页面
  if (!userData.username || userData.username === '未登录') {
    ElMessage.warning('请先登录')
    // 可以添加重定向逻辑
    // router.push('/login')
  }
})

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = async () => {
  try {
    // 打印检查发送的数据
    console.log('Sending data:', {
      userid: user.value.userid,
      username: user.value.username,
      gender: user.value.gender
    });

    const response = await fetch('/apis/profile/update-profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userid: user.value.userid,
        username: user.value.username,
        gender: user.value.gender
      })
    });

    const data = await response.json();

    if (data.success) {
      // 更新本地存储
      localStorage.setItem('username', user.value.username);
      localStorage.setItem('gender', user.value.gender);
      localStorage.setItem('userid', user.value.userid); // 确保也存储 userid
      ElMessage.success('信息保存成功');
      isEditing.value = false;
    } else {
      ElMessage.error(data.message || '保存失败');
    }
  } catch (error) {
    console.error('Error:', error);
    ElMessage.error('网络错误，请稍后重试');
  }
}

const handleCancel = () => {
  // 恢复原始数据
  user.value.username = localStorage.getItem('username') || '小星'
  user.value.gender = localStorage.getItem('gender') || '男'
  isEditing.value = false
}

// 计算上传需要的数据
const uploadData = computed(() => ({
  userid: user.value.userid
}))

// 设置上传请求头
const uploadHeaders = {
  'Accept': 'application/json'
}

// 计算头像URL
const avatarUrl = computed(() => {
  if (avatar.value && avatar.value.startsWith('http')) {
    return avatar.value
  }
  return avatar.value ? `http://localhost:5000${avatar.value}` : 'https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png'
})

// 处理头像上传成功
const handleAvatarSuccess = (response) => {
  if (response.message === '头像上传成功') {
    avatar.value = response.avatar
    localStorage.setItem('avatar', response.avatar)
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error('头像上传失败')
  }
}

// 处理头像上传错误
const handleAvatarError = (error) => {
  console.error('Avatar upload error:', error)
  ElMessage.error('头像上传失败，请重试')
}

// 上传前的验证
const beforeAvatarUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG 格式的图片!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
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
  border-right: 1px solid #eeeeee;

  .avatar-card {
    text-align: center;
  }

  .user-info-text {
    margin-top: 10px;

    p {
      margin-top: -10px;
      font-size: 16px;
      color:var(--font-color)
    }
  }
}

.avatar-uploader {
  position: relative;
  display: inline-block;
}

.upload-button {
  position: absolute;
  top: 30px;
  right: 30px;
  transform: translate(50%, -50%);
  padding:10px;
  font-size: 12px;
  z-index: 1;
  border-radius: 5px;
  background-color: #fff;
}

:deep(.el-button.is-disabled){
  background-color: #fff;
}

:deep(.el-button.is-disabled:hover){
  background-color: #fff;
}

.user-avatar {
  cursor: pointer;
  border: none !important;
  background-color: transparent !important;
}

.form-section {
  flex: 1;
  padding: 0 20px;

  .el-form {
    width: 60%;
  }
}

.update-button {
  margin-left: 0 !important;
}

:deep(.el-form-item__label) {
  color:var(--font-color);
  margin-top:10px ;
}
</style>
