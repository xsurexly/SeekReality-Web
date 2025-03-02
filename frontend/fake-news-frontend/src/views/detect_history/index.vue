<template>
  <div class="history-container">
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-text">
          <h1>检测记录</h1>
          <p class="subtitle">查看您的新闻真伪检测历史记录，助您追踪每一次真相探索</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-number">{{ totalDetections }}</div>
            <div class="stat-label">总检测次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ trueNewsCount }}</div>
            <div class="stat-label">真实新闻</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ falseNewsCount }}</div>
            <div class="stat-label">虚假新闻</div>
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
            placeholder="搜索新闻内容"
            prefix-icon="Search"
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
            v-model="resultFilter"
            placeholder="检测结果"
            class="filter-select"
            clearable
          >
            <el-option label="全部" value="" />
            <el-option label="真实新闻" value="true" />
            <el-option label="虚假新闻" value="false" />
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

    <!-- 记录列表 -->
    <el-card class="records-card">
      <el-table
        :data="filteredRecords"
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa' }"
        border
      >
        <el-table-column prop="date" label="检测时间" width="180" />
        <el-table-column prop="content" label="新闻内容" show-overflow-tooltip>
          <template #default="scope">
            <div class="news-content">
              <el-tooltip :content="scope.row.content" placement="top">
                <p class="news-text">{{ scope.row.content }}</p>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="检测结果" width="120" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.result ? 'success' : 'danger'"
              effect="dark"
              class="result-tag"
            >
              {{ scope.row.result ? '真实新闻' : '虚假新闻' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="180" align="center">
          <template #default="scope">
            <el-progress
              :percentage="(scope.row.confidence * 100)"
              :color="getConfidenceColor(scope.row.confidence)"
              :format="(percentage) => percentage.toFixed(2) + '%'"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button type="primary" link @click="viewDetail(scope.row)">
              查看详情
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
import { Refresh } from '@element-plus/icons-vue'

export default {
  name: 'DetectHistory',
  setup() {
    const searchKeyword = ref('')
    const resultFilter = ref('')
    const dateRange = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(100)
    const totalDetections = ref(156)
    const trueNewsCount = ref(98)
    const falseNewsCount = ref(58)

    // 模拟数据
    const records = ref([
      {
        id: 1,
        date: '2024-03-20 10:30:00',
        content: '这是一条测试新闻内容，用于演示检测记录界面。这是一条很长的内容，需要显示省略号。',
        result: true,
        confidence: 0.95
      },
      // ... 更多记录
    ])

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }

    const filteredRecords = computed(() => {
      return records.value.filter(record => {
        const matchKeyword = !searchKeyword.value ||
          record.content.includes(searchKeyword.value)
        const matchResult = !resultFilter.value ||
          record.result.toString() === resultFilter.value
        return matchKeyword && matchResult
      })
    })

    const refreshData = () => {
      ElMessage.success('数据已刷新')
    }

    const viewDetail = (record) => {
      ElMessage.info(`查看记录：${record.id}`)
    }

    const deleteRecord = (record) => {
      ElMessage.success(`删除记录：${record.id}`)
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    return {
      searchKeyword,
      resultFilter,
      dateRange,
      currentPage,
      pageSize,
      total,
      totalDetections,
      trueNewsCount,
      falseNewsCount,
      filteredRecords,
      viewDetail,
      deleteRecord,
      handleSizeChange,
      handleCurrentChange,
      getConfidenceColor,
      refreshData,
      Refresh
    }
  }
}
</script>

<style scoped>
.history-container {
  padding: 20px;
  background-color: var(--bg-color);
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
  color: var(--font-color);
  margin-bottom: 8px;
  font-weight: 600;
}

.subtitle {
  color: var(--font-color);
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
  color: var(--font-color);
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

.news-content {
  padding: 8px 0;
}

.news-text {
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-tag {
  padding: 6px 12px;
  font-weight: 500;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

:deep(.el-card__body) {
  padding: 20px;
  background: var(--navbar-bg);
}

:deep(.el-table td.el-table__cell, .el-table th.el-table__cell.is-leaf)
{
  background: var(--navbar-bg);
  color: var(--font-color);
}

:deep(.el-table th.el-table__cell)
{
  background: var(--navbar-bg);
  color: var(--font-color);
}


:deep(.el-table tr)
{
  background: var(--navbar-bg);
  color: var(--font-color);
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

:deep(.el-progress-bar__outer) {
  border-radius: 4px;
}

:deep(.el-input__wrapper),
:deep(.el-select),
:deep(.el-date-editor) {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

:deep(.el-button) {
  font-weight: 500;
}
</style>
