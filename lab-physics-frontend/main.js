import { createSSRApp } from 'vue'
import App from './App.vue'

// 提供给 uni-app 的入口（HBuilderX/小程序等环境会调用）
export function createApp() {
  const app = createSSRApp(App)
  return { app }
}

// 纯 Vite H5 环境下自动挂载，避免出现空白页
// 当未定义 uni（非 uni-app 运行时）时，执行手动挂载
if (typeof window !== 'undefined' && typeof uni === 'undefined') {
  const { app } = createApp()
  app.mount('#app')
}