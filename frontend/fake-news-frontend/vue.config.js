const { defineConfig } = require('@vue/cli-service');
const AutoImport = require('unplugin-auto-import/webpack').default;
const Components = require('unplugin-vue-components/webpack').default;
const { ElementPlusResolver } = require('unplugin-vue-components/resolvers');

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      AutoImport({
        resolvers: [ElementPlusResolver()],
      }),
      Components({
        resolvers: [ElementPlusResolver()],
      }),
    ],
  },
  devServer: {
    port: 8080, // 明确指定端口号
    open: true,
    client: { // 将 overlay 移动到 client 对象中
      overlay: {
        warnings: false,
        errors: true
      }
    },
    proxy: {
      '/apis': {
        target: 'http://api.jisuapi.com', // 修复了 URL 的格式
        secure: false,
        changeOrigin: true,
        pathRewrite: { '^/apis': '' }
      }
    }
  },
});