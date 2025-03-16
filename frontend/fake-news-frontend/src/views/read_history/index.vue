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
    <el-card class="search-card" v-if="isDataLoaded">
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
    <el-card class="search-card" v-else>
      <div class="loading-placeholder">
        <el-skeleton :rows="3" animated />
      </div>
    </el-card>
    <!-- 阅读记录列表 -->
    <el-card class="records-card">
      <el-table
        v-if="isDataLoaded"
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
              :type="scope.row.is_finished ? 'success' : 'info'"
              effect="light"
            >
              {{ scope.row.is_finished ? '已读完' : '未读完' }}
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
      <div v-else class="loading-placeholder">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-if="isDataLoaded && Number(total) > 0"
          :current-page="Number(currentPage)"
          :page-size="Number(pageSize)"
          :total="Number(total)"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
        <div v-else-if="isDataLoaded" class="no-records">
          暂无记录
        </div>
        <div v-else class="loading-text">
          加载中...
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue'
import {  useRouter } from 'vue-router';

export default {
  name: 'ReadHistory',
  components: {
    Search
  },
  setup() {
    const router = useRouter();

    // 基础数据
    const searchKeyword = ref('')
    const categoryFilter = ref('')
    const dateRange = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const isDataLoaded = ref(false) // 控制组件渲染的状态变量
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
        console.log('开始获取阅读历史记录...');
        const response = await axios.get(`http://localhost:5000/readhistory/user/${username}`);
        console.log('API 响应:', response);

        if (response.data && Array.isArray(response.data)) {
          // 处理记录，确保日期格式一致
          records.value = response.data.map(record => {
            // 确保日期字段存在
            if (!record.date) {
              const now = new Date();
              record.date = now.toUTCString();
            }

            // 统一使用 UTC 时间，保持与数据库时区一致
            const dbDate = new Date(record.date);
            const dateStr = dbDate.toUTCString();

            console.log('日期转换:', {
              原始日期: record.date,
              UTC日期: dateStr,
              数据库时间戳: dbDate.getTime()
            });

            return {
              ...record,
              date: dateStr
            };
          });

          total.value = Number(records.value.length);
          console.log('处理后的记录:', records.value);
        } else {
          console.error('API 返回的数据不是数组:', response.data);
          records.value = [];
          total.value = 0;
        }

        // 更新统计数据
        await Promise.all([
          fetchFavoriteCount(),
          fetchReadingStats()
        ]);

        // 标记数据已加载
        isDataLoaded.value = true;
      } catch (error) {
        console.error('获取阅读历史失败:', error);
        ElMessage.error('获取阅读历史失败');
        isDataLoaded.value = true;
        records.value = [];
        total.value = 0;
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
    //获取收藏量方法
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
      // 如果记录为空，直接返回空数组
      if (!records.value || records.value.length === 0) {
        return [];
      }

      // 先根据筛选条件过滤记录
      const filtered = records.value.filter(record => {
        if (!record) return false;

        // 关键字筛选
        const matchKeyword = !searchKeyword.value ||
          (record.title && record.title.includes(searchKeyword.value)) ||
          (record.content && record.content.includes(searchKeyword.value));

        // 分类筛选
        const matchCategory = !categoryFilter.value ||
          (record.category && record.category === categoryFilter.value);

        // 日期筛选
        let matchDate = true;
        if (dateRange.value && Array.isArray(dateRange.value) && dateRange.value.length === 2) {
          try {
            // 将记录日期转换为 UTC 时间
            const recordDate = new Date(record.date);
            const recordYear = recordDate.getUTCFullYear();
            const recordMonth = recordDate.getUTCMonth() + 1;
            const recordDay = recordDate.getUTCDate();

            // 将筛选范围转换为 UTC 时间
            const startDate = dateRange.value[0];
            const startYear = startDate.getFullYear();
            const startMonth = startDate.getMonth() + 1;
            const startDay = startDate.getDate();

            const endDate = dateRange.value[1];
            const endYear = endDate.getFullYear();
            const endMonth = endDate.getMonth() + 1;
            const endDay = endDate.getDate();

            // 转换为数字进行比较（YYYYMMDD）
            const recordNum = recordYear * 10000 + recordMonth * 100 + recordDay;
            const startNum = startYear * 10000 + startMonth * 100 + startDay;
            const endNum = endYear * 10000 + endMonth * 100 + endDay;

            matchDate = recordNum >= startNum && recordNum <= endNum;

            console.log('日期比较:', {
              原始日期: record.date,
              UTC年月日: `${recordYear}-${String(recordMonth).padStart(2, '0')}-${String(recordDay).padStart(2, '0')}`,
              记录数值: recordNum,
              开始日期: `${startYear}-${String(startMonth).padStart(2, '0')}-${String(startDay).padStart(2, '0')}`,
              开始数值: startNum,
              结束日期: `${endYear}-${String(endMonth).padStart(2, '0')}-${String(endDay).padStart(2, '0')}`,
              结束数值: endNum,
              是否匹配: matchDate
            });
          } catch (error) {
            console.error('日期比较出错:', error);
            matchDate = true; // 出错时默认显示
          }
        }

        return matchKeyword && matchCategory && matchDate;
      });

      // 分页处理
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;

      // 格式化显示日期，使用 UTC 时间
      return filtered.slice(start, end).map(record => {
        const date = new Date(record.date);
        return {
          ...record,
          date: `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')} ${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}:${String(date.getUTCSeconds()).padStart(2, '0')}`
        };
      });
    });

    // 计算过滤后的总记录数
    const filteredTotal = computed(() => {
      // 如果记录为空，直接返回0
      if (!records.value || records.value.length === 0) {
        return 0;
      }

      const count = records.value.filter(record => {
        if (!record) return false;

        // 关键字筛选
        const matchKeyword = !searchKeyword.value ||
          (record.title && record.title.includes(searchKeyword.value)) ||
          (record.content && record.content.includes(searchKeyword.value));

        // 分类筛选
        const matchCategory = !categoryFilter.value ||
          (record.category && record.category === categoryFilter.value);

        // 日期筛选
        let matchDate = true;
        if (dateRange.value && Array.isArray(dateRange.value) && dateRange.value.length === 2) {
          try {
            // 将记录日期转换为 UTC 时间
            const recordDate = new Date(record.date);
            const recordYear = recordDate.getUTCFullYear();
            const recordMonth = recordDate.getUTCMonth() + 1;
            const recordDay = recordDate.getUTCDate();

            // 将筛选范围转换为 UTC 时间
            const startDate = dateRange.value[0];
            const startYear = startDate.getFullYear();
            const startMonth = startDate.getMonth() + 1;
            const startDay = startDate.getDate();

            const endDate = dateRange.value[1];
            const endYear = endDate.getFullYear();
            const endMonth = endDate.getMonth() + 1;
            const endDay = endDate.getDate();

            // 转换为数字进行比较（YYYYMMDD）
            const recordNum = recordYear * 10000 + recordMonth * 100 + recordDay;
            const startNum = startYear * 10000 + startMonth * 100 + startDay;
            const endNum = endYear * 10000 + endMonth * 100 + endDay;

            matchDate = recordNum >= startNum && recordNum <= endNum;
          } catch (error) {
            console.error('日期比较出错:', error);
            matchDate = true; // 出错时默认显示
          }
        }

        return matchKeyword && matchCategory && matchDate;
      }).length;

      console.log('过滤后的记录数量:', count);
      return Number(count);
    });

    // 监听过滤条件变化，更新总记录数
    watch([filteredTotal], (newVal) => {
      console.log('过滤后的总记录数变化:', newVal);
      total.value = Number(newVal);
    });

    // 监听日期范围变化
    watch(dateRange, (newVal) => {
      console.log('日期范围变化:', newVal);
      // 不需要重新获取数据，只需要重新过滤
      // 重置当前页为第一页
      currentPage.value = 1;
    });

    // 监听搜索关键字和分类过滤器变化
    watch([searchKeyword, categoryFilter], () => {
      console.log('搜索条件变化');
      // 重置当前页为第一页
      currentPage.value = 1;
    });

    // 方法
    const refreshData = async () => {
      try {
        ElMessage.info('正在刷新数据...'); // Provide feedback to the user
        // 先将数据加载状态设为 false
        isDataLoaded.value = false;
        // 重置筛选条件
        searchKeyword.value = '';
        categoryFilter.value = '';
        dateRange.value = [];
        currentPage.value = 1;
        // 获取数据
        await fetchReadHistory();
        ElMessage.success('数据已刷新'); // Confirm the refresh
      } catch (error) {
        console.error('刷新数据失败:', error);
        ElMessage.error('刷新数据失败');
        // 即使出错，也标记为已加载，以便显示错误状态
        isDataLoaded.value = true;
      }
    }
    //继续阅读
    const continueReading = (record) => {
      // 跳转到新闻页面并显示指定新闻
      router.push({
        path: '/newspage',
        query: {
          newsId: record.news_id,
          autoOpen: 'true'
        }
      });
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
    onMounted(async () => {
      try {
        console.log('组件开始挂载...');

        // 从 localStorage 获取日期参数
        const targetDate = localStorage.getItem('targetReadDate');
        const count = localStorage.getItem('targetReadCount');

        if (targetDate) {
          console.log('检测到日期参数:', targetDate);

          // 解析目标日期字符串（格式：YYYY-MM-DD）
          const [year, month, day] = targetDate.split('-').map(Number);

          // 使用本地时间创建日期对象
          const startOfDay = new Date(year, month - 1, day);
          startOfDay.setHours(0, 0, 0, 0);

          const endOfDay = new Date(year, month - 1, day);
          endOfDay.setHours(23, 59, 59, 999);

          dateRange.value = [startOfDay, endOfDay];

          const formattedStartDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          console.log('设置的日期范围:', {
            开始日期: formattedStartDate,
            结束日期: formattedStartDate,
            开始时间对象: startOfDay,
            结束时间对象: endOfDay
          });

          // 如果有阅读数量参数，显示提示信息
          if (count) {
            ElMessage.info(`显示 ${formattedStartDate} 的 ${count} 条阅读记录`);
          }

          // 清除 localStorage 中的参数，避免影响下次访问
          localStorage.removeItem('targetReadDate');
          localStorage.removeItem('targetReadCount');
        }

        // 获取阅读历史记录
        await fetchReadHistory();

        console.log('组件挂载完成，总记录数:', total.value);
      } catch (error) {
        console.error('组件挂载时出错:', error);
        ElMessage.error('加载数据失败，请刷新页面重试');
        isDataLoaded.value = true;
      }
    });

    // 添加一个调试函数，用于检查日期格式
    const debugDateFormat = (date) => {
      if (!date) return 'null';
      return {
        original: date,
        jsDate: new Date(date),
        iso: new Date(date).toISOString(),
        localeString: new Date(date).toLocaleString()
      };
    };

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
      filteredTotal,
      refreshData,
      continueReading,
      toggleFavorite,
      deleteRecord,
      handleSizeChange,
      handleCurrentChange,
      Search,
      Refresh,
      debugDateFormat,
      isDataLoaded
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
  background:var(--navbar-bg);
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.header-content {
  color: var(--font-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  font-size: 28px;
  color: var(--font-color);
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
  background:var(--bg-color);
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
  background:var(--bg-color);
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
  background:var(--bg-color);
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
  width: 100%;
}

.no-records {
  color: #909399;
  font-size: 14px;
  text-align: center;
  width: 100%;
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

.loading-placeholder {
  padding: 20px;
  width: 100%;
}

.loading-text {
  color: #909399;
  font-size: 14px;
  text-align: center;
  width: 100%;
  padding: 20px 0;
}
</style>
