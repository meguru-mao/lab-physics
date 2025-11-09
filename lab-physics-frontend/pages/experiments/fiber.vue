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
        <view class="label">U (逗号分隔)</view>
        <textarea v-model="form.U" placeholder="例如：0,0.75,1.0,1.1" />
      </view>
      <view class="field">
        <view class="label">I (逗号分隔，单位 mA)</view>
        <textarea v-model="form.I" placeholder="例如：0,0.2,5,10" />
      </view>
    </view>

    <!-- P-I 输入 -->
    <view v-if="plotType==='pi'" class="section">
      <view class="title">P-I 图数据</view>
      <view class="field">
        <view class="label">I (逗号分隔，单位 mA)</view>
        <textarea v-model="form.I" placeholder="例如：0,5,10,15" />
      </view>
      <view class="field">
        <view class="label">P (逗号分隔，单位 mW)</view>
        <textarea v-model="form.P" placeholder="例如：0,0.001,0.167,0.411" />
      </view>
    </view>

    <!-- 光电二极管输入 -->
    <view v-if="plotType==='photodiode'" class="section">
      <view class="title">光电二极管 I-V 数据</view>
      <view class="field">
        <view class="label">V (逗号分隔，单位 V)</view>
        <textarea v-model="form.V" placeholder="例如：0,1,2,3,4,5" />
      </view>
      <view class="field">
        <view class="label">I0 (P=0mW，逗号分隔)</view>
        <textarea v-model="form.I0" placeholder="例如：0,0,0,0,0,0" />
      </view>
      <view class="field">
        <view class="label">I1 (P=0.100mW，逗号分隔)</view>
        <textarea v-model="form.I1" placeholder="例如：98,99,99,100,98,99" />
      </view>
      <view class="field">
        <view class="label">I2 (P=0.200mW，逗号分隔)</view>
        <textarea v-model="form.I2" placeholder="例如：200,200,199,200,200,200" />
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
      form: { U: '', I: '', P: '', V: '', I0: '', I1: '', I2: '' },
      images: []
    }
  },
  methods: {
    onTypeChange(e) {
      const v = e.detail && e.detail.value
      if (v) this.plotType = v
      this.images = []
    },
    parseNums(str) {
      return (str || '')
        .split(/[,\s]+/)
        .map(s => parseFloat(s))
        .filter(v => !isNaN(v))
    },
    async onSubmit() {
      const type = this.plotType
      let payload = { plot_type: type }
      if (type === 'iu') {
        const U = this.parseNums(this.form.U)
        const I = this.parseNums(this.form.I)
        if (!U.length || !I.length || U.length !== I.length) {
          uni.showToast({ title: 'U 与 I 必须均为非空且长度一致', icon: 'none' })
          return
        }
        payload.U = U; payload.I = I
      } else if (type === 'pi') {
        const I = this.parseNums(this.form.I)
        const P = this.parseNums(this.form.P)
        if (!I.length || !P.length || I.length !== P.length) {
          uni.showToast({ title: 'I 与 P 必须均为非空且长度一致', icon: 'none' })
          return
        }
        payload.I = I; payload.P = P
      } else if (type === 'photodiode') {
        const V = this.parseNums(this.form.V)
        const I0 = this.parseNums(this.form.I0)
        const I1 = this.parseNums(this.form.I1)
        const I2 = this.parseNums(this.form.I2)
        const ok = V.length && I0.length && I1.length && I2.length &&
                   V.length === I0.length && V.length === I1.length && V.length === I2.length
        if (!ok) {
          uni.showToast({ title: 'V、I0、I1、I2 必须非空且长度一致', icon: 'none' })
          return
        }
        payload.V = V; payload.I0 = I0; payload.I1 = I1; payload.I2 = I2
      }
      try {
        const res = await apiRequest({ url: '/api/plots/fiber', method: 'POST', data: Object.assign({}, payload, { return_data_uri: IS_PROD }) })
        const imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        this.images = imgs
        if (!this.images.length) uni.showToast({ title: '未返回图像', icon: 'none' })
      } catch (e) {}
    },
    fullUrl(u) {
      if (!u) return ''
      return u.startsWith('data:') ? u : (u.startsWith('http') ? u : (API_BASE + u))
    },
    downloadImage(u) {
      const url = this.fullUrl(u)
      if (!url) return
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
.section { margin-bottom: 24rpx; background: #fff; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.radio-item { margin-right: 24rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>