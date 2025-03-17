<template>
  <div class="visual-container">
    <!-- 标题区 -->
    <h3 class="main-title">数据可视化</h3>
    <h5 class="sub-title">数据可视化展示了用户最近阅读新闻情况和上传检测新闻的情况</h5>
    <p class="update-time">数据更新时间：{{ currentTime }}</p>

    <!-- 数据概览 -->
    <el-card class="data-view">
        <template #header>
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span>实时数据概览</span>
          </div>
        </template>
        <div class="stats-container">
          <div class="stat-item">
            <label>今日检测次数</label>
            <el-statistic :value="stats.todayChecks" />
          </div>
          <div class="stat-item">
            <label>今日阅读量</label>
            <el-statistic :value="stats.todayReads" />
          </div>
          <div class="stat-item">
            <label>今日阅读时长</label>
            <el-statistic :value="stats.todayTime" suffix="分钟" />
          </div>
          <div class="stat-item">
            <label>高风险内容</label>
            <el-statistic :value="stats.riskCount" />
          </div>
        </div>
      </el-card>

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
            <span>每日阅读量趋势</span>
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
      todayChecks: 0,
      todayReads: 0,
      todayTime: 0,
      riskCount: 0
    })

    // 图表引用
    const timeChartRef = ref(null)
    const volumeChartRef = ref(null)
    const detectChartRef = ref(null)

    let timeChart = null
    let volumeChart = null
    let detectChart = null

    // 获取用户数据
    const fetchUserData = async () => {
      const username = localStorage.getItem('username');
      const user_id = localStorage.getItem('userid');
      console.log('Username:',username)
      console.log('UserID:', user_id)

      // 检查参数完整性
      if (!username || !user_id) {
        console.error('缺少用户标识参数');
        return;
      }

      try {
        const response = await fetch('/visualization/get-user-data?user_id=${user_id}&username=${username}', {
          method: 'GET'
        });
        const text = await response.text();  // 先打印原始内容
        console.log('服务器返回内容:', text);

        const data = JSON.parse(text);  // 手动解析 JSON
        console.log('返回的数据:', data);

        if (data.success) {
          console.log('Received data:', data.data);
          initCharts(data.data);
          updateStats(data.data);
        } else {
          console.error('获取数据失败:', data.message);
        }
      } catch (error) {
        console.error('请求失败:', error);
      }
    }

    // 更新统计数据
    const updateStats = (data) => {
      stats.value.todayChecks = data.todayChecks || 0;
      stats.value.todayReads = data.todayReads || 0;
      stats.value.todayTime = data.todayTime || 0;
      stats.value.riskCount = data.riskCount || 0;
    }

    // 图表初始化
    const initCharts = (data) => {
      console.log('Chart Data:', data); 
      nextTick(() => {
        if (!timeChartRef.value || !volumeChartRef.value || !detectChartRef.value) {
          console.error('图表容器未找到');
          return;
        }
        // 销毁旧实例（防止内存泄漏）
        if (timeChart) timeChart.dispose();
        if (volumeChart) volumeChart.dispose();
        if (detectChart) detectChart.dispose();

        // 初始化新实例
        timeChart = echarts.init(timeChartRef.value);
        volumeChart = echarts.init(volumeChartRef.value);
        detectChart = echarts.init(detectChartRef.value);

        // 阅读时长分布（柱状图）
        timeChart.setOption({
          title: { text: '阅读时长分布', left: 'center' },
          tooltip: {},
          xAxis: {
            type: 'category',
            data: Object.keys(data.readingTimeDistribution)
          },
          yAxis: { type: 'value' },
          series: [{
            data: Object.values(data.readingTimeDistribution),
            type: 'bar',
            itemStyle: { color: '#409EFF' }
          }]
        });

        // 每日阅读量趋势（折线图）
        volumeChart.setOption({
          xAxis: {
            type: 'category',
            data: data.volumeTrendDates
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            data: data.volumeTrendValues,
            type: 'line'
          }]
        });

        // 检测结果（饼图）
        detectChart.setOption({
          series: [{
            type: 'pie',
            data: Object.entries(data.detectionResults).map(([name, value]) => ({ name, value })),
            radius: '65%',
            label: {
              formatter: '{b}: {d}%'
            },
            color: ['#42b983', '#ff5252']
          }]
        });

        // 窗口resize监听
        window.addEventListener('resize', handleResize)
      })
    }

    // 处理窗口大小变化
    const handleResize = () => {
      timeChart?.resize()
      volumeChart?.resize()
      detectChart?.resize()
    }

    // 生命周期
    onMounted(() => {
      fetchUserData();
      setInterval(() => {
        currentTime.value = new Date().toLocaleString()
      }, 1000)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      timeChart?.dispose()
      volumeChart?.dispose()
      detectChart?.dispose()
    })

    return {
      currentTime,
      stats,
      timeChartRef,
      volumeChartRef,
      detectChartRef
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

.data-view{
  font-size: 14px;
  margin-bottom: 20px;
  border-radius: 10px;
}

.data-view:hover {
  transform: translateY(-5px);
}

.data-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  min-height: 400px;
  border-radius: 10px;
}

.card-item {
  height: 400px;
  transition: transform 0.3s;
  background: var(--navbar-bg);
  color: var(--font-color);
  border: 0px solid #b5b5b5;
  border-radius: 10px;
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
  width: 100%;
  margin-top: 10px;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 10px;
}

.stat-item {
  background: var(--navbar-bg);
  color: var(--font-color);
  border: 1px solid #b5b5b5;
  padding: 10px;
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
