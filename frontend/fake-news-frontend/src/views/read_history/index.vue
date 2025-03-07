<template>
  <div class="history-container">
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-text">
          <h1>阅读历史</h1>
          <p class="subtitle">记录您的新闻阅读足迹，重温精彩内容</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-number">{{ totalReads }}</div>
            <div class="stat-label">总阅读量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ todayReads }}</div>
            <div class="stat-label">今日阅读</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ favoriteCount }}</div>
            <div class="stat-label">收藏数量</div>
          </div>
        </div>
      </div>
    </el-card>
    <!-- 搜索和筛选区域 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索新闻标题或内容"
            clearable
            class="search-input"
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
          />
        </el-col>
        <el-col :span="2">
          <el-button type="primary" :icon="Refresh" circle @click="refreshData" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 阅读记录列表 -->
    <el-card class="records-card">
      <el-table
        :data="filteredRecords"
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa' }"
        border
      >
        <el-table-column prop="date" label="阅读时间" width="180" />
        <el-table-column label="新闻信息" min-width="400">
          <template #default="scope">
            <div class="news-info">
              <h3 class="news-title">{{ scope.row.title }}</h3>
              <p class="news-excerpt">{{ scope.row.content }}</p>
              <div class="news-meta">
                <el-tag size="small" effect="plain">{{ scope.row.category }}</el-tag>
                <span class="source">来源：{{ scope.row.source }}</span>
                <span class="read-time">阅读时长：{{ scope.row.readtime }}秒</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.isFinished ? 'success' : 'info'"
              effect="light"
            >
              {{ scope.row.isFinished ? '未读完' : '已读完' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button type="primary" link @click="continueReading(scope.row)">
              继续阅读
            </el-button>
            <el-button
              type="warning"
              link
              @click="toggleFavorite(scope.row)"
            >
              {{ scope.row.isFavorite ? '取消收藏' : '收藏' }}
            </el-button>
            <el-popconfirm
              title="确定要删除这条记录吗？"
              @confirm="deleteRecord(scope.row)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed,onMounted } from 'vue'
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'ReadHistory',
  setup() {
    // 基础数据
    const searchKeyword = ref('')
    const categoryFilter = ref('')
    const dateRange = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(100)
    // 统计数据
    const totalReads = ref(0)
    const todayReads = ref(0)
    const favoriteCount = ref(0)
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
    // 阅读历史数据
    const records = ref([])
    // 获取用户的阅读历史记录
    const fetchReadHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/readhistory/user/${username}`);
        records.value = response.data;
        total.value = response.data.length; // 设置总记录数
        console.log('获取的阅读历史记录:', response.data);
        // 更新统计数据
        await fetchFavoriteCount();
        await fetchReadingStats();
      } catch (error) {
        console.error('获取阅读历史失败:', error);
        ElMessage.error('获取阅读历史失败');
      }
    };
    //获取统计数据方法
    const fetchReadingStats = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/readhistory/reading_stats/${username}`);
        totalReads.value = response.data.total_reads;
        todayReads.value = response.data.today_reads;
      } catch (error) {
        console.error('获取阅读统计失败:', error);
        ElMessage.error('获取阅读统计失败');
      }
    };
    const fetchFavoriteCount = async () => {
      try {
        const response = await axios.get('http://localhost:5000/news/get_favorite_count',
          {params:{username:username}});
        console.log(username);
        favoriteCount.value = response.data.favorite_count;
      } catch (error) {
        console.error('获取收藏量失败:', error);
        ElMessage.error('获取收藏量失败');
      }
    };
    // 过滤记录
    const filteredRecords = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value; // 计算当前页的起始索引
      const end = start + pageSize.value; // 计算当前页的结束索引
      return records.value.slice(start, end).filter(record => {
        const matchKeyword = !searchKeyword.value ||
          (record.title && record.title.includes(searchKeyword.value)) ||
          (record.content && record.content.includes(searchKeyword.value));
        const matchCategory = !categoryFilter.value ||
          (record.category && record.category === categoryFilter.value);
        return matchKeyword && matchCategory;
      });
    });
    // 方法
    const refreshData = async () => {
      ElMessage.info('正在刷新数据...'); // Provide feedback to the user
      await fetchReadHistory(); // Call fetchReadHistory to refresh data
      ElMessage.success('数据已刷新'); // Confirm the refresh
    }
    //继续阅读，还没有实现
    const continueReading = (record) => {
      ElMessage.info(`继续阅读：${record.title}`)
    }
    // 收藏和取消收藏
    const toggleFavorite = async (record) => {
      record.is_favorite = !record.is_favorite;
      try {
        await axios.put(`http://localhost:5000/readhistory/favorite/${record.news_id}`, {
          is_favorite: record.is_favorite,
          username:username
        });
        ElMessage.success(record.is_favorite ? '已添加到收藏' : '已取消收藏');
        // 更新统计数据
        await fetchFavoriteCount();
        await fetchReadingStats();
      } catch (error) {
        console.error('更新收藏状态失败:', error);
        ElMessage.error('更新收藏状态失败');
      }
    };
    // 删除记录
    const deleteRecord = async (record) => {
      try {
    // 获取要删除的 news_id
        const newsId = record.news_id;
    // 从 records 中移除所有与该 news_id 相关的记录
        records.value = records.value.filter(r => r.news_id !== newsId); // 过滤掉所有与该 news_id 相关的记录
    // 发送删除请求
        await axios.delete(`http://localhost:5000/readhistory/deleterecord/${record.id}`,
          {data:{username:username}});
        console.log(username);
        ElMessage.success('所有相关记录已删除');
    // 更新统计数据
        await fetchReadHistory ();
        await fetchFavoriteCount();
        await fetchReadingStats();
      } catch (error) {
        console.error('删除记录失败:', error);
        ElMessage.error('删除记录失败');
      }
    };

    const handleSizeChange = (val) => {
      pageSize.value = val
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    // 组件加载时获取数据
    onMounted(() => {
      fetchReadHistory();
    });

    return {
      searchKeyword,
      categoryFilter,
      dateRange,
      currentPage,
      pageSize,
      total,
      totalReads,
      todayReads,
      favoriteCount,
      filteredRecords,
      refreshData,
      continueReading,
      toggleFavorite,
      deleteRecord,
      handleSizeChange,
      handleCurrentChange,
      Search,
      Refresh
    }
  }
}
</script>

<style scoped>
.history-container {
  padding: 20px;
  min-height: 100vh;
}

.header-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 600;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-input,
.filter-select,
.date-picker {
  width: 100%;
}

.records-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.news-info {
  padding: 8px 0;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 8px 0;
}

.news-excerpt {
  font-size: 14px;
  color: #606266;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.source, .read-time {
  color: #909399;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  font-weight: 600;
}

:deep(.el-button--link) {
  padding: 4px 8px;
}

:deep(.el-input__wrapper),
:deep(.el-select),
:deep(.el-date-editor) {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:deep(.el-button) {
  font-weight: 500;
}

:deep(.el-tag) {
  border-radius: 4px;
}
</style>
