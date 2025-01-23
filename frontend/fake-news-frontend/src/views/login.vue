<template>
  <div class="login-container">
    <h1>用户登录</h1>
    <form @submit.prevent="login">
      <label for="username">用户名：</label>
      <input type="text" v-model="username" id="username" placeholder="请输入用户名" required>
      <label for="password">密码：</label>
      <input type="password" v-model="password" id="password" placeholder="请输入密码" required>
      <input type="submit" value="登录">
    </form>
    <p>
      还没有账号？
      <router-link to="/register" class="register-link">点击注册</router-link>
    </p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });
        const data = await response.json();
        if (data.success) {
          alert('登录成功！');
          localStorage.setItem('user', JSON.stringify(data.user));
          this.$router.push('/home');
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('登录请求出错：', error);
        alert('登录请求出现问题，请稍后再试！');
      }
    }
  }
};
</script>

<style scoped>

body, html {
  height: 100%;
  margin: 0;
  font-family: 'Arial', sans-serif;
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
  background-color: #f0f4f1; /* 背景色 */
}

/* 登录容器样式 */
.login-container {
  
  font-family: 'Arial', sans-serif;
  background-color: #e8f5e9; /* 浅绿色背景 */
  width: 350px;
  margin: 0px auto;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  align-items: center;
  margin-top: 200px;
}

/* 标题样式 */
.login-container h1 {
  margin-bottom: 20px;
  color: #2e7d32; /* 深绿色标题 */
  font-size: 1.8rem;

}

/* 表单标签样式 */
form label {
  display: block;
  font-weight: bold;
  color: #2e7d32;
  margin-bottom: 5px;
  text-align: left;
}

/* 输入框样式 */
input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #c8e6c9;
  border-radius: 5px;
  background-color: #f1f8e9; /* 浅绿色背景 */
  font-size: 1rem;
  box-sizing: border-box;
}

/* 输入框聚焦效果 */
input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #81c784; /* 聚焦时边框变深绿色 */
  box-shadow: 0 0 5px rgba(46, 125, 50, 0.5);
}

/* 按钮样式 */
input[type="submit"] {
  background-color: #4caf50; /* 按钮绿色背景 */
  color: white;
  padding: 12px;
  width: 100%;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.register-link {
  color: #388e3c;
  text-decoration: none;
  font-weight: bold;
}

.register-link:hover {
  text-decoration: underline;
}

/* 按钮悬停效果 */
input[type="submit"]:hover {
  background-color: #388e3c; /* 悬停时按钮变深绿色 */
}
input[type="submit"]:active {
  background-color: #388e3c;
}

/* 响应式支持 */
@media (max-width: 400px) {
  .login-container {
    width: 90%;
    padding: 20px;
  }

  input[type="submit"] {
    font-size: 0.9rem;
  }
}
</style>
