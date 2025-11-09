<template>
  <view class="page">
    <view class="section">
      <view class="title">x 轴：VG2K 默认使用 1 到 82（共 82 个点），无需填写</view>
      <view class="hint">请仅填写各组 currents，长度需为 82</view>
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
          <view class="label">currents（与 VG2K 等长，逗号分隔）</view>
          <textarea v-model="g.currents" :maxlength="-1" placeholder="例如：0,0.002,0.014,0.045,...（支持超长文本）" />
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
import { apiRequest, API_BASE } from '../../utils/request.js'

export default {
  data() {
    return {
      // VG2K 固定默认生成，无需用户填写
      groups: [
        { vg1: '', vg2a: '', vg2p: '', currents: '' }
      ],
      images: []
    }
  },
  methods: {
    parseNums(str) {
      return (str || '').split(/[,\s]+/).map(s => parseFloat(s)).filter(v => !isNaN(v))
    },
    addGroup() { this.groups.push({ vg1: '', vg2a: '', vg2p: '', currents: '' }) },
    removeGroup(i) { this.groups.splice(i, 1) },
    async onSubmit() {
      const VG2K = Array.from({ length: 82 }, (_, i) => i + 1)
      const payload = { VG2K, groups: [] }
      for (let idx = 0; idx < this.groups.length; idx++) {
        const g = this.groups[idx]
        const currents = this.parseNums(g.currents)
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
        const res = await apiRequest({ url: API_BASE + '/api/plots/frank-hertz', method: 'POST', data: payload })
        this.images = (res && res.images) || []
        if (!this.images.length) uni.showToast({ title: '未返回图像', icon: 'none' })
      } catch (e) {}
    },
    fullUrl(u) { return u && (u.startsWith('http') ? u : (API_BASE + u)) },
    downloadImage(u) {
      const url = this.fullUrl(u)
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
.section { margin-bottom: 24rpx; background: #fff; border-radius: 16rpx; padding: 20rpx; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05); }
.title { font-size: 28rpx; margin-bottom: 16rpx; }
.field { margin-bottom: 12rpx; }
.label { font-size: 24rpx; color: #666; margin-bottom: 4rpx; }
textarea { width: 100%; min-height: 120rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 12rpx; }
input { width: 100%; height: 72rpx; line-height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx; box-sizing: border-box; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; align-items: center; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
.danger { height: 64rpx; background: #e94f4f; color: #fff; border-radius: 10rpx; font-size: 26rpx; }
.mini { margin-top: 8rpx; }
.divider { height: 1rpx; background: #eee; margin: 16rpx 0; }
.image-card { margin-top: 16rpx; }
.image-card image { width: 100%; }
</style>