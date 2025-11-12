<template>
  <view class="page">
    <view class="section">
      <view class="title">T²-M 数据</view>
      <view class="field"><view class="label">滑块质量 m0（g）</view><input v-model="t2m.m0_g" type="digit" placeholder="例如：241.68" /></view>
      <view class="field"><view class="label">砝码质量 m（两行，3+2，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in weightsArr" :key="'w_'+i">
            <input v-model="weightsArr[i]" type="digit" placeholder="m" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">10T 平均值（两行，3+2，单位 s，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in t10Arr" :key="'t10_'+i">
            <input v-model="t10Arr[i]" type="digit" placeholder="T10" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="title">v²-x² 数据</view>
      <view class="field"><view class="label">位移（3 行，每行 3 个，单位 cm，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in xArr" :key="'x_'+i">
            <input v-model="xArr[i]" type="digit" placeholder="x" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">速度平均值（3 行，每行 3 个，单位 cm/s，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in vAvgArr" :key="'vavg_'+i">
            <input v-model="vAvgArr[i]" type="digit" placeholder="v" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
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
      t2m: { m0_g: '' },
      weightsArr: Array(5).fill(''),
      t10Arr: Array(5).fill(''),
      xArr: Array(9).fill(''),
      vAvgArr: Array(9).fill(''),
      images: []
    }
  },
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '力学实验', path: '/pages/experiments/mechanics', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '力学实验', query: 'from=timeline', imageUrl: '/static/logo.png' }
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
    // 支持英文/中文逗号
    parseNums(str) { return (str || '').split(/[,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const m0_g = parseFloat(this.t2m.m0_g)
      const weights_g = this.weightsArr.map(s => parseFloat(s)).filter(v => !isNaN(v))
      const T10_avg_s = this.t10Arr.map(s => parseFloat(s)).filter(v => !isNaN(v))
      if (isNaN(m0_g) || weights_g.length !== 5 || T10_avg_s.length !== 5) {
        uni.showToast({ title: 'T²-M：请填写 m0 及 5 项 weights/T10', icon: 'none' }); return
      }
      const x_cm = this.xArr.map(s => parseFloat(s)).filter(v => !isNaN(v))
      const v_avg_cms = this.vAvgArr.map(s => parseFloat(s)).filter(v => !isNaN(v))
      if (x_cm.length !== 9 || v_avg_cms.length !== 9) {
        uni.showToast({ title: 'v²-x²：请填写各 9 项数据', icon: 'none' }); return
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
.section { margin-bottom: 24rpx; background: #ffb69d; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; background: #fff; }
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 44rpx 0 12rpx; background: #fff; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.cell { position: relative; }
.cell-index { position: absolute; top: 8rpx; right: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>
