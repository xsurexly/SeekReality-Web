// src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // 从环境变量读取API地址
  timeout: 15000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在这里添加全局请求头
    // 例如添加token：
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers['Authorization'] = `Bearer ${token}`
    // }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 处理二进制数据（如文件下载）
    if (response.request.responseType === 'blob') {
      return response.data
    }

    const res = response.data
    
    // 根据业务状态码处理逻辑（这里假设状态码字段是code）
    if (res.code !== 200) {
      // 处理业务错误
      ElMessage({
        message: res.message || '业务错误',
        type: 'error',
        duration: 3 * 1000
      })
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    // 返回有效数据
    return res.data
  },
  error => {
    // 处理HTTP错误状态码
    let errorMessage = '请求失败'
    
    if (error.response) {
      switch (error.response.status) {
        case 400:
          errorMessage = '请求参数错误'
          break
        case 401:
          errorMessage = '登录已过期，请重新登录'
          // 这里可以跳转到登录页
          break
        case 403:
          errorMessage = '没有操作权限'
          break
        case 404:
          errorMessage = '资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = `未知错误 (${error.response.status})`
      }
    } else if (error.message.includes('timeout')) {
      errorMessage = '请求超时'
    } else if (error.message.includes('Network Error')) {
      errorMessage = '网络连接失败'
    }

    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 3 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service
