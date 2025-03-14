import axios from "axios";
import baseUrl from "./baseUrl.js";

const service = axios.create({
  baseURL: baseUrl,
  timeout: 30000, // 增加超时时间到 30 秒
  retries: 3,     // 添加重试次数
  retryDelay: 1000, // 重试间隔时间（毫秒）
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 添加重试配置
    config.retryCount = config.retryCount || 0;
    return config;
  },
  (error) => {
    console.log(error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const { config } = error;
    
    // 如果配置不存在，或者重试选项没有设置，返回 Promise.reject
    if (!config || !config.retries) {
      return Promise.reject(error);
    }
    
    // 设置重试计数器
    config.retryCount = config.retryCount || 0;
    
    // 检查是否已经达到最大重试次数
    if (config.retryCount >= config.retries) {
      return Promise.reject(error);
    }
    
    // 增加重试计数
    config.retryCount += 1;
    
    // 创建新的 Promise 来处理重试
    const backoff = new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, config.retryDelay || 1000);
    });
    
    // 等待延迟时间后重试
    await backoff;
    console.log(`Retrying request (${config.retryCount}/${config.retries}): ${config.url}`);
    
    // 返回新的请求
    return service(config);
  }
);

const get = function (url, options = {}) {
  // options默认值为空对象
  return new Promise((resolve, reject) => {
    service
      .get(url, options)
      .then((response) => {
        if (response && response.data) {
          resolve(response.data);
        } else {
          reject(new Error("No data received"));
        }
      })
      .catch((error) => {
        reject(error);
      });
  });
};

const post = function (url, data, options = {}) {
  return new Promise((resolve, reject) => {
    service
      .post(url, data, options)
      .then((response) => {
        if (response && response.data) {
          resolve(response.data);
        } else {
          reject(new Error("No data received"));
        }
      })
      .catch((error) => {
        reject(error);
      });
  });
};

export default {
  get,
  post,
};
