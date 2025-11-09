// 统一请求封装：
// - dev：使用 uni.request + API_BASE
// - prod：使用微信云托管 wx.cloud.callContainer（仅在小程序端）
import { API_BASE, IS_PROD, CLOUD_ENV_ID, CLOUD_SERVICE_NAME } from './config.js'
export function apiRequest({ url, method = 'GET', data = {}, header = {} }) {
  const token = uni.getStorageSync('token')
  const finalHeader = Object.assign({}, header)
  if (token) {
    finalHeader['Authorization'] = `Bearer ${token}`
  }
  return new Promise((resolve, reject) => {
    // 生产：使用云托管（仅微信小程序端有效）
    // #ifdef MP-WEIXIN
    if (IS_PROD && typeof wx !== 'undefined' && wx.cloud && wx.cloud.callContainer) {
      const cloudHeader = Object.assign({}, finalHeader, {
        'X-WX-SERVICE': CLOUD_SERVICE_NAME,
      })
      // 兼容调用者传入完整 URL 的情况：提取路径部分作为云托管 path
      const pathOnly = (typeof url === 'string') ? url.replace(/^https?:\/\/[^/]+/, '') : '/'
      wx.cloud.callContainer({
        config: { env: CLOUD_ENV_ID },
        path: pathOnly, // 必须为 /api/... 路径
        header: cloudHeader,
        method,
        data,
        success: (res) => {
          const statusCode = res.statusCode || (res.result && res.result.statusCode) || 200
          let dataObj = res.data || res.result || {}
          // 云托管可能返回字符串形式的 JSON，需要兼容解析
          if (typeof dataObj === 'string') {
            try { dataObj = JSON.parse(dataObj) } catch (e) {}
          }
          if (statusCode >= 200 && statusCode < 300) {
            resolve(dataObj)
          } else {
            const msg = (dataObj && dataObj.detail) || '请求错误'
            uni.showToast({ title: msg, icon: 'none' })
            reject(res)
          }
        },
        fail: (err) => {
          uni.showToast({ title: '网络异常', icon: 'none' })
          reject(err)
        }
      })
      return
    }
    // #endif

    // 开发或非微信端：使用本地后端 API_BASE
    const fullUrl = url.startsWith('http') ? url : (API_BASE + url)
    uni.request({
      url: fullUrl,
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
// 对外仍然导出 API_BASE 与 IS_PROD，保持现有页面兼容
export { API_BASE, IS_PROD }