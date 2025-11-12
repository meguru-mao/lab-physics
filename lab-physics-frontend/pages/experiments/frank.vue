<template>
  <view class="page">
    <view class="section">
      <view class="title">x 轴：VG2K 默认使用 1 到 82（共 82 个点）无需填写</view>
      <view class="hint">请仅填写各组电流IA，82个数据</view>
    </view>

    <view class="section">
      <view class="title">数据组（至少一组）</view>
      <view v-for="(g, idx) in groups" :key="idx" class="group">
        <view class="field">
          <view class="label">组 1 参数（仅填数字）：VG1 / VG2A / VG2P</view>
          <view class="grid-3">
            <input v-model="g.vg1" type="digit" placeholder="VG1" />
            <input v-model="g.vg2a" type="digit" placeholder="VG2A" />
            <input v-model="g.vg2p" type="digit" placeholder="VG2P" />
          </view>
        </view>
        <view class="field">
          <view class="label">电流 IA（微安）</view>
          <view class="grid-4">
            <view class="cell" v-for="(v, i) in g.currentsArr" :key="'ia_'+idx+'_'+i">
              <input v-model="g.currentsArr[i]" type="digit" placeholder="IA" />
              <text class="cell-index">{{ i + 1 }}</text>
            </view>
          </view>
        </view>
        <button class="danger mini" @click="removeGroup(idx)" v-if="groups.length>1">移除该组</button>
        <view class="divider" />
      </view>
      <button class="secondary mini" @click="addGroup">新增数据组</button>
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
      // VG2K 固定默认生成，无需用户填写
      groups: [
        { vg1: '', vg2a: '', vg2p: '', currentsArr: Array(82).fill('') }
      ],
      images: []
    }
  },
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '弗兰克赫兹', path: '/pages/experiments/frank', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '弗兰克赫兹', query: 'from=timeline', imageUrl: '/static/logo.png' }
  },
  methods: {
    toWxFileFromDataUri(dataUri, prefix = 'frank') {
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
    parseNums(str) {
      return (str || '').split(/[,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v))
    },
    addGroup() { this.groups.push({ vg1: '', vg2a: '', vg2p: '', currentsArr: Array(82).fill('') }) },
    removeGroup(i) { this.groups.splice(i, 1) },
    async onSubmit() {
      const VG2K = Array.from({ length: 82 }, (_, i) => i + 1)
      const payload = { VG2K, groups: [] }
      for (let idx = 0; idx < this.groups.length; idx++) {
        const g = this.groups[idx]
        const currents = g.currentsArr.map(s => parseFloat(s)).filter(v => !isNaN(v))
        const vg1 = parseFloat(g.vg1)
        const vg2a = parseFloat(g.vg2a)
        const vg2p = parseFloat(g.vg2p)
        if ([vg1, vg2a, vg2p].some(v => isNaN(v))) {
          uni.showToast({ title: `组 ${idx+1} 的 VG1/VG2A/VG2P 必须填写数字`, icon: 'none' })
          return
        }
        const label = `VG1=${vg1}V, VG2A=${vg2a}V, VG2P=${vg2p}V`
        if (!currents.length || currents.length !== VG2K.length) {
          uni.showToast({ title: '每组 currents 与 VG2K 长度需一致（82项）', icon: 'none' })
          return
        }
        payload.groups.push({ currents, label })
      }
      if (!payload.groups.length) { uni.showToast({ title: '请至少添加一组数据', icon: 'none' }); return }
      try {
        const res = await apiRequest({ url: '/api/plots/frank-hertz', method: 'POST', data: Object.assign({}, payload, { return_data_uri: IS_PROD }) })
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
          const filePath = `${wx.env.USER_DATA_PATH}/frank_${Date.now()}.png`
          const fs = wx.getFileSystemManager()
          fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => {
            wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) })
          } })
        } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'frank-hertz.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'frank-hertz.png';
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
input { width: 100%; height: 72rpx; line-height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 44rpx 0 12rpx; box-sizing: border-box; background: #fff; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; align-items: center; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.cell { position: relative; }
.cell-index { position: absolute; top: 8rpx; right: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.danger { height: 64rpx; background: #e94f4f; color: #fff; border-radius: 10rpx; font-size: 26rpx; }
.mini { margin-top: 8rpx; }
.divider { height: 1rpx; background: #eee; margin: 16rpx 0; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>
