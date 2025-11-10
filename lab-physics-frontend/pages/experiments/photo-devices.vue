<template>
  <view class="page">
    <view class="section">
      <view class="title">光电器件性能数据（10子图合成一张）</view>
      <view class="label strong">LED</view>
      <view class="field"><view class="label">I (mA)</view><textarea v-model="form.led_I" :maxlength="-1" placeholder="例如：0.4,5,10,15,20,25,30" /></view>
      <view class="field"><view class="label">V (V)</view><textarea v-model="form.led_V" :maxlength="-1" placeholder="例如：0.13,0.88,0.92,0.92,0.97,1.00,1.02" /></view>
      <view class="field"><view class="label">P (μW)</view><textarea v-model="form.led_P" :maxlength="-1" placeholder="例如：0.1,1.669,2.899,3.931,4.846,5.659,6.385" /></view>

      <view class="label strong">LD（含阈值线性拟合）</view>
      <view class="field"><view class="label">I (mA)</view><textarea v-model="form.ld_I" :maxlength="-1" placeholder="例如：0.5,3,6,9,12,15,18,21" /></view>
      <view class="field"><view class="label">V (V)</view><textarea v-model="form.ld_V" :maxlength="-1" placeholder="例如：0.14,0.92,0.97,1.00,1.03,1.07,1.10,1.13" /></view>
      <view class="field"><view class="label">P (μW)</view><textarea v-model="form.ld_P" :maxlength="-1" placeholder="例如：0.0001,0.06793,0.246,17.4,68.53,121.2,172.6,224.8" /></view>
      <view class="field"><view class="label">拟合起始索引（默认4）</view><input v-model="form.ld_linear_start_idx" type="number" placeholder="4" /></view>

      <view class="label strong">光敏二极管</view>
      <view class="field"><view class="label">照度 L (Lx)</view><textarea v-model="form.pd_L" :maxlength="-1" placeholder="例如：50,100,150,200,250,300" /></view>
      <view class="field"><view class="label">光照特性电流 I (μA)</view><textarea v-model="form.pd_I_L" :maxlength="-1" placeholder="例如：1.6,2.8,4.0,5.3,6.5,7.7" /></view>
      <view class="field"><view class="label">伏安特性电压 V (V)</view><textarea v-model="form.pd_V" :maxlength="-1" placeholder="例如：0,2,4,6,8" /></view>
      <view class="field"><view class="label">伏安特性电流 I (μA)</view><textarea v-model="form.pd_I_V" :maxlength="-1" placeholder="例如：4.8,5.0,5.2,5.4,5.6" /></view>
      <view class="field"><view class="label">光谱波长 λ (nm)</view><textarea v-model="form.pd_wl" :maxlength="-1" placeholder="例如：650,610,570,530,450,400,550" /></view>
      <view class="field"><view class="label">光谱电流 I (μA)</view><textarea v-model="form.pd_I_wl" :maxlength="-1" placeholder="例如：0,0,0,1.4,1.3,2.4,1.6" /></view>

      <view class="label strong">光敏三极管</view>
      <view class="field"><view class="label">照度 L (Lx)</view><textarea v-model="form.pt_L" :maxlength="-1" placeholder="例如：50,100,150,200,250,300" /></view>
      <view class="field"><view class="label">光照特性电流 I (mA)</view><textarea v-model="form.pt_I_L" :maxlength="-1" placeholder="例如：0.24,0.58,0.93,1.29,1.66,2.03" /></view>
      <view class="field"><view class="label">伏安特性电压 V (V)</view><textarea v-model="form.pt_V" :maxlength="-1" placeholder="例如：2,4,6,8,10" /></view>
      <view class="field"><view class="label">伏安特性电流 I (mA)</view><textarea v-model="form.pt_I_V" :maxlength="-1" placeholder="例如：1.21,1.27,1.32,1.37,1.41" /></view>
      <view class="field"><view class="label">光谱波长 λ (nm)</view><textarea v-model="form.pt_wl" :maxlength="-1" placeholder="例如：650,610,570,530,450,400,550" /></view>
      <view class="field"><view class="label">光谱电流 I (mA)</view><textarea v-model="form.pt_I_wl" :maxlength="-1" placeholder="例如：0,0,0,0.03,0.02,0.02,0.13" /></view>
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
      form: {
        led_I: '', led_V: '', led_P: '',
        ld_I: '', ld_V: '', ld_P: '', ld_linear_start_idx: '4',
        pd_L: '', pd_I_L: '', pd_V: '', pd_I_V: '', pd_wl: '', pd_I_wl: '',
        pt_L: '', pt_I_L: '', pt_V: '', pt_I_V: '', pt_wl: '', pt_I_wl: ''
      },
      images: []
    }
  },
  methods: {
    parseNums(str) { return (str || '').split(/[\,\s]+/).map(s => parseFloat(s)).filter(v => !isNaN(v)) },
    async onSubmit() {
      const f = this.form
      const required = ['led_I','led_V','led_P','ld_I','ld_V','ld_P','pd_L','pd_I_L','pd_V','pd_I_V','pd_wl','pd_I_wl','pt_L','pt_I_L','pt_V','pt_I_V','pt_wl','pt_I_wl']
      for (const k of required) {
        if (!f[k] || !this.parseNums(f[k]).length) { uni.showToast({ title: `请填写 ${k} 数据`, icon: 'none' }); return }
      }
      const payload = {
        led_I: this.parseNums(f.led_I), led_V: this.parseNums(f.led_V), led_P: this.parseNums(f.led_P),
        ld_I: this.parseNums(f.ld_I), ld_V: this.parseNums(f.ld_V), ld_P: this.parseNums(f.ld_P), ld_linear_start_idx: parseInt(f.ld_linear_start_idx || '4'),
        pd_L: this.parseNums(f.pd_L), pd_I_L: this.parseNums(f.pd_I_L), pd_V: this.parseNums(f.pd_V), pd_I_V: this.parseNums(f.pd_I_V), pd_wl: this.parseNums(f.pd_wl), pd_I_wl: this.parseNums(f.pd_I_wl),
        pt_L: this.parseNums(f.pt_L), pt_I_L: this.parseNums(f.pt_I_L), pt_V: this.parseNums(f.pt_V), pt_I_V: this.parseNums(f.pt_I_V), pt_wl: this.parseNums(f.pt_wl), pt_I_wl: this.parseNums(f.pt_I_wl),
        return_data_uri: IS_PROD
      }
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
input { width: 100%; height: 72rpx; border: 1rpx solid #eee; border-radius: 8rpx; padding: 0 12rpx; background: #fff; }
.primary { width: 100%; height: 88rpx; background: #07c160; color: #fff; border-radius: 12rpx; font-size: 30rpx; }
.secondary { margin-top: 12rpx; height: 72rpx; background: #4a90e2; color: #fff; border-radius: 12rpx; font-size: 28rpx; }
</style>