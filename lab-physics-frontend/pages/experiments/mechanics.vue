<template>
  <view class="page">
    <view class="section">
      <view class="title">T²-M 数据</view>
      <view class="field"><view class="label">滑块质量 m0（g）</view><input v-model="t2m.m0_g" type="digit" placeholder="例如：241.68" /></view>
      <view class="field"><view class="label">weights_g（逗号分隔，砝码质量）</view><textarea v-model="t2m.weights_g" placeholder="例如：20,40,50,70,100" /></view>
      <view class="field"><view class="label">T10_avg_s（逗号分隔，10T平均值，单位 s）</view><textarea v-model="t2m.T10_avg_s" placeholder="例如：17.0158,17.6387,17.9340,18.5316,19.3818" /></view>
    </view>

    <view class="section">
      <view class="title">v²-x² 数据</view>
      <view class="field"><view class="label">x_cm（逗号分隔，位移，单位 cm）</view><textarea v-model="v2x2.x_cm" placeholder="例如：0,4,6,8,10,12,14,16,18" /></view>
      <view class="field"><view class="label">v_avg_cms（逗号分隔，速度平均值，单位 cm/s）</view><textarea v-model="v2x2.v_avg_cms" placeholder="例如：77.34,72.47,71.17,69.17,63.92,57.30,49.67,41.67,29.70" /></view>
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
      t2m: { m0_g: '', weights_g: '', T10_avg_s: '' },
      v2x2: { x_cm: '', v_avg_cms: '' },
      images: []
    }
  },
  methods: {
    toWxFileFromDataUri(dataUri, prefix = 'mechanics') {
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
    parseNums(str) { return (str || '').split(/[,\s]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const m0_g = parseFloat(this.t2m.m0_g)
      const weights_g = this.parseNums(this.t2m.weights_g)
      const T10_avg_s = this.parseNums(this.t2m.T10_avg_s)
      if (isNaN(m0_g) || !weights_g.length || !T10_avg_s.length || weights_g.length !== T10_avg_s.length) {
        uni.showToast({ title: 'T²-M 数据不合法：m0、weights、T10 必须非空且长度匹配', icon: 'none' }); return
      }
      const x_cm = this.parseNums(this.v2x2.x_cm)
      const v_avg_cms = this.parseNums(this.v2x2.v_avg_cms)
      if (!x_cm.length || !v_avg_cms.length || x_cm.length !== v_avg_cms.length) {
        uni.showToast({ title: 'v²-x² 数据不合法：x 与 v 必须非空且长度匹配', icon: 'none' }); return
      }
      const payload = { t2m: { m0_g, weights_g, T10_avg_s }, v2x2: { x_cm, v_avg_cms } }
      try {
        const res = await apiRequest({ url: '/api/plots/mechanics', method: 'POST', data: Object.assign({}, payload, { return_data_uri: IS_PROD }) })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // #ifdef MP-WEIXIN
        if (imgs && imgs.length && String(imgs[0]).startsWith('data:')) {
          try {
            const files = await Promise.all(imgs.map((d) => this.toWxFileFromDataUri(d)))
            imgs = files
          } catch (e) {}
        }
        // #endif
        this.images = imgs
      } catch (e) {}
    },
    fullUrl(u) {
      if (!u) return ''
      if (typeof u === 'string' && (u.startsWith('data:') || u.startsWith('wxfile://') || u.startsWith('/'))) return u
      return u.startsWith('http') ? u : (API_BASE + u)
    },
    downloadImage(u) {
      const url = this.fullUrl(u)
      if (!url) return
      if (url.startsWith('wxfile://')) {
        // #ifdef MP-WEIXIN
        wx.saveImageToPhotosAlbum({ filePath: url, success: () => uni.showToast({ title: '已保存到相册' }) })
        // #endif
        return
      }
      if (url.startsWith('data:')) {
        // #ifdef MP-WEIXIN
        try {
          const base64 = url.split(',')[1]
          const filePath = `${wx.env.USER_DATA_PATH}/mechanics_${Date.now()}.png`
          const fs = wx.getFileSystemManager()
          fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => {
            wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) })
          } })
        } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'mechanics.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'mechanics.png';
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
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
.section { margin-bottom: 24rpx; background: #fff; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; }
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>