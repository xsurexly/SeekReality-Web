<template>
  <div class="text-detect">
    <div class="detect-container">
      <h1>虚假新闻检测</h1>

      <!-- 文本检测 -->
      <div class="text-section">
        <h2>文本检测</h2>
        <textarea v-model="text" placeholder="输入文本..."></textarea>
        <button @click="detectText">提交文本检测</button>
      </div>

      <!-- 文件检测 -->
      <div class="file-section">
        <h2>文件检测</h2>
        <input type="file" @change="handleFileChange" />
        <button @click="detectFile" :disabled="!file">提交文件检测</button>
      </div>

      <!-- 检测结果 -->
      <div v-if="result" class="result-section">
        <h2>检测结果</h2>
        <p>{{ result }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      text: '', // 文本输入内容
      file: null, // 上传的文件
      result: null, // 检测结果
    };
  },
  methods: {
    // 文本检测
    detectText() {
      axios
        .post('/api/text-detect', { text: this.text })
        .then((res) => {
          this.result = res.data.result;
        })
        .catch(() => alert('文本检测失败，请重试'));
    },
    // 文件改变处理
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    // 文件检测
    detectFile() {
      const formData = new FormData();
      formData.append('file', this.file);
      axios
        .post('/api/file-detect', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((res) => {
          this.result = res.data.result;
        })
        .catch(() => alert('文件检测失败，请重试'));
    },
  },
};
</script>

<style scoped>
/* 整体居中对齐 */
.text-detect {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #ffffff;
}

/* 检测容器样式 */
.detect-container {
  margin-top: -150px;
  background-color: #ffffff;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 400px;
  text-align: center;
}

/* 标题样式 */
h1 {
  color: #4caf50;
  margin-bottom: 20px;
}

h2 {
  color: #555;
  font-size: 1.2rem;
  margin-bottom: 15px;
}

/* 文本框样式 */
textarea {
  width: 100%;
  height: 80px;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 15px;
  box-sizing: border-box;
  resize: none;
}

/* 按钮样式 */
button {
  padding: 10px 15px;
  background-color: #4caf50;
  color: white;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #388e3c;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 文件输入框样式 */
input[type="file"] {
  margin: 15px 0;
  padding: 5px;
}

/* 检测结果样式 */
.result-section {
  margin-top: 20px;
  background-color: #f1f8e9;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.result-section p {
  font-size: 14px;
  color: #333;
}

/* 响应式支持 */
@media (max-width: 450px) {
  .detect-container {
    width: 90%;
    padding: 20px;
  }

  textarea {
    height: 60px;
  }
}
</style>
