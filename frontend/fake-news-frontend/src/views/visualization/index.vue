<template>
  <div class="visual-container">
    <!-- 标题区 -->
    <h3 class="main-title">数据可视化</h3>
    <h5 class="sub-title">数据可视化展示了用户最近阅读新闻情况和上传检测新闻的情况</h5>
    <p class="update-time">数据更新时间：{{ currentTime }}</p>


    <!-- 数据卡片容器 -->
    <div class="data-cards">
      <!-- 阅读时长分布 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><Timer /></el-icon>
            <span>新闻阅读时长分布</span>
          </div>
        </template>
        <div ref="timeChart" class="chart-container" style="width: 100%; height: 400px"></div>
      </el-card>

      <!-- 阅读量趋势 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><Histogram /></el-icon>
            <span>周阅读量趋势</span>
          </div>
        </template>
        <div ref="volumeChart" class="chart-container" style="width: 100%; height: 400px"></div>
      </el-card>

      <!-- 检测结果统计 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>虚假新闻检测统计</span>
          </div>
        </template>
        <div ref="detectChart" class="chart-container" style="width: 100%; height: 400px"></div>
      </el-card>

      <!-- 用户互动 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><Histogram /></el-icon>
            <span>用户互动分布</span>
          </div>
        </template>
        <div ref="interactionChart" class="chart-container" style="width: 100%; height: 400px"></div>
      </el-card>

      <!-- 内容类型分布 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>内容类型分布</span>
          </div>
        </template>
        <div ref="contentTypeChart" class="chart-container" style="width: 100%; height: 400px"></div>
      </el-card>

      <!-- 数据概览 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>实时数据概览</span>
          </div>
        </template>
        <div class="stats-container">
          <div class="stat-item">
            <label>今日检测量</label>
            <el-statistic :value="stats.todayChecks" />
          </div>
          <div class="stat-item">
            <label>准确率</label>
            <el-statistic :value="stats.accuracy" suffix="%" />
          </div>
          <div class="stat-item">
            <label>高风险内容</label>
            <el-statistic :value="stats.riskCount" />
          </div>
        </div>
      </el-card>
    </div>
    <!-- 地图 -->
    <OverView />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Timer,
  Histogram,
  PieChart,
  DataAnalysis
} from '@element-plus/icons-vue'
import OverView from './Overview/OverView.vue'

export default {
  name: 'Visualization',
  components: {
    Timer,
    Histogram,
    PieChart,
    DataAnalysis,
    OverView
  },
  setup() {
    // 响应式数据
    const currentTime = ref(new Date().toLocaleString())
    const stats = ref({
      todayChecks: 2456,
      accuracy: 92.4,
      riskCount: 186
    })

    // 图表引用
    const timeChartRef = ref(null)
    const volumeChartRef = ref(null)
    const detectChartRef = ref(null)
    const interactionChartRef = ref(null)
    const contentTypeChartRef = ref(null)

    let timeChart = null
    let volumeChart = null
    let detectChart = null
    let interactionChart = null
    let contentTypeChart = null

    // 图表初始化
    const initCharts = () => {
      nextTick(() => {
        // 阅读时长分布（柱状图）
        if (timeChartRef.value && !timeChart) {
          timeChart = echarts.init(timeChartRef.value)
          timeChart.setOption({
            xAxis: {
              type: 'category',
              data: ['<1min', '1-3min', '3-5min', '5-10min', '>10min']
            },
            yAxis: { type: 'value' },
            series: [{
              data: [120, 200, 150, 80, 70],
              type: 'bar',
              itemStyle: { color: '#409EFF' }
            }]
          })
        }

        // 周阅读趋势（折线图）
        if (volumeChartRef.value && !volumeChart) {
          volumeChart = echarts.init(volumeChartRef.value)
          volumeChart.setOption({
            xAxis: {
              type: 'category',
              data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            yAxis: { type: 'value' },
            series: [{
              data: [820, 932, 901, 934, 1290, 1330, 1320],
              type: 'line',
              smooth: true,
              areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
            }]
          })
        }

        // 检测结果（饼图）
        if (detectChartRef.value && !detectChart) {
          detectChart = echarts.init(detectChartRef.value)
          detectChart.setOption({
            series: [{
              type: 'pie',
              data: [
                { value: 735, name: '真实新闻' },
                { value: 265, name: '疑似虚假' }
              ],
              radius: '65%',
              label: {
                formatter: '{b}: {d}%'
              },
              color: ['#67C23A', '#F56C6C']
            }]
          })
        }

        // 用户互动（柱状图）
        if (interactionChartRef.value && !interactionChart) {
          interactionChart = echarts.init(interactionChartRef.value)
          interactionChart.setOption({
            xAxis: {
              type: 'category',
              data: ['评论', '点赞', '分享', '阅读']
            },
            yAxis: { type: 'value' },
            series: [{
              data: [500, 1200, 800, 3500],
              type: 'bar',
              itemStyle: { color: '#67C23A' }
            }]
          })
        }

        // 内容类型分布（饼图）
        if (contentTypeChartRef.value && !contentTypeChart) {
          contentTypeChart = echarts.init(contentTypeChartRef.value)
          contentTypeChart.setOption({
            series: [{
              type: 'pie',
              data: [
                { value: 400, name: '政治' },
                { value: 300, name: '娱乐' },
                { value: 250, name: '体育' },
                { value: 100, name: '科技' }
              ],
              radius: '65%',
              label: {
                formatter: '{b}: {d}%'
              },
              color: ['#409EFF', '#67C23A', '#F56C6C', '#E6A23C']
            }]
          })
        }

        // 窗口resize监听
        window.addEventListener('resize', handleResize)
      })
    }

    // 处理窗口大小变化
    const handleResize = () => {
      timeChart?.resize()
      volumeChart?.resize()
      detectChart?.resize()
      interactionChart?.resize()
      contentTypeChart?.resize()
    }

    // 生命周期
    onMounted(() => {
      // 添加延迟确保 DOM 完全渲染
      setTimeout(initCharts, 100)

      setInterval(() => {
        currentTime.value = new Date().toLocaleString()
      }, 1000)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      timeChart?.dispose()
      volumeChart?.dispose()
      detectChart?.dispose()
      interactionChart?.dispose()
      contentTypeChart?.dispose()
    })

    return {
      currentTime,
      stats,
      timeChartRef,
      volumeChartRef,
      detectChartRef,
      interactionChartRef,
      contentTypeChartRef
    }
  }
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;
.visual-container {
  min-height: 100vh;
}

.header-section {
  margin-bottom: 30px;
  padding: 20px;
  background: var(--navbar-bg);
  border-radius: 15px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.main-title {
  margin-top: 10px;
  text-align: left;
  margin-bottom: 10px;
  color: var(--font-color);
  font-size: 24px;
}

.sub-title{

  text-align: left;
  margin-bottom: 10px;
  color: var(--font-color);
  font-size: 14px;
  font-weight: 400;
}

.update-time {
  text-align: left;
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.data-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.card-item {
  height: 400px;
  transition: transform 0.3s;
  background: var(--navbar-bg);
  color: var(--font-color);
  border: 0px solid #b5b5b5;
}

.card-item:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.card-header .el-icon {
  margin-right: 8px;
  font-size: 20px;
}

.chart-container {
  height: 320px;
  margin-top: 10px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 15px;
}

.stat-item {
  background: var(--navbar-bg);
  color: var(--font-color);
  border: 1px solid #b5b5b5;
  padding: 20px;
  border-radius: 15px;
  text-align: center;
}

.stat-item label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
}

:deep(.el-statistic__content){
  color: var(--font-color);
}

@media (max-width: 768px) {
  .data-cards {
    grid-template-columns: 1fr;
  }

  .card-item {
    height: auto;
    min-height: 300px;
  }

  .stats-container {
    grid-template-columns: 1fr;
  }
}
</style>
