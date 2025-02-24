<template>
  <div class="register-container">
    <img src="../assets/logo.png" alt="" style="width: 250px;margin-bottom: 50px;">

    <form @submit.prevent="register">
      <label for="username"></label>
      <input type="text" v-model="username" id="username" placeholder="请输入用户名" required><br>
      <label for="password"></label>
      <input type="password" v-model="password" id="password" placeholder="请输入密码" required><br>
      <label for="confirmPassword"></label>
      <input type="password" v-model="confirmPassword" id="confirmPassword" placeholder="请确认密码" required><br>
      <label for="email"></label>
      <input type="email" v-model="email" id="email" placeholder="请输入邮箱"><br>
      <input type="submit" value="注册">
    </form>
    <p>
      <router-link to="/password_modify" class="password_modify">忘记密码</router-link>
      <router-link to="/login" class="login-link">前往登录</router-link>
    </p>

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
  color: #000000;
  width: 350px;
  margin: 0px auto;
  border-radius: 10px;
  text-align: center;
  margin-top: 100px;
  margin-bottom: 30px;
  background-color: #fff;
  padding: 60px;
  border-radius: 5px;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
}

p {
  color:black;
}

.login-link {
  color: #409EFF;
  text-decoration: none;
  float: right;
}

.login-link:hover {
  text-decoration: underline;
}

.password_modify {
  color: #409EFF;
  text-decoration: none;
  float: left;
}

.password_modify:hover {
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
  margin-bottom: 25px;
  border: 1px solid #b5b5b5;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1rem;
}
input[type="text"]:focus,
input[type="password"]:focus,
input[type="email"]:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
}

input[type="submit"] {
  background-color: #409EFF; /* 按钮绿色背景 */
  color: white;
  padding: 12px;
  width: 100%;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 15px;
}
input[type="submit"]:hover {
  background-color: rgb(121.3, 187.1, 255);
}
input[type="submit"]:active {
  background-color: rgb(121.3, 187.1, 255);
}

/* 响应式支持 */
@media (max-width: 400px) {
  .register-container {
    width: 90%;
    padding: 20px;
  }

  input[type="submit"] {
    font-size: 0.9rem;
  }
}

</style>