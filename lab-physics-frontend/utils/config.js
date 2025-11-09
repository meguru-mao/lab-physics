// 前端环境配置统一出口
// 支持两种模式：
// - APP_ENV: 'dev' | 'prod'（运行时或构建时控制）
//   - dev：使用本地后端（API_BASE + uni.request）
//   - prod：使用微信云托管（wx.cloud.callContainer）
// - API_BASE: 本地后端基础地址（优先级：运行时覆盖 -> 构建时注入 -> 默认值）

// 1) 环境名：默认根据 NODE_ENV 判定
const NODE_ENV = (typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'production') ? 'prod' : 'dev'

// 2) 构建时注入（仅在 H5/Vite 编译模式下生效）。
//    使用 try/catch 与 typeof 判断，避免某些小程序编译器对 import.meta 的处理不兼容。
let injectedBase
try {
  injectedBase = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL)
    ? import.meta.env.VITE_API_BASE_URL
    : undefined
} catch (e) {
  injectedBase = undefined
}

// 3) 运行时临时覆盖：便于联调或在设置页中手动指定接口地址
const runtimeOverride = (typeof uni !== 'undefined') ? uni.getStorageSync('API_BASE') : ''

// 4) 默认值：dev 使用 localhost；prod 预留云托管地址（后续替换）
const DEFAULTS = {
  dev: 'http://localhost:8000',
  // 默认云托管外网地址（可在 .env.production 或运行时覆盖）
  prod: 'https://meguru-198464-5-1386089595.sh.run.tcloudbase.com'
}

// 最终导出：优先顺序为 运行时覆盖 -> 构建时注入 -> 默认值
export const API_BASE = runtimeOverride || injectedBase || DEFAULTS[NODE_ENV]

// 运行时 APP_ENV（优先级高于 NODE_ENV）：可在设置页或调试脚本中切换
const runtimeEnv = (typeof uni !== 'undefined') ? (uni.getStorageSync('APP_ENV') || '') : ''
let injectedEnv
try {
  injectedEnv = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_APP_ENV)
    ? String(import.meta.env.VITE_APP_ENV)
    : undefined
} catch (e) {
  injectedEnv = undefined
}
// 在微信小程序端默认使用云托管（prod），除非运行时或构建时显式覆盖
export const APP_ENV = (runtimeEnv || injectedEnv || (typeof wx !== 'undefined' ? 'prod' : NODE_ENV))
export const IS_DEV = APP_ENV === 'dev'
export const IS_PROD = APP_ENV === 'prod'

// 云托管配置（仅 prod 模式使用）
let injectedCloudEnvId, injectedCloudService
try {
  injectedCloudEnvId = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_CLOUD_ENV_ID) ? import.meta.env.VITE_CLOUD_ENV_ID : ''
  injectedCloudService = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_CLOUD_SERVICE_NAME) ? import.meta.env.VITE_CLOUD_SERVICE_NAME : ''
} catch (e) {
  injectedCloudEnvId = ''
  injectedCloudService = ''
}
const runtimeCloudEnvId = (typeof uni !== 'undefined') ? (uni.getStorageSync('CLOUD_ENV_ID') || '') : ''
const runtimeCloudService = (typeof uni !== 'undefined') ? (uni.getStorageSync('CLOUD_SERVICE_NAME') || '') : ''
export const CLOUD_ENV_ID = runtimeCloudEnvId || injectedCloudEnvId || 'prod-2gxc597293b6ef5d'
export const CLOUD_SERVICE_NAME = runtimeCloudService || injectedCloudService || 'meguru'