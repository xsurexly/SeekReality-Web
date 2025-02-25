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
        <span style="margin-top:5px">进行对话</span>
        <button @click="closeAI">
          <SvgIcon iconName="icon-guanbi" style="width:20px;height:20px"></SvgIcon>
        </button>
      </div>
      <!-- 聊天内容区域 -->
      <div class="ai-popup-content" v-show="!isCollapsed">
        <!-- 问答区域 -->
        <div class="chat-container">
          <div class="messages-container">
            <div v-for="(msg, index) in messages" :key="index" class="message-group">
              <!-- 用户消息 -->
              <div class="user-message">
                <div class="avatar">
                  <i class="fas fa-user"></i>
                </div>
                <div class="message-content">{{ msg.user }}</div>
              </div>

              <!-- 助手回复 -->
              <div class="assistant-message">
                <div class="avatar">
                  <i class="fas fa-robot"></i>
                </div>
                <div class="message-content" v-html="formatResponse(msg.assistant)"></div>
              </div>
            </div>
          </div>
        </div>
        <!-- 输入区域 -->
        <!-- 文本输入+上传文件按钮 -->
        <div class="input-section">
          <textarea
            v-model="userMessage"
            @keyup.enter="sendMessage"
            placeholder="请输入需要分析的新闻内容..."
            :disabled="loading"
            rows="3"
          ></textarea>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div class="upload-section">
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
        </div>
      </div>
      <!-- 调整滚动条 -->
      <div class="resizer" @mousedown="startResize"></div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
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

    // 聊天相关状态
    const messages = ref([]);
    const userMessage = ref('');
    const loading = ref(false);
    const error = ref('');
    const fileInput = ref(null);
    const selectedFile = ref(null);

    // AI助手控制方法
    const openAI = () => {
      aiOpen.value = true;
    };

    const closeAI = () => {
      aiOpen.value = false;
    };

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value;
    };

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
      currentWidth.value = initialWidth.value + diff;
      if (currentWidth.value < 300) currentWidth.value = 300;
      if (currentWidth.value > 800) currentWidth.value = 800;
    };

    const stopResize = () => {
      isResizing.value = false;
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResize);
    };

    // 聊天相关方法
    const formatResponse = (response) => {
      if (!response) return '';
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
            .replace(/详细分析：\n/, '')
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

    const triggerFileUpload = () => {
      fileInput.value.click();
    };

    const handleFileUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      selectedFile.value = file;
      loading.value = true;
      error.value = '';

      try {
        const formData = new FormData();
        formData.append('file', file);

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

    const sendMessage = async () => {
      if (!userMessage.value || loading.value) return;

      loading.value = true;
      error.value = '';

      try {
        messages.value.push({ user: userMessage.value, assistant: '正在分析中...' });
        const response = await fetch('http://localhost:5000/aihelper/talk', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage.value }),
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
        userMessage.value = '';
      }
    };

    return {
      // AI助手状态
      aiOpen,
      isCollapsed,
      currentWidth,
      offsetX,
      offsetY,

      // AI助手方法
      openAI,
      closeAI,
      toggleCollapse,
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
      sendMessage
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
  margin-bottom: 16px;
}

.user-message, .assistant-message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar i {
  color: white;
  font-size: 16px;
}

.message-content {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.user-message .message-content {
  background-color: #10B981;
  color: white;
  border-top-right-radius: 4px;
  margin-left: auto;
}

.assistant-message .message-content {
  background-color: #ffffff;
  border-top-left-radius: 4px;
  color: #374151;
}

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
</style>
