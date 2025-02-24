import axios from 'axios'

axios.defaults.baseURL = '/apis'

// 向极速数据免费新闻接口获取新闻频道
export function getNewChannel() {
  return new Promise((resolve, reject) => {
    axios.get('/news/channel?appkey=自己在极速数据上申请的appkey')
      .then(res => {
        resolve(res)
      }).catch(error => { reject(error) })
  })
}

// 向极速数据免费新闻接口获取新闻列表
export function getNewList(type) {
  return new Promise((resolve, reject) => {
    axios.get('/news/get?channel=' + type + '&start=0&num=30&appkey=自己在极速数据上申请的appkey')
      .then(res => {
        resolve(res)
      }).catch(error => { reject(error) })
  })
}

