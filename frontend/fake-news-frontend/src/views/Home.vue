<template>
  <div class="home-container">
    <div class="hello-part">
      <el-avatar
        :size="45"
        :src="avatarUrl"
        style="margin-left: 10px;margin-right: 20px;"
        class="custom-avatar"
      >
        <img src="https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png" />
      </el-avatar>
      <span class="hello-text" style="margin-top:-30px">{{ greeting }}{{ user.username }}，欢迎进入智能虚假新闻检测平台</span>
    </div>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="15">
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
            <el-statistic :value="stats.todayTime" suffix="秒"/>
          </div>
          <div class="stat-item">
            <label>高风险内容</label>
            <el-statistic :value="stats.riskCount" />
          </div>
        </div>
      </el-card>
        <el-card class="dashboard-item" style="margin-top: 20px;">
          <template #header>
              <div class="card-header">
                <el-icon><Grid /></el-icon>
                <span>今日推荐</span>
              </div>
            </template>
          <div class="dashboard-item-content">
            <el-carousel
              :interval="4000"
              type="card"
              height="200px"
              :indicator-position="'outside'"
              class="custom-carousel">
              <el-carousel-item
                v-for="item in recommendedNews"
                :key="item.id"
                @click="navigateToNews(item)">
                <div class="carousel-item-content">
                  <el-image
                    :src="item.picUrl || defaultImage"
                    fit="cover"
                    class="carousel-image">
                    <template #error>
                      <div class="image-slot">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <div class="carousel-title">{{ item.title }}</div>
                </div>
              </el-carousel-item>
            </el-carousel>
          </div>
        </el-card>


        <el-card class="dashboard-item"  style="margin-top: 20px;">
          <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>阅读记录</span>
              </div>
            </template>
          <div class="dashboard-item-content">
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
          <template #header>
              <div class="card-header">
                <el-icon><Menu /></el-icon>
                <span>常用功能</span>
              </div>
            </template>
          <div class="dashboard-item-content">
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
              <el-card class="quick-access-item" @click="$router.push('/read_history')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-wenjian" /></el-icon>
                <span>阅读历史</span>
              </el-card>
              <el-card class="quick-access-item" @click="$router.push('/visualization')">
                <el-icon style="vertical-align: top;margin-right: 5px;"><svg-icon icon-name="icon-shuju" /></el-icon>
                <span>数据可视化</span>
              </el-card>
            </div>
          </div>
        </el-card>


        <el-card class="dashboard-item modern-fake-news" style="margin-top: 20px;">
          <template #header>
              <div class="card-header">
                <el-icon><WarningFilled /></el-icon>
                <span>常见虚假信息</span>
              </div>
            </template>
          <div class="modern-fake-news-header">
          </div>
          <div class="modern-fake-news-body">
            <div class="fake-news-grid">
              <el-card
                v-for="(news, index) in commonFakeNews"
                :key="index"
                class="fake-news-card"
                shadow="hover"
                style="position: relative;"
              >
                <div class="news-content">{{ news }}</div>
                <img :src="require('@/assets/image4.png')" class="fake-news-image" >
              </el-card>
            </div>
          </div>
        </el-card>
        <el-card class="dashboard-item" style="margin-top: 20px;">
          <template #header>
              <div class="card-header">
                <el-icon><UploadFilled /></el-icon>
                <span>最近上传</span>
              </div>
            </template>
          <div class="dashboard-item-content">
            <el-table
              :data="recentUploads"
              style="width: 100%"
              :header-cell-style="{ background: 'var(--navbar-bg)' }"
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
                    :percentage="(scope.row.confidence )"
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
import { ref, onMounted,computed  } from 'vue';
import axios from "axios";
import router from "@/router";
import {
  Picture,
  DataAnalysis,
  Grid,
  Menu,
  WarningFilled,
  UploadFilled,
  Clock
} from '@element-plus/icons-vue'

export default {
  components: {
    Picture,
    DataAnalysis,
    Grid,
    Menu,
    WarningFilled,
    UploadFilled,
    Clock
  },
  setup() {
    const avatar = ref(localStorage.getItem('avatar') || '')

    // 计算头像URL
    const avatarUrl = computed(() => {
      if (!avatar.value) {
        return 'https://cube.elemecdn.com/e/5c/e3a01e0ff18b42925b7a830931fb8png.png'
      }

      if (avatar.value.startsWith('http')) {
        return avatar.value
      }

      return `http://localhost:5000${avatar.value}`
    })

    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#67C23A'
      if (confidence >= 0.6) return '#E6A23C'
      return '#F56C6C'
    }
    const stats = ref({
      todayChecks: 0,
      todayReads: 0,
      todayTime: 0,
      riskCount: 0
    })

    const greeting = ref("");
    const getGreeting = () => {
      const hour = new Date().getHours(); // 获取当前小时
      if (hour >= 5 && hour < 12) {
        return "早安！";
      } else if (hour >= 12 && hour < 18) {
        return "午安！";
      } else {
        return "晚安！";
      }
    };


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
          updateStats(data.data);
        } else {
          console.error('获取数据失败:', data.message);
        }
      } catch (error) {
        console.error('请求失败:', error);
      }
    };

    const updateStats = (data) => {
      stats.value.todayChecks = Number(data.todayChecks) || 0;
      stats.value.todayReads = Number(data.todayReads) || 0;
      stats.value.todayTime = Number(data.todayTime) || 0;  // 确保是数字
      stats.value.riskCount = Number(data.riskCount) || 0;
    };


    // 初始化空的阅读统计数据
    const readingStats = ref([]);

    // 获取用户信息

    const username = localStorage.getItem('username');
      const userid = localStorage.getItem('userid');
    // 从后端获取阅读统计数据
    const fetchReadingStats = async () => {
      try {
        const response = await axios.get(`/apis/readhistory/reading_stats/${username}`);
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
      if (count >= 20) return 'reading-very-high';    // 非常高的阅读量
      if (count >= 10) return 'reading-high';         // 高阅读量
      if (count >= 5) return 'reading-medium';        // 中等阅读量
      return 'reading-low';                           // 低阅读量
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

    //最近上传记录的响应式引用
    const recentUploads=ref([]);
    // 获取最近的检测记录
    const fetchRecentUploads = async () => {
      try {
        console.log(userid)
        const response = await axios.get('/apis/history/detection-records', {
          params: {
            username: username,
            userid: userid
          }
        });

        if (response.data && response.data.history) {
          // 格式化数据以匹配表格需求
          recentUploads.value = response.data.history.map(record => ({
            date: new Date(record.created_at).toLocaleString('zh-CN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }),
            content: record.content,
            result: record.result,
            confidence: record.score // 假设后端返回的分数字段为 score
          })).slice(0, 5); // 确保只显示最近5条记录
        }
      } catch (error) {
        console.error('获取最近检测记录失败:', error);
      }
    };

    //今日推荐部分
    const recommendedNews = ref([]);
    const defaultImage = 'http://localhost:8080/default-news.jpg'; // 设置默认图片
    // 获取推荐新闻
    const fetchRecommendedNews = async () => {
      try {
        const response = await axios.get('/apis/news/get_recommended_news');
        if (response.data && response.data.recommended) {
          recommendedNews.value = response.data.recommended;
        }
      } catch (error) {
        console.error('获取推荐新闻失败:', error);
      }
    };
    // 跳转到新闻详情
    const navigateToNews = (news) => {
      router.push({
        path: '/newspage',
        query: {
          newsId: news.id,
          autoOpen: 'true'
        }
      });
    };

    // 常见虚假信息
    const commonFakeNews = ref([
      "广东医保基金出现赤字？",
      "AI可以预测彩票中奖号码、提高中奖率？",
      "首例智能驾驶致死案宣判？",
    ]);
    // 组件挂载时获取数据
    onMounted(() => {
      fetchReadingStats();
      fetchRecentUploads();
      fetchRecommendedNews();
      fetchUserData();
      greeting.value = getGreeting(); // 设置初始问候语

      // 每分钟更新一次问候语
      setInterval(() => {
        greeting.value = getGreeting();
      }, 600000);
    });

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
      recommendedNews,
      defaultImage,
      navigateToNews,
      commonFakeNews,
      stats,
      greeting,
      avatarUrl
    };
  }
};
</script>

<style scoped>
/* fakenews图标 */
.fake-news-card {
  position: relative; /* 确保子元素可以绝对定位 */
}

.fake-news-image {
  position: absolute; /* 绝对定位 */
  top: -28px; /* 距离顶部0 */
  left: 180px; /* 距离左侧0 */
  width: 25%; /* 宽度100% */
  height: auto; /* 高度自适应 */
  z-index: 1; /* 确保图片在文本上方 */
  opacity: 0.8; /* 可选：设置透明度 */
}

.news-content {
  position: relative; /* 确保文本在图片之上 */
  z-index: 2; /* 确保文本在图片之上 */
  color:var(--font-color); /* 可选：设置文本颜色以提高可读性 */
}

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

.hello-part {
  text-align: left;

}

.hello-text {
  display: inline-block;
  vertical-align: middle;
  font-weight: 600;
  font-size:24px;

}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 5px;
}

.quick-access-item {
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0px;
  background: var(--navbar-bg);
  border-radius: 10px;

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

/* 常见虚假信息卡片网格布局 */
.fake-news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 5px;
}

/* 单个虚假信息卡片样式 */
.fake-news-card {
  background: var(--navbar-bg);
  border-radius: 8px;
  padding: 6px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: var(--font-color);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: default;
}

.fake-news-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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

/*今日推荐部分*/
.carousel-item-content {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
.carousel-title {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 14px;
  text-align: left;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: var(--navbar-bg);
  color: var(--font-color);
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

[data-theme="dark"] .carousel-title {
  background: rgba(0, 0, 0, 0.8);
}

.el-carousel__item {
  border-radius: 8px;
  overflow: hidden;
}

.el-carousel__item:hover{
  transform: translateY(-5px);
  transition: all 0.3s ease;
}

:deep(.el-carousel__item--card) {
  border-radius: 8px;
}

:deep(.el-carousel__mask) {
  border-radius: 8px;
}

/*日历部分*/
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
  --el-calendar-selected-bg-color: var(--border-color) !important;
  height: 80%;
}

.upload-stats {
  padding: 15px;
  border-radius: 8px;
}

.stat-item {
  margin-bottom: 8px;
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
.hello-text{
  font-size: 16px;
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
  background-color: var(--navbar-bg);
  color: #409EFF;
  border: 1px solid #409EFF;
}

.reading-medium {
  background-color: var(--navbar-bg);
  color: #67C23A;
  border: 1px solid #67C23A;
}

.reading-high {
  background-color: var(--navbar-bg);
  color: #E6A23C;
  border: 1px solid #E6A23C;
}

.reading-very-high {
  background-color: var(--navbar-bg);
  color: #F56C6C;
  border: 1px solid #F56C6C;
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


/* 修改表格样式以支持深色模式 */
:deep(.el-table) {
  background-color: var(--navbar-bg);
  color: var(--font-color);
}

:deep(.el-table th.el-table__cell) {
  background-color: var(--navbar-bg);
  color: var(--font-color);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table tr) {
  background-color: var(--navbar-bg);
}

:deep(.el-table td.el-table__cell) {
  background-color: var(--navbar-bg);
  color: var(--font-color);
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell) {
  background-color: var(--hover-nav);
}

/* 修改新闻内容文本样式 */
.news-text {
  color: var(--font-color);
  margin: 0;
  line-height: 1.4;
}

/* 修改tooltip样式 */
:deep(.el-tooltip__trigger) {
  color: var(--font-color);
}

/* 修改进度条背景色 */
:deep(.el-progress-bar__outer) {
  background-color: var(--border-color);
}

/* 修改表格头部样式 */
:deep(.el-table__header) {
  background-color: var(--navbar-bg);
}

:deep(.el-table__header-wrapper) {
  background-color: var(--navbar-bg);
}

/* 修改空状态样式 */
:deep(.el-empty__description) {
  color: var(--font-color);
}

/* 修改按钮样式 */
:deep(.el-button) {
  background-color: var(--navbar-bg);
  border-color: var(--border-color);
  color: var(--font-color);
}

:deep(.el-button:hover) {
  background-color: var(--hover-nav);
  border-color: var(--border-color);
}

/* 修改标题样式 */
h2 {
  color: var(--font-color);
}



:deep(.el-carousel__indicators) {
  bottom: 0px; /* 调整指示器位置 */
}

:deep(.el-carousel__indicator) {
  padding: 12px 4px;
}

:deep(.el-carousel__button) {
  background-color: var(--border-color);
}

:deep(.el-carousel__indicator.is-active .el-carousel__button) {
  background-color: var(--font-color);
}

.fake-news-item {
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.fake-news-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.reading-tag {
  margin-top: 4px;
  border-radius: 12px;
  font-size: 14px;
  padding: 4px 10px;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.reading-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.data-view{
  font-size: 14px;
  margin-bottom: 20px;
  border-radius: 10px;
  background: var(--navbar-bg);
  color: var(--font-color);
}

.stat-item:hover {
  transform: translateY(-5px);
  transition: all 0.3s ease;
}

.card-header .el-icon {
  margin-right: 8px;
  font-size: 20px;
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
  padding: 10px;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-item label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
}

:deep(.el-statistic__content){
  color: var(--font-color);
}

@media screen and (max-width: 768px) {
  /* 强制栅格系统转为单列 */

  .el-row {
    display: block !important;

    .el-col {
      width: 96% !important;
      max-width: 96% !important;
      display: block !important;

      /* 移除所有栅格间隔 */
      &[class*="el-col-"] {
        margin-left: 10px !important;
        margin-right: 10px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
      }
    }
  }

  /* 强制所有卡片占满宽度 */
  .dashboard-item {
    width: 96% !important;
    max-width: 96% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  /* 调整主内容顺序 */
  .el-col:first-child {
    order: 1;
  }

  .el-col:last-child {
    order: 2;
    margin-top: 20px !important;
  }
}


</style>
