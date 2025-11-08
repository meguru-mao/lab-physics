// 前端环境配置统一出口
// - ENV: 'dev' | 'prod'
// - API_BASE: 接口基础地址（优先级：运行时覆盖 -> 构建时注入 -> 默认值）

// 1) 环境名：默认根据 NODE_ENV 判定
const ENV = (typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'production') ? 'prod' : 'dev'

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
  // TODO: 将来接入云托管后替换为正式地址，或在 .env.production 中设置 VITE_API_BASE_URL
  prod: 'https://your-cloud-host-api.example.com'
}

// 最终导出：优先顺序为 运行时覆盖 -> 构建时注入 -> 默认值
export const API_BASE = runtimeOverride || injectedBase || DEFAULTS[ENV]
export const ENV_NAME = ENV
export const IS_DEV = ENV === 'dev'