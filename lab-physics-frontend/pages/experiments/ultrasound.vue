<template>
  <view class="page">
    <view class="section">
      <view class="title">超声波实验（含自由落体、三组匀变速、牛顿第二定律）</view>
      <view class="label strong">自由落体</view>
      <view class="label">时间 t 固定为 0.05 ~ 0.40（步长 0.05，共 8 点），无需填写</view>
      <view class="label">请填写四组速度（每组 8 个），采用两行四列的输入布局</view>
      <view class="sub-title">速度组 v1</view>
      <view class="grid-4 group-row">
        <view class="cell" v-for="(v, i) in vff1Arr" :key="'v1_'+i">
          <input v-model="vff1Arr[i]" type="digit" placeholder="v1" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>
      <view class="sub-title">速度组 v2</view>
      <view class="grid-4 group-row">
        <view class="cell" v-for="(v, i) in vff2Arr" :key="'v2_'+i">
          <input v-model="vff2Arr[i]" type="digit" placeholder="v2" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>
      <view class="sub-title">速度组 v3</view>
      <view class="grid-4 group-row">
        <view class="cell" v-for="(v, i) in vff3Arr" :key="'v3_'+i">
          <input v-model="vff3Arr[i]" type="digit" placeholder="v3" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>
      <view class="sub-title">速度组 v4</view>
      <view class="grid-4 group-row">
        <view class="cell" v-for="(v, i) in vff4Arr" :key="'v4_'+i">
          <input v-model="vff4Arr[i]" type="digit" placeholder="v4" />
          <text class="cell-index">{{ i + 1 }}</text>
        </view>
      </view>

      <view class="label strong">匀变速运动 第1组</view>
      <view class="field"><view class="label">时间 t1 (s)</view><textarea v-model="form.t1" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v1_1 (m/s)</view><textarea v-model="form.v1_1" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v1_2 (m/s)</view><textarea v-model="form.v1_2" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v1_3 (m/s)</view><textarea v-model="form.v1_3" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v1_4 (m/s)</view><textarea v-model="form.v1_4" :maxlength="-1" /></view>

      <view class="label strong">匀变速运动 第2组</view>
      <view class="field"><view class="label">时间 t2 (s)</view><textarea v-model="form.t2" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v2_1 (m/s)</view><textarea v-model="form.v2_1" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v2_2 (m/s)</view><textarea v-model="form.v2_2" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v2_3 (m/s)</view><textarea v-model="form.v2_3" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v2_4 (m/s)</view><textarea v-model="form.v2_4" :maxlength="-1" /></view>

      <view class="label strong">匀变速运动 第3组</view>
      <view class="field"><view class="label">时间 t3 (s)</view><textarea v-model="form.t3" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v3_1 (m/s)</view><textarea v-model="form.v3_1" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v3_2 (m/s)</view><textarea v-model="form.v3_2" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v3_3 (m/s)</view><textarea v-model="form.v3_3" :maxlength="-1" /></view>
      <view class="field"><view class="label">速度 v3_4 (m/s)</view><textarea v-model="form.v3_4" :maxlength="-1" /></view>

      <view class="label strong">牛顿第二定律验证</view>
      <view class="field"><view class="label">砝码质量 m (kg)</view><textarea v-model="form.m" :maxlength="-1" placeholder="例如：0.01999,0.03219,0.440" /></view>
      <view class="field"><view class="label">测得加速度 a (m/s²)</view><textarea v-model="form.a_measured" :maxlength="-1" placeholder="例如：5.4374,4.3351,3.3228" /></view>
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
      // 自由落体：固定时间 + 四组速度数组（两行四列共 8 个）
      tFreeFixed: Array.from({ length: 8 }, (_, i) => Number(((i + 1) * 0.05).toFixed(2))),
      vff1Arr: Array(8).fill(''),
      vff2Arr: Array(8).fill(''),
      vff3Arr: Array(8).fill(''),
      vff4Arr: Array(8).fill(''),
      form: {
        t1: '', v1_1: '', v1_2: '', v1_3: '', v1_4: '',
        t2: '', v2_1: '', v2_2: '', v2_3: '', v2_4: '',
        t3: '', v3_1: '', v3_2: '', v3_3: '', v3_4: '',
        m: '', a_measured: ''
      },
      images: []
    }
  },
  methods: {
    // 支持英文/中文逗号
    parseNums(str) { return (str || '').split(/[\,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const f = this.form
      // 自由落体：四组速度需各填满 8 个数字
      const v1 = this.toNums(this.vff1Arr), v2 = this.toNums(this.vff2Arr), v3 = this.toNums(this.vff3Arr), v4 = this.toNums(this.vff4Arr)
      if (v1.length !== 8 || v2.length !== 8 || v3.length !== 8 || v4.length !== 8) {
        uni.showToast({ title: '请填写完整的 4 组速度，每组 8 个数据', icon: 'none' }); return
      }
      const t_free = this.tFreeFixed.slice()
      // 三组匀变速长度一致
      const t1 = this.parseNums(f.t1), t2 = this.parseNums(f.t2), t3 = this.parseNums(f.t3)
      for (const [tArr, keys] of [[t1,['v1_1','v1_2','v1_3','v1_4']], [t2,['v2_1','v2_2','v2_3','v2_4']], [t3,['v3_1','v3_2','v3_3','v3_4']]]) {
        for (const k of keys) { const v = this.parseNums(f[k]); if (v.length !== tArr.length) { uni.showToast({ title: `${k} 与对应时间长度需一致`, icon: 'none' }); return } }
      }

      const payload = {
        t_free_fall: t_free,
        v_free_fall_1: v1,
        v_free_fall_2: v2,
        v_free_fall_3: v3,
        v_free_fall_4: v4,
        t1, v1_1: this.parseNums(f.v1_1), v1_2: this.parseNums(f.v1_2), v1_3: this.parseNums(f.v1_3), v1_4: this.parseNums(f.v1_4),
        t2, v2_1: this.parseNums(f.v2_1), v2_2: this.parseNums(f.v2_2), v2_3: this.parseNums(f.v2_3), v2_4: this.parseNums(f.v2_4),
        t3, v3_1: this.parseNums(f.v3_1), v3_2: this.parseNums(f.v3_2), v3_3: this.parseNums(f.v3_3), v3_4: this.parseNums(f.v3_4),
        m: this.parseNums(f.m), a_measured: this.parseNums(f.a_measured),
        return_data_uri: IS_PROD
      }
      try {
        const res = await apiRequest({ url: '/api/plots/ultrasound', method: 'POST', data: payload })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // #ifdef MP-WEIXIN
        if (imgs && imgs.length && String(imgs[0]).startsWith('data:'))
          imgs = await Promise.all(imgs.map((d) => this.toWxFileFromDataUri(d, 'ultra')))
        // #endif
        this.images = imgs
      } catch (e) {}
    },
    toWxFileFromDataUri(dataUri, prefix = 'ultra') {
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
        try { const base64 = url.split(',')[1]; const filePath = `${wx.env.USER_DATA_PATH}/ultra_${Date.now()}.png`; const fs = wx.getFileSystemManager(); fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) }) }) } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'ultrasound.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'ultrasound.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
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
.sub-title { margin-top: 8rpx; font-size: 24rpx; color: #555; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.group-row { margin-bottom: 12rpx; }
.cell { position: relative; }
input { width: 100%; height: 72rpx; line-height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx 0 44rpx; box-sizing: border-box; background: #fff; }
.cell-index { position: absolute; top: 8rpx; left: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
</style>