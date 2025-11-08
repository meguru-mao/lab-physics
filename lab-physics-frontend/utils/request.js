// 统一请求封装：自动附加 JWT、统一错误提示
import { API_BASE } from './config.js'
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
// 对外仍然导出 API_BASE，保持现有页面兼容
export { API_BASE }