<template>
  <div class="app-container home">
    
    <el-row>
      <el-col :lg="12" style="padding-left: 20px">
        <h2>项目说明</h2>
        <p>这是虚假信息检测系统首页</p>
        <p>欢迎，{{ user.username }}！</p>
      </el-col>
    </el-row>
  </div>
</template>

<script>


export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {}  // 从 localStorage 获取用户信息
    };
  },
  methods: {
    logout() {
      // 清除用户信息并跳转到登录页面
      localStorage.removeItem('user');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 50px;
}

button {
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #388e3c;
}
</style>

