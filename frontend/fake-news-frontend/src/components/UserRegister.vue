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
        const response = await fetch('http://127.0.0.1:5000/register', {
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
          this.$router.push('/');
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
<style>
.register-container {
  font-family: 'Roboto', sans-serif;
  background-color: #e8f5e9;
  color: #2e7d32;
  width: 350px;
  margin: 50px auto;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  text-align: center;
}
.register-container h1 {
  margin-bottom: 20px;
  color: #2e7d32; /* 深绿色标题 */
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
  border: 1px solid #c8e6c9;
  border-radius: 5px;
  background-color: #f1f8e9; /* 浅绿色背景 */
  box-sizing: border-box;
  font-size: 1rem;
}
input[type="text"]:focus,
input[type="password"]:focus,
input[type="email"]:focus {
  border-color: #81c784;
  outline: none;
  box-shadow: 0 0 5px rgba(46, 125, 50, 0.5);
}
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
input[type="submit"]:hover {
  background-color: #388e3c;
}
input[type="submit"]:active {
  background-color: #388e3c;
}
</style>