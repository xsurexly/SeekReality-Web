<template>
  <div class="aboutUs-container">
    <div class="content">
      <h1>关于我们</h1>
      <section class="team">
        <h2>团队介绍</h2>
        <p>我们的团队由一群充满激情和专业的成员组成，致力于为客户提供卓越的服务。</p>
        <!-- 团队成员列表 -->
        <div class="team-members">
          <div class="team-member">
            <img src="path-to-team-member-photo.jpg" alt="团队成员照片">
            <h3>姓名</h3>
            <p>职位</p>
          </div>
          <!-- 更多团队成员 -->
        </div>
      </section>

      <section class="history">
        <h2>公司历史</h2>
        <p>自公司成立以来，我们始终坚持创新和卓越的价值观，不断为客户提供高质量的产品和服务。</p>
      </section>

      <section class="vision">
        <h2>我们的愿景</h2>
        <p>我们致力于成为行业的领导者，通过不断的技术创新和卓越的客户服务，实现可持续发展。</p>
      </section>

      <section class="mission">
        <h2>我们的使命</h2>
        <p>我们的使命是通过提供高质量的产品和服务，满足客户的需求，同时为社会做出积极的贡献。</p>
      </section>
    </div>
  </div>
</template>

<script>


export default {
  components: {

  },
  name: 'AboutUs'
};
</script>

<style>
.aboutUs-container {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  background-color: #f7f7f7;
  color: #333;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex-grow: 1;
  padding: 20px;
  text-align: center;
}

h1, h2 {
  color: #2c3e50;
}

h1 {
  margin-bottom: 20px;
  font-size: 2.5em;
}

h2 {
  margin-bottom: 15px;
  font-size: 1.5em;
}

p {
  line-height: 1.6;
  margin-bottom: 20px;
}

.team-members {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
}

.team-member {
  text-align: center;
  max-width: 200px;
}

.team-member img {
  width: 100%;
  height: auto;
  border-radius: 50%;
  margin-bottom: 10px;
}

/* 添加响应式设计 */
@media (max-width: 768px) {
  .team-members {
    flex-direction: column;
  }
}
</style>
