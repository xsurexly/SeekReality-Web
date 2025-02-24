<template>
  <svg :class="svgClass" aria-hidden="true">
      <use :xlink:href="iconClassName" :fill="color" />
  </svg>
</template>


<script setup>
import { computed } from 'vue'
const props = defineProps({
  iconName: {
      type: String,
      required: true
  },
  className: {
      type: String,
      default: ''
  },
  color: {
      type: String,
      default: '#409eff'
  },
  size: {
      type: String,
      default: '16px'
  }
})
// 图标在 iconfont 中的名字
const iconClassName = computed(() => {
  return `#${props.iconName}`
})
// 给图标添加上类名
const svgClass = computed(() => {
  if (props.className) {
      return `svg-icon ${props.className}`
  }
  return 'svg-icon'
});
</script>


<style scoped>
.svg-icon {
  /* v-bind 是 Vue3 才支持的功能，可以将 CSS 的值与 js 的值绑定 */
  width: v-bind('props.size');
  height: v-bind('props.size');
  position: relative;
  fill: currentColor;
  vertical-align: -2px;
  height:20px;
  width: 20px;
}
</style>

