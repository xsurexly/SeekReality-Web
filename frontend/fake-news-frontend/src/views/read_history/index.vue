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
            <el-option label="社会" value="society" />
            <el-option label="科技" value="tech" />
            <el-option label="财经" value="finance" />
            <el-option label="体育" value="sports" />
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
                <span class="read-time">阅读时长：{{ scope.row.readTime }}分钟</span>
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
              {{ scope.row.isFinished ? '已读完' : '未读完' }}
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
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
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
    const totalReads = ref(328)
    const todayReads = ref(12)
    const favoriteCount = ref(45)

    // 模拟数据
    const records = ref([
      {
        id: 1,
        date: '2024-03-20 10:30:00',
        title: '人工智能新突破：大模型在医疗领域取得重要进展',
        content: '近日，某研究团队开发的医疗大模型在诊断准确率方面取得显著突破，准确率达到95%以上...',
        category: '科技',
        source: '科技日报',
        readTime: 5,
        isFinished: true,
        isFavorite: false
      },
      // ... 更多记录
    ])

    // 过滤记录
    const filteredRecords = computed(() => {
      return records.value.filter(record => {
        const matchKeyword = !searchKeyword.value ||
          record.title.includes(searchKeyword.value) ||
          record.content.includes(searchKeyword.value)
        const matchCategory = !categoryFilter.value ||
          record.category === categoryFilter.value
        return matchKeyword && matchCategory
      })
    })

    // 方法
    const refreshData = () => {
      ElMessage.success('数据已刷新')
    }

    const continueReading = (record) => {
      ElMessage.info(`继续阅读：${record.title}`)
    }

    const toggleFavorite = (record) => {
      record.isFavorite = !record.isFavorite
      ElMessage.success(record.isFavorite ? '已添加到收藏' : '已取消收藏')
    }

    const deleteRecord = (record) => {
      ElMessage.success(`删除记录：${record.title}`)
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

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
