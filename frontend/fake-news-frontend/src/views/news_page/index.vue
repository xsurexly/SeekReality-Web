<template>
  <div class="home-container">
    
    <el-row>
      <el-col :lg="12">
        <h2>项目说明</h2>
        <p>这是虚假信息检测系统首页</p>
      </el-col>
    </el-row>
  </div>
</template>


<style lang="scss" scoped>
.channel-box {
  width: 100%;
  padding: 0 20px;
  height: 46px;
  position: fixed;
  align-items: center;
  top: 1.2rem;
  font-size: 18px;
  letter-spacing: 3px;
  background-color: rgb(252, 248, 248);
  .channel-list {
    width: 100%;
    height: 100%;
    overflow: hidden;
    position: relative;
    margin-top: 0.2rem;
    ul {
      transition-duration: 0.3s;
      position: absolute;
      top: 0px;
      left: 0px;
      margin: 0;
      padding: 0;
      display: flex;
      flex-wrap: nowrap;
      li {
        white-space: nowrap;
        display: inline-block;
        white-space: nowrap;
        padding: 0 10px;
      }
      li:first-child {
        padding-left: 0;
      }
      li:last-child {
        padding-right: 0;
      }
    }
    .channel {
      cursor: pointer;
      display: inline-block;
      height: 28px;
      line-height: 28px;
      transition: border-color 0.2s;
      &:hover {
        color: #e72521;
      }
    }
    .channel-active {
      color: #e72521;
    }
  }
  .icon-lf {
    cursor: pointer;
    line-height: 30px;
    position: absolute;
    left: 5px;
    top: 6px;
  }
  .icon-rt {
    line-height: 30px;
    cursor: pointer;
    position: absolute;
    right: 5px;
    top: 6px;
  }
}
</style>

