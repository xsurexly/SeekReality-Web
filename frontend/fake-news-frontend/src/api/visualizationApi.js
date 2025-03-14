import http from "./http.js";

const visualizationApi = {
  // 获取新闻来源分布数据
  getNewsSourceDistribution() {
    return http.get("/visualization/news/source-distribution");
  },

  // 获取每日新闻趋势数据
  getDailyNewsTrend(days = 30) {
    return http.get(`/visualization/news/daily-trend?days=${days}`);
  },

  // 获取真假新闻分布数据
  getFakeNewsDistribution() {
    return http.get("/visualization/news/fake-distribution");
  },

  // 获取用户阅读习惯数据
  getUserReadingHabits(username) {
    return http.get(`/visualization/user/reading-habits?username=${username}`);
  },

  // 获取用户兴趣分布数据
  getUserInterests(username) {
    return http.get(`/visualization/user/interests?username=${username}`);
  },

  // 获取检测统计数据
  getDetectionStatistics() {
    return http.get("/visualization/detection/statistics");
  },

  // 获取基于时间的分析数据
  getTimeBasedAnalysis() {
    return http.get("/visualization/news/time-analysis");
  },

  // 获取地图时间数据
  getMapTimeData() {
    return http.get("/visualization/map2time");
  },

  // 获取主题时间数据
  getTopicTimeData() {
    return http.get("/visualization/time2topic");
  },

  // 发送主题河流关键词
  sendThemeRiverKeywords(keywords) {
    return http.post("/visualization/theme-river", keywords);
  },

  // 获取中间数据
  getMiddleData(ids) {
    return http.post("/visualization/middle", ids);
  },

  // 获取树图数据
  getTreeMapData(id) {
    return http.get(`/visualization/treemap/${id}`);
  }
};

export default visualizationApi; 