import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 本地纯 Vite 运行时的配置（不用于 HBuilderX）
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    open: false
  }
})