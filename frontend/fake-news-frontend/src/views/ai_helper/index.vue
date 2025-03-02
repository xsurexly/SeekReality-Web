<template>
  <div>
    <!-- AI助手图标 -->
    <div
      v-if="!aiOpen"
      class="ai-icon"
      @mousedown="startDrag"
      ref="aiIcon"
      @click="openAI"
    >
      <SvgIcon iconName="icon-liaotian" style="width:30px;height:30px;margin-top:15px;margin-left:15px"></SvgIcon>
    </div>

    <!-- AI助手区域 -->
    <div v-if="aiOpen" class="ai-popup" :style="{ width: currentWidth + 'px' }">
      <!-- 最上面的指示 -->
      <div class="ai-popup-header">
        <span style="margin-top:5px">AI智能助手</span>
        <button @click="closeAI">
          <SvgIcon iconName="icon-guanbi" style="width:20px;height:20px"></SvgIcon>
        </button>
      </div>
      <!-- 聊天内容区域 -->
      <div class="ai-popup-content" v-show="!isCollapsed">
        <!-- 对话模式选择 -->
        <div class="conversation-mode">
          <label class="mode-label">
            <input type="radio" v-model="conversationMode" value="chat" /> 普通对话
          </label>
          <label class="mode-label">
            <input type="radio" v-model="conversationMode" value="analysis" /> 新闻分析
          </label>
        </div>

        <!-- 模式说明 -->
        <div class="mode-description">
          <p v-if="conversationMode === 'chat'">
            当前模式：普通对话 - 可以进行日常交谈和问答
          </p>
          <p v-else>
            当前模式：新闻分析 - 输入新闻内容，AI将帮助分析其真实性
          </p>
        </div>

        <!-- 问答区域 -->
        <div class="chat-container">
          <div class="messages-container" ref="messagesContainer">
            <div v-for="(msg, index) in messages" :key="index" class="message-group">
              <!-- 用户消息 -->
              <div class="user-message">
                <div class="message-content">{{ msg.user }}</div>
                <div class="avatar">
                  <i class="fas fa-user"></i>
                </div>
              </div>

              <!-- 助手回复 -->
              <div class="assistant-message">
                <div class="avatar">
                  <i :class="conversationMode === 'analysis' ? 'fas fa-search' : 'fas fa-robot'"></i>
                </div>
                <div class="message-content">
                  <div v-if="msg.assistant === '正在思考中...' || msg.assistant === '正在分析中...'" class="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <div v-else>
                    <div v-if="conversationMode === 'analysis' && msg.assistant.includes('真实性评分')" class="analysis-report">
                      <div class="report-header">
                        <div class="report-title">
                          <h2>新闻真实性分析报告</h2>
                          <span class="report-subtitle">AI智能分析结果</span>
                        </div>
                        <div class="report-actions">
                          <div class="export-dropdown">
                            <button class="export-btn" @click="toggleExportMenu">
                              <i class="fas fa-file-export"></i>
                              导出报告
                              <i class="fas fa-chevron-down ml-2"></i>
                            </button>
                            <div class="export-menu" v-if="showExportMenu">
                              <button class="export-option" @click="exportReport(msg.assistant, 'html')">
                                <i class="fas fa-file-code"></i>
                                导出为HTML
                              </button>
                              <button class="export-option" @click="exportReport(msg.assistant, 'pdf')">
                                <i class="fas fa-file-pdf"></i>
                                导出为PDF
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="report-content" v-html="formatResponse(msg.assistant)"></div>
                    </div>
                    <div v-else v-html="formatResponse(msg.assistant)"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-section">
          <textarea
            v-model="userMessage"
            @keyup.enter.exact="sendMessage"
            @keyup.ctrl.enter="handleNewLine"
            :placeholder="getPlaceholder"
            :disabled="loading"
            rows="3"
          ></textarea>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div class="button-group">
            <div class="upload-section" v-if="conversationMode === 'analysis'">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileUpload"
                accept=".docx,.pdf"
                style="display: none"
              />
              <button @click="triggerFileUpload" :disabled="loading" class="upload-button">
                <i class="fas fa-file-upload"></i>
                上传文件
              </button>
              <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
            </div>
            <button
              @click="sendMessage"
              :disabled="loading || !userMessage.trim()"
              class="send-button"
            >
              <i class="fas fa-paper-plane"></i>
              发送
            </button>
          </div>
        </div>
      </div>
      <!-- 调整滚动条 -->
      <div class="resizer" @mousedown="startResize"></div>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick, computed, onMounted } from 'vue';

export default {
  setup() {
    // AI助手状态相关
    const aiOpen = ref(false);
    const isCollapsed = ref(false);
    const isResizing = ref(false);
    const currentWidth = ref(400);
    const offsetX = ref(0);
    const offsetY = ref(0);
    const initialMouseX = ref(0);
    const initialWidth = ref(0);
    const messagesContainer = ref(null);

    // 聊天相关状态
    const messages = ref([]);
    const userMessage = ref('');
    const loading = ref(false);
    const error = ref('');
    const fileInput = ref(null);
    const selectedFile = ref(null);
    const conversationMode = ref('chat'); // 默认为普通对话模式
    const showExportMenu = ref(false);

    // 计算属性
    const getPlaceholder = computed(() => {
      return conversationMode.value === 'chat'
        ? '输入您想说的话，按Enter发送，Ctrl+Enter换行...'
        : '请输入需要分析的新闻内容，或上传新闻文件...';
    });

    // 监听消息变化，自动滚动到底部
    watch(() => messages.value.length, async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    });

    // AI助手控制方法
    const openAI = () => {
      aiOpen.value = true;
      // 添加欢迎消息
      if (messages.value.length === 0) {
        messages.value.push({
          user: '你好',
          assistant: '你好！我是AI助手。我可以进行日常对话，也可以帮你分析新闻的真实性。请选择合适的对话模式开始我们的交谈。'
        });
      }
    };

    const closeAI = () => {
      aiOpen.value = false;
    };

    const handleNewLine = (event) => {
      event.preventDefault();
      userMessage.value += '\n';
    };

    // 调整大小相关方法
    const startResize = (event) => {
      isResizing.value = true;
      initialMouseX.value = event.clientX;
      initialWidth.value = currentWidth.value;
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResize);
    };

    const resize = (event) => {
      if (!isResizing.value) return;
      const diff = event.clientX - initialMouseX.value;
      currentWidth.value = Math.max(300, Math.min(800, initialWidth.value + diff));
    };

    const stopResize = () => {
      isResizing.value = false;
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResize);
    };

    // 格式化响应
    const formatResponse = (response) => {
      if (!response) return '';
      if (conversationMode.value === 'chat') {
        return `<div class="chat-response">${response}</div>`;
      }

      const sections = response.split(/(?=真实性评分：|详细分析：|相关事实依据：|总结：)/g);
      const formattedSections = sections.map(section => {
        if (section.startsWith('真实性评分：')) {
          return section.replace(
            /真实性评分：(.*)/,
            '<div class="score-section"><div class="score-content"><span class="score-label">真实性评分</span><span class="score">$1</span></div></div>'
          );
        }

        if (section.startsWith('详细分析：')) {
          const analysisContent = section
            .replace(/详细分析：\n/, ' ')
            .split(/(?=\d+\.\s)/g)
            .filter(item => item.trim())
            .map(item => `<div class="analysis-item">${item.trim()}</div>`)
            .join('');

          return `<div class="analysis-block">
            <h3 class="section-title"><i class="fas fa-search"></i>详细分析</h3>
            ${analysisContent}
          </div>`;
        }

        if (section.startsWith('相关事实依据：')) {
          return section
            .replace(/相关事实依据：\n/, '<div class="evidence-block"><h3 class="section-title"><i class="fas fa-check-circle"></i>相关事实依据</h3>')
            .replace(/- (.*?)(?=\n|$)/g, '<div class="evidence-item">$1</div>')
            + '</div>';
        }

        if (section.startsWith('总结：')) {
          return section
            .replace(
              /总结：\n/,
              '<div class="summary-block"><h3 class="section-title"><i class="fas fa-flag"></i>总结</h3>'
            )
            .replace(/\n(.*?)(?=\n|$)/g, '<div class="summary-content">$1</div>')
            + '</div>';
        }

        return section;
      });

      return formattedSections.join('');
    };

    // 文件上传相关方法
    const triggerFileUpload = () => {
      fileInput.value.click();
    };

    // 添加获取用户信息的函数
    const getUserInfo = () => {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          return { username: '未登录用户' };
        }
        const userInfo = JSON.parse(userStr);
        return {
          username: userInfo.username || '未登录用户'
        };
      } catch (e) {
        console.error('解析用户信息失败:', e);
        return { username: '未登录用户' };
      }
    };

    // 修改发送消息的函数
    const sendMessage = async () => {
      if (!userMessage.value.trim() || loading.value) return;

      loading.value = true;
      error.value = '';
      const currentMessage = userMessage.value.trim();
      userMessage.value = '';

      // 获取用户信息
      const userInfo = getUserInfo();

      try {
        messages.value.push({ user: currentMessage, assistant: '正在思考中...' });

        const response = await fetch('http://localhost:5000/aihelper/talk', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: currentMessage,
            conversation_mode: conversationMode.value,
            needs_analysis: conversationMode.value === 'analysis',
            username: userInfo.username  // 添加用户名
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.response) {
          messages.value[messages.value.length - 1].assistant = data.response;
        } else {
          throw new Error(data.error || '未知错误');
        }
      } catch (e) {
        error.value = `错误: ${e.message}`;
        if (messages.value.length > 0) {
          messages.value[messages.value.length - 1].assistant = '处理过程中出现错误，请重试';
        }
      } finally {
        loading.value = false;
      }
    };

    // 修改文件上传函数
    const handleFileUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      selectedFile.value = file;
      loading.value = true;
      error.value = '';

      // 获取用户信息
      const userInfo = getUserInfo();

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', userInfo.username);  // 添加用户名

        messages.value.push({ user: `文件：${file.name}`, assistant: '正在分析中...' });

        const response = await fetch('http://localhost:5000/aihelper/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.response) {
          messages.value[messages.value.length - 1].assistant = data.response;
        } else {
          throw new Error(data.error || '未知错误');
        }
      } catch (e) {
        error.value = `错误: ${e.message}`;
        if (messages.value.length > 0) {
          messages.value[messages.value.length - 1].assistant = '分析过程中出现错误，请重试';
        }
      } finally {
        loading.value = false;
        selectedFile.value = null;
        event.target.value = '';
      }
    };

    // 添加导出报告方法
    const toggleExportMenu = () => {
      showExportMenu.value = !showExportMenu.value;
    };

    // Close export menu when clicking outside
    onMounted(() => {
      document.addEventListener('click', (event) => {
        const dropdown = document.querySelector('.export-dropdown');
        if (dropdown && !dropdown.contains(event.target)) {
          showExportMenu.value = false;
        }
      });
    });

    const exportReport = async (content, format) => {
      showExportMenu.value = false;

      if (format === 'html') {
        // HTML export logic
        const reportHTML = `
          <!DOCTYPE html>
          <html>
          <head>
            <meta charset="UTF-8">
            <title>新闻真实性分析报告</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
              }
              .report-header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
                color: white;
                border-radius: 10px;
              }
              .score-section {
                background: #EFF6FF;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #93C5FD;
              }
              .score-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
              }
              .score {
                font-size: 32px;
                font-weight: bold;
                color: #2563EB;
              }
              .analysis-block, .evidence-block, .summary-block {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #E5E7EB;
              }
              .section-title {
                color: #2563EB;
                font-size: 20px;
                margin-bottom: 15px;
              }
              .analysis-item {
                margin-bottom: 10px;
                padding: 10px;
                background: #F8FAFC;
                border-radius: 5px;
              }
              .evidence-item {
                margin-bottom: 10px;
                padding: 10px;
                background: #EFF6FF;
                border-left: 3px solid #3B82F6;
                border-radius: 5px;
              }
              .summary-content {
                padding: 15px;
                background: #F8FAFC;
                border-radius: 5px;
              }
              .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #E5E7EB;
                color: #6B7280;
              }
            </style>
          </head>
          <body>
            <div class="report-header">
              <h1>新闻真实性分析报告</h1>
              <p>生成时间：${new Date().toLocaleString()}</p>
            </div>
            ${formatResponse(content)}
            <div class="footer">
              <p>由AI助手生成的新闻真实性分析报告</p>
            </div>
          </body>
          </html>
        `;

        const blob = new Blob([reportHTML], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `新闻分析报告_${new Date().toISOString().slice(0,10)}.html`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else if (format === 'pdf') {
        try {
          // Convert content to PDF format
          const element = document.createElement('div');
          element.innerHTML = formatResponse(content);

          const opt = {
            margin: 1,
            filename: `新闻分析报告_${new Date().toISOString().slice(0,10)}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
          };

          // Use html2pdf library
          const html2pdf = (await import('html2pdf.js')).default;
          await html2pdf().set(opt).from(element).save();
        } catch (error) {
          console.error('PDF generation failed:', error);
          // Show error message to user
          error.value = '生成PDF失败，请稍后重试';
        }
      }
    };

    return {
      // AI助手状态
      aiOpen,
      isCollapsed,
      currentWidth,
      offsetX,
      offsetY,
      messagesContainer,

      // AI助手方法
      openAI,
      closeAI,
      startResize,
      stopResize,
      resize,

      // 聊天相关
      messages,
      userMessage,
      loading,
      error,
      fileInput,
      selectedFile,
      formatResponse,
      triggerFileUpload,
      handleFileUpload,
      sendMessage,
      handleNewLine,
      getPlaceholder,

      // 对话模式
      conversationMode,
      exportReport,

      // Export menu
      showExportMenu,
      toggleExportMenu,
    };
  }
};
</script>

<style scoped>
/* AI助手图标 */
.ai-icon {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  cursor: pointer;
  z-index: 1000;
  background-color: #fff;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  transition: background-color 0.3s;
}

.ai-icon:hover {
  background-color: #f0f0f0;
}

/* AI助手弹窗 */
.ai-popup {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh; /* 竖向铺满 */
  width: 400px;  /* 默认宽度 */
  max-width: 90vw; /* 最大宽度 */
  min-width: 300px; /* 最小宽度 */
  background-color: #ffffff;
  border-left: 3px solid #10B981;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  transition: width 0.3s;
  resize: horizontal; /* 允许横向调整大小 */
}

.ai-popup-header {
  padding: 20px;
  background-color: #10B981;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.ai-popup-header button {
  background-color: #B0E4C8;
  color: black;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.ai-popup-header button:hover {
  background-color: #A0D3B8;
}

.ai-popup-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.conversation-mode {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #F9FAFB;
  border-radius: 8px;
  margin-bottom: 10px; /* 与输入区域保持间距 */
}

.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: #E5E7EB;
  border-radius: 4px;
}

.message-group {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-message {
  display: flex;
  justify-content: flex-end; /* 将内容靠右对齐 */
  align-items: flex-start;
  gap: 12px;
  padding: 0 8px;
  margin-left: auto; /* 整体靠右 */
  width: 100%; /* 确保有足够的空间 */
}

.assistant-message {
  display: flex;
  justify-content: flex-start; /* 将内容靠左对齐 */
  align-items: flex-start;
  gap: 12px;
  padding: 0 8px;
  margin-right: auto; /* 整体靠左 */
  width: 100%;
}

.avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--chat-gradient, linear-gradient(135deg, #10B981 0%, #059669 100%));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
}

.avatar i {
  color: white;
  font-size: 18px;
}

.message-content {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  max-width: 70%; /* 限制消息内容的最大宽度 */
}

.user-message .message-content {
  background: var(--chat-gradient, linear-gradient(135deg, #10B981 0%, #059669 100%));
  color: white;
  border-top-right-radius: 4px;
  margin-right: 0; /* 移除右边距 */
}

.assistant-message .message-content {
  background: white;
  border: 1px solid var(--neutral-200, #E5E7EB);
  border-top-left-radius: 4px;
  margin-left: 0; /* 移除左边距 */
  color: var(--neutral-800, #1F2937);
}

.user-message .message-content::after {
  content: '';
  position: absolute;
  right: -8px;
  top: 14px;
  width: 0;
  height: 0;
  border-left: 8px solid var(--chat-primary, #10B981);
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.assistant-message .message-content::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 14px;
  width: 0;
  height: 0;
  border-right: 8px solid var(--neutral-200, #E5E7EB);
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}

.analysis-mode .user-message .message-content {
  background: var(--analysis-gradient, linear-gradient(135deg, #3B82F6 0%, #2563EB 100%));
}

.analysis-mode .user-message .message-content::after {
  border-left-color: var(--analysis-primary, #3B82F6);
}

.analysis-mode .avatar {
  background: var(--analysis-gradient, linear-gradient(135deg, #3B82F6 0%, #2563EB 100%));
}

/* 加载动画 */
.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
}

.typing span {
  width: 8px;
  height: 8px;
  background: var(--neutral-400, #9CA3AF);
  border-radius: 50%;
  display: inline-block;
  animation: typing 1s infinite;
}

@keyframes typing {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
  100% { transform: translateY(0px); }
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

/* 输入区域 */
.input-section {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  gap: 10px; /* 增加间距 */
  position: relative; /* 使上传按钮相对定位 */
}

.upload-section {
  display: flex;
  align-items: center;
}

.upload-button {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  background-color: #3B82F6;
  color: white;
  cursor: pointer;
  transition: transform 0.2s, filter 0.2s;
}

.upload-button:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

textarea {
  flex: 1; /* 使文本框填满剩余空间 */
  padding: 12px;
  border: 2px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  min-height: 80px;
  resize: none; /* 禁止调整大小 */
}

textarea:focus {
  outline: none;
  border-color: #10B981;
  background-color: #f9f9f9;
}

.error-message {
  color: #DC2626;
  font-size: 12px;
  padding: 8px;
  background-color: #FEF2F2;
  border-radius: 6px;
  border-left: 3px solid #EF4444;
  margin-top: 8px;
}

/* 调整大小拖拽条 */
/* 居中，比较小，有交互 */
.resizer {
  position: absolute;
  top: 50%; /* 垂直居中 */
  left: -10px; /* 固定左侧位置 */
  width: 10px; /* 固定宽度 */
  height: 10%; /* 高度为容器的 10% */
  background-color: #007aff;
  border-radius: 5px;
  cursor: ew-resize;
  transition: background-color 0.3s, transform 0.3s;
  transform: translateY(-50%); /* 垂直居中 */
}

.resizer:hover {
  background-color: #005fcc;
  transform: scale(1.2) translateY(-50%); /* 悬停时放大并保持居中 */
}

/* 响应式调整 */
@media (max-width: 768px) {
  .ai-popup {
    width: 100% !important;
    height: 100% !important;
    right: 0;
    left: 0;
    border-radius: 0; /* 去掉圆角 */
  }

  .chat-container {
    padding: 16px;
  }

  .messages-container {
    padding: 12px;
  }

  .message-content {
    max-width: 90%;
  }

  .input-section {
    flex-direction: column;
    gap: 10px;
  }

  textarea {
    width: 100%;
  }

  .upload-button {
    width: 100%;
  }
}

.mode-label {
  padding: 8px 16px;
  border-radius: 20px;
  background-color: #f3f4f6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-label:hover {
  background-color: #e5e7eb;
}

.mode-label input[type="radio"] {
  margin-right: 8px;
}

.mode-description {
  margin: 10px 0;
  padding: 10px;
  background-color: #f8fafc;
  border-radius: 8px;
  font-size: 14px;
  color: #64748b;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.send-button {
  padding: 10px 20px;
  border-radius: 8px;
  background-color: #10B981;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.send-button:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
}

.send-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.send-button i {
  font-size: 14px;
}

.chat-response {
  white-space: pre-wrap;
  word-break: break-word;
}

/* 分析结果样式 */
.score-section {
  background-color: #f0fdf4;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.score-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.score-label {
  font-weight: 600;
  color: #059669;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: #10B981;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: #10B981;
}

.analysis-block, .evidence-block, .summary-block {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.analysis-item {
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f8fafc;
  border-radius: 4px;
}

.evidence-item {
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f0fdf4;
  border-radius: 4px;
  border-left: 3px solid #10B981;
}

.summary-content {
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 4px;
  color: #374151;
  font-weight: 500;
}

/* Add new styles for the analysis report */
.analysis-report {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.report-header {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  border-radius: 12px 12px 0 0;
}

.report-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.report-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.report-actions {
  display: flex;
  gap: 12px;
}

.export-dropdown {
  position: relative;
  display: inline-block;
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 8px;
  min-width: 180px;
  z-index: 1000;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.export-option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  color: #1F2937;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.export-option:hover {
  background: #F3F4F6;
  color: #2563EB;
}

.export-option i {
  font-size: 16px;
  color: #2563EB;
}

.ml-2 {
  margin-left: 8px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn i.fa-chevron-down {
  font-size: 12px;
  transition: transform 0.2s ease;
}

.export-dropdown:hover .export-btn i.fa-chevron-down {
  transform: rotate(180deg);
}

.history-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  width: 100%;
  padding: 0 4px;
}

.history-header h1 {
  font-size: 24px;
  color: #1F2937;
  margin: 0;
  text-align: center;
}

.search-bar {
  position: relative;
  width: 400px;
  max-width: 90%;
  margin: 0 auto;
}

.search-bar input {
  width: 100%;
  padding: 10px 36px 10px 16px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: white;
  box-sizing: border-box;
}

.search-bar input:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.search-bar i {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  pointer-events: none;
}

@media (max-width: 768px) {
  .history-header {
    padding: 0 8px;
    gap: 12px;
  }

  .history-header h1 {
    font-size: 20px;
  }

  .search-bar {
    width: 100%;
  }
}
</style>
