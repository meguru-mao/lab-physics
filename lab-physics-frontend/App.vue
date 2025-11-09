<script>
  import { IS_PROD, CLOUD_ENV_ID } from './utils/config.js'
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
	/*每个页面公共css */
</style>
