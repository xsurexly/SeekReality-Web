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
        <div ref="timeChartRef" class="chart-container" style="width: 100%; height: 300px"></div>
      </el-card>

      <!-- 阅读量趋势 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><Histogram /></el-icon>
            <span>每日阅读量趋势</span>
          </div>
        </template>
        <div ref="volumeChartRef" class="chart-container" style="width: 100%; height: 300px"></div>
      </el-card>

      <!-- 检测结果统计 -->
      <el-card class="card-item">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>虚假新闻检测统计</span>
          </div>
        </template>
        <div ref="detectChartRef" class="chart-container" style="width: 100%; height: 300px"></div>
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
  PieChart
} from '@element-plus/icons-vue'
import OverView from './Overview/OverView.vue'

export default {
  name: 'Visualization',
  components: {
    Timer,
    Histogram,
    PieChart,
    OverView
  },
  setup() {
    // 响应式数据
    const currentTime = ref(new Date().toLocaleString())

    // 图表引用
    const timeChartRef = ref(null);
    const volumeChartRef = ref(null);
    const detectChartRef = ref(null);

    let timeChart =null;
    let volumeChart =null;
    let detectChart =null;

    // 获取用户数据
    const fetchUserData = async () => {
      const username = localStorage.getItem('username');
      const userid = localStorage.getItem('userid');
      console.log('Username:',username)
      console.log('UserID:', userid)

      // 检查参数完整性
      if (!username || !userid) {
        console.error('缺少用户标识参数');
        return;
      }

      try {
        const response = await fetch(`/apis/visualization/get-user-data?userid=${userid}&username=${username}`, {
          method: 'GET'
        });
        const text = await response.text();  // 先打印原始内容
        console.log('服务器返回内容:', text);
        const data = JSON.parse(text);
        console.log('返回的数据:', data);

        if (data.success) {
          console.log('Received data:', data.data);

          // 等待 DOM 渲染完成
          nextTick(() => {
            console.log("检查 ref:", timeChartRef.value, volumeChartRef.value, detectChartRef.value);

            if (!timeChartRef.value || !volumeChartRef.value || !detectChartRef.value) {
              console.error('图表容器未找到，尝试延迟初始化');
              setTimeout(() => initCharts(data.data), 500); // 再等 500ms
              return;
            }
            initCharts(data.data);
          });
        } else {
          console.error('获取数据失败:', data.message);
        }
      } catch (error) {
        console.error('请求失败:', error);
      }
    };

    // 图表初始化
    const initCharts = (data) => {
      console.log('Chart Data:', data);
      nextTick(() => {
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
          tooltip: {},
          xAxis: {
            type: 'category',
            data: Object.keys(data.readingTimeDistribution)
          },
          yAxis: { type: 'value' },
          series: [{
            data: Object.values(data.readingTimeDistribution),
            type: 'bar',
            color: '#409EFF'
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
            color: ['rgb(148.6, 212.3, 117.1)', 'rgb(248, 152.1, 152.1)']
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
      setTimeout(() => {
        fetchUserData();
      }, 500);
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      timeChart?.dispose()
      volumeChart?.dispose()
      detectChart?.dispose()
    })

    return {
      currentTime,
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
  background: var(--navbar-bg);
  color: var(--font-color);
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
  color: var(--font-color);
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
