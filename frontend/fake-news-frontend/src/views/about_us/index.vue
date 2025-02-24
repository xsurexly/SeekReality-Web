<template>
  <div class="aboutUs-container">
    <el-card class="hero-section">
      <h1>关于我们</h1>
      <p>我们致力于通过科技创新解决虚假新闻问题，为用户提供可靠的信息来源。</p>
    </el-card>

    <div class="text">
      <!-- 团队介绍 -->
      <h2>团队使命</h2>
      <p>我们的团队汇聚了来自不同领域的专家，旨在通过先进的技术手段，为社会提供更加透明、可靠的信息。我们使用机器学习和人工智能技术，帮助用户识别虚假新闻和不实信息，提升信息消费的质量。</p>
      
      <el-divider></el-divider>

      <!-- 公司历史、愿景、使命 -->
      <h2>我们的愿景与使命</h2>
      <el-row :gutter="20">
        <el-col :span="8" v-for="item in infoSections" :key="item.title">
          <el-card class="info-card">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ElCard, ElRow, ElCol, ElDivider } from 'element-plus';

export default {
  name: 'AboutUs',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElDivider
  },
  data() {
    return {
      infoSections: [
        { title: '公司历史', description: '我们的项目始于对虚假新闻问题的深刻思考，并且不断优化技术，以应对信息流通中日益严重的虚假信息问题。' },
        { title: '我们的愿景', description: '通过技术手段，帮助人们准确获取真实信息，成为虚假新闻识别领域的领导者，推动全球信息透明化进程。' },
        { title: '我们的使命', description: '我们的使命是建立一个智能、透明的新闻验证平台，提升用户的信息甄别能力，保护公众免受虚假信息的侵害。' }
      ]
    };
  }
};
</script>

<style scoped>
.aboutUs-container {
  font-family: 'Poppins', sans-serif;
  color: black;
  text-align: center;
  padding-bottom: 50px;
}

.hero-section {
  margin: 0 auto;
  width: 95%;
  padding: 60px 20px;
  background: linear-gradient(135deg, #EBF5F4, #409EFF);
  border-radius: 15px;
  text-align: center;
  transition: transform 0.3s ease;
}

.hero-section:hover {
  transform: scale(1.02);
  border-radius: 15px;
}

h1 {
  font-size: 3em;
  font-weight: bold;
  margin-bottom: 10px;
}

p {
  font-size: 1.2em;
  opacity: 0.8;
}

.text {
  padding: 20px 20px;
}

.info-card {
  background: linear-gradient(135deg, #EBF5F4, #409EFF);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: scale(1.05);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .hero-section {
    margin: 10px;
  }
  .info-card {
    margin: 10px;
  }
}
</style>