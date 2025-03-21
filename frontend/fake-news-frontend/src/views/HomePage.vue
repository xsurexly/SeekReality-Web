<template>
  <div class="home">
    <!-- 头部 -->
    <div class="header">
      <h1>星眸查讯</h1>
      <h2>智能虚假新闻分析平台 这是星眸查讯的第一个完整版本</h2>
      <p>
        星眸查讯是一个创新的虚假新闻检测平台，旨在通过先进的深度学习技术，提供精确的虚假新闻检测和分析，同时给用户提供新闻阅读功能。
      </p>
      <el-button type="primary" size="large" class="start-btn" @click="goToLogin">开始使用</el-button>
    </div>

    <!-- 功能介绍 -->
    <div class="features">
      <h2>功能服务</h2>
      <p>平台提供多样的服务，确保良好的用户体验</p>
      <el-row :gutter="20">
        <!-- 第一排：3个功能 -->
        <el-col :span="8" v-for="(feature, index) in features.slice(0, 3)" :key="index">
          <div class="feature-item">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </el-col>
      </el-row>
      <!-- 上下两排的间隔 -->
      <div style="margin-top: 20px;"></div>
      <el-row :gutter="20">
        <!-- 第二排：3个功能 -->
        <el-col :span="8" v-for="(feature, index) in features.slice(3, 6)" :key="index + 3">
          <div class="feature-item">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 底部 -->
    <div class="footer">
      <p>© 2025 星眸查讯. 版权所有.</p>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
  name: "HomeView",
  setup() {
    const router = useRouter();
    const goToLogin = () => {
      router.push({ name: 'login' });
    };
    return { goToLogin };
  },
  data() {
    return {
      features: [
        { title: "多种模型选择", description: "提供3种检测模型，确保检测效果。" },
{ title: "文本文件检测", description: "提供多种检测方式，方便用户使用。" },
        { title: "AI助手交互", description: "内置AI助手，提升用户体验。" },

        { title: "多来源新闻阅读", description: "多样化新闻阅读，获取最新资讯。" },
        { title: "丰富可视化", description: "提供地图、图表等可视化分析。" },
        { title: "精美UI界面", description: "简洁美观，提升用户体验。" },

      ]
    };
  }
};
</script>

<style scoped>
.home {
  font-family: 'Arial', sans-serif;
}

/* 头部样式 */
.header {
  text-align: center;
  padding: 10px 20px;
  background-image:url("image.png");
  background-size: contain;
  background-position: right;
  background-repeat: no-repeat;
  color: black;
  border-radius: 12px;
}


.header h1 {
  font-size: 40px;
  font-weight: bold;
}

.header h2 {
  font-size: 24px;
  margin-top: 10px;
  opacity: 0.9;
}

.header p {
  font-size: 16px;
  max-width: 600px;
  margin: 20px auto;
  opacity: 0.8;
}
.nav {
  position: absolute;
  top: 20px;
  right: 20px;
}

.nav .el-button {
  color: white;
  font-size: 16px;
  margin: 0 5px;
}

.nav .el-button:hover {
  text-decoration: underline;
}
.start-btn {
  margin-top: 20px;
  background-color: #409EFF;
  border: none;
  padding: 12px 24px;
  font-size: 18px;
  border-radius: 8px;
  transition: all 0.3s;
}

.start-btn:hover {
  background-color: rgb(131, 193, 255);
}


/* 功能介绍 */
.features {
  margin-top: 20px;
  padding: 10px 20px;
  text-align: center;
}

.features h2 {
  font-size: 28px;
  color: #333;
  text-align: center;
}

.features p {
  font-size: 16px;
  color: #666;
  margin-bottom: 40px;
}

.feature-item {
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15);
}

.feature-item h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
}

.feature-item p {
  font-size: 16px;
  color: #666;
}

/* 底部样式 */
.footer {
  text-align: center;

  background: var(--bg-color);
  border-radius: 12px;
}

.footer p {
  font-size: 14px;
  color: #666;
}
</style>
