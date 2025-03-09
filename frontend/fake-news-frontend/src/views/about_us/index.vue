<template>
  <div class="aboutus-container">
    <h3 class="main-title">关于我们</h3>
    <h5 class="sub-title">展示本项目相关技术</h5>
    <div class="tab-container">
      <el-tabs tab-position="left" class="tabs">
        <el-tab-pane label="技术展示">
          <div class="content-section">
            <h4 class="section-title">动态分析与自适应虚假新闻鉴别器（DDAD）</h4>
            <p class="section-text">
              DAAD 是一个专为假新闻检测设计的动态分析和自适应判别模型。它不仅融合了最新的人工智能技术，还深入考虑了多模态信息在假新闻识别中的特点。这个模型主要包括以下两个创新模块：
            </p>
            <ul class="section-list">
              <li>
                <strong>动态分析与提示优化（Dynamic Analysis and Prompt Optimization）：</strong>
                该模块利用大型语言模型（LLMs）的自我反思能力，通过蒙特卡洛树搜索（MCTS）算法动态生成特定提示，引导 LLMs 提供更丰富的、针对假新闻检测的评论和预测。这种方法提高了模型对新闻内容分析的灵活性和准确性。
              </li>
              <li>
                <strong>自适应判别器建模（Adaptive Discriminator Modeling）：</strong>
                该模块包含四个专门的判别器，分别针对情感夸张、逻辑不一致、图像操纵和语义不一致等欺骗模式。通过软路由机制，模型能够自适应地选择最佳检测路径，从而更有效地识别假新闻。
              </li>
            </ul>
            <p class="section-text">
              此外，DAAD 模型还与可视化技术结合使用，进一步提高假新闻检测的准确性和可解释性。通过展示模型在判断新闻真实性时所关注的证据和模式，帮助用户理解模型的决策过程。
            </p>
            <img :src="require('@/assets/image1.png')" alt="DDAD 模型架构图" class="section-image">
          </div>

          <div class="content-section">
            <h4 class="section-title">多模态多尺度虚假新闻检测（MMFN）</h4>
            <p class="section-text">
              MMFN 是一种多模态虚假新闻检测方法，通过融合细粒度和粗粒度的信息来多尺度提高在社交媒体上检测假新闻的准确性。该方法的核心在于利用预训练的 BERT 模型和 Swin Transformer 分别提取文本和图像的细粒度特征，同时使用 CLIP 模型捕获文本和图像的粗粒度特征。
            </p>
            <p class="section-text">
              MMFN 设计了两个独立的单模态分支，并引入了基于 CLIP 相似度的权重调整机制，以适应性地调整多模态特征的使用，有效解决模态间冲突或弱相关性引起的歧义问题。
            </p>
            <img :src="require('@/assets/image2.png')" alt="MMFN 模型架构图" class="section-image">
          </div>

          <div class="content-section">
            <h4 class="section-title">多模型融合推理框架</h4>
            <p class="section-text">
              我们的多模型融合框架基于三个核心组件：DDAD 模型、MMFN 模型和一个基于 ERNIE 3.0 的虚假新闻检测模型。首先，利用 ERNIE 3.0 对文本数据进行预处理，提取深层次的语义特征。然后，将这些特征与 DDAD 和 MMFN 提取的细粒度和粗粒度的文本和图像特征进行融合，以增强模型对多模态数据的理解能力。
            </p>
            <p class="section-text">
              在模型的最后阶段，设计了一个综合决策层，整合来自三个模型的输出，以实现最终的假新闻检测判断。
            </p>
            <img :src="require('@/assets/image3.png')" alt="多模型融合推理框架图" class="section-image">
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>



<style scoped>
.aboutus-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  text-align: left;
}


.tab-container {
  background: var(--bg-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.tabs {
  margin-top: 20px;
}

.content-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--font-color);
  margin-bottom: 15px;
}

.section-text {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--font-color);
  margin-bottom: 15px;
}

.section-list {
  list-style-type: disc;
  padding-left: 20px;
  margin-bottom: 15px;
}

.section-list li {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--font-color);
  margin-bottom: 10px;
}

.section-image {
  width: 100%;
  max-width: 800px;
  display: block;
  margin: 20px auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.aboutus-container {
  max-width: 1400px;
  margin: 0 auto;
  color: var(--font-color);
}

.tab-container {
  background-color: var(--card-bg);
  padding: 40px;
  border-radius: 10px;
  box-shadow: var(--shadow-color);
  min-height: 250px;
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

.el-tabs {
  height: 100%;
  color: var(--font-color);
}

.el-tabs--left .el-tabs__content {
  padding-left: 30px;
}

:deep(.el-tabs__item){
  color: var(--font-color);
}
</style>
