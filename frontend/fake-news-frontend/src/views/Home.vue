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
              <template #dateCell="{ data }">
                <div class="calendar-cell" :class="getReadingClass(data.day)">
                  {{ data.day.split('-').slice(-1)[0] }}
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
import { ref } from 'vue';

export default {
  setup() {
    const avatar = ref(localStorage.getItem('avatar') || 'avatar.png');

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }

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
      getConfidenceColor
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
  align-items: center;
  justify-content: center;
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
</style>
