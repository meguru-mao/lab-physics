<template>
  <view class="page">
    <view class="section">
      <view class="title">请选择绘图类型</view>
      <radio-group @change="onTypeChange">
        <label class="radio-item"><radio value="iu" :checked="plotType==='iu'" /> I-U 图</label>
        <label class="radio-item"><radio value="pi" :checked="plotType==='pi'" /> P-I 图</label>
        <label class="radio-item"><radio value="photodiode" :checked="plotType==='photodiode'" /> 光电二极管 I-V 图</label>
      </radio-group>
    </view>

    <!-- I-U 输入 -->
    <view v-if="plotType==='iu'" class="section">
      <view class="title">I-U 图数据</view>
      <view class="field">
        <view class="label">U（一行四个输入框，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in iuU" :key="'iuU_'+i">
            <input v-model="iuU[i]" type="digit" placeholder="U" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <view class="label">I（mA，一行四个输入框，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in iuI" :key="'iuI_'+i">
            <input v-model="iuI[i]" type="digit" placeholder="I" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- P-I 输入 -->
    <view v-if="plotType==='pi'" class="section">
      <view class="title">P-I 图数据</view>
      <view class="field">
        <view class="label">I（mA，一行四个输入框，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in piI" :key="'piI_'+i">
            <input v-model="piI[i]" type="digit" placeholder="I" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <view class="label">P（mW，一行四个输入框，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in piP" :key="'piP_'+i">
            <input v-model="piP[i]" type="digit" placeholder="P" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 光电二极管输入 -->
    <view v-if="plotType==='photodiode'" class="section">
      <view class="title">光电二极管 I-V 数据</view>
      <view class="field">
        <view class="label">V（两行，每行三个输入框，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdV" :key="'pdV_'+i">
            <input v-model="pdV[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <view class="label">I0（两行，每行三个输入框，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdI0" :key="'pdI0_'+i">
            <input v-model="pdI0[i]" type="digit" placeholder="I0" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <view class="label">I1（两行，每行三个输入框，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdI1" :key="'pdI1_'+i">
            <input v-model="pdI1[i]" type="digit" placeholder="I1" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field">
        <view class="label">I2（两行，每行三个输入框，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdI2" :key="'pdI2_'+i">
            <input v-model="pdI2[i]" type="digit" placeholder="I2" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
    </view>

    <button class="primary" @click="onSubmit">生成图像</button>

    <!-- 结果展示 -->
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
      plotType: 'iu',
      iuU: Array(4).fill(''),
      iuI: Array(4).fill(''),
      piI: Array(4).fill(''),
      piP: Array(4).fill(''),
      pdV: Array(6).fill(''),
      pdI0: Array(6).fill(''),
      pdI1: Array(6).fill(''),
      pdI2: Array(6).fill(''),
      images: []
    }
  },
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '光纤传感与通讯', path: '/pages/experiments/fiber', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '光纤传感与通讯', query: 'from=timeline', imageUrl: '/static/logo.png' }
  },
  methods: {
    toWxFileFromDataUri(dataUri, prefix = 'fiber') {
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
    onTypeChange(e) {
      const v = e.detail && e.detail.value
      if (v) this.plotType = v
      this.images = []
    },
    parseNums(str) {
      return (str || '')
        .split(/[,\s，]+/)
        .map(s => parseFloat(s))
        .filter(v => !isNaN(v))
    },
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const type = this.plotType
      let payload = { plot_type: type }
      if (type === 'iu') {
        const U = this.toNums(this.iuU)
        const I = this.toNums(this.iuI)
        if (U.length !== 4 || I.length !== 4 || U.length !== I.length) {
          uni.showToast({ title: 'U 与 I 需各填满4项且长度一致', icon: 'none' })
          return
        }
        payload.U = U; payload.I = I
      } else if (type === 'pi') {
        const I = this.toNums(this.piI)
        const P = this.toNums(this.piP)
        if (I.length !== 4 || P.length !== 4 || I.length !== P.length) {
          uni.showToast({ title: 'I 与 P 需各填满4项且长度一致', icon: 'none' })
          return
        }
        payload.I = I; payload.P = P
      } else if (type === 'photodiode') {
        const V = this.toNums(this.pdV)
        const I0 = this.toNums(this.pdI0)
        const I1 = this.toNums(this.pdI1)
        const I2 = this.toNums(this.pdI2)
        const ok = (V.length === 6 && I0.length === 6 && I1.length === 6 && I2.length === 6)
        if (!ok) {
          uni.showToast({ title: 'V、I0、I1、I2 需各填满6项且长度一致', icon: 'none' })
          return
        }
        payload.V = V; payload.I0 = I0; payload.I1 = I1; payload.I2 = I2
      }
      try {
        const res = await apiRequest({ url: '/api/plots/fiber', method: 'POST', data: Object.assign({}, payload, { return_data_uri: IS_PROD }) })
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
        if (!this.images.length) uni.showToast({ title: '未返回图像', icon: 'none' })
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
          const filePath = `${wx.env.USER_DATA_PATH}/fiber_${Date.now()}.png`
          const fs = wx.getFileSystemManager()
          fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => {
            wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) })
          } })
        } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'fiber-plot.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a')
      a.href = url
      a.download = 'fiber-plot.png'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      // #endif
      // #ifdef MP-WEIXIN
      uni.downloadFile({
        url,
        success: (res) => {
          const tempFilePath = res.tempFilePath
          wx.saveImageToPhotosAlbum({ filePath: tempFilePath, success: () => uni.showToast({ title: '已保存到相册' }) })
        },
        fail: () => uni.showToast({ title: '下载失败', icon: 'none' })
      })
      // #endif
    }
  }
}
</script>

<style>
.page { padding: 24rpx; }
.section { margin-bottom: 24rpx; background: #ffb69d; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.radio-item { margin-right: 24rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; background: #fff; }
input { width: 100%; height: 72rpx; line-height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 44rpx 0 12rpx; box-sizing: border-box; background: #fff; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.cell { position: relative; }
.cell-index { position: absolute; top: 8rpx; right: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>
