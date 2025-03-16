<template>
  <div class="news-container">
    <!-- 搜索和筛选区域 -->
    <el-card class="search-card" >
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索新闻标题或内容"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="categoryFilter"
            placeholder="新闻分类"
            class="filter-select"
            clearable
            @change="handleFilterChange"
          >
            <el-option label="全部" value="" />
            <el-option label="社会" value="社会" />
            <el-option label="科技" value="科技" />
            <el-option label="财经" value="财经" />
            <el-option label="体育" value="体育" />
            <el-option label="娱乐" value="娱乐" />
            <el-option label="其它" value="其它" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            class="date-picker"
            clearable
            @change="handleDateChange"
          />
        </el-col>
        <el-col :span="2">
          <el-button type="primary" :icon="Refresh" circle @click="refreshData" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 新闻网格 -->
    <div class="news-grid">
      <el-empty v-if="paginatedNews.length === 0" description="暂无新闻" />

      <transition-group name="news-fade">
        <div
          v-for="item in paginatedNews"
          :key="item.id"
          class="news-grid-item"
          @click="item ? showNewsDetail(item) : null"
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
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
      v-if="!loading && paginatedNews.length > 0"
      :current-page="currentPage"
      :page-size="itemsPerPage"
      :total="filteredNews.length"
      :page-sizes="[12, 15, 24, 30]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      background
  />
  </div>

    <!-- 新闻详情弹窗 -->
    <div class="dialog-wrapper">
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
    </div>
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <el-loading :fullscreen="true" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { ref, onMounted, watch, computed } from 'vue';
import { Search, Picture,Refresh } from '@element-plus/icons-vue';
import debounce from 'lodash/debounce';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'NewsPage',
  components: {
    Search,
    Picture,
  },
  props: {
    newsId: {
      type: String,
      default: ''
    },
    autoOpen: {
      type: String,
      default: 'false'
    }
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const news = ref([]);
    const selectedNews = ref(null);
    const relatedNews = ref([]);
    const loading = ref(false);
    const searchQuery = ref('');
    const selectedSource = ref('');
    const sources = ref([]);
    const sourceStats = ref([]);
    const defaultImage = 'http://localhost:8080/default-news.jpg';
    const dialogVisible = ref(false);
    const readingTime = ref(0);
    let readingInterval = null;
    const currentPage = ref(1);
    const itemsPerPage = 12; // 每页显示的新闻数量
    const total = ref(0); // 总新闻数量
    const searchInput = ref(''); // 新增中间搜索变量
    const searchKeyword = ref('')
    const categoryFilter = ref('')
    const dateRange = ref([])

    //获取用户信息的函数
    const getUserInfo = () => {
      try {
        const userStr = localStorage.getItem('user');
        console.log('从 localStorage 获取的用户信息:', userStr);
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
        const response = await axios.get('http://localhost:5000/news/get_news', {
          params: { username: username }
        });
        news.value = response.data.news;
        sources.value = response.data.sources;

        // 如果有 newsId 参数，查找并显示对应的新闻
        const targetNewsId = props.newsId || route.query.newsId;
        if (targetNewsId) {
          const targetNews = news.value.find(item => item.id === targetNewsId);
          if (targetNews) {
            await showNewsDetail(targetNews);
          } else {
            // 如果在当前列表中找不到，直接从服务器获取
            await showNewsDetail(null);
          }
        }
      } catch (error) {
        console.error('获取新闻失败:', error);
        ElMessage.error('获取新闻列表失败');
      } finally {
        loading.value = false;
      }
    };

    // 获取新闻详情
    const showNewsDetail = async (newsItem) => {
      console.log('Selected news item:', newsItem);
      try {
        loading.value = true;
        let targetNews = newsItem;

        // 如果没有传入 newsItem，但有 newsId，则从服务器获取新闻详情
        if (!newsItem && (props.newsId || route.query.newsId)) {
          const newsId = props.newsId || route.query.newsId;
          const response = await axios.get(`http://localhost:5000/news/news/${newsId}`);
          if (response.data && response.data.news) {
            targetNews = response.data.news;
          } else {
            throw new Error('未找到指定新闻');
          }
        }

        if (!targetNews) {
          throw new Error('新闻信息不存在');
        }

        selectedNews.value = targetNews;
        dialogVisible.value = true;

        // 更新 URL，但不触发新的导航
        router.replace({
          path: '/newspage',
          query: {
            ...route.query,
            newsId: targetNews.id,
            autoOpen: 'true'
          }
        });

        // 记录阅读历史
        const readHistoryData = {
          news_id: targetNews.id,
          read_time: 0,
          is_finished: false,
          is_favorite: false
        };

        // 发送初始阅读记录
        await axios.post(`http://localhost:5000/readhistory/read_history/${targetNews.id}`, {
          readHistoryData,
          username: username
        });

        // 开始计时
        readingInterval = setInterval(() => {
          readingTime.value += 1;
        }, 1000);

        // 获取相关新闻
        const detailResponse = await axios.get(`http://localhost:5000/news/news/${targetNews.id}`);
        if (detailResponse.data.related_news) {
          relatedNews.value = detailResponse.data.related_news;
        }

      } catch (error) {
        console.error('获取新闻详情失败:', error);
        ElMessage.error(error.message || '获取新闻详情失败');
      } finally {
        loading.value = false;
      }
    };

    // 关闭弹窗时更新阅读历史和 URL
    const closeDialog = async () => {
      dialogVisible.value = false;
      if (readingInterval) {
        clearInterval(readingInterval); // 清除定时器
      }

      // 记录阅读历史
      if (selectedNews.value) {
        await axios.post(`http://localhost:5000/readhistory/read_history/${selectedNews.value.id}`, {
          read_time: readingTime.value,
          is_finished: true,
          username: username
        });
      }

      // 移除 URL 中的 newsId 参数，但保持在 newspage 路径
      const query = { ...route.query };
      delete query.newsId;
      delete query.autoOpen;
      router.replace({ path: '/newspage', query });
    };

    // 监听路由参数变化
    watch(
      [() => searchQuery.value, () => selectedSource.value, () => dateRange.value],
      () => {
        currentPage.value = 1;
      },
      { deep: true }
    );

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
      searchQuery.value = searchInput.value;
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

    // 过滤逻辑
    const filteredNews = computed(() => {
  let filtered = news.value;

  // 关键词搜索（标题和内容）
  if (searchKeyword.value) {
    const query = searchKeyword.value.toLowerCase();
    filtered = filtered.filter(item =>
      item.title.toLowerCase().includes(query) ||
      (item.content && item.content.toLowerCase().includes(query))
    );
  }

  // 分类过滤
  if (categoryFilter.value) {
    filtered = filtered.filter(item => item.category === categoryFilter.value);
  }

  // 日期过滤
  if (dateRange.value?.length === 2) {
    const start = new Date(dateRange.value[0]);
    const end = new Date(dateRange.value[1]);
    end.setHours(23, 59, 59, 999);

    filtered = filtered.filter(item => {
      const itemDate = new Date(item.ctime);
      return itemDate >= start && itemDate <= end;
    });
  }

  return filtered;
});

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(filteredNews.value.length / itemsPerPage);
    });

    // 计算当前页的新闻
    const paginatedNews = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      return filteredNews.value.slice(start, start + itemsPerPage);
    });

    // 翻页功能
    const nextPage = () => {
      if (currentPage.value < Math.ceil(filteredNews.value.length / itemsPerPage)) {
        currentPage.value++;
      }
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page;
    };

    // 处理每页显示数量变化
    const handleSizeChange = (size) => {
      itemsPerPage.value = size;
      currentPage.value = 1; // 重置为第一页
    };

    const handleSearch = () => {
      currentPage.value = 1;
    }

    const handleFilterChange = () => {
      currentPage.value = 1;
    }

    const handleDateChange = () => {
      currentPage.value = 1;
    }

    // 修改后的刷新方法
    const refreshData = () => {
      searchKeyword.value = '';
      categoryFilter.value = '';
      dateRange.value = [];
      currentPage.value = 1;
      fetchNews()
    }
    // 监听搜索和来源变化，重置当前页
    watch([searchQuery, selectedSource], () => {
      currentPage.value = 1; // Reset to first page on filter change
    });

    onMounted(async () => {
      await fetchNews();
    });

    return {
      news,
      selectedNews,
      relatedNews,
      loading,
      searchQuery,
      selectedSource,
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
      currentPage,
      totalPages,
      nextPage,
      prevPage,
      handleCurrentChange,
      handleSizeChange,
      paginatedNews,
      total,
      itemsPerPage,
      filteredNews,
      searchKeyword,
      categoryFilter,
      dateRange,
      handleSearch,
      handleFilterChange,
      handleDateChange,
      refreshData,
      Refresh
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
.search-card {
  background: var(--bg-color);
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-input {
  flex: 1;
}


.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* 自适应列宽 */
  grid-template-rows: auto; /* 启用瀑布流布局 */
  gap: 16px; /* 统一间距 */
  margin-bottom: 24px;
}

.news-grid-item {
  cursor: pointer;
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
}

.news-grid-item:hover {
  transform: translateY(-4px);
}

.news-card {
  background: var(--navbar-bg);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light);
  display: flex;
  flex-direction: column;
}

.news-image {
  width: 100%;
  max-height: 200px; /* 统一图片最大高度 */
  object-fit: cover;
}

.news-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.news-title {
  font-size: 16px;
  font-color:var(--font-color);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.news-time {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

/* 弹窗样式 */

.dialog-content {
  background: var(--bg-color);
  color: var(--font-color);
  max-height: 70vh;
  overflow-y: auto;
}

.article-meta {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 元素组件深色模式适配 */
.dialog-wrapper :deep(.el-dialog) {
  background-color: var(--bg-color); /* 修改对话框背景颜色 */
  border-radius: 8px; /* 修改对话框圆角 */
}

.dialog-wrapper :deep(.el-dialog__header) {
  background-color: var(--bg-color); /* 修改标题栏背景颜色 */
}
.dialog-wrapper :deep(.el-dialog__title) {
  color: var(--newstitle-color) ; /* 修改标题文字颜色 */
}
.dialog-wrapper :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white; /* 修改关闭按钮颜色 */
}

/* 滚动条深色模式适配 */
.dialog-content::-webkit-scrollbar {
  width: 6px;
}

.dialog-content::-webkit-scrollbar-track {
  background: var(--bg-color);
}

.dialog-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
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
  color: var(--font-color);
}

.article-content p {
  margin-bottom: 1em;
  color: var(--font-color);
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
  color: var(--font-color);
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

.pagination-controls {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
  width: 100%;
}

</style>
