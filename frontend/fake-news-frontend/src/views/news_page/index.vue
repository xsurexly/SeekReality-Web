<template>
  <div class="news-container">
    <!-- 搜索和筛选区域 -->
    <div class="search-filters">
      <el-input
        v-model="searchQuery"
        placeholder="搜索新闻..."
        class="search-input"
        @input="debounceSearch"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select v-model="selectedSource" placeholder="选择来源" clearable @change="fetchNews">
        <el-option
          v-for="source in sources"
          :key="source.name"
          :label="`${source.name} (${source.count})`"
          :value="source.name"
        />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        placeholder="选择日期范围"
        @change="fetchNews"
        style="width: 250px;"
      />
    </div>

    <!-- 新闻网格 -->
    <div class="news-grid">
      <el-empty v-if="news.length === 0" description="暂无新闻" />

      <transition-group name="news-fade">
        <div
          v-for="item in news"
          :key="item.id"
          class="news-grid-item"
          @click="item?showNewsDetail(item) :null"
        >
          <div class="news-card">
            <el-image
              :src="item.picUrl || defaultImage"
              :alt="item.title"
              class="news-image"
              fit="cover"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>

            <div class="news-content">
              <h3 class="news-title">{{ item.title }}</h3>
              <div class="news-meta">
                <el-tag size="small" type="info">{{ item.source }}</el-tag>
                <span class="news-time">{{ formatTime(item.ctime) }}</span>
                <el-tag
                  size="small"
                  :type="getFakeNewsTagType(item.fake_score)"
                  class="fake-news-tag"
                >
                  真实度: {{ formatScore(item.fake_score) }}
                </el-tag>
              </div>
              <p class="news-description">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 新闻详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedNews?.title"
      width="80%"
      class="news-dialog"
      @close="closeDialog"
      destroy-on-close
    >
      <div v-if="selectedNews" class="dialog-content">
        <div class="article-meta">
          <el-tag size="small" type="info">{{ selectedNews.source }}</el-tag>
          <span class="time">{{ formatTime(selectedNews.ctime) }}</span>
          <div class="detection-info">
            <el-tag
              :type="getFakeNewsTagType(selectedNews.fake_score)"
              effect="dark"
              @click="$router.push('/textdetect')"
            >
              真实度: {{ formatScore(selectedNews.fake_score) }}
            </el-tag>
          </div>
          <el-button
            type="warning"
            @click="toggleFavorite(selectedNews)"
          >
            {{ selectedNews.is_favorite ? '取消收藏' : '收藏' }}
          </el-button>
          <a :href="selectedNews.url" target="_blank" class="source-link">
            <el-button type="primary" size="small">查看原文</el-button>
          </a>
        </div>

        <div class="article-main">
          <el-image
            v-if="selectedNews.picUrl"
            :src="selectedNews.picUrl"
            class="article-image"
            fit="cover"
          />

          <div v-if="selectedNews.content" class="article-content">
            <p v-for="(paragraph, index) in formatContent(selectedNews.content)" :key="index">
              {{ paragraph }}
            </p>
          </div>
          <div v-else class="loading-content">
            <el-skeleton :rows="10" animated />
          </div>
        </div>

        <!-- 相关新闻 -->
        <div v-if="relatedNews.length > 0" class="related-news">
          <h3>相关新闻</h3>
          <div class="related-news-grid">
            <div
              v-for="news in relatedNews"
              :key="news.id"
              class="related-news-item"
              @click="showNewsDetail(news)"
            >
              <el-image
                :src="news.picUrl || defaultImage"
                class="related-news-image"
                fit="cover"
              />
              <div class="related-news-title">{{ news.title }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-loading :fullscreen="true" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { ref, onMounted } from 'vue';
import { Search, Picture } from '@element-plus/icons-vue';
import debounce from 'lodash/debounce';

export default {
  name: 'NewsPage',
  components: {
    Search,
    Picture
  },
  setup() {
    const news = ref([]);
    const selectedNews = ref(null);
    const relatedNews = ref([]);
    const loading = ref(false);
    const searchQuery = ref('');
    const selectedSource = ref('');
    const dateRange = ref('');
    const sources = ref([]);
    const sourceStats = ref([]);
    const defaultImage = 'http://localhost:8080/default-news.jpg';
    const dialogVisible = ref(false);

    //获取用户信息的函数
    const getUserInfo = () => {
      try {
        const userStr = localStorage.getItem('user');
        console.log('从 localStorage 获取的用户信息:', userStr); // 添加调试信息
        if (!userStr) {
          return { username: '未登录用户' };
        }
        const userInfo = JSON.parse(userStr);
        return {
          username: userInfo.username || '未登录用户',
        };
      } catch (e) {
        console.error('解析用户信息失败:', e);
        return { username: '未登录用户' };
      }
    };
    const userInfo = getUserInfo();
    const username=userInfo.username;

    // 获取新闻列表
    const fetchNews = async () => {
      try {
        loading.value = true;
        const params = {
          query: searchQuery.value,
          source: selectedSource.value,
          date_range: dateRange.value,
          username:username
        };

        const response = await axios.get('http://localhost:5000/news/get_news', { params});
        news.value = response.data.news;
        sources.value = response.data.sources;
      } catch (error) {
        console.error('获取新闻失败:', error);
        ElMessage.error('获取新闻列表失败');
      } finally {
        loading.value = false;
      }
    };
    const readingTime = ref(0); // 用于记录阅读时间
    let readingInterval = null; // 用于存储定时器
    // 获取新闻详情
    const showNewsDetail = async (newsItem) => {
      console.log('Selected news item:', newsItem);
      try {
        loading.value = true;
        selectedNews.value = newsItem; // 设置选中的新闻
        dialogVisible.value = true;

    // 记录阅读历史
        const readHistoryData = {
        news_id: newsItem.id,
        read_time: 0,
        is_finished: false,
        is_favorite: false
      };
    // 发送初始阅读记录
        await axios.post(`http://localhost:5000/readhistory/read_history/${newsItem.id}`, {readHistoryData,username:username});

    // 开始计时
        readingInterval = setInterval(() => {
        readingTime.value += 1;
      }, 1000);

    // 获取新闻详情
        const response = await axios.get(`http://localhost:5000/news/news/${newsItem.id}`);
        selectedNews.value = response.data.news;
        relatedNews.value = response.data.related_news;
      } catch (error) {
        console.error('获取新闻详情失败:', error);
        ElMessage.error('获取新闻详情失败');
      } finally {
      loading.value = false;
    }
    };
    // 关闭弹窗时更新阅读历史
    const closeDialog = async () => {
      dialogVisible.value = false;
      if (readingInterval) {
        clearInterval(readingInterval); // 清除定时器
      }

  // 记录阅读历史
      console.log(selectedNews.value.id);
      await axios.post(`http://localhost:5000/readhistory/read_history/${selectedNews.value.id}`, {
      read_time: readingTime.value, // 记录阅读时长
      is_finished: true, // 假设用户已读完
      username: username
    });
  };
    //收藏
    const toggleFavorite = async () => {
      try {
    // 确保 newFavoriteStatus 有一个有效的初始值
        const newFavoriteStatus = selectedNews.value.is_favorite=== true ? false : true ; // 如果是 null，默认设置为 false
         console.log('Updating favorite status for news ID:', selectedNews.value.id);
         console.log('New favorite status:', newFavoriteStatus);
    // 更新新闻表中的 is_favorite
        await axios.put(`http://localhost:5000/news/update_favorite/${selectedNews.value.id}`, {
          is_favorite: newFavoriteStatus,
          username: username
        });

    // 更新本地状态
        selectedNews.value.is_favorite = newFavoriteStatus;
        ElMessage.success(newFavoriteStatus ? '已添加到收藏' : '已取消收藏');
      } catch (error) {
        console.error('更新收藏状态失败:', error);
        ElMessage.error('更新收藏状态失败');
      }
    };
    // 搜索防抖
    const debounceSearch = debounce(() => {
      fetchNews();
    }, 300);

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '';
      const date = new Date(time);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    // 格式化内容
    const formatContent = (content) => {
      if (!content) return [];
      return content.split('\\n').filter(p => p.trim());
    };

    // 格式化检测分数
    const formatScore = (score) => {
      if (score === undefined || score === null) return '未检测';
      return `${((1 - score) * 100).toFixed(1)}%`;
    };

    // 获取标签类型
    const getFakeNewsTagType = (score) => {
      if (score === undefined || score === null) return 'info';
      if (score > 0.7) return 'danger';
      if (score > 0.4) return 'warning';
      return 'success';
    };

    // 格式化检测详情
    const formatDetectionDetails = (details) => {
      try {
        const parsed = JSON.parse(details.replace(/'/g, '"'));
        return JSON.stringify(parsed, null, 2);
      } catch (e) {
        return details;
      }
    };

    onMounted(() => {
      fetchNews();
    });

    return {
      news,
      selectedNews,
      relatedNews,
      loading,
      searchQuery,
      selectedSource,
      dateRange,
      sources,
      sourceStats,
      defaultImage,
      dialogVisible,
      fetchNews,
      showNewsDetail,
      debounceSearch,
      formatTime,
      formatContent,
      formatScore,
      getFakeNewsTagType,
      formatDetectionDetails,
      closeDialog,
      toggleFavorite,
    };
  }
};
</script>

<style scoped>
.news-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.search-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
}

/* 新闻来源统计样式 */
.source-stats {
  margin-bottom: 32px;
}

.source-stats h3 {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.news-grid-item {
  aspect-ratio: 1;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.news-grid-item:hover {
  transform: translateY(-4px);
}

.news-card {
  height: 100%;
  background: var(--el-bg-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light);
  display: flex;
  flex-direction: column;
}

.news-image {
  width: 100%;
  height: 50%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
  font-size: 32px;
}

.news-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.news-title {
  margin: 0 0 12px;
  font-size: 16px;
  line-height: 1.4;
  color: var(--el-text-color-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.news-time {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.news-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 弹窗样式 */
.news-dialog :deep(.el-dialog__header) {
  padding: 20px;
  margin-right: 0;
  border-bottom: 1px solid var(--el-border-color-light);
}

.news-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.article-meta {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.source-link {
  margin-left: auto;
  text-decoration: none;
}

.article-main {
  margin-bottom: 24px;
}

.article-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  margin-bottom: 24px;
  border-radius: 8px;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
}

.article-content p {
  margin-bottom: 1em;
}

.related-news {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-light);
}

.related-news h3 {
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

.related-news-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.related-news-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.related-news-item:hover {
  transform: translateY(-2px);
}

.related-news-image {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 4px;
  margin-bottom: 8px;
}

.related-news-title {
  font-size: 14px;
  line-height: 1.4;
  color: var(--el-text-color-regular);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 动画效果 */
.news-fade-enter-active,
.news-fade-leave-active {
  transition: all 0.3s ease;
}

.news-fade-enter-from,
.news-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 1024px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .related-news-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
  }

  .news-grid {
    grid-template-columns: 1fr;
  }

  .related-news-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .news-dialog {
    width: 95% !important;
  }
}

.fake-news-tag {
  margin-left: auto;
}

.detection-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  margin-right: 16px;
}

.detection-tooltip {
  max-width: 300px;
  font-size: 14px;
}

.detection-tooltip pre {
  margin-top: 8px;
  white-space: pre-wrap;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.1);
  padding: 8px;
  border-radius: 4px;
}
</style>
