const { defineConfig } = require('@vue/cli-service');
const AutoImport = require('unplugin-auto-import/webpack').default;
const Components = require('unplugin-vue-components/webpack').default;
const { ElementPlusResolver } = require('unplugin-vue-components/resolvers');

module.exports = defineConfig({
  transpileDependencies: true, // 转译 node_modules 中的依赖
  productionSourceMap: true,
  configureWebpack: {
    plugins: [
      AutoImport({
        resolvers: [ElementPlusResolver()], // 自动导入 Element Plus 相关 API
      }),
      Components({
        resolvers: [ElementPlusResolver()], // 自动导入 Element Plus 组件
      }),
    ],
  },
  devServer: {
    port: 5000, // 开发服务器端口
    open: true, // 启动后自动打开浏览器
    client: {
      overlay: {
        warnings: false, // 禁用警告覆盖层
        errors: true, // 启用错误覆盖层
      },
    },
    proxy: {
      '/apis': {
        target: 'http://localhost:5000', // 代理目标地址
        changeOrigin: true, // 修改请求头中的 Origin
        pathRewrite: { '^/apis': '' }, // 重写路径
      },
    },
  }
});
