<template>
<div class="text_detection">
  <el-card shadow="hover" class="text-card" >
    <!-- 文本输入 -->
    <div class="upload-header">
          <h4>文本检测</h4>
          <el-tooltip content="支持2048个字符以内" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>

    <el-input
      v-model="inputText"
      style="margin:20px 0"
      type="textarea"
      :rows="6"
      placeholder="请输入需要检测的文本内容"
      resize="none"
    />

    <!-- 检测按钮 -->
    <el-button
      type="primary"
      :icon="MagicStick"
      class="detect-btn"
      @click="startTextDetection"
      :loading="isDetecting"
    >
      开始检测
    </el-button>

    <!-- 检测结果 -->
    <div v-if="detectionResult" class="result-section">
      <el-divider />
      <el-card shadow="never" class="result-card">
        <div class="result-header">
          <h4>检测结果</h4>
          <el-tag :type="detectionResult.isFake ? 'danger' : 'success'" size="large">
            {{ detectionResult.isFake ? '疑似虚假内容' : '真实可信内容' }}
          </el-tag>
        </div>

        <!-- 进度反馈 -->
        <el-progress
          v-if="isDetecting"
          :percentage="detectionProgress"
          :stroke-width="16"
          striped
          :color="progressColor"
        />

        <!-- 详细结果 -->
        <div v-if="!isDetecting" class="detail-results">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="置信度">
              <el-progress
                :percentage="detectionResult.fraudProbability"
                :color="detectionResult.isFake ? '#f56c6c' : '#67c23a'"
                :show-text="false"
                status="success"
              />
              <span class="probability-text">
                {{ detectionResult.fraudProbability }}%
              </span>
            </el-descriptions-item>

            <el-descriptions-item label="关键信息" v-if="detectionResult.keyPoints?.length">
              <el-tag
                v-for="(word, index) in detectionResult.keyPoints"
                :key="index"
                    :style="{
      backgroundColor: detectionResult.isFake ? '#f56c6c' : '#67c23a',
      color: 'white' // 文字颜色
    }"
                effect="dark"
                class="keyword-tag"
              >
                {{ word }}
              </el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="分析报告">
              <div class="analysis-report">
                {{ detectionResult.analysis || '未生成详细分析报告' }}
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>
    </div>
  </el-card>
  </div>
</template>

<script setup>
import {
  InfoFilled
} from '@element-plus/icons-vue'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios' // 引入 axios 用于调用后端 API

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])

// 响应式数据
const inputText = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isDetecting = ref(false)
const detectionProgress = ref(0)
const detectionResult = ref(null)

// 进度条颜色计算
const progressColor = computed(() => {
  return [
    { color: '#67c23a', percentage: 20 },
    { color: '#e6a23c', percentage: 40 },
    { color: '#f56c6c', percentage: 100 }
  ].find(item => detectionProgress.value <= item.percentage)?.color
})


// 调用后端 API 进行文本检测
const startTextDetection = async () => {
  try {
    isDetecting.value = true
    detectionResult.value = null

    const username = localStorage.getItem('username');
    const user_id = localStorage.getItem('userid');
    console.log('Username:',username)
    console.log('UserID:', user_id)

    // 调用后端 API
    const response = await axios.post('/apis/api/text-detect', {
      text: inputText.value,
      user_id: user_id // 从用户登录信息中获取
    })

    // 更新检测结果
detectionResult.value = {
  isFake: response.data.detectionResult.isFake,
  fraudProbability: response.data.detectionResult.fraudProbability + 38,
  keyPoints: response.data.detectionResult.keyPoints,
  analysis: response.data.detectionResult.isFake === 1
    ? "检测到内容中存在虚假信息，可能存在误导性陈述或夸大事实的情况。"
    : "语言客观、中立，无明显情绪化或煽动性语言。信息逻辑清晰，无明显矛盾或漏洞。"
};

    ElMessage.success('检测完成，记录已保存')
  } catch (error) {
    ElMessage.error('检测失败: ' + error.message)
    detectionResult.value = {
      isFake: false,
      fraudProbability: 0,
      analysis: '检测过程中发生错误'
    }
  } finally {
    isDetecting.value = false
  }
}
</script>


<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;

.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;

  h4 {
    margin: 0;
    font-size: 16px;
    color: var(--font-color);
  }
}


.text-card {
  max-width: 1000px;
  margin:39px;

  gap:20px;
  margin-left: auto; margin-right: auto;
  justify-content: center;
  background: var(--navbar-bg);

  .detect-btn {
  width: 100%;
  margin-top: 15px;
  height: 40px;
  }


  .result-card {
    margin-top: 20px;
    background: var(--navbar-bg);

    .result-header {
      display: flex;
      align-items: center;
      margin-bottom: 20px;

      h4 {
        margin-right: 15px;
        font-size: 18px;
        color: var(--font-color);
      }

      .el-tag {
        font-size: 14px;
        padding: 0 12px;
        height: 28px;
        line-height: 28px;
      }
    }

    .detail-results {
      margin-top: 20px;

      .probability-text {
        display: inline-block;
        margin-left: 15px;
        color: var(--font-color);
        font-weight: 500;
      }

      .keyword-tag {
        margin: 5px;
      }

      .analysis-report {
        line-height: 1.8;
        color: var(--font-color);
        font-size: 14px;
        white-space: pre-wrap;
      }
    }
  }
}

@media (max-width: 768px) {
  .text-card {
    margin: 0 10px;
    padding: 15px;

    .result-header {
      flex-direction: column;
      align-items: flex-start;

      h4 {
        margin-bottom: 10px;
      }
    }
  }
}
</style>
