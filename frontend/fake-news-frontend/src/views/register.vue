<template>
  <div class="register-container">
    <h1>新用户注册</h1>
    <form @submit.prevent="register">
      <label for="username">用户名：</label>
      <input type="text" v-model="username" id="username" placeholder="请输入用户名" required><br>
      <label for="password">密码：</label>
      <input type="password" v-model="password" id="password" placeholder="请输入密码" required><br>
      <label for="confirmPassword">确认密码：</label>
      <input type="password" v-model="confirmPassword" id="confirmPassword" placeholder="请确认密码" required><br>
      <label for="email">邮箱（可选）：</label>
      <input type="email" v-model="email" id="email" placeholder="请输入邮箱"><br>
      <input type="submit" value="注册">
    </form>
    <p>已有账户？<router-link to="/login" class="login-link">登录</router-link></p>

  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      email: ''
    };
  },
  methods: {
    async register() {
      if (this.password!== this.confirmPassword) {
        alert('两次输入的密码不一致，请重新输入！');
        return;
      }
      try {
        const response = await fetch('http://127.0.0.1:5000/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
            email: this.email
          })
        });
        const data = await response.json();
        if (data.success) {
          alert('注册成功！');
          this.$router.push('/login');
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('注册请求出错：', error);
        alert('注册请求出现问题，请稍后再试！');
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  font-family: 'Roboto', sans-serif;
  background-color: #EBF5F4;
  color: #000000;
  width: 350px;
  margin: 0px auto;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
  margin-top: 100px;
  margin-bottom: 30px;
}

p {
  color:black;
}

.login-link {
  color: #4EBFB9;
  text-decoration: none;
  font-weight: bold;
}

.login-link:hover {
  text-decoration: underline;
}

.register-container h1 {
  margin-bottom: 20px;
  color: #000000; /* 深绿色标题 */
  font-size: 1.8rem;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  text-align: left;
}
input[type="text"],
input[type="password"],
input[type="email"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #86D9D4;
  border-radius: 5px;
  background-color: #c8e9e6a5; /* 浅绿色背景 */
  box-sizing: border-box;
  font-size: 1rem;
}
input[type="text"]:focus,
input[type="password"]:focus,
input[type="email"]:focus {
  border-color: #279C9C;
  outline: none;
  box-shadow: 0 0 5px 000000ae(46, 125, 50, 0.5);
}
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
input[type="submit"]:hover {
  background-color: #86D9D4;
}
input[type="submit"]:active {
  background-color: #86D9D4;
}

</style>