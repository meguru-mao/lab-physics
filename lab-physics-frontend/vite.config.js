// HBuilderX 编译使用其内置的 Vite/Uni 依赖，这里保持空配置，避免版本不兼容
import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

// 兼容不同打包器的导出形式：有的环境返回函数，需要调用；有的环境返回已生成的插件对象
const uniPlugin = typeof uni === 'function'
  ? uni()
  : (uni && typeof uni.default === 'function' ? uni.default() : uni)

export default defineConfig({
  plugins: [uniPlugin]
})