<template>
  <div class="login-container">
    <img src="../assets/logo.png" alt="" style="width: 250px;margin-bottom: 50px;">

    <form @submit.prevent="login">
      <label for="email"></label>
      <input type="text" v-model="email" id="email" placeholder="请输入注册邮箱" autocomplete="off" required>
      <label for="password"></label>
      <input type="password" v-model="password" id="password" placeholder="请输入密码" autocomplete="off" required >
      <input type="submit" value="登录">
    </form>
    <p>
      <router-link to="/password_modify" class="password_modify">忘记密码</router-link>
      <router-link to="/register" class="register-link">点击注册</router-link>
    </p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    async login() {
      console.log('登录按钮被点击');
      try {
        const response = await fetch('/apis/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        });

        const data = await response.json();
        console.log(data); // 打印返回的数据，确保返回的字段和结构正确

        if (data.success) {
          console.log('登录成功，用户信息：', data.user);
          localStorage.setItem('user', JSON.stringify(data.user)); // 保存用户信息到 localStorage
          localStorage.setItem('userid', data.user.userid);
          localStorage.setItem('username', data.user.username);
          localStorage.setItem('email', data.user.email);  // 存储邮箱
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

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

body, html {
  height: 100%;
  margin: 0;
  font-family: 'Arial', sans-serif;
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
}

/* 登录容器样式 */
.login-container {
  width: 350px;
  margin: 0px auto;
  margin-top: 150px;
  margin-bottom: 30px;
  text-align: center;
  align-items: center;
  background-color: var(--card-bg);
  padding: 60px;
  border-radius: 10px;
  box-shadow: #b5b5b5 0px 5px 15px;
  border: 1px solid #b5b5b5;
}

/* 标题样式 */
.login-container h1 {
  margin-bottom: 20px;
  color: var(--font-color);
  font-size: 1.8rem;
  font-weight: 550;

}

/* 表单标签样式 */
form label {
  display: block;
  font-weight: bold;
  color: var(--font-color);
  margin-bottom: 5px;
  text-align: left;
}

/* 输入框样式 */
input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 25px;
  border: 1px solid #b5b5b5;
  border-radius: 5px;
  font-size: 1rem;
  box-sizing: border-box;
}

/* 输入框聚焦效果 */
input[type="text"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
}

/* 按钮样式 */
input[type="submit"] {
  background-color: #409EFF;
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

.register-link {
  color: #409EFF;
  text-decoration: none;
  float: right;
}

.register-link:hover {
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

/* 按钮悬停效果 */
input[type="submit"]:hover {
  background-color: rgb(121.3, 187.1, 255); /* 悬停时按钮变深绿色 */
}
input[type="submit"]:active {
  background-color: rgb(121.3, 187.1, 255);
}

/* 响应式支持 */
@media (max-width: 300px) {
  .login-container {
    width: 60%;
    padding: 20px;
  }

  input[type="submit"] {
    font-size: 0.9rem;
  }
}
</style>
