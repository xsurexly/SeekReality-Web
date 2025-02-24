<template>
  <div class="file-detection">
    <!-- 左侧上传区域 -->
    <div class="upload-section">
      <el-card shadow="hover">
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
          :on-change="$emit('file-change', $event)"
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
          @click="$emit('start-detection')"
          :disabled="!fileList.length"
          :loading="isDetecting"
          style="background-color: #409EFF;"
        >
          开始检测
        </el-button>
      </el-card>
    </div>

    <!-- 右侧结果区域 -->
    <div class="result-section">
      <el-card shadow="hover">
        <h4>检测进度</h4>
        
        <!-- 总进度 -->
        <div class="total-progress">
          <el-progress
            :percentage="totalProgress"
            :stroke-width="16"
            :color="customColors"
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
              <el-button v-if="result.keyPoints" type="primary" link>
                查看详情
              </el-button>
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

import { ElMessage } from 'element-plus'


defineProps({
  fileList: Array,
  detectionResults: Array,
  totalProgress: Number,
  completedCount: Number,
  isDetecting: Boolean
})

defineEmits(['file-change', 'remove-file', 'start-detection'])

// 文件大小格式化
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const beforeUpload = (file) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  return true
}

// 状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    '等待中': 'info',
    '检测中': 'warning',
    '成功': 'success',
    '失败': 'danger'
  }
  return statusMap[status] || 'info'
}

// 进度条颜色
const customColors = [
  { color: '#e6a23c', percentage: 30 },
  { color: '#1989fa', percentage: 70 },
  { color: '#5cb87a', percentage: 100 }
]
</script>

<style scoped>
.file-detection {
  display: flex;
  gap: 20px;
  height: 100vh;

  .upload-section, .result-section {
    flex: 1;
    min-width: 450px;
  }
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;

  h4 {
    margin: 0;
    font-size: 16px;
    color: #303133;
  }
}

.upload-area {
  margin: 20px 0;

  :deep(.el-upload-dragger) {
    padding: 30px;
    background: #f8fafc;
    border-color: #e2e8f0;
  }

  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;

    .upload-icon {
      color: #94a3b8;
      margin-bottom: 10px;
    }

    .el-upload__text {
      color: #64748b;
      font-size: 14px;

      .el-upload__subtext {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 6px;
      }
    }
  }
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
    background: #f8fafc;
    border-radius: 6px;

    .file-info {
      display: flex;
      align-items: center;
      gap: 10px;

      .file-icon {
        color: #64748b;
      }

      .file-details {
        .file-name {
          font-size: 13px;
          color: #1e293b;
        }

        .file-size {
          font-size: 12px;
          color: #64748b;
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
    color: #64748b;
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
        color: #1e293b;
      }
    }

    .result-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      font-size: 12px;
      color: #64748b;
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
