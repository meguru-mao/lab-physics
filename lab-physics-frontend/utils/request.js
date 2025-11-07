// 统一请求封装：自动附加 JWT、统一错误提示
export function apiRequest({ url, method = 'GET', data = {}, header = {} }) {
  const token = uni.getStorageSync('token')
  const finalHeader = Object.assign({}, header)
  if (token) {
    finalHeader['Authorization'] = `Bearer ${token}`
  }
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method,
      data,
      header: finalHeader,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = (res.data && res.data.detail) || '请求错误'
          uni.showToast({ title: msg, icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      }
    })
  })
}
// API 基础地址：统一采用 127.0.0.1，避免引入 import.meta/env 导致小程序端编译器注入 require('url')
const API_BASE = uni.getStorageSync('API_BASE') || 'http://127.0.0.1:8000'

export { API_BASE }