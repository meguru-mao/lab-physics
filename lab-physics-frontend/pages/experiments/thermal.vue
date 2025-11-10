<template>
  <view class="page">
    <view class="section">
      <view class="title">热学综合实验数据</view>
      <view class="label strong">温度固定为 55, 60, 65, 70, 75, 80（无需填写）</view>
      <view class="label">请按两行三列填写对应的 Pt100 与 NTC 电阻值</view>
      <view class="grid-3 group-row">
        <view class="cell" v-for="(v, i) in pt100Arr" :key="'pt'+i">
          <input v-model="pt100Arr[i]" type="digit" placeholder="Pt100 电阻" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>
      <view class="grid-3 group-row">
        <view class="cell" v-for="(v, i) in ntcArr" :key="'ntc'+i">
          <input v-model="ntcArr[i]" type="digit" placeholder="NTC 电阻" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
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
      // 固定温度序列（无需用户输入）
      tempsFixed: [55, 60, 65, 70, 75, 80],
      // 两行三列，共 6 个输入框
      pt100Arr: Array(6).fill(''),
      ntcArr: Array(6).fill(''),
      images: []
    }
  },
  methods: {
    // 支持英文/中文逗号
    parseNums(str) { return (str || '').split(/[\,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const temps = this.tempsFixed.slice()
      const pt100 = this.toNums(this.pt100Arr)
      const ntc = this.toNums(this.ntcArr)
      if (pt100.length !== 6 || ntc.length !== 6) { uni.showToast({ title: '请填写完整的 6 个 Pt100 与 6 个 NTC 电阻值', icon: 'none' }); return }
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
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.group-row { margin-bottom: 12rpx; }
.cell { position: relative; }
input { width: 100%; height: 72rpx; line-height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx 0 44rpx; box-sizing: border-box; background: #fff; }
.cell-index { position: absolute; top: 8rpx; left: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>