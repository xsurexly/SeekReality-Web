<template>
  <div class="detect-container">
    <h3 class="main-title">虚假新闻检测</h3>
    <el-tabs v-model="activeName">
      <!-- 文本检测 -->
        <el-tab-pane label="上传文本" name="text">
            <text-detection
              v-model="inputText"
              :is-detecting="isDetecting"
              :text-result="textResult"
              @detect="handleTextDetection"
            />
        </el-tab-pane>

      <!-- 文件检测 -->
        <el-tab-pane label="上传文件" name="file">
            <file-detection
            :file-list="fileList"
            :detection-results="detectionResults"
            :total-progress="totalProgress"
            :completed-count="completedCount"
            :is-detecting="isDetecting"
            @file-change="handleFileChange"
            @remove-file="removeFile"
            @start-detection="startFileDetection"
          />
        </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import axios from 'axios'
import TextDetection from './TextDetection.vue'
import FileDetection from './FileDetection.vue'

// 共用状态
const activeName = ref('text')
const isDetecting = ref(false)

// 文本检测相关
const inputText = ref('')
const textResult = ref(null)

// 文件检测相关
const fileList = ref([])
const detectionResults = ref([])

// 进度计算
const totalProgress = computed(() => {
  return fileList.value.length
    ? Math.round((completedCount.value / fileList.value.length) * 100)
    : 0
})

const completedCount = computed(() => {
  return detectionResults.value.filter(r => r.status === 'success').length
})

// 文本检测处理
const handleTextDetection = async () => {
  try {
    const { data } = await request.post('/api/text-detect', {
      text: inputText.value
    })
    textResult.value = data
    ElMessage.success('检测完成')
  } catch (error) {
    ElMessage.error('检测失败')
  }
}

// 文件处理
const handleFileChange = (file) => {
  fileList.value.push({
    ...file,
    status: '等待中',
    progress: 0
  })
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
}

const startFileDetection = async () => {
  isDetecting.value = true
  detectionResults.value = []

  for (const [index, file] of fileList.value.entries()) {
    try {
      fileList.value[index].status = '检测中'
      const formData = new FormData()
      formData.append('file', file.raw)

      const { data } = await axios.post('/api/file-detect', formData, {
        onUploadProgress: progressEvent => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          fileList.value[index].progress = progress
        }
      })

      detectionResults.value.push({
        fileName: file.name,
        ...data,
        progress: 100,
        status: 'success'
      })
      fileList.value[index].status = '成功'
    } catch (error) {
      fileList.value[index].status = '失败'
      detectionResults.value.push({
        fileName: file.name,
        progress: 100,
        status: 'exception',
        error: error.message
      })
    }
  }
  isDetecting.value = false
}
</script>

<style scoped>
.detect-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  margin-top: -20px;
  color: var(--font-color);

  .main-title {
    text-align: left;
    margin-bottom: 20px;

    font-size: 24px;
  }
}

:deep(.el-tabs__item){
  color: var(--font-color);
}

@media (max-width: 768px) {
  .detect-container {
    padding: 10px;

    .main-title {
      font-size: 20px;

    }
  }
}
</style>
