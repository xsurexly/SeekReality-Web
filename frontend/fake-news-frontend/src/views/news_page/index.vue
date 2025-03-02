<template>
  <div class="news-container">
    <h1>新闻阅读</h1>
    <div v-if="news.length" class="news-list">
      <div v-for="item in news" :key="item.id" class="news-item">
        <img :src="item.picUrl || defaultAvatar" alt="新闻图片" class="news-image" />
        <div class="news-content">
          <h2>{{ item.title }}</h2>
          <p class="news-description">{{ item.description }}</p>
          <a :href="item.url" target="_blank" class="read-more">阅读全文</a> <!-- 确保链接指向目标新闻 -->
        </div>
      </div>
    </div>
    <div v-else>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NewsPage',
  data() {
    return {
      news: [],
      defaultAvatar: 'http://localhost:8080/default-avatar.png', // 默认头像路径
    };
  },
  created() {
    this.fetchNews();
  },
  methods: {
    async fetchNews() {
      try {
        const response = await axios.get('http://localhost:5000/news/get_news', {
          params: { num: 10, page: 3 }
        });
        console.log("获取到的新闻数据:", response.data);
        this.news = response.data;
      } catch (error) {
        console.error('获取新闻失败:', error);
        console.error('请求的URL:', error.config.url);
      }
    }
  }
};
</script>

<style scoped>
.news-container {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
  padding: 20px;
  max-width: 800px;
  margin: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.news-list {
  display: flex;
  flex-direction: column;
}

.news-item {
  background: white;
  border-radius: 8px;
  margin: 10px 0;
  padding: 15px;
  display: flex;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.news-item:hover {
  transform: scale(1.02);
}

.news-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  margin-right: 15px;
}

.news-content {
  flex-grow: 1;
}

.news-description {
  font-size: 14px;
  color: #555;
}

.read-more {
  display: inline-block;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.read-more:hover {
  background-color: #0056b3;
}
</style>
