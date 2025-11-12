<template>
  <view class="page">
    <view class="section">
      <view class="title">密立根油滴数据（上下数据位置需要对应）</view>
      <view class="label strong">第一行：ni（正整数）</view>
      <view class="grid-3 group-row">
        <view class="cell" v-for="(v, i) in niArr" :key="'ni'+i">
          <input v-model="niArr[i]" type="number" placeholder="ni" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>
      <view class="label strong">第二行：qi（x10^-19 C）</view>
      <view class="grid-3 group-row">
        <view class="cell" v-for="(v, i) in qiArr" :key="'qi'+i">
          <input v-model="qiArr[i]" type="digit" placeholder="qi" />
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
      niArr: Array(6).fill(''),
      qiArr: Array(6).fill(''),
      images: []
    }
  },
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '密里根油滴', path: '/pages/experiments/millikan', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '密里根油滴', query: 'from=timeline', imageUrl: '/static/logo.png' }
  },
  methods: {
    toWxFileFromDataUri(dataUri, prefix = 'millikan') {
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
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      if (this.niArr.some(v => v === '') || this.qiArr.some(v => v === '')) {
        uni.showToast({ title: '请填写完整的 6 个 ni 与 6 个 qi', icon: 'none' }); return
      }
      const ni = this.toNums(this.niArr)
      const qi = this.toNums(this.qiArr)
      if (ni.length !== 6 || qi.length !== 6) { uni.showToast({ title: '输入必须为数字', icon: 'none' }); return }
      try {
        const res = await apiRequest({ url: '/api/plots/millikan', method: 'POST', data: { ni, qi, return_data_uri: IS_PROD } })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // 在微信端，image 不支持 dataURI，转换为本地临时文件路径
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
      // 直接保存本地文件（微信端）
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
          const filePath = `${wx.env.USER_DATA_PATH}/millikan_${Date.now()}.png`
          const fs = wx.getFileSystemManager()
          fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => {
            wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) })
          } })
        } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'millikan.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'millikan.png';
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
.section { margin-bottom: 24rpx; background: #ffb69d; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.label { font-size: 24rpx; color: #666; margin: 8rpx 0; }
.label.strong { color: #333; font-weight: 600; }
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
