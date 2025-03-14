import http from "./http.js";

const api = {
  // 获取地图时间数据
  getMapData() {
    return http.get("/visualization/map2time");
  },

  // 获取主题时间数据
  getTopicData() {
    return http.get("/visualization/time2topic");
  },

  // 获取主题河流图数据
  sendRiverKeywords(keywords) {
    return http.post("/visualization/theme-river", keywords);
  },

  // 获取中间数据
  getMiddleData(ids) {
    return http.post("/visualization/middle", ids);
  },

  // 获取树图数据
  getTreeMap(id) {
    return http.get(`/visualization/treemap/${id}`);
  },

  // 获取新闻来源分布
  getSourceDistribution() {
    return http.get("/visualization/news/source-distribution");
  },

  // 获取每日新闻趋势
  getDailyTrend(days = 30) {
    return http.get(`/visualization/news/daily-trend?days=${days}`);
  },

  // 获取真假新闻分布
  getFakeDistribution() {
    return http.get("/visualization/news/fake-distribution");
  },

  // 获取用户阅读习惯
  getReadingHabits(username) {
    return http.get(`/visualization/user/reading-habits?username=${username}`);
  },

  // 获取用户兴趣分布
  getUserInterests(username) {
    return http.get(`/visualization/user/interests?username=${username}`);
  },

  // 获取检测统计数据
  getDetectionStats() {
    return http.get("/visualization/detection/statistics");
  },

  // 获取时间分析数据
  getTimeAnalysis() {
    return http.get("/visualization/news/time-analysis");
  }
};

export default api;