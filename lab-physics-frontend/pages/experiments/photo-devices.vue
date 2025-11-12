<template>
  <view class="page">
    <view class="section">
      <view class="title">光电器件性能数据（10子图合成一张）</view>
      <view class="label strong">LED</view>
      <view class="label">LED 电流 I 固定为 0,5,10,15,20,25,30（7 点），无需填写</view>
      <view class="field"><view class="label">V（两行，第一行4个，第二行3个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ledVArr" :key="'ledV_'+i">
            <input v-model="ledVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">P（两行，第一行4个，第二行3个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ledPArr" :key="'ledP_'+i">
            <input v-model="ledPArr[i]" type="digit" placeholder="P" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>

      <view class="label strong">LD（含阈值线性拟合）</view>
      <view class="label">LD 电流 I 固定为 0,3,6,9,12,15,18,21（8 点），无需填写</view>
      <view class="field"><view class="label">V（两行，均为4个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ldVArr" :key="'ldV_'+i">
            <input v-model="ldVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">P（两行，均为4个，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ldPArr" :key="'ldP_'+i">
            <input v-model="ldPArr[i]" type="digit" placeholder="P" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">拟合起始索引（默认4）</view><input v-model="ldLinearStartIdx" type="number" placeholder="4" /></view>

      <view class="label strong">光敏二极管</view>
      <view class="field"><view class="label">照度 L（两行，均为3个，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdLArr" :key="'pdL_'+i">
            <input v-model="pdLArr[i]" type="digit" placeholder="L" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光照特性电流 I（两行，均为3个，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdILArr" :key="'pdIL_'+i">
            <input v-model="pdILArr[i]" type="digit" placeholder="I(L)" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">伏安特性电压 V（两行，3+2，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdVArr" :key="'pdV_'+i">
            <input v-model="pdVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">伏安特性电流 I（两行，3+2，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in pdIVArr" :key="'pdIV_'+i">
            <input v-model="pdIVArr[i]" type="digit" placeholder="I(V)" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光谱波长 λ（两行，4+3，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in pdWlArr" :key="'pdWl_'+i">
            <input v-model="pdWlArr[i]" type="digit" placeholder="λ" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光谱电流 I（两行，4+3，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in pdIWlArr" :key="'pdIWl_'+i">
            <input v-model="pdIWlArr[i]" type="digit" placeholder="I(λ)" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>

      <view class="label strong">光敏三极管</view>
      <view class="field"><view class="label">照度 L（两行，均为3个，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in ptLArr" :key="'ptL_'+i">
            <input v-model="ptLArr[i]" type="digit" placeholder="L" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光照特性电流 I（两行，均为3个，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in ptILArr" :key="'ptIL_'+i">
            <input v-model="ptILArr[i]" type="digit" placeholder="I(L)" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">伏安特性电压 V（两行，3+2，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in ptVArr" :key="'ptV_'+i">
            <input v-model="ptVArr[i]" type="digit" placeholder="V" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">伏安特性电流 I（两行，3+2，含编号）</view>
        <view class="grid-3">
          <view class="cell" v-for="(v, i) in ptIVArr" :key="'ptIV_'+i">
            <input v-model="ptIVArr[i]" type="digit" placeholder="I(V)" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光谱波长 λ（两行，4+3，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ptWlArr" :key="'ptWl_'+i">
            <input v-model="ptWlArr[i]" type="digit" placeholder="λ" />
            <text class="cell-index">{{ i + 1 }}</text>
          </view>
        </view>
      </view>
      <view class="field"><view class="label">光谱电流 I（两行，4+3，含编号）</view>
        <view class="grid-4">
          <view class="cell" v-for="(v, i) in ptIWlArr" :key="'ptIWl_'+i">
            <input v-model="ptIWlArr[i]" type="digit" placeholder="I(λ)" />
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
      ledVArr: Array(7).fill(''), ledPArr: Array(7).fill(''),
      ldVArr: Array(8).fill(''), ldPArr: Array(8).fill(''), ldLinearStartIdx: '4',
      pdLArr: Array(6).fill(''), pdILArr: Array(6).fill(''), pdVArr: Array(5).fill(''), pdIVArr: Array(5).fill(''), pdWlArr: Array(7).fill(''), pdIWlArr: Array(7).fill(''),
      ptLArr: Array(6).fill(''), ptILArr: Array(6).fill(''), ptVArr: Array(5).fill(''), ptIVArr: Array(5).fill(''), ptWlArr: Array(7).fill(''), ptIWlArr: Array(7).fill(''),
      images: []
    }
  },
  methods: {
    // 支持英文/中文逗号
    parseNums(str) { return (str || '').split(/[\,\s，]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    toNums(arr) { return arr.map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const led_V = this.toNums(this.ledVArr), led_P = this.toNums(this.ledPArr)
      if (led_V.length !== 7 || led_P.length !== 7) { uni.showToast({ title: 'LED 的 V 与 P 需各填满7项', icon: 'none' }); return }
      const led_I = [0,5,10,15,20,25,30]
      const ld_I = [0,3,6,9,12,15,18,21]
      const ld_V = this.toNums(this.ldVArr), ld_P = this.toNums(this.ldPArr)
      if (ld_V.length !== 8 || ld_P.length !== 8) { uni.showToast({ title: 'LD 的 V 与 P 需各填满8项', icon: 'none' }); return }
      const payload = {
        led_I, led_V, led_P,
        ld_I, ld_V, ld_P, ld_linear_start_idx: parseInt(this.ldLinearStartIdx || '4'),
        pd_L: this.toNums(this.pdLArr), pd_I_L: this.toNums(this.pdILArr), pd_V: this.toNums(this.pdVArr), pd_I_V: this.toNums(this.pdIVArr), pd_wl: this.toNums(this.pdWlArr), pd_I_wl: this.toNums(this.pdIWlArr),
        pt_L: this.toNums(this.ptLArr), pt_I_L: this.toNums(this.ptILArr), pt_V: this.toNums(this.ptVArr), pt_I_V: this.toNums(this.ptIVArr), pt_wl: this.toNums(this.ptWlArr), pt_I_wl: this.toNums(this.ptIWlArr),
        return_data_uri: IS_PROD
      }
      for (const [name, arr] of Object.entries({ pd_L: payload.pd_L, pd_I_L: payload.pd_I_L })) { if (arr.length !== 6) { uni.showToast({ title: `${name} 需填满6项`, icon: 'none' }); return } }
      for (const [name, arr] of Object.entries({ pd_V: payload.pd_V, pd_I_V: payload.pd_I_V })) { if (arr.length !== 5) { uni.showToast({ title: `${name} 需填满5项`, icon: 'none' }); return } }
      for (const [name, arr] of Object.entries({ pd_wl: payload.pd_wl, pd_I_wl: payload.pd_I_wl })) { if (arr.length !== 7) { uni.showToast({ title: `${name} 需填满7项`, icon: 'none' }); return } }
      for (const [name, arr] of Object.entries({ pt_L: payload.pt_L, pt_I_L: payload.pt_I_L })) { if (arr.length !== 6) { uni.showToast({ title: `${name} 需填满6项`, icon: 'none' }); return } }
      for (const [name, arr] of Object.entries({ pt_V: payload.pt_V, pt_I_V: payload.pt_I_V })) { if (arr.length !== 5) { uni.showToast({ title: `${name} 需填满5项`, icon: 'none' }); return } }
      for (const [name, arr] of Object.entries({ pt_wl: payload.pt_wl, pt_I_wl: payload.pt_I_wl })) { if (arr.length !== 7) { uni.showToast({ title: `${name} 需填满7项`, icon: 'none' }); return } }
      try {
        const res = await apiRequest({ url: '/api/plots/photo-devices', method: 'POST', data: payload })
        let imgs = (res && res.images_data && res.images_data.length) ? res.images_data : ((res && res.images) || [])
        // #ifdef MP-WEIXIN
        if (imgs && imgs.length && String(imgs[0]).startsWith('data:'))
          imgs = await Promise.all(imgs.map((d) => this.toWxFileFromDataUri(d, 'photo')))
        // #endif
        this.images = imgs
      } catch (e) {}
    },
    toWxFileFromDataUri(dataUri, prefix = 'photo') {
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
        try { const base64 = url.split(',')[1]; const filePath = `${wx.env.USER_DATA_PATH}/photo_${Date.now()}.png`; const fs = wx.getFileSystemManager(); fs.writeFile({ filePath, data: base64, encoding: 'base64', success: () => wx.saveImageToPhotosAlbum({ filePath, success: () => uni.showToast({ title: '已保存到相册' }) }) }) } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
        // #endif
        // #ifdef H5
        const a = document.createElement('a'); a.href = url; a.download = 'photo-devices.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
        // #endif
        return
      }
      // #ifdef H5
      const a = document.createElement('a'); a.href = url; a.download = 'photo-devices.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a)
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
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 44rpx 0 12rpx; background: #fff; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-column-gap: 16rpx; grid-row-gap: 16rpx; }
.cell { position: relative; }
.cell-index { position: absolute; top: 8rpx; right: 10rpx; background: #f2f2f2; color: #666; border-radius: 20rpx; padding: 4rpx 10rpx; font-size: 22rpx; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
</style>
