<template>
  <view class="page">
    <view class="section">
      <view class="title">太阳能电池特性数据（将生成6张图）</view>
      <view class="label strong">图1：全暗伏安特性</view>
      <view class="field"><view class="label">电压（四行，4+4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in darkVArr" :key="'darkV_'+i">
            <input v-model="darkVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">电流（四行，4+4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in darkIArr" :key="'darkI_'+i">
            <input v-model="darkIArr[i]" type="digit" placeholder="I" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>

      <view class="label strong">图2：光照输出伏安特性</view>
      <view class="field"><view class="label">电压（五行，每行 4 个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in lightVArr" :key="'lightV_'+i">
            <input v-model="lightVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">电流（五行，每行 4 个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in lightIArr" :key="'lightI_'+i">
            <input v-model="lightIArr[i]" type="digit" placeholder="I" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>

      <view class="label strong">图3-图6：光照特性</view>
      <view class="field"><view class="label">相对光强（3 行，4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in relIntArr" :key="'rel_'+i">
            <input v-model="relIntArr[i]" type="digit" placeholder="相对光强" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光功率（3 行，4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in lightPowerArr" :key="'lp_'+i">
            <input v-model="lightPowerArr[i]" type="digit" placeholder="光功率" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">短路电流（3 行，4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in scIArr" :key="'sci_'+i">
            <input v-model="scIArr[i]" type="digit" placeholder="短路电流" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">开路电压（3 行，4+4+2，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ocVArr" :key="'ocv_'+i">
            <input v-model="ocVArr[i]" type="digit" placeholder="开路电压" />
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
      darkVArr: Array(14).fill(''), darkIArr: Array(14).fill(''),
      lightVArr: Array(20).fill(''), lightIArr: Array(20).fill(''),
      relIntArr: Array(10).fill(''), lightPowerArr: Array(10).fill(''), scIArr: Array(10).fill(''), ocVArr: Array(10).fill(''),
      images: []
    }
  },
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '太阳能电池特性', path: '/pages/experiments/solar-cell', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '太阳能电池特性', query: 'from=timeline', imageUrl: '/static/logo.png' }
  },
  methods: {
    // 支持英文/中文逗号
    parseNums(str) { return (str || '').split(/[\,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const payload = {
        dark_voltage: this.toNums(this.darkVArr), dark_current: this.toNums(this.darkIArr),
        light_voltage: this.toNums(this.lightVArr), light_current: this.toNums(this.lightIArr),
        relative_intensity: this.toNums(this.relIntArr), light_power: this.toNums(this.lightPowerArr), short_circuit_current: this.toNums(this.scIArr), open_circuit_voltage: this.toNums(this.ocVArr),
        return_data_uri: IS_PROD
      }
      if (payload.dark_voltage.length !== 14 || payload.dark_current.length !== 14) { uni.showToast({ title: '全暗伏安需各填满14项', icon: 'none' }); return }
      if (payload.light_voltage.length !== 20 || payload.light_current.length !== 20) { uni.showToast({ title: '光照输出伏安需各填满20项', icon: 'none' }); return }
      for (const [name, arr] of Object.entries({ relative_intensity: payload.relative_intensity, light_power: payload.light_power, short_circuit_current: payload.short_circuit_current, open_circuit_voltage: payload.open_circuit_voltage })) { if (arr.length !== 10) { uni.showToast({ title: `${name} 需填满10项`, icon: 'none' }); return } }
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
.cell { position: relative; }
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 44rpx 0 12rpx; background: #fff; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.cell { position: relative; }
.cell-index { position: absolute; top: 8rpx; right: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
</style>
