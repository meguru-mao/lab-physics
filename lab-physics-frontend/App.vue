<script>
  import { IS_PROD, CLOUD_ENV_ID } from './utils/config.js'
  import { apiRequest } from './utils/request.js'
  export default {
    onLaunch: function() {
      console.log('App Launch')
      // 仅在微信小程序端初始化云托管
      // #ifdef MP-WEIXIN
      try {
        if (IS_PROD && typeof wx !== 'undefined' && wx.cloud && wx.cloud.init) {
          wx.cloud.init({ env: CLOUD_ENV_ID })
          console.log('wx.cloud inited with env:', CLOUD_ENV_ID)
        }
      } catch (e) {
        console.warn('wx.cloud init failed:', e)
      }
      // #endif

      // 后端预热：在应用启动时主动触发一次 /api/ping
      // 目的：云托管环境下确保容器启动、执行后端的自动建表逻辑
      try {
        apiRequest({ url: '/api/ping', method: 'GET' })
          .then(() => console.log('backend warm-up success'))
          .catch((err) => console.warn('backend warm-up failed', err))
      } catch (e) {
        console.warn('warm-up error:', e)
      }
    },
    onShow: function() {
      console.log('App Show')
    },
    onHide: function() {
      console.log('App Hide')
    }
  }
</script>

<style>
  /* 全局表单与栅格样式，解决部分设备上输入框宽度溢出或与其他输入框重叠的问题 */
  .page { box-sizing: border-box; max-width: 750rpx; margin: 0 auto; }
  .section { box-sizing: border-box; }
  .field { display: flex; flex-direction: column; }

  /* 统一输入控件的盒模型，避免在 grid/flex 中出现最小内容宽度导致的溢出 */
  input, textarea {
    width: 100%;
    min-width: 0; /* 关键：允许在网格列中收缩，防止溢出 */
    box-sizing: border-box;
    word-break: break-word; /* 文本换行，避免占位符过长撑破布局 */
  }

  /* 统一三列网格，兼容不同页面的使用（避免使用 > * 选择器以兼容 WXSS）*/
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); grid-gap: 16rpx; }
  /* WXSS 不完全支持子选择器与通配符，改为明确列举控件 */
  .grid-3 input, .grid-3 textarea, .grid-3 view, .grid-3 button { min-width: 0; }
</style>
