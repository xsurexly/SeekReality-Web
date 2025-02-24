<template>
  <div class="content-area">
    <!-- 用户信息模块 -->
    <div class="info-card">
      <div class="user-header">
        
        <div class="user-meta">
          <h2>小星 2</h2>
          <div class="tags">
            <span class="tag">航空航天爱好者</span>
            <span class="tag">大学生</span>
          </div>
          <p class="custom-info">自定义个性化信息</p>
        </div>
      </div>
      
      <div class="action-row">
        <button class="detail-btn">详细信息</button>
        <button class="edit-btn">修改信息</button>
      </div>
    </div>

    <!-- 个性化设置 -->
    <div class="settings-section">
      <h3>个性化设置</h3>
      <div class="settings-grid">
        <div class="setting-item">
          <span>新闻阅读记录</span>
          <span class="arrow">›</span>
        </div>
        <div class="setting-item">
          <span>新闻检测记录</span>
          <span class="arrow">›</span>
        </div>
        <div class="setting-item">
          <span>修改信息</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 统计模块 -->
    <div class="stats-grid">
      <!-- 检测统计 -->
      <div class="stat-card">
        <h4>检测统计</h4>
        <div class="progress-group">
          <div class="progress-item">
            <div class="progress-header">
              <span>检测速率</span>
              <span>92%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 92%"></div>
            </div>
          </div>
          <div class="progress-item">
            <div class="progress-header">
              <span>检测时间</span>
              <span>1m 36s</span>
            </div>
          </div>
          <div class="progress-stack">
            <div class="stack-item" style="width: 30%; background: #3498db"></div>
            <div class="stack-item" style="width: 50%; background: #e74c3c"></div>
          </div>
        </div>
      </div>

      <!-- 阅读统计 -->
      <div class="stat-card">
        <h4>阅读统计</h4>
        <div class="stat-grid">
          <div class="metric">
            <div class="value">50</div>
            <div class="label">阅读数量</div>
          </div>
          <div class="metric">
            <div class="value">1h 10m</div>
            <div class="label">阅读时间</div>
          </div>
          <div class="metric trend-down">
            <div class="value">3,086</div>
            <div class="label">在线时长 <span>23.5% (-10)</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部链接 -->
    <div class="footer-links">
      <a>联系我们</a>
      <a>隐私政策</a>
      <a>服务条款</a>
    </div>
  </div>
</template>

<style scoped>
.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}

.user-meta h2 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
}

.tags {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.tag {
  background: #ecf0f1;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.9em;
}

.custom-info {
  color: #7f8c8d;
  margin: 0;
}

.action-row {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.detail-btn, .edit-btn {
  padding: 8px 20px;
  border-radius: 20px;
  border: 1px solid #bdc3c7;
  background: white;
  cursor: pointer;
}

.settings-section {
  margin-top: 30px;
}

.settings-grid {
  display: grid;
  gap: 12px;
  background: white;
  padding: 16px;
  border-radius: 12px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 30px 0;
}

.progress-bar {
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  margin: 8px 0;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: #3498db;
}

.progress-stack {
  height: 8px;
  border-radius: 4px;
  margin-top: 15px;
  display: flex;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.value {
  font-size: 1.4rem;
  font-weight: bold;
  color: #2c3e50;
}

.label {
  color: #7f8c8d;
  font-size: 0.9em;
}

.trend-down span {
  color: #e74c3c;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 40px;
  color: #7f8c8d;
}
</style>