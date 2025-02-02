<template>
  <div class="hamburger" @click="toggleMenu">
    <!-- 三条横线，使用动态绑定类来控制其样式 -->
    <div :class="['hamburger-line', 'line1', { active: isActive }]"></div>
    <div :class="['hamburger-line', 'line2', { active: isActive }]"></div>
    <div :class="['hamburger-line', 'line3', { active: isActive }]"></div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isActive: false, // 用来控制菜单状态
    };
  },
  methods: {
    toggleMenu() {
      this.isActive = !this.isActive;
      this.$emit('toggle-menu', this.isActive); // 将状态传递给父组件
    },
  },
};
</script>

<style scoped>
/* 作为按钮的容器，显示为纵向的3条横线 */
.hamburger {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 25px;
  cursor: pointer; /* 鼠标指针 */
  transition: all 0.3s ease; /* 动画效果 */
}

/* 每条横线的基础样式 */
.hamburger-line {
  height: 4px;
  width: 100%;
  background-color: black;
  border-radius: 10px; /* 圆角效果 */
  transition: all 0.3s ease; /* 动画效果 */
}

/* 动画效果 - 第一条线变成 45 度角 */
.line1.active {
  transform: rotate(45deg) translateY(6px);
}

/* 动画效果 - 第二条线消失 */
.line2.active {
  opacity: 0;
}

/* 动画效果 - 第三条线变成 -45 度角 */
.line3.active {
  transform: rotate(-45deg) translateY(-6px);
}
</style>
