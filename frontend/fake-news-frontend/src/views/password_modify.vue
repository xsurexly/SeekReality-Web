<template>
  <div class="findpassword-container">
    <img src="../assets/logo.png" alt="" style="width: 250px; margin-bottom: 50px;">
    
    <form @submit.prevent="submitForm">
      <label for="email"></label>
      <input type="email" v-model="email" id="email" placeholder="请输入邮箱" autocomplete="off" required>
      
      <label for="username"></label>
      <input type="text" v-model="username" id="username" placeholder="请输入用户名" autocomplete="off" required>

      <label for="password"></label>
      <input type="password" v-model="password" id="password" placeholder="请输入新密码" autocomplete="off" required>

      <label for="comfirmCode"></label>
      <div class="verification-container">
        <input type="text" v-model="comfirmCode" id="comfirmCode" placeholder="请输入验证码" autocomplete="off" required>
        <button @click.prevent="sendVerificationCode" class="send-code-btn">发送验证码</button>
      </div>
      
      <input type="submit" value="找回密码">
    </form>

    <p>
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
      email: '',
      comfirmCode: '',
      verificationCodeSent: false, // 判断验证码是否已发送
    };
  },
  methods: {
    async submitForm() {
      if (!this.verificationCodeSent) {
        alert('请先发送验证码');
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:5000/auth/find-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
            email: this.email,
            verificationCode: this.comfirmCode,
          }),
        });

        const data = await response.json();

        if (data.success) {
          alert('密码修改成功');
          this.$router.push('/login');
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('请求失败：', error);
        alert('找回密码失败，请稍后再试');
      }
    },

    async sendVerificationCode() {
      console.log('发送验证码按钮被点击');
      try {
        const response = await fetch('http://127.0.0.1:5000/auth/request-verification-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            email: this.email,
          }),
        });

        const data = await response.json();

        if (data.success) {
          alert('验证码已发送');
          this.verificationCodeSent = true;
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error('请求失败：', error);
        alert('验证码发送失败，请稍后再试');
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
.findpassword-container {
  width: 350px;
  height: 100%;
  margin: 0px auto;
  margin-top: 100px;
  margin-bottom: 30px;
  text-align: center;
  align-items: center;
  background-color: #fff;
  padding: 60px;
  border-radius: 5px;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
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
input[type="email"],
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
input[type="email"]:focus,
input[type="password"]:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
}

/* 验证码输入框和按钮容器样式 */
.verification-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.verification-container input {
  width: 60%;  /* 使输入框占大部分空间 */
  margin-top: 10px;
  margin-bottom: 10px;
  margin-right: 30px;  /* 输入框和按钮之间留一些空间 */
}

.send-code-btn {
  background-color: #409EFF; /* 按钮绿色背景 */
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.send-code-btn:hover {
  background-color: rgb(121.3, 187.1, 255); /* 悬停时按钮变深绿色 */
}

.send-code-btn:active {
  background-color: rgb(121.3, 187.1, 255);
}

/* 按钮样式 */
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
  margin-top: 10px;
}

/* 按钮悬停效果 */
input[type="submit"]:hover {
  background-color: rgb(121.3, 187.1, 255); /* 悬停时按钮变深绿色 */
}
input[type="submit"]:active {
  background-color: rgb(121.3, 187.1, 255);
}

.login-link {
  color: #409EFF;
  text-decoration: none;
  float: right;
}

.login-link:hover {
  text-decoration: underline;
}

/* 响应式支持 */
@media (max-width: 400px) {
  .findpassword-container {
    width: 90%;
    padding: 20px;
  }

  input[type="submit"] {
    font-size: 0.9rem;
  }

  .verification-container input {
    width: 70%;  /* 在小屏幕上调整输入框的宽度 */
  }

  .verification-container .send-code-btn {
    padding: 8px 12px; /* 调整按钮的大小 */
  }
}
</style>
