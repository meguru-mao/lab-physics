<template>
  <view class="page">
    <view class="section">
      <view class="title">密立根油滴数据（两行三列，共 6 个输入框）</view>
      <view class="label strong">第一行：ni（正整数）</view>
      <view class="grid-3">
        <input v-for="(v, i) in niArr" :key="'ni'+i" v-model="niArr[i]" type="number" placeholder="ni" />
      </view>
      <view class="label strong">第二行：qi（x10^-19 C）</view>
      <view class="grid-3">
        <input v-for="(v, i) in qiArr" :key="'qi'+i" v-model="qiArr[i]" type="digit" placeholder="qi" />
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
import { apiRequest, API_BASE } from '../../utils/request.js'
export default {
  data() {
    return {
      niArr: Array(6).fill(''),
      qiArr: Array(6).fill(''),
      images: []
    }
  },
  methods: {
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      if (this.niArr.some(v => v === '') || this.qiArr.some(v => v === '')) {
        uni.showToast({ title: '请填写完整的 6 个 ni 与 6 个 qi', icon: 'none' }); return
      }
      const ni = this.toNums(this.niArr)
      const qi = this.toNums(this.qiArr)
      if (ni.length !== 6 || qi.length !== 6) { uni.showToast({ title: '输入必须为数字', icon: 'none' }); return }
      try {
        const res = await apiRequest({ url: API_BASE + '/api/plots/millikan', method: 'POST', data: { ni, qi } })
        this.images = (res && res.images) || []
      } catch (e) {}
    },
    fullUrl(u) { return u && (u.startsWith('http') ? u : (API_BASE + u)) },
    downloadImage(u) {
      const url = this.fullUrl(u)
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
.section { margin-bottom: 24rpx; background: #fff; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.label { font-size: 24rpx; color: #666; margin: 8rpx 0; }
.label.strong { color: #333; font-weight: 600; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; grid-gap: 16rpx; }
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>