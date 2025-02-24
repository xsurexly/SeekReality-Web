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

    <!-- AI助手弹窗 -->
    <div v-if="aiOpen" class="ai-popup" :style="{ width: currentWidth + 'px' }">
      <div class="ai-popup-header">
        <span style="margin-top:5px">进行对话</span>
        <button @click="closeAI"><SvgIcon iconName="icon-guanbi" style="width:20px;height:20px"></SvgIcon></button>
      </div>
      <div class="ai-popup-content">
        <!-- AI助手的内容 -->
        <p>这里是AI助手的内容...</p>
      </div>
      <div class="resizer" @mousedown="startResize"></div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      aiOpen: false, // 控制AI助手是否显示
      isResizing: false,  // 用来判断是否正在拖动
      currentWidth: 400,  // 默认宽度
      offsetX: 0, // 鼠标点击时的相对位置
      offsetY: 0, // 鼠标点击时的相对位置
    };
  },
  methods: {
    openAI() {
      this.aiOpen = true; // 打开AI助手
    },
    closeAI() {
      this.aiOpen = false; // 关闭AI助手
    },
    startResize(event) {
      this.isResizing = true;

      // 记录鼠标初始位置和当前宽度
      this.initialMouseX = event.clientX;
      this.initialWidth = this.currentWidth;

      // 绑定鼠标移动和松开事件
      window.addEventListener('mousemove', this.resize);
      window.addEventListener('mouseup', this.stopResize);
    },

    resize(event) {
      if (!this.isResizing) return;

      const diff = event.clientX - this.initialMouseX;  // 鼠标移动的距离
      this.currentWidth = this.initialWidth + diff;  // 更新宽度

      // 限制宽度在一定范围内
      if (this.currentWidth < 200) this.currentWidth = 200;  // 最小宽度
      if (this.currentWidth > 800) this.currentWidth = 800;  // 最大宽度
    },

    stopResize() {
      this.isResizing = false;

      // 移除事件监听器
      window.removeEventListener('mousemove', this.resize);
      window.removeEventListener('mouseup', this.stopResize);
    }
  },
};
</script>

<style scoped>
.ai-icon {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width:60px;
  height:60px;
  cursor: pointer;
  z-index: 1000;
  background-color: #fff;
  box-shadow: -4px 0 10px rgba(0, 0, 0, 0.3);
  border-radius:60px;
}

.ai-popup {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 400px;  /* 默认宽度 */
  height: 100%;
  background-color: rgb(255, 255, 255);
  border-left: 3px solid #B0E4C8;
  box-shadow: -4px 0 10px rgba(0, 0, 0, 0.3);
  border-radius:10px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.resizer {
  position: absolute;
  top: 450px;
  left: 0;
  width: 4px;  /* 可调节的拖拽条宽度 */
  height: 5%;
  cursor: ew-resize;  /* 变为水平拖动箭头 */
  background-color: #ccc;
  border-radius:5px;
}

.resizer:hover{
  background-color: #007aff;
  position: absolute;
  top: 2px;
  left: 0;
  width: 3px;  /* 可调节的拖拽条宽度 */
  height: 99.5%;
  border-radius:5px;
}

.ai-popup-header {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #B0E4C8;
  color: black;
  font-weight: bold;
  border-radius:8px;
}

.ai-popup-header button {
  background-color: #B0E4C8;
  color: black;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius:10px;
}

.ai-popup-header button:hover {
  background-color: #B0E4C8;
}

.ai-popup-content {
  padding: 20px;
  overflow-y: auto;
  flex-grow: 1;
}
</style>
