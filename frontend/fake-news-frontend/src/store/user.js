import axios from 'axios';
import urlData from "../api_list/index";  // 确保urlData.getUserAvatar指向正确的接口

const app = {
  state: {
    avatar: '', // 存储头像的状态
  },

  getters: {
    // 可以添加对头像的处理，比如返回默认头像等
    getAvatar: (state) => state.avatar,
  },

  mutations: {
    // 更新头像
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar;
    },
  },

  actions: {
    // 获取头像图片并转换为 Base64
    async getFileImg({ commit, state }, avatar) {
      try {
        const response = await axios({
          url: urlData.getUserAvatar,  // 假设这是获取头像的接口
          method: 'post',
          data: { filePath: avatar }, // 向后端传递文件路径或其他需要的参数
          responseType: 'arraybuffer', // 以字节流的格式返回
          headers: {
            rtoken: localStorage.getItem("rtoken"), // 如果有 token，需要附加在请求头
          },
        });

        // 将字节流转换为 Base64
        const base64 = "data:image/png;base64," + btoa(
          new Uint8Array(response.data)
            .reduce((data, byte) => data + String.fromCharCode(byte), "")
        );

        // 提交 mutation 更新头像
        commit("SET_AVATAR", base64);

        // 返回 base64 字符串
        return base64;
      } catch (error) {
        console.error("获取头像失败:", error);
        return null;
      }
    },
  },
};

export default app;
