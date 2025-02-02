<template>
  <div class="profile-container">
    <h1>个人资料</h1>
    <div class="profile-info">
      <div class="avatar-container">
        <img :src="user.avatar || defaultAvatar" alt="用户头像" class="avatar" />
        <input type="file" @change="uploadAvatar" accept="image/*" class="avatar-upload" />
      </div>
      <p>用户名: <input v-model="user.username" class="input-field" /></p>
      <p>邮箱: <input v-model="user.email" class="input-field" /></p>
      <button @click="saveProfile">保存个人资料</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      defaultAvatar: 'https://via.placeholder.com/150', // 默认头像
    };
  },
  methods: {
    // 上传头像
    uploadAvatar(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          this.user.avatar = reader.result; // 将头像图片转换为 base64 并保存
          localStorage.setItem('user', JSON.stringify(this.user)); // 保存到 localStorage
        };
        reader.readAsDataURL(file); // 读取文件内容为 base64
      }
    },

    // 保存个人资料（模拟）
    saveProfile() {
      // 这里你可以通过 API 调用将更新的用户信息保存到数据库
      localStorage.setItem('user', JSON.stringify(this.user)); // 更新本地存储的用户信息
      alert('个人资料保存成功');
    }
  }
};
</script>

<style scoped>
.profile-container {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background-color: #ffffff;
  color: #333;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  align-items: center;
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 2.5em;
}

.profile-info {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
}

.avatar-upload {
  margin-top: 10px;
}

.input-field {
  padding: 8px;
  font-size: 1rem;
  margin-bottom: 10px;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover {
  background-color: #388e3c;
}
</style>
