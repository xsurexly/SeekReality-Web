<template>
  <div class="login-container">
    <h1>用户登录</h1>
    <form @submit.prevent="login">
      <label for="username">用户名：</label>
      <input type="text" v-model="username" id="username" placeholder="请输入用户名" autocomplete="off" required>
      <label for="password">密码：</label>
      <input type="password" v-model="password" id="password" placeholder="请输入密码" autocomplete="off" required >
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
      password: '',
    };
  },
  methods: {
    async login() {
      console.log('登录按钮被点击');
      try {
        const response = await fetch('http://127.0.0.1:5000/auth/login', {
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
        console.log(data); // 打印返回的数据，确保返回的字段和结构正确

        if (data.success) {
          console.log('登录成功，用户信息：', data.user);
          localStorage.setItem('user', JSON.stringify(data.user)); // 保存用户信息到 localStorage
          this.$router.push('/home'); // 登录成功后跳转到主页
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
  background-color: #EBF5F4; /* 浅绿色背景 */
  width: 350px;
  margin: 0px auto;
  margin-top: 150px;
  margin-bottom: 30px;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  align-items: center;
  
}

/* 标题样式 */
.login-container h1 {
  margin-bottom: 20px;
  color: #000000; /* 深绿色标题 */
  font-size: 1.8rem;

}

/* 表单标签样式 */
form label {
  display: block;
  font-weight: bold;
  color: #000000;
  margin-bottom: 5px;
  text-align: left;
}

/* 输入框样式 */
input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #87C1AA;
  border-radius: 5px;
  background-color: #c8e9e6a5; /* 浅绿色背景 */
  font-size: 1rem;
  box-sizing: border-box;
}

/* 输入框聚焦效果 */
input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #279C9C; /* 聚焦时边框变深绿色 */
  box-shadow: 0 0 5px #000000ae (46, 125, 50, 0.5);
}

/* 按钮样式 */
input[type="submit"] {
  background-color: #4EBFB9; /* 按钮绿色背景 */
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
  color: #4EBFB9;
  text-decoration: none;
  font-weight: bold;
}

.register-link:hover {
  text-decoration: underline;
}

/* 按钮悬停效果 */
input[type="submit"]:hover {
  background-color: #86D9D4; /* 悬停时按钮变深绿色 */
}
input[type="submit"]:active {
  background-color: #86D9D4;
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
