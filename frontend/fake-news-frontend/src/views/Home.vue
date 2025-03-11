<template>
  <div class="home-container">
    <h1 class="main-title">首页</h1>
    <el-row :gutter="30" style="margin-top: 30px;">
      <el-col :span="15">
        <el-card class="dashboard-item">
          <div class="dashboard-item-content">
            <h2 class="hello-text">你好，{{ user.username }}！</h2>
          </div>
        </el-card>
        <el-card class="dashboard-item" style="margin-top: 20px;">
          <div class="dashboard-item-content">
            <h2>今日推荐</h2>
            <el-carousel :interval="4000" type="card" height="200px">
              <el-carousel-item v-for="item in 6" :key="item">
                <h3 text="2xl" justify="center">{{ item }}</h3>
              </el-carousel-item>
            </el-carousel>
          </div>
        </el-card>

        <el-card class="dashboard-item" style="margin-top: 20px;">
          <div class="dashboard-item-content">
            <h2>阅读记录</h2>
            <el-calendar>
              <template #date-cell="{ data }">
                <div class="calendar-cell">
                  <!-- 显示日期 -->
                  <div class="date">{{ data.day.split('-').slice(-1)[0] }}</div>
                  <!-- 显示阅读量 -->
                  <div class="reading-container">
                    <div v-for="item in readingStats" :key="item.Day">
                      <el-tag
                        class="reading-tag"
                        :class="getReadingTagClass(parseInt(item.content))"
                        effect="light"
                        v-if="(item.Day).indexOf(data.day.split('-').slice(2).join('-'))!=-1"
                        @click="navigateToReadHistory(data.day, item.content)">
                        <el-tooltip
                          content="当日阅读数量 (点击查看详情)"
                          placement="top"
                          :show-after="300">
                          <span>{{ item.content }}</span>
                        </el-tooltip>
                      </el-tag>
                    </div>
                  </div>
                </div>
              </template>
            </el-calendar>
          </div>
        </el-card>
      </el-col>
      <el-col :span="9">
        <el-card class="dashboard-item">
          <div class="dashboard-item-content">
            <h2>常用功能</h2>
            <div class="quick-access-grid">
              <el-card class="quick-access-item" @click="$router.push('/textdetect')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-jilu" /></el-icon>
                <span>新闻检测</span>
              </el-card>
              <el-card class="quick-access-item" @click="$router.push('/detecthistory')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-jiancejilu" /></el-icon>
                <span>检测记录</span>
              </el-card>
              <el-card class="quick-access-item" @click="$router.push('/profile')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-wode"/></el-icon>
                <span>个人主页</span>
              </el-card>
              <el-card class="quick-access-item" @click="$router.push('/newspage')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-pinlei" /></el-icon>
                <span>新闻阅读</span>
              </el-card>
            </div>
          </div>
        </el-card>
        <el-card class="dashboard-item" style="margin-top: 20px;">
          <div class="dashboard-item-content-notification">
            <h2>最近通知</h2>
            <div class="notification-content">
              <el-empty :image-size="120" style="padding: 20px;">
                <el-button type="primary">刷新</el-button>
              </el-empty>
            </div>
          </div>
        </el-card>
        <el-card class="dashboard-item" style="margin-top: 20px;">
          <div class="dashboard-item-content">
            <h2>最近上传</h2>
            <el-table
              :data="recentUploads"
              style="width: 100%"
              :header-cell-style="{ background: '#f5f7fa' }"
              border>
              <el-table-column prop="date" label="检测时间" width="145" />
              <el-table-column prop="content" label="新闻内容" show-overflow-tooltip>
                <template #default="scope">
                  <div class="news-content">
                    <el-tooltip :content="scope.row.content" placement="top">
                      <p class="news-text">{{ scope.row.content }}</p>
                    </el-tooltip>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="result" label="检测结果" width="100" align="center">
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
              <el-table-column prop="confidence" label="置信度" width="120" align="center">
                <template #default="scope">
                  <el-progress
                    :percentage="(scope.row.confidence * 100)"
                    :color="getConfidenceColor(scope.row.confidence)"
                    :format="(percentage) => percentage.toFixed(2) + '%'"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from "axios";
import router from "@/router";

export default {
  setup() {
    const avatar = ref(localStorage.getItem('avatar') || 'avatar.png');

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }

    // 初始化空的阅读统计数据
    const readingStats = ref([]);

    // 获取用户信息
    const getUserInfo = () => {
      try {
        const userStr = localStorage.getItem('user');
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
    const username = userInfo.username;

    // 从后端获取阅读统计数据
    const fetchReadingStats = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/readhistory/reading_stats/${username}`);
        console.log('获取的阅读统计数据:', response.data);

        // 将后端返回的数据转换为日历组件所需的格式
        if (response.data && response.data.daily_reads) {
          const dailyReadsData = [];

          // 遍历 daily_reads 对象，将其转换为数组格式
          for (const [date, count] of Object.entries(response.data.daily_reads)) {
            // 从日期中提取日部分 (DD)
            const day = date.split('-')[2];

            dailyReadsData.push({
              Day: day,
              content: count.toString()
            });
          }

          readingStats.value = dailyReadsData;
        }
      } catch (error) {
        console.error('获取阅读统计失败:', error);
      }
    };

    // 根据阅读量返回不同的样式类
    const getReadingTagClass = (count) => {
      if (count >= 100) return 'reading-very-high';
      if (count >= 50) return 'reading-high';
      if (count >= 20) return 'reading-medium';
      return 'reading-low';
    };

    // 跳转到阅读历史记录页面
    const navigateToReadHistory = (date, count) => {
      // 确保日期格式正确
      let targetDate;
      
      // 如果 date 是字符串，尝试解析它
      if (typeof date === 'string') {
        // 检查是否是完整的日期格式 (YYYY-MM-DD)
        if (date.split('-').length === 3) {
          targetDate = new Date(date);
        } 
        // 如果只有日部分 (DD)，需要构建完整日期
        else {
          const now = new Date();
          const year = now.getFullYear();
          const month = now.getMonth();
          targetDate = new Date(year, month, parseInt(date));
        }
      } else {
        targetDate = new Date(date);
      }
      
      // 格式化为 YYYY-MM-DD
      const year = targetDate.getFullYear();
      const month = String(targetDate.getMonth() + 1).padStart(2, '0');
      const day = String(targetDate.getDate()).padStart(2, '0');
      const formattedDate = `${year}-${month}-${day}`;
      
      console.log('跳转到阅读历史，日期:', formattedDate, '数量:', count);
      
      // 使用 localStorage 存储日期参数，确保页面刷新后仍然可用
      localStorage.setItem('targetReadDate', formattedDate);
      localStorage.setItem('targetReadCount', count);
      
      // 跳转到阅读历史页面
      router.push('/read_history');
    };

    // 组件挂载时获取数据
    onMounted(() => {
      fetchReadingStats();
    });

    const recentUploads = [
      {
        date: '2024-03-21 15:30',
        content: '人工智能技术在医疗领域取得重大突破，AI诊断准确率达到95%',
        result: true,
        confidence: 0.95
      },
      {
        date: '2024-03-21 10:45',
        content: '科学家发现可以在沙漠中种植水稻的革命性方法',
        result: false,
        confidence: 0.23
      },
      {
        date: '2024-03-20 16:20',
        content: '新能源汽车续航能力突破2000公里大关',
        result: false,
        confidence: 0.46
      },
      {
        date: '2024-03-20 09:15',
        content: '全球气候变化导致北极圈温度升高，科学家呼吁关注',
        result: true,
        confidence: 0.85
      },
      {
        date: '2024-03-20 09:15',
        content: '全球气候变化导致北极圈温度升高，科学家呼吁关注',
        result: true,
        confidence: 0.85
      }
    ];

    return {
      avatar,
      user: JSON.parse(localStorage.getItem('user')) || {},
      todayUploads: 12,
      totalUploads: 156,
      recentUploads,
      getConfidenceColor,
      readingStats,
      getReadingTagClass,
      navigateToReadHistory,
    };
  }
};
</script>

<style scoped>
.home-container {
  text-align: center;
  background-color: var(--bg-color);
  padding: 0;
  margin: 0;
}

.main-title {
  text-align: left;
  margin: 10px 0;
  font-weight: 600;
  font-size: 24px;
}

.dashboard-item {
  background: var(--navbar-bg);
  color:var(--font-color);
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.dashboard-item-content {
  height: 100%;
}

.hello-text {
  text-align: left;
  margin-bottom: 20px;
  font-weight: 400;
  font-size: 20px;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 10px;
}

.quick-access-item {
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px 5px 0px 5px;
  background: var(--navbar-bg);
}

.quick-access-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.quick-access-item .el-icon {
  text-align: left;
  font-size: 20px;
  color: #409EFF;
  margin-bottom: 10px;
}

.quick-access-item span {
  font-size: 16px;
  color: var(--font-color);
  margin-top: 5px;
}

.notification-content {
  min-height: 200px;
}

.activity-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 20px;
}


.recent-uploads, .reading-calendar {
  background: var(--navbar-bg);
  padding: 10px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.recent-uploads h2, .reading-calendar h2 {
  text-align: left;
  margin-bottom: 10px;
  color: var(--font-color);
  font-size: 20px;
}

.el-carousel__item {
  border-radius: 8px;
  overflow: hidden;
}

.el-carousel__item h3 {
  background: var(--navbar-bg);
  font-size: 18px;
  font-weight: 500;
  line-height: 200px;
  margin: 0;
  text-align: center;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.el-carousel__item:nth-child(2n) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.el-carousel__item:nth-child(2n + 1) {
  background: linear-gradient(135deg, #7f7fd5 0%, #86a8e7 50%, #91eae4 100%);
}

.calendar-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 2px 0;
}

.el-calendar {
  background-color: var(--navbar-bg);
  margin: 5px;
}

:deep


.upload-stats {
  padding: 15px;
  border-radius: 8px;
}

.stat-item {
  margin-bottom: 8px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  color: var(--font-color);
  font-size: 14px;
  margin-right: 8px;
}

.stat-value {
  color: #409EFF;
  font-size: 16px;
  font-weight: 600;
}

.dashboard-item-content-notification{
  height:355px;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .el-row {
    flex-direction: column;
  }
  .el-col {
    span: 24;
  }
}

/* 阅读容器样式 */
.reading-container {
  margin-top: auto;
  width: 100%;
  display: flex;
  justify-content: center;
  padding-bottom: 2px;
}

/* 阅读标签样式 */
.reading-tag {
  margin-top: 4px;
  border-radius: 12px;
  font-size: 12px;
  padding: 2px 8px;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.reading-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.reading-low {
  background-color: #e1f3ff;
  color: #409EFF;
}

.reading-medium {
  background-color: #e6f7ff;
  color: #1890ff;
}

.reading-high {
  background-color: #f0f9ff;
  color: #0050b3;
}

.reading-very-high {
  background: linear-gradient(45deg, #1890ff, #36cfc9);
  color: white;
}

/* 日期样式 */
.date {
  font-weight: 500;
  margin-bottom: 4px;
}

/* 日历单元格样式 */
:deep(.el-calendar-day) {
  height: 60px;
  padding: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
}

:deep(.el-calendar-day:hover) {
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 8px;
}
</style>
