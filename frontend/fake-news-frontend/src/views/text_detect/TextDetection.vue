<template>
  <el-card shadow="hover" class="text-card" style="margin: 20px;padding: 20px;width: auto;border-radius: 10px;justify-content: center;">
    <!-- 文本输入 -->
    <el-input
      v-model="inputText"
      type="textarea"
      :rows="6"
      placeholder="请输入需要检测的文本内容"
      resize="none"
    />

    <!-- 检测按钮 -->
    <el-button
      type="primary"
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

            <el-descriptions-item label="可疑关键词" v-if="detectionResult.keyPoints?.length">
              <el-tag
                v-for="(word, index) in detectionResult.keyPoints"
                :key="index"
                type="danger"
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

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

// 模拟检测进度更新
let progressInterval = null
const startTextDetection = async () => {
  try {
    isDetecting.value = true
    detectionResult.value = null

    // 模拟进度更新
    progressInterval = setInterval(() => {
      detectionProgress.value = Math.min(detectionProgress.value + 10, 95)
    }, 500)

    // 实际应该调用API
    const mockResult = await new Promise(resolve => {
      setTimeout(() => {
        resolve({
          isFake: Math.random() > 0.5,
          fraudProbability: Math.floor(Math.random() * 30 + 30),
          keyPoints: ['不实信息', '夸张表述', '未经验证'],
          analysis: '检测到文本中存在多个未经证实的断言，建议结合权威信息源进行交叉验证。'
        })
      }, 3000)
    })

    // 完成进度
    detectionProgress.value = 100
    detectionResult.value = mockResult
    ElMessage.success('检测完成')
  } catch (error) {
    ElMessage.error('检测失败: ' + error.message)
    detectionResult.value = {
      isFake: false,
      fraudProbability: 0,
      analysis: '检测过程中发生错误'
    }
  } finally {
    clearInterval(progressInterval)
    isDetecting.value = false
  }
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;
.text-card {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  background: var(--navbar-bg);

  .detect-btn {
    margin-top: 20px;
    width: 100%;
    height: 40px;
    font-size: 16px;
  }

  .result-card {
    margin-top: 25px;
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
