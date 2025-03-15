<template>
  <div class="file-detection">
    <!-- 左侧上传区域 -->
    <div class="upload-section">
      <el-card shadow="hover" style="background: var(--navbar-bg);">
        <!-- 上传头部 -->
        <div class="upload-header">
          <h4>文件上传</h4>
          <el-tooltip content="支持格式:txt/pdf/docx/jpg/png" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>

        <!-- 上传组件 -->
        <el-upload
          class="upload-area"
          drag
          multiple
          :auto-upload="false"

          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          accept=".txt,.pdf,.docx,.png,.jpg"
          :show-file-list="false"
        >
          <template #trigger>
            <div class="upload-content">
              <el-icon :size="40" class="upload-icon"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                点击或拖拽文件到此处
                <div class="el-upload__subtext">单个文件不超过10MB</div>
              </div>
            </div>
          </template>
        </el-upload>

        <!-- 文件列表 -->
        <div class="file-list" v-if="fileList.length > 0">
          <div
            class="file-item"
            v-for="(file, index) in fileList"
            :key="file.uid"
          >
            <div class="file-info">
              <el-icon :size="20" class="file-icon">
                <Document />
              </el-icon>
              <div class="file-details">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
            <div class="file-actions">
              <el-tag :type="getStatusType(file.status)" size="small">
                {{ file.status }}
              </el-tag>
              <el-button
                v-if="file.status === '等待中'"
                type="danger"
                text
                :icon="Delete"
                @click="$emit('remove-file', index)"
              />
            </div>
          </div>
        </div>

        <!-- 检测按钮 -->
        <el-button
          type="success"
          :icon="MagicStick"
          class="detect-button"
          @click="startFileDetection(fileList)"
          :disabled="!fileList.length"
          :loading="isDetecting"
          style="background-color: #409EFF;">
          开始检测
        </el-button>

      </el-card>
    </div>

    <!-- 右侧结果区域 -->
    <div class="result-section">
      <el-card shadow="hover" style="background: var(--navbar-bg);color: var(--font-color);">
        <h4>检测进度</h4>


 <div class="total-progress">
        <el-progress
          :percentage="totalProgress"
          :stroke-width="16"
          :color="customGradient"
          striped
        />
        <div class="progress-info">
          已完成 {{ completedCount }}/{{ fileList.length }}
        </div>
      </div>
        <!-- 实时结果 -->
        <div class="realtime-results">
          <div
            v-for="(result, index) in detectionResults"
            :key="index"
            class="result-item"
          >
            <div class="result-header">
              <span class="filename">{{ result.fileName }}</span>
              <el-tag :type="result.isFake ? 'danger' : 'success'" size="small">
                {{ result.isFake ? '疑似虚假' : '真实可信' }}
              </el-tag>
            </div>
            <el-progress
              :percentage="result.progress"
              :status="result.status"
              :stroke-width="8"
            />
            <div class="result-details">
              <span>置信度：{{ result.fraudProbability }}%</span>

               <el-button
              v-if="result.keyPoints"
              type="primary"
              link
              @click="showFileDetails(result)"
            >
                查看详情
              </el-button>
            </div>
            <div v-if="showDetails" class="file-content">
            <el-card shadow="hover" style="margin-top: 20px;">

              <pre>{{ selectedFileContent }}</pre>
            </el-card>

</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>
<script setup>
import {
  Document,
  Delete,
  UploadFilled,
  MagicStick,
  InfoFilled
} from '@element-plus/icons-vue'

import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const fileList = ref([])
const detectionResults = ref([])
const isDetecting = ref(false)

const completedCount = computed(() => detectionResults.value.filter(res => res.status === '成功').length)
const totalProgress = computed(() => fileList.value.length ? Math.floor((completedCount.value / fileList.value.length) * 100) : 0)

const handleFileChange = (file) => {
  file.status = '等待中'
  fileList.value.push(file)
}

const selectedFileContent = ref('') // 存储选中的文件内容
const showDetails = ref(false) // 控制是否显示详情

const showFileDetails = async () => {
 for (const file of fileList.value) {
    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('user_id', localStorage.getItem('userid'))

  try {
    const response = await axios.post('http://localhost:5000/api/file-detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    selectedFileContent.value = response.data.content
    showDetails.value = true // 显示详情
  } catch (error) {
    ElMessage.error('加载文件内容失败: ' + error.message)
  }
}}

// 动态渐变色
const customGradient = computed(() => {
  const percentage = totalProgress.value
  if (percentage < 30) {
    return 'linear-gradient(to right, #ebf5ee,#92d5c6)' // 浅绿到深绿
  } else if (percentage < 70) {
    return 'linear-gradient(to right, #ebf5ee,#92d5c6, #00c9a7)' // 深绿到蓝绿
  } else {
    return 'linear-gradient(to right,#ebf5ee,#92d5c6, #00c9a7,#0088a9   )' // 蓝绿到深绿
  }
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusType = (status) => {
  const statusMap = {
    '等待中': 'info',
    '检测中': 'warning',
    '成功': 'success',
    '失败': 'danger'
  }
  return statusMap[status] || 'info'
}

const beforeUpload = (file) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  return true
}

const startFileDetection = async () => {
  if (!fileList.value.length) return

  isDetecting.value = true
  detectionResults.value = []

  for (const file of fileList.value) {
    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('user_id', localStorage.getItem('userid'))

    try {
      const response = await axios.post('http://localhost:5000/api/file-detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.success) {
        detectionResults.value.push({
          fileName: file.name,
          isFake: response.data.isFake,
          fraudProbability: response.data.fraudProbability,
          keyPoints: response.data.keyPoints,
          progress: 100,
          status: '成功'
        })
        file.status = '成功'
        ElMessage.success(`${file.name} 检测完成`)
      } else {
        file.status = '失败'
        detectionResults.value.push({ fileName: file.name, status: '失败' })
        ElMessage.error(`${file.name} 检测失败: ${response.data.message}`)
      }
    } catch (error) {
      file.status = '失败'
      detectionResults.value.push({ fileName: file.name, status: '失败' })
      ElMessage.error(`${file.name} 上传失败: ${error.message}`)
    }
  }

  isDetecting.value = false
}

</script>




<style scoped lang="scss">
@use "@/assets/styles/_themes.scss" as *;
.file-detection {
  padding: 20px;
  margin: 20px;
  display: flex;
  gap: 20px;


  .upload-section, .result-section {
    flex: 1;
    min-width: 450px;

  }
}

:deep(.el_card__body){
  background: var(--navbar-bg);
}



.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;

  h4 {
    margin: 0;
    font-size: 16px;
    color: var(--font-color);
  }
}

.upload-area {
  margin: 20px 0;

  :deep(.el-upload-dragger) {
    padding: 30px;
    background: var(--navbar-bg);
    border-color: #e2e8f0;
  }

  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;

    .upload-icon {
      color: var(--font-color);
      margin-bottom: 10px;
    }

    .el-upload__text {
      color: var(--font-color);
      font-size: 14px;

      .el-upload__subtext {
        color: var(--font-color);
        font-size: 12px;
        margin-top: 6px;
      }
    }
  }
}
pre {
  white-space: pre-wrap; /* 保留换行和空格 */
  word-wrap: break-word; /* 长单词换行 */

  padding: 10px; /* 内边距 */
  border-radius: 4px; /* 圆角 */
  max-height: 300px; /* 最大高度 */
  overflow-y: auto; /* 超出内容滚动 */
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 15px 0;

  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    margin: 8px 0;
    background: var(--navbar-bg);
    border-radius: 6px;

    .file-info {
      display: flex;
      align-items: center;
      gap: 10px;

      .file-icon {
        color: var(--font-color);
      }

      .file-details {
        .file-name {
          font-size: 13px;
          color: var(--font-color);
        }

        .file-size {
          font-size: 12px;
          color: var(--font-color);
        }
      }
    }

    .file-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

.detect-button {
  width: 100%;
  margin-top: 15px;
  height: 40px;
}

.total-progress {
  margin: 20px 0;

  .progress-info {
    text-align: right;
    color: var(--font-color);
    font-size: 12px;
    margin-top: 8px;
  }
}

.realtime-results {
  height: calc(100% - 120px);
  overflow-y: auto;

  .result-item {
    padding: 12px;
    margin: 12px 0;
    border: 1px solid #f1f5f9;
    border-radius: 6px;

    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .filename {
        font-size: 13px;
        color: var(--font-color);
      }
    }

    .result-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      font-size: 12px;
      color: var(--font-color);
    }
  }
}

@media (max-width: 768px) {
  .file-detection {
    flex-direction: column;
    height: auto;

    .upload-section, .result-section {
      min-width: unset;
    }
  }
}
</style>
