<template>
  <div class="detection-wrapper">
    <div class="unified-detection">
      <el-row :gutter="20">
        <!-- 左侧输入区域 -->
        <el-col :span="9">
          <el-card class="input-section" shadow="hover">
            <!-- 检测模式选择 -->
            <div class="mode-selector">
              <el-radio-group v-model="detectionMode" size="large">
                <el-radio-button label="text">文本检测</el-radio-button>
                <el-radio-button label="multimodal">文件检测</el-radio-button>
              </el-radio-group>
            </div>

            <!-- 文本输入区域 -->
            <div v-show="detectionMode === 'text'" class="text-input">
              <el-input
                v-model="inputText"
                type="textarea"
                :rows="6"
                placeholder="请输入要检测的文本内容（最多2000字）"
                resize="none"
                show-word-limit
                maxlength="2000"
              />
            </div>

            <!-- 文件上传区域 -->
            <div v-show="detectionMode === 'multimodal'" class="file-upload">
              <el-upload
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                accept=".txt,.pdf,.docx,.jpg,.jpeg,.png"
                :show-file-list="false"
                :disabled="isDetecting"
                multiple
              >
                <template #trigger>
                  <div class="upload-content">
                    <el-icon :size="40"><UploadFilled /></el-icon>
                    <div class="upload-text">
                      <p>点击或拖拽文件到此处</p>
                      <p class="tip">支持图片（jpg/png）、PDF、Word文档</p>
                      <p class="tip">多模态检测支持文字和图像分析</p>
                    </div>
                  </div>
                </template>
              </el-upload>

              <!-- 文件列表 -->
              <div class="file-list" v-if="fileList.length > 0">
                <div class="selected-file-title">已选择的文件：</div>
                <el-scrollbar max-height="200px">
                  <div v-for="(file, index) in fileList" :key="index" class="file-item">
                    <div class="file-info">
                      <el-icon><Document /></el-icon>
                      <div class="file-meta">
                        <span class="filename">{{ file.name }}</span>
                        <span class="filesize">{{ formatSize(file.size) }}</span>
                      </div>
                    </div>
                    <el-button
                      size="small"
                      type="danger"
                      :icon="Delete"
                      @click="removeFile(index)"
                      :disabled="isDetecting"
                      circle
                    />
                  </div>
                </el-scrollbar>
              </div>
            </div>

            <!-- 检测控制 -->
            <div class="detect-control">
              <div class="model-selector">
                <div class="model-title">选择检测模型：</div>
                <el-radio-group v-model="selectedModel" :disabled="isDetecting">
                  <el-radio label="model1">文本检测模型</el-radio>
                  <el-radio label="model2">多模态检测模型</el-radio>
                </el-radio-group>
              </div>
              <el-button
                type="primary"
                :icon="MagicStick"
                :loading="isDetecting"
                @click="startDetection"
                class="detect-button"
              >
                {{ isDetecting ? '检测中...' : '开始检测' }}
              </el-button>
            </div>

            <!-- 检测进度 -->
            <div class="progress-section">
              <template v-if="detectionMode === 'multimodal' && fileList.length > 0">
                <div v-for="(file, index) in fileList" :key="index" class="file-progress-item">
                  <div class="file-progress-header">
                    <span class="filename">{{ file.name }}</span>
                    <el-button
                      size="small"
                      :type="selectedFileIndex === index ? 'primary' : 'default'"
                      @click="selectedFileIndex = index"
                    >
                      查看详情
                    </el-button>
                  </div>
                  <el-progress
                    :percentage="fileProgress[file.name] || 0"
                    :status="getProgressStatus(file.name)"
                    striped
                    :stroke-width="18"
                    :color="getProgressColor(file.name)"
                  />
                  <div v-if="detectionResults[index]" class="file-result-summary">
                    <el-tag :type="getResultTagType(detectionResults[index])" size="small">
                      {{ detectionResults[index].verdict }}
                    </el-tag>
                    <span class="confidence">置信度: {{ formatConfidence(detectionResults[index]) }}%</span>
                  </div>
                </div>
              </template>
              <el-progress
                v-else
                :percentage="progress"
                :status="progressStatus"
                striped
                :stroke-width="18"
                :color="progressColor"
              />
            </div>
          </el-card>
        </el-col>

        <!-- 右侧结果区域 -->
        <el-col :span="15">
          <el-card class="result-section" shadow="hover">
            <!-- 检测结果区 -->
            <div class="detection-result">
              <h3 class="section-title">检测结果</h3>
              <div v-if="detectionMode === 'multimodal' && fileList.length > 0" class="file-selector">
                <el-select v-model="selectedFileIndex" placeholder="选择要查看的文件">
                  <el-option
                    v-for="(file, index) in fileList"
                    :key="index"
                    :label="file.name"
                    :value="index"
                  />
                </el-select>
              </div>
              <div v-if="detectionResult.status" class="result-content">
                <div class="model-info">
                  <el-tag type="info">使用模型：{{ activeModel }}</el-tag>
                </div>

                <el-tag :type="resultTagType" effect="dark" class="result-tag">
                  {{ detectionResult.verdict }}
                </el-tag>

                <div class="confidence-meter">
                  <el-progress
                    :percentage="detectionResult.confidence.toFixed(2)"
                    :color="confidenceColor"
                    :stroke-width="24"
                    striped
                  />
                  <div class="confidence-info">
                    <span>置信度：{{ detectionResult.confidence.toFixed(2) }}%</span>
                  </div>
                </div>

                <!-- AI分析报告 -->
                <div class="ai-report" v-if="aiReport">
                    <div class="report-header">
                        <h3>AI深度分析报告</h3>
                        <div class="report-actions">
                          <el-button type="primary" size="small" @click="showExportMenu = true">
                            <el-icon><Download /></el-icon>导出报告
                          </el-button>
                        </div>
                      </div>

                    <div class="report-content">
                      <!-- 综合分析 -->
                      <div class="report-section">
                        <div class="section-header">
                          <el-icon><Document /></el-icon>
                          <h4>综合分析</h4>
                        </div>
                        <div class="section-content">
                          <pre class="report-text" v-html="formattedReport?.summary"></pre>
                        </div>
                      </div>

                      <!-- 信息来源分析 -->
                      <div class="report-section">
                        <div class="section-header">
                          <el-icon><Link /></el-icon>
                          <h4>信息来源分析</h4>
                        </div>
                        <div class="section-content">
                          <pre class="report-text" v-html="formattedReport?.sourceAnalysis"></pre>
                        </div>
                      </div>

                      <!-- 内容真实性核查 -->
                      <div class="report-section">
                        <div class="section-header">
                          <el-icon><Check /></el-icon>
                          <h4>内容真实性核查</h4>
                        </div>
                        <div class="section-content">
                          <pre class="report-text" v-html="formattedReport?.contentAnalysis"></pre>
                        </div>
                      </div>

                      <!-- 情感倾向分析 -->
                      <div class="report-section">
                        <div class="section-header">
                          <el-icon><DataAnalysis /></el-icon>
                          <h4>情感倾向分析</h4>
                        </div>
                        <div class="section-content">
                          <pre class="report-text" v-html="formattedReport?.sentimentAnalysis"></pre>
                        </div>
                      </div>
                    </div>
                </div>
              </div>
              <div v-else class="empty-result">
                <el-empty description="等待检测结果..." />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 导出菜单 -->
    <el-dialog
      v-model="showExportMenu"
      title="导出报告"
      width="300px"
      :close-on-click-modal="true"
      :show-close="true"
    >
      <div class="export-menu">
        <el-button type="primary" @click="handleExport('html')">
          <el-icon><Document /></el-icon>导出为HTML
        </el-button>
        <el-button type="primary" @click="handleExport('pdf')">
          <el-icon><Document /></el-icon>导出为PDF
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, computed, watch} from 'vue'
import {
  Document,
  Delete,
  UploadFilled,
  MagicStick,
  Download,
  Link,
  Check,
  DataAnalysis
} from '@element-plus/icons-vue'
import axios from 'axios'
import {ElMessage} from 'element-plus'
import { marked } from 'marked'

const detectionMode = ref('text')
const selectedModel = ref('model1')
const inputText = ref('')
const fileList = ref([])
const isDetecting = ref(false)
const progress = ref(0)
const detectionResult = ref({
  status: '',
  verdict: '',
  confidence: 0,
  keyPoints: [],
  content: ''
})
const aiReport = ref(null)
const activeModel = ref('')
const detectionResults = ref([])
const selectedFileIndex = ref(0)
const fileProgress = ref({})
const showExportMenu = ref(false)

// 计算属性
const resultTagType = computed(() =>
  detectionResult.value.verdict?.includes('真实') ? 'success' : 'danger'
)

const confidenceColor = computed(() =>
  detectionResult.value.confidence > 75 ? '#67c23a' :
    detectionResult.value.confidence > 50 ? '#e6a23c' : '#f56c6c'
)

const progressStatus = computed(() => {
  if (progress.value === 0) return ''
  if (progress.value === 100) return 'success'
  if (isDetecting.value) return ''
  return 'exception'
})

const progressColor = computed(() => {
  if (progress.value < 40) return '#409eff'
  if (progress.value < 80) return '#e6a23c'
  return '#67c23a'
})

// 配置marked
marked.setOptions({
  gfm: true, // 启用GitHub风格的Markdown
  breaks: true, // 允许回车换行
  headerIds: false, // 禁用标题ID
  mangle: false, // 禁用标题ID混淆
  sanitize: false // 禁用sanitize以允许HTML标签
})

// 添加格式化函数
const formatText = (text) => {
  if (!text) return '';
  try {
    // 确保文本中的换行符被正确处理
    const processedText = text
      .replace(/\n\n/g, '\n&nbsp;\n') // 处理连续换行
      .replace(/\n/g, '  \n'); // 确保单行换行被正确处理

    // 使用marked渲染Markdown
    const htmlContent = marked.parse(processedText);

    // 返回处理后的HTML内容
    return htmlContent;
  } catch (error) {
    console.error('Markdown渲染错误:', error);
    return text; // 如果渲染失败，返回原始文本
  }
};

// 修改样式以支持Markdown渲染
const formattedReport = computed(() => {
  if (!aiReport.value) return null;
  return {
    summary: formatText(aiReport.value.summary),
    sourceAnalysis: formatText(aiReport.value.sourceAnalysis),
    contentAnalysis: formatText(aiReport.value.contentAnalysis),
    sentimentAnalysis: formatText(aiReport.value.sentimentAnalysis)
  };
});

// 处理方法
const handleFileChange = (file) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  fileList.value.push(file)
}

const removeFile = (index) => {
  fileList.value.splice(index, 1)
}

const formatSize = (size) => {
  if (size < 1024) {
    return size + 'B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(1) + 'KB'
  } else {
    return (size / (1024 * 1024)).toFixed(1) + 'MB'
  }
}

const startDetection = async () => {
  try {
    isDetecting.value = true
    progress.value = 0
    detectionResults.value = []
    fileProgress.value = {}

    // 更新当前使用的模型名称用于显示
    activeModel.value = selectedModel.value === 'model2' ? '多模态检测模型' : '文本检测模型'

    // 验证输入
    if (detectionMode.value === 'text' && !inputText.value.trim()) {
      ElMessage.error('请输入要检测的文本内容')
      isDetecting.value = false
      return
    }

    if (detectionMode.value === 'multimodal' && fileList.value.length === 0) {
      ElMessage.error('请上传要检测的文件')
      isDetecting.value = false
      return
    }

    // 如果选择了多模态模型但检测模式是文本
    if (selectedModel.value === 'model2' && detectionMode.value === 'text') {
      ElMessage.warning('多模态检测模型需要上传文件，已切换到文件检测模式')
      detectionMode.value = 'multimodal'
      isDetecting.value = false
      return
    }

    try {
      if (selectedModel.value === 'model1') {
        if (detectionMode.value === 'text') {
          // 文本模型 + 文本检测
          const apiUrl = '/apis/api/text-detect'
          const response = await axios.post(apiUrl, {
            text: inputText.value,
            user_id: localStorage.getItem('userid')
          })
          detectionResult.value = processResponse(response.data)
        } else {
          // 文本模型 + 文件检测 - 逐个处理文件
          const apiUrl = '/apis/api/file-detect'
          const totalFiles = fileList.value.length

          for (let i = 0; i < totalFiles; i++) {
            const file = fileList.value[i]
            fileProgress.value[file.name] = 0

            const formData = new FormData()
            formData.append('file', file.raw)
            formData.append('user_id', localStorage.getItem('userid'))

            const response = await axios.post(apiUrl, formData)
            const result = processResponse(response.data)
            detectionResults.value.push({
              filename: file.name,
              ...result
            })

            // 更新当前文件的进度
            fileProgress.value[file.name] = 100
          }

          // 设置第一个文件的结果为当前显示结果
          if (detectionResults.value.length > 0) {
            detectionResult.value = detectionResults.value[0]
          }
        }
      } else if (selectedModel.value === 'model2') {
        // 多模态模型只能用于文件检测 - 逐个处理文件
        const apiUrl = '/apis/multidetect/file_predict'
        const totalFiles = fileList.value.length

        for (let i = 0; i < totalFiles; i++) {
          const file = fileList.value[i]
          fileProgress.value[file.name] = 0

          const formData = new FormData()
          formData.append('file', file.raw)
          formData.append('user_id', localStorage.getItem('userid'))

          const response = await axios.post(apiUrl, formData)
          const result = processMultiResponse(response.data)
          detectionResults.value.push({
            filename: file.name,
            ...result
          })

          // 更新当前文件的进度
          fileProgress.value[file.name] = 100
        }

        // 设置第一个文件的结果为当前显示结果
        if (detectionResults.value.length > 0) {
          detectionResult.value = detectionResults.value[0]
        }
      }

      // 显示检测成功消息
      ElMessage({
        message: '检测完成，正在生成分析报告...',
        type: 'success',
        duration: 2000
      })

    } catch (error) {
      console.error('检测API调用错误:', error)
      ElMessage.error(`检测失败: ${error.message || '未知错误'}`)
      isDetecting.value = false
      return
    }

    // 将检测结果传给AI助手生成报告
    try {
      await generateAIReport()
      ElMessage.success('检测流程全部完成')
    } catch (error) {
      console.error('生成AI报告失败:', error)
      ElMessage.warning('检测已完成，但AI分析报告生成失败，已生成基础分析报告')
    }

    progress.value = 100
  } catch (error) {
    console.error('检测过程发生错误:', error)
    ElMessage.error(`检测失败: ${error.message || '未知错误'}`)
  } finally {
    isDetecting.value = false
  }
}

//生成ai检测报告
const generateAIReport = async () => {
  try {
    // 获取正文内容
    let content = ''
    let currentResult = null

    if (detectionMode.value === 'text') {
      content = inputText.value
      currentResult = detectionResult.value
    } else {
      // 如果是多文件模式，使用当前选中文件的内容
      currentResult = detectionResults.value[selectedFileIndex.value]
      // 对于多模态检测，只使用提取的文本内容
      content = currentResult?.content || '无法提取文件内容'
    }

    // 如果检测内容太长，截断它以避免传输问题
    const maxContentLength = 2000
    if (content.length > maxContentLength) {
      content = content.substring(0, maxContentLength) + '...(内容已截断)'
    }

    if (!currentResult) {
      throw new Error('无法获取检测结果')
    }

    // 构建新的分析提示，符合AI助手格式
    const analysisPrompt = `请作为虚假新闻检测专家，基于以下检测结果对内容进行分析：
      检测结论：${currentResult.verdict}
      置信度：${currentResult.confidence}%
      检测模型：${activeModel.value}
      检测内容：
      ${content}
      ${detectionMode.value === 'text' ? `关键指标：${currentResult.keyPoints?.join('; ')}` : ''}

      请按照以下格式生成分析报告：

      真实性评分：${currentResult.confidence}

      详细分析：
      1. 内容可信度评估：基于检测模型的判定结果和置信度分析内容的可信程度
      ${detectionMode.value === 'text' ? `2. 关键特征分析：${currentResult.keyPoints?.map((point, index) => `分析点${index + 1}: ${point}`).join('\n')}` : '2. 文本特征分析：分析文本内容的的表达方式、语气和逻辑性'}
      3. 语言特征分析：分析内容的表达方式、语气和逻辑性
      4. 信息完整性：评估内容的完整性和连贯性

      相关事实依据：
      - 检测模型判定：${currentResult.verdict}
      - 置信度指标：${currentResult.confidence}%
      ${detectionMode.value === 'text' ? `- 关键特征：${currentResult.keyPoints?.join('\n- ')}` : '- 文本分析：基于提取的文本内容进行分析'}

      总结：
      基于${activeModel.value}的检测结果，结合上述分析，${
            currentResult.confidence > 75
              ? '该内容具有较高的真实性，建议可以参考。'
              : currentResult.confidence > 50
                ? '该内容真实性一般，建议进一步核实。'
                : '该内容真实性较低，建议谨慎对待。'
          }`

    // 获取用户信息
    const userInfo = {
      username: localStorage.getItem('username') || '未登录用户'
    }

    try {
      // 直接使用axios发送请求，设置更长的超时时间
      const response = await axios.post('/apis/aihelper/getreport', {
        message: analysisPrompt,
        conversation_mode: 'analysis',
        needs_analysis: true,
        username: userInfo.username
      }, {
        timeout: 120000, // 设置120秒超时
        retry: 3, // 添加重试次数
        retryDelay: 2000, // 重试延迟2秒
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      })

      if (response.data && response.data.response) {
        // 解析AI助手的响应
        const aiResponse = response.data.response

        // 将响应转换为前端需要的格式
        aiReport.value = {
          summary: extractSection(aiResponse, '总结'),
          sourceAnalysis: extractSection(aiResponse, '相关事实依据'),
          contentAnalysis: extractSection(aiResponse, '详细分析'),
          sentimentAnalysis: extractSection(aiResponse, '语言特征分析')
        }
      } else {
        throw new Error('AI助手返回的响应为空')
      }
    } catch (error) {
      console.error('AI助手请求错误:', error)

      // 创建降级报告
      aiReport.value = createFallbackReport(currentResult)

      // 根据错误类型显示不同的错误消息
      if (error.code === 'ECONNABORTED') {
        ElMessage.warning('AI助手服务响应超时，正在重试...')
        // 尝试重新发送请求
        try {
          const retryResponse = await axios.post('/apis/aihelper/getreport', {
            message: analysisPrompt,
            conversation_mode: 'analysis',
            needs_analysis: true,
            username: userInfo.username
          }, {
            timeout: 120000,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          })

          if (retryResponse.data && retryResponse.data.response) {
            const aiResponse = retryResponse.data.response
            aiReport.value = {
              summary: extractSection(aiResponse, '总结：'),
              sourceAnalysis: extractSection(aiResponse, '相关事实依据：'),
              contentAnalysis: extractSection(aiResponse, '详细分析：'),
              sentimentAnalysis: extractSection(aiResponse, '语言特征分析：')
            }
            ElMessage.success('AI分析报告生成成功')
          }
        } catch (retryError) {
          console.error('重试请求失败:', retryError)
          ElMessage.warning('AI助手服务暂时不可用，已生成基础分析报告')
        }
      } else if (error.response?.status === 500) {
        ElMessage.warning('AI助手服务暂时不可用，已生成基础分析报告')
      } else if (error.message?.includes('proxy') || error.message?.includes('SSL')) {
        ElMessage.warning('网络连接问题，请检查网络设置或代理配置')
      } else {
        ElMessage.warning(`AI分析报告生成失败: ${error.message || '未知错误'}，已生成基础分析报告`)
      }
    }
  } catch (error) {
    console.error('生成AI报告错误:', error)
    if (!aiReport.value) {
      const currentResult = detectionMode.value === 'text' ?
        detectionResult.value :
        detectionResults.value[selectedFileIndex.value]
      aiReport.value = createFallbackReport(currentResult)
    }
    ElMessage.warning('生成AI分析报告失败，已生成基础分析报告')
  }
}

// 添加辅助函数来提取报告各个部分
const extractSection = (text, marker) => {
  const start = text.indexOf(marker)
  if (start === -1) return ''

  // 找下一个标记的位置
  const nextMarkers = ['真实性评分：', '详细分析：', '相关事实依据：', '总结：']
  let end = text.length

  for (const nextMarker of nextMarkers) {
    if (nextMarker !== marker) {
      const pos = text.indexOf(nextMarker, start + marker.length)
      if (pos !== -1 && pos < end) {
        end = pos
      }
    }
  }

  return text.slice(start + marker.length, end).trim()
}

// 修改降级报告生成函数，使其符合新格式
const createFallbackReport = (result) => {
  const confidence = result.confidence || 0
  const verdict = result.verdict || '未知'
  const keyPoints = result.keyPoints || ['无详细分析']

  return `真实性评分：${confidence}

详细分析：
1. 内容可信度评估：根据检测结果，该内容的真实性评分为${confidence}分，${
    confidence > 75 ? '表现出较高的可信度' :
    confidence > 50 ? '表现出中等可信度' :
    '表现出较低的可信度'
  }。
2. 检测结果：系统判定为"${verdict}"
3. 关键特征分析：
${keyPoints.map((point, index) => `   - 特征${index + 1}：${point}`).join('\n')}

相关事实依据：
- 检测结果：${verdict}
- 置信度：${confidence}%
${keyPoints.map(point => `- ${point}`).join('\n')}

总结：
基于${activeModel.value}的自动检测结果，该内容${
    confidence > 75 ? '展现出较高的真实性特征，建议可以参考使用。' :
    confidence > 50 ? '真实性特征一般，建议在使用前进行进一步核实。' :
    '真实性特征较弱，建议谨慎对待，并寻求其他可靠来源验证。'
}`
}


const processResponse = (data) => {
  // 检查和处理响应中的字段
  if (!data) {
    return {
      status: 'error',
      verdict: '检测失败',
      confidence: 0,
      keyPoints: ['无法获取检测结果'],
      content: ''
    }
  }

  // 处理text-detect接口响应
  if (data.detectionResult || data.isFake !== undefined) {
    const result = data.detectionResult || data
    return {
      status: 'complete',
      verdict: result.isFake ? '疑似虚假内容' : '真实可信内容',
      confidence: result.fraudProbability || 0,
      keyPoints: result.keyPoints || [],
      content: data.content || inputText.value
    }
  }

  // 处理file-detect接口响应
  if (data.content || data.savedPath) {
    return {
      status: 'complete',
      verdict: data.isFake ? '疑似虚假内容' : '真实可信内容',
      confidence: data.fraudProbability || 0,
      keyPoints: data.keyPoints || [],
      content: data.content || '提取的文件内容'
    }
  }

  // 默认情况
  return {
    status: 'complete',
    verdict: '未知结果',
    confidence: 50,
    keyPoints: ['无法解析检测结果'],
    content: ''
  }
}

const processMultiResponse = (data) => {
  // 检查和处理响应中的字段
  if (!data || !data.result) {
    return {
      status: 'error',
      verdict: '检测失败',
      confidence: 0,
      keyPoints: ['无法获取多模态检测结果'],
      content: ''
    }
  }

  // 处理多模态检测结果
  try {
    const keyPoints = []
    if (data.result.analysis) {
      // 提取分析说明和建议
      if (data.result.analysis['分析说明']) {
        keyPoints.push(data.result.analysis['分析说明'])
      }
      if (data.result.analysis['建议']) {
        keyPoints.push(data.result.analysis['建议'])
      }
      if (data.result.analysis['真实度级别']) {
        keyPoints.push(`真实度级别: ${data.result.analysis['真实度级别']}`)
      }
    }

    // 确保confidence是数字类型
    let confidence = 0
    if (data.result.truth_probability !== undefined) {
      confidence = parseFloat(data.result.truth_probability) * 100
    } else if (data.result.confidence !== undefined) {
      confidence = parseFloat(data.result.confidence)
    }

    return {
      status: 'complete',
      verdict: data.result.prediction || '未知结果',
      confidence: confidence,
      keyPoints: keyPoints.length > 0 ? keyPoints : ['未提供详细分析'],
      content: data.extracted_text || '无法提取文件内容'
    }
  } catch (error) {
    console.error('解析多模态检测结果出错:', error)
    return {
      status: 'error',
      verdict: '解析结果出错',
      confidence: 0,
      keyPoints: ['处理多模态检测结果时出错'],
      content: data.extracted_text || ''
    }
  }
}

// 修改文件结果摘要的显示
const formatConfidence = (result) => {
  if (!result || typeof result.confidence !== 'number') return '0.0'
  return result.confidence.toFixed(1)
}

// 新增：获取进度条状态
const getProgressStatus = (filename) => {
  const progress = fileProgress.value[filename] || 0
  if (progress === 0) return ''
  if (progress === 100) return 'success'
  if (isDetecting.value) return ''
  return 'exception'
}

// 新增：获取进度条颜色
const getProgressColor = (filename) => {
  const progress = fileProgress.value[filename] || 0
  if (progress < 40) return '#409eff'
  if (progress < 80) return '#e6a23c'
  return '#67c23a'
}

// 新增：获取结果标签类型
const getResultTagType = (result) => {
  return result.verdict?.includes('真实') ? 'success' : 'danger'
}

// 修改：监听选中文件变化
watch(selectedFileIndex, (newIndex) => {
  if (detectionResults.value[newIndex]) {
    detectionResult.value = detectionResults.value[newIndex]
    // 重新生成AI报告
    generateAIReport().catch(error => {
      console.error('切换文件时生成AI报告失败:', error)
      ElMessage.warning('生成AI分析报告失败，请稍后重试')
    })
  }
})

// 添加导出相关的状态和方法
const handleExport = (type) => {
  ElMessage.success(`导出${type === 'html' ? 'HTML' : 'PDF'}报告功能即将上线`)
  showExportMenu.value = false
}
</script>

<style lang="scss" scoped>
.detection-wrapper {
  height: 100%;

  .unified-detection {
    padding: 20px;
    height: calc(100vh - 80px);

    .el-row {
      height: 100%;

      .el-col {
        height: 100%;
        display: flex;
        flex-direction: column;
      }
    }

    .input-section {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .mode-selector {
        margin-bottom: 15px;
      }

      .text-input {
        margin-bottom: 15px;
      }

      .file-upload {
        margin-bottom: 15px;

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 20px 0;

          .upload-text {
            margin-top: 10px;
            text-align: center;

            .tip {
              font-size: 12px;
              color: #909399;
              margin-top: 5px;
            }
          }
        }

        .file-list {
          margin-top: 15px;
          border: 1px dashed #d9d9d9;
          border-radius: 4px;
          padding: 10px;
          background-color: #f8f8f8;
          max-height: 150px;
          overflow-y: auto;

          .selected-file-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #606266;
          }

          .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            border-bottom: 1px solid #ebeef5;

            &:last-child {
              border-bottom: none;
            }

            .file-info {
              display: flex;
              align-items: center;
              gap: 8px;
              max-width: 80%;

              .filename {
                font-size: 14px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }

              .filesize {
                font-size: 12px;
                color: #909399;
              }
            }
          }
        }
      }

      .detect-control {
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;

        .model-selector {
          .model-title {
            margin-bottom: 10px;
            font-weight: bold;
            color: #606266;
          }
        }

        .detect-button {
          margin-top: 10px;
          width: 100%;
          padding: 12px 0;
          font-size: 16px;
        }
      }

      .progress-section {
        margin-top: 20px;
        overflow-y: auto;
        max-height: 300px;
        padding-right: 10px;

        .file-progress-item {
          margin-bottom: 15px;
          padding: 10px;
          border: 1px solid #ebeef5;
          border-radius: 4px;
          background-color: #f8f8f8;

          .file-progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;

            .filename {
              font-size: 14px;
              color: #606266;
              flex: 1;
              margin-right: 10px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }

          .file-result-summary {
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 10px;

            .confidence {
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }
    }

    .result-section {
      height: 100%;

      .section-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #ebeef5;
      }

      .detection-result {
        .model-info {
          margin-bottom: 15px;

          .el-tag {
            font-size: 14px;
            padding: 8px 12px;
          }
        }

        .result-tag {
          margin: 15px 0;
          display: inline-block;
          padding: 8px 16px;
          font-size: 16px;
        }

        .confidence-meter {
          margin: 20px 0;

          .confidence-info {
            margin-top: 5px;
            text-align: right;
            font-size: 14px;
            color: #606266;
          }
        }

        .ai-report {
          margin-top: 20px;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
          overflow: hidden;

          .report-header {
            padding: 16px 20px;
            background: var(--el-color-primary-light-9);
            border-bottom: 1px solid var(--el-border-color-light);
            display: flex;
            justify-content: space-between;
            align-items: center;

            h3 {
              margin: 0;
              color: var(--el-color-primary);
              font-size: 18px;
              font-weight: 600;
            }
          }

          .report-content {
            padding: 20px;
          }

          .report-section {
            margin-bottom: 24px;
            background: var(--el-bg-color-page);
            border-radius: 6px;
            padding: 16px;
            border: 1px solid var(--el-border-color-lighter);

            &:last-child {
              margin-bottom: 0;
            }

            .section-header {
              display: flex;
              align-items: center;
              margin-bottom: 12px;

              .el-icon {
                margin-right: 8px;
                font-size: 20px;
                color: var(--el-color-primary);
              }

              h4 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--el-text-color-primary);
              }
            }

            .section-content {
              .report-text {
                font-size: 14px;
                line-height: 1.8;
                color: #606266;
                white-space: pre-wrap;
                padding: 16px;
                background: white;
                border-radius: 6px;
                border: 1px solid #ebeef5;

                /* Markdown 样式 */
                :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
                  margin-top: 16px;
                  margin-bottom: 12px;
                  font-weight: 600;
                  line-height: 1.4;
                }

                :deep(p) {
                  margin: 8px 0;
                  line-height: 1.8;
                }

                :deep(ul), :deep(ol) {
                  padding-left: 24px;
                  margin: 8px 0;
                }

                :deep(li) {
                  margin: 4px 0;
                }

                :deep(blockquote) {
                  margin: 8px 0;
                  padding: 8px 16px;
                  border-left: 4px solid #409eff;
                  background-color: #f8f9fa;
                  color: #666;
                }

                :deep(code) {
                  background-color: #f6f8fa;
                  padding: 2px 6px;
                  border-radius: 4px;
                  font-family: monospace;
                }

                :deep(pre) {
                  background-color: #f6f8fa;
                  padding: 12px;
                  border-radius: 6px;
                  overflow-x: auto;
                  margin: 8px 0;
                }

                :deep(table) {
                  border-collapse: collapse;
                  width: 100%;
                  margin: 8px 0;
                }

                :deep(th), :deep(td) {
                  border: 1px solid #ebeef5;
                  padding: 8px;
                  text-align: left;
                }

                :deep(th) {
                  background-color: #f8f9fa;
                }

                :deep(a) {
                  color: #409eff;
                  text-decoration: none;
                  &:hover {
                    text-decoration: underline;
                  }
                }

                :deep(hr) {
                  border: none;
                  border-top: 1px solid #ebeef5;
                  margin: 16px 0;
                }

                &::selection {
                  background: #409eff;
                  color: white;
                }
              }
            }
          }
        }

        .empty-result {
          padding: 30px 0;
          display: flex;
          justify-content: center;
        }
      }
    }
  }

  .file-progress-item {
    margin-bottom: 15px;
    padding: 10px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background-color: #f8f8f8;

    .file-progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .filename {
        font-size: 14px;
        color: #606266;
        flex: 1;
        margin-right: 10px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .file-result-summary {
      margin-top: 8px;
      display: flex;
      align-items: center;
      gap: 10px;

      .confidence {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .file-selector {
    margin-bottom: 20px;
  }

  .export-menu {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 10px;

    .el-button {
      width: 100%;
      justify-content: center;

      .el-icon {
        margin-right: 8px;
      }
    }
  }
}
// 修改AI报告样式
.ai-report {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
  overflow: hidden;
  background: #ffffff;

  .report-header {
    padding: 18px 24px;
    background: #f8fafc;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: space-between;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      font-weight: 600;
    }
  }

  .report-content {
    padding: 24px;
    max-height: 500px;
    overflow-y: auto;

    .report-section {
      margin-bottom: 28px;
      background: #f8fafc;
      border-radius: 8px;
      padding: 20px;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }

      .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;

        .el-icon {
          font-size: 24px;
          color: #409eff;
          margin-right: 12px;
        }

        h4 {
          margin: 0;
          font-size: 16px;
          color: #303133;
          font-weight: 500;
          position: relative;
          padding-left: 8px;

          &::before {
            content: "";
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 3px;
            height: 16px;
            background: #409eff;
            border-radius: 2px;
          }
        }
      }

      .section-content {
        .report-text {
          font-size: 14px;
          line-height: 1.8;
          color: #606266;
          white-space: pre-wrap;
          padding: 16px;
          background: white;
          border-radius: 6px;
          border: 1px solid #ebeef5;

          /* Markdown 样式 */
          :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
            margin-top: 16px;
            margin-bottom: 12px;
            font-weight: 600;
            line-height: 1.4;
          }

          :deep(p) {
            margin: 8px 0;
            line-height: 1.8;
          }

          :deep(ul), :deep(ol) {
            padding-left: 24px;
            margin: 8px 0;
          }

          :deep(li) {
            margin: 4px 0;
          }

          :deep(blockquote) {
            margin: 8px 0;
            padding: 8px 16px;
            border-left: 4px solid #409eff;
            background-color: #f8f9fa;
            color: #666;
          }

          :deep(code) {
            background-color: #f6f8fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
          }

          :deep(pre) {
            background-color: #f6f8fa;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
          }

          :deep(table) {
            border-collapse: collapse;
            width: 100%;
            margin: 8px 0;
          }

          :deep(th), :deep(td) {
            border: 1px solid #ebeef5;
            padding: 8px;
            text-align: left;
          }

          :deep(th) {
            background-color: #f8f9fa;
          }

          :deep(a) {
            color: #409eff;
            text-decoration: none;
            &:hover {
              text-decoration: underline;
            }
          }

          :deep(hr) {
            border: none;
            border-top: 1px solid #ebeef5;
            margin: 16px 0;
          }

          &::selection {
            background: #409eff;
            color: white;
          }
        }
      }
    }
  }
}
</style>
