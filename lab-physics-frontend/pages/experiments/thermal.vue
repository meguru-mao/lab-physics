<template>
  <view class="page">
    <view class="section">
      <view class="title">热学综合实验数据</view>
      <view class="field">
        <view class="label">温度 Temperatures (℃，逗号分隔)</view>
        <textarea v-model="form.temperatures" :maxlength="-1" placeholder="例如：55,60,65,70,75,80" />
      </view>
      <view class="field">
        <view class="label">Pt100 电阻 (Ω，逗号分隔)</view>
        <textarea v-model="form.pt100_resistance" :maxlength="-1" placeholder="例如：126.56,128.55,130.71,132.85,134.97,137.09" />
      </view>
      <view class="field">
        <view class="label">NTC 电阻 (Ω，逗号分隔)</view>
        <textarea v-model="form.ntc_resistance" :maxlength="-1" placeholder="例如：2883,2424,2027,1701,1435,1217" />
      </view>
    </view>
    <button class="primary" @click="onSubmit">生成图像</button>
    <view v-if="images.length" class="section">
      <view class="title">生成结果</view>
      <view v-for="(img, idx) in images" :key="idx" class="image-card">
        <image :src="fullUrl(img)" mode="widthFix" />
        <button class="secondary" @click="downloadImage(img)">下载图像</button>
      </view>
    </view>
  </view>
</template>

<script>
import { apiRequest, API_BASE, IS_PROD } from '../../utils/request.js'
export default {
  data() {
    return {
      form: { temperatures: '', pt100_resistance: '', ntc_resistance: '' },
      images: []
    }
  },
  methods: {
    parseNums(str) { return (str || '').split(/[\,\s]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const temps = this.parseNums(this.form.temperatures)
      const pt100 = this.parseNums(this.form.pt100_resistance)
      const ntc = this.parseNums(this.form.ntc_resistance)
      if (!temps.length || !pt100.length || !ntc.length || !(temps.length === pt100.length && temps.length === ntc.length)) {
        uni.showToast({ title: '温度、Pt100、NTC 需非空且长度一致', icon: 'none' }); return
      }
      try {
        const res = await apiRequest({ url: '/api/plots/thermal', method: 'POST', data: { temperatures: temps, pt100_resistance: pt100, ntc_resistance: ntc, return_data_uri: IS_PROD } })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // #ifdef MP-WEIXIN
        if (imgs && imgs.length && String(imgs[0]).startsWith('data:'))
          imgs = await Promise.all(imgs.map((d) => this.toWxFileFromDataUri(d, 'thermal')))
        // #endif
        this.images = imgs
      } catch (e) {}
    },
    toWxFileFromDataUri(dataUri, prefix = 'thermal') {
      return new Promise((resolve, reject) => {
        // #ifdef MP-WEIXIN
        try {
          const base64 = String(dataUri || '').split(',')[1]
          const filePath = `${wx.env.USER_DATA_PATH}/${prefix}_${Date.now()}_${Math.floor(Math.random()*1000)}.png`
          const fs = wx.getFileSystemManager()
          fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => resolve(filePath), fail: reject })
        } catch (e) { reject(e) }
        // #endif
        // #ifndef MP-WEIXIN
        resolve(dataUri)
        // #endif
      })
    },
    fullUrl(u) { if (!u) return ''; if (typeof u === 'string' && (u.startsWith('data:') || u.startsWith('wxfile://') || u.startsWith('/'))) return u; return u.startsWith('http') ? u : (API_BASE + u) },
    downloadImage(u) {
      const url = this.fullUrl(u); if (!url) return
      if (url.startsWith('wxfile://')) { // #ifdef MP-WEIXIN
        wx.saveImageToPhotosAlbum({ filePath: url, success: () => uni.showToast({ title: '已保存到相册' }) }); return
      } // #endif
      if (url.startsWith('data:')) {
        // #ifdef MP-WEIXIN
        try { const base64 = url.split(',')[1]; const filePath = `${wx.env.USER_DATA_PATH}/thermal_${Date.now()}.png`; const fs = wx.getFileSystemManager(); fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) }) }) } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'thermal-plot.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'thermal-plot.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
      // #endif
      // #ifdef MP-WEIXIN
      uni.downloadFile({ url, success: (res) => wx.saveImageToPhotosAlbum({ filePath: res.tempFilePath }) })
      // #endif
    }
  }
}
</script>

<style>
.page { padding: 24rpx; }
.section { margin-bottom: 24rpx; background: #ffb69d; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; background: #fff; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>