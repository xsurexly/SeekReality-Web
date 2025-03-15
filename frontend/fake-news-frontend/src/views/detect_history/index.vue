<template>
  <!--统计数据-->
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
      <el-row :gutter="24">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索新闻内容"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="detectionMode"
            placeholder="检测方式"
            class="filter-select"
            clearable
          >
            <el-option label="全部" value="" />
            <el-option label="AI助手" value="analysis" />
            <el-option label="模型检测" value="model" />
          </el-select>
        </el-col>
        <el-col :span="4">
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
        :header-cell-style="{ background: 'var(--bg-color)',color:'var(--font-color)' }"
        border
      >
        <el-table-column prop="created_at" label="检测时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="content" label="新闻内容" min-width="300">
          <template #default="scope">
            <div class="news-content">
              <el-popover
                placement="top-start"
                trigger="hover"
                :width="400"
                popper-class="news-content-popover"
              >
                <template #default>
                  <div class="news-content-full">
                    <p class="news-text-full">{{ scope.row.content }}</p>
                  </div>
                </template>
                <template #reference>
                  <p class="news-text-truncate">{{ scope.row.content }}</p>
                </template>
              </el-popover>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="detection_mode" label="检测方式" width="120" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.detection_mode === 'analysis' ? 'primary' : 'success'"
              effect="light"
            >
              {{ scope.row.detection_mode === 'analysis' ? 'AI助手' : '模型检测' }}
            </el-tag>
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
              :percentage="scope.row.score"
              :color="getConfidenceColor(scope.row.confidence)"
              :format="(percentage) => percentage + '%'"
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
          v-model="currentPage"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="检测详情"
      width="60%"
      class="detail-dialog"
    >
  <div v-if="selectedRecord" class="report-container">
    <!-- 报告头部 -->
    <div class="report-header">
      <h1>新闻真实性分析报告</h1>
      <p>生成时间：{{ new Date().toLocaleString() }}</p>
    </div>
    <!-- 报告主体 -->
    <div class="report-content">
      <!-- 评分区 -->
      <div class="score-section">
        <div class="score-content">
          <span class="score-label">真实性评分：</span>
          <span class="score">{{ selectedRecord.score }}</span>
          <span class="score-unit">分</span>
        </div>
      </div>
      <!-- 详细分析 -->
      <div class="analysis-block">
        <div class="section-title">详细分析</div>
        <div class="analysis-item" v-html="formatDetail(selectedRecord.detailed_analysis)"></div>
      </div>
      <!-- 相关事实依据 -->
      <div class="evidence-block">
        <div class="section-title">相关事实依据</div>
        <div class="analysis-item" v-html="formatDetail(selectedRecord.evidence)"></div>
      </div>
      <!-- 总结 -->
      <div class="summary-block">
        <div class="section-title">总结</div>
        <div class="summary-content" v-html="formatDetail(selectedRecord.summary)"></div>
      </div>
    </div>
    <!-- 报告底部 -->
    <div class="footer">
      <p>由AI助手生成的新闻真实性分析报告</p>
      <el-button type="primary" @click="exportReport">导出报告</el-button>
      <el-button @click="detailDialogVisible = false">关闭</el-button>
    </div>
  </div>
</el-dialog>

  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'DetectHistory',
  setup() {
    const searchKeyword = ref('')
    const detectionMode = ref('')
    const resultFilter = ref('')
    const dateRange = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const records = ref([])
    const detailDialogVisible = ref(false)
    const selectedRecord = ref(null)

    // 统计数据
    const totalDetections = computed(() => records.value.length)
    const trueNewsCount = computed(() =>
      records.value.filter(record => record.result).length
    )
    const falseNewsCount = computed(() =>
      records.value.filter(record => !record.result).length
    )

    // 格式化日期
    const formatDate = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    // 获取置信度颜色
    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }

    // 过滤记录
    const filteredRecords = computed(() => {
      const filtered = records.value.filter(record => {
        const matchKeyword = !searchKeyword.value ||
          record.content.toLowerCase().includes(searchKeyword.value.toLowerCase())
        const matchMode = !detectionMode.value || record.detection_mode === detectionMode.value
        const matchResult = !resultFilter.value ||
          (resultFilter.value === 'true' ? record.result : !record.result)
        const matchDate = !dateRange.value || !dateRange.value.length ||
          (new Date(record.created_at) >= dateRange.value[0] &&
           new Date(record.created_at) <= dateRange.value[1])

        return matchKeyword && matchMode && matchResult && matchDate
      })

      // 进行分页处理
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filtered.slice(start, end)
    })

    // 获取历史记录
    const fetchRecords = async () => {
      try {
        const userInfo = JSON.parse(localStorage.getItem('user'))
        if (!userInfo || !userInfo.username) {
          ElMessage.error('请先登录')
          return
        }

        const response = await axios.get(`http://localhost:5000/history/detection-records`, {
          params: {
            username: userInfo.username,
          }
        })

        if (response.data && response.data.history) {
          records.value = response.data.history
          total.value = records.value.length // 更新总记录数
        }
      } catch (error) {
        console.error('获取历史记录失败:', error)
        ElMessage.error('获取历史记录失败')
      }
    }

    // 刷新数据
    const refreshData = () => {
      fetchRecords()
      ElMessage.success('数据已刷新')
    }

    // 查看详情
    const viewDetail = (record) => {
      selectedRecord.value = record
      detailDialogVisible.value = true
    }

    // 删除记录
    const deleteRecord = async (record) => {
      try {
        const response = await axios.delete(`http://localhost:5000/history/detection-records/${record.id}`)
        if (response.status === 200) {
          ElMessage.success('记录已删除')
          // 从本地数据中移除该记录
          records.value = records.value.filter(r => r.id !== record.id)
          // 更新统计数据
          total.value = records.value.length
        } else {
          ElMessage.error('删除失败：' + response.data.error)
        }
      } catch (error) {
        console.error('删除记录失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }

    // 分页处理
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      fetchRecords(); // 重新获取数据
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      fetchRecords(); // 重新获取数据
    }

    // 格式化详细内容
    const formatDetail = (content) => {
      return content.replace(/\n/g, '<br>'); // 将换行符替换为 <br>
    }

    // 导出报告功能，生成 HTML 文件并触发下载
    const exportReport = () => {
      if (!selectedRecord.value) return
      const reportHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>新闻真实性分析报告</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              line-height: 1.6;
              color: #333;
              max-width: 800px;
              margin: 0 auto;
              padding: 20px;
            }
            .report-header {
              text-align: center;
              margin-bottom: 30px;
              padding: 20px;
              background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
              color: white;
              border-radius: 10px;
            }
            .score-section {
              background: #EFF6FF;
              padding: 20px;
              border-radius: 10px;
              margin-bottom: 20px;
              border: 1px solid #93C5FD;
            }
            .score-content {
              display: flex;
              justify-content: center;
              align-items: center;
            }
            .score-label {
              font-size: 20px;
              margin-right: 10px;
            }
            .score {
              font-size: 32px;
              font-weight: bold;
              color: #2563EB;
            }
            .score-unit {
              font-size: 20px;
              margin-left: 10px;
            }
            .analysis-block, .evidence-block, .summary-block {
              background: white;
              padding: 20px;
              border-radius: 10px;
              margin-bottom: 20px;
              border: 1px solid #E5E7EB;
            }
            .section-title {
              color: #2563EB;
              font-size: 20px;
              margin-bottom: 15px;
            }
            .analysis-item, .summary-content {
              padding: 10px;
              background: #F8FAFC;
              border-radius: 5px;
            }
            .footer {
              text-align: center;
              margin-top: 30px;
              padding-top: 20px;
              border-top: 1px solid #E5E7EB;
              color: #6B7280;
            }
          </style>
        </head>
        <body>
          <div class="report-header">
            <h1>新闻真实性分析报告</h1>
            <p>生成时间：${new Date().toLocaleString()}</p>
          </div>
          <div class="score-section">
            <div class="score-content">
              <span class="score-label">真实性评分：</span>
              <span class="score">${selectedRecord.value.score}</span>
              <span class="score-unit">分</span>
            </div>
          </div>
          <div class="analysis-block">
            <div class="section-title">详细分析</div>
            <div class="analysis-item">${formatDetail(selectedRecord.value.detailed_analysis)}</div>
          </div>
          <div class="evidence-block">
            <div class="section-title">相关事实依据</div>
            <div class="analysis-item">${formatDetail(selectedRecord.value.evidence)}</div>
          </div>
          <div class="summary-block">
            <div class="section-title">总结</div>
            <div class="summary-content">${formatDetail(selectedRecord.value.summary)}</div>
          </div>
          <div class="footer">
            <p>由AI助手生成的新闻真实性分析报告</p>
          </div>
        </body>
        </html>
      `
      const blob = new Blob([reportHTML], { type: 'text/html' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `新闻分析报告_${new Date().toISOString().slice(0,10)}.html`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    onMounted(() => {
      fetchRecords()
    })

    return {
      searchKeyword,
      detectionMode,
      resultFilter,
      dateRange,
      currentPage,
      pageSize,
      total,
      totalDetections,
      trueNewsCount,
      falseNewsCount,
      records,
      filteredRecords,
      detailDialogVisible,
      selectedRecord,
      formatDate,
      getConfidenceColor,
      viewDetail,
      deleteRecord,
      handleSizeChange,
      handleCurrentChange,
      refreshData,
      Refresh,
      Search,
      formatDetail,
      exportReport,
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

.news-text-truncate {
  margin: 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--font-color);
  font-size: 14px;
}

.news-content-full {
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
}

.news-text-full {
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
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


:deep(.el-table th) {
  font-weight: 600;
}

.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: var(--font-color);
}

.score-section {
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  margin-bottom: 10px; /* 增加底部间距 */
}

.scorelabel {
  font-weight: bold; /* 加粗评分标签 */
  font-size: 16px; /* 调整字体大小 */
  margin-right: 8px; /* 增加右侧间距 */
}

.score {
  font-size: 24px; /* 增加评分字体大小 */
  font-weight: bold; /* 加粗评分 */
  color: #2563EB; /* 设置评分颜色 */
}

.detail-prompt {
  font-size: 12px; /* 减小提示词字体大小 */
  color: #666; /* 设置提示词颜色 */
  margin-top: 5px; /* 增加顶部间距 */
}

.analysis-section,
.evidence-section,
.summary-section {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--navbar-bg);
  border-radius: 8px;
}

/* 优化搜索筛选区域布局 */
.search-card :deep(.el-row) {
  margin-bottom: -12px;
}

.search-card :deep(.el-col) {
  margin-bottom: 12px;
}

.search-input,
.filter-select,
.date-picker {
  width: 100%;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-date-editor.el-input__wrapper) {
  width: 100%;
}

/* 确保表格内容对齐 */
.el-table :deep(.cell) {
  white-space: nowrap;
}

:deep(.news-content-popover) {
  background-color: var(--navbar-bg);
  border: 1px solid var(--border-color);
  color: var(--font-color);
  max-width: 80vw;
}

:deep(.el-popover.news-content-popover .el-popper__arrow::before) {
  background: var(--navbar-bg);
  border: 1px solid var(--border-color);
}

/*查看详情的报告样式*/
.report-container {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #000000;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.report-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  border-radius: 10px;
}
.score-section {
  background: #EFF6FF;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid #93C5FD;
}
.score-content {
  display: flex;
  justify-content: center;
  align-items: center;
}
.score-label {
  font-size: 20px;
  margin-right: 10px;
}
.score {
  font-size: 32px;
  font-weight: bold;
  color: #2563EB;
}
.score-unit {
  font-size: 20px;
  margin-left: 10px;
}
.analysis-block,
.evidence-block,
.summary-block {
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid #E5E7EB;
}
.section-title {
  color: #2563EB;
  font-size: 20px;
  margin-bottom: 15px;
}
.analysis-item,
.summary-content {
  padding: 10px;
  background: #F8FAFC;
  border-radius: 5px;
}
.footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #E5E7EB;
  color: #6B7280;
}

</style>
