<template>
  <view class="page">
    <view class="section">
      <view class="title">太阳能电池特性数据（将生成6张图）</view>
      <view class="label strong">图1：全暗伏安特性</view>
      <view class="field"><view class="label">电压 (V)</view><textarea v-model="form.dark_voltage" :maxlength="-1" placeholder="例如：2.86,2.67,2.48,2.29,2.10,1.91,..." /></view>
      <view class="field"><view class="label">电流 (mA)</view><textarea v-model="form.dark_current" :maxlength="-1" placeholder="例如：0.135,0.109,0.087,0.069,0.055,0.043,..." /></view>

      <view class="label strong">图2：光照输出伏安特性</view>
      <view class="field"><view class="label">电压 (V)</view><textarea v-model="form.light_voltage" :maxlength="-1" placeholder="例如：0.92,1.82,2.70,3.50,4.13,4.47,..." /></view>
      <view class="field"><view class="label">电流 (mA)</view><textarea v-model="form.light_current" :maxlength="-1" placeholder="例如：17.5,17.4,17.3,16.9,15.9,14.5,..." /></view>

      <view class="label strong">图3-图6：光照特性</view>
      <view class="field"><view class="label">相对光强</view><textarea v-model="form.relative_intensity" :maxlength="-1" placeholder="例如：1,0.853,0.729,..." /></view>
      <view class="field"><view class="label">光功率 (mW)</view><textarea v-model="form.light_power" :maxlength="-1" placeholder="例如：0.225,0.192,0.164,..." /></view>
      <view class="field"><view class="label">短路电流 (mA)</view><textarea v-model="form.short_circuit_current" :maxlength="-1" placeholder="例如：16.2,14.1,12.1,..." /></view>
      <view class="field"><view class="label">开路电压 (V)</view><textarea v-model="form.open_circuit_voltage" :maxlength="-1" placeholder="例如：5.63,5.55,5.48,..." /></view>
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
      form: {
        dark_voltage: '', dark_current: '',
        light_voltage: '', light_current: '',
        relative_intensity: '', light_power: '', short_circuit_current: '', open_circuit_voltage: ''
      },
      images: []
    }
  },
  methods: {
    parseNums(str) { return (str || '').split(/[\,\s]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const f = this.form
      const required = ['dark_voltage','dark_current','light_voltage','light_current','relative_intensity','light_power','short_circuit_current','open_circuit_voltage']
      for (const k of required) { if (!f[k] || !this.parseNums(f[k]).length) { uni.showToast({ title: `请填写 ${k} 数据`, icon: 'none' }); return } }
      const payload = {
        dark_voltage: this.parseNums(f.dark_voltage), dark_current: this.parseNums(f.dark_current),
        light_voltage: this.parseNums(f.light_voltage), light_current: this.parseNums(f.light_current),
        relative_intensity: this.parseNums(f.relative_intensity), light_power: this.parseNums(f.light_power), short_circuit_current: this.parseNums(f.short_circuit_current), open_circuit_voltage: this.parseNums(f.open_circuit_voltage),
        return_data_uri: IS_PROD
      }
      try {
        const res = await apiRequest({ url: '/api/plots/solar-cell', method: 'POST', data: payload })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // #ifdef MP-WEIXIN
        if (imgs && imgs.length && String(imgs[0]).startsWith('data:'))
          imgs = await Promise.all(imgs.map((d) => this.toWxFileFromDataUri(d, 'solar')))
        // #endif
        this.images = imgs
      } catch (e) {}
    },
    toWxFileFromDataUri(dataUri, prefix = 'solar') {
      return new Promise((resolve, reject) => {
        // #ifdef MP-WEIXIN
        try { const base64 = String(dataUri || '').split(',')[1]; const filePath = `${wx.env.USER_DATA_PATH}/${prefix}_${Date.now()}_${Math.floor(Math.random()*1000)}.png`; const fs = wx.getFileSystemManager(); fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => resolve(filePath), fail: reject }) } catch (e) { reject(e) }
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
        try { const base64 = url.split(',')[1]; const filePath = `${wx.env.USER_DATA_PATH}/solar_${Date.now()}.png`; const fs = wx.getFileSystemManager(); fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) }) }) } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'solar-cell.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'solar-cell.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
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
.label { font-size: 24rpx; color: #666; margin: 8rpx 0; }
.label.strong { color: #333; font-weight: 600; }
.field { margin-bottom: 12rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
textarea { width: 100%; min-height: 100rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; background: #fff; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
</style>