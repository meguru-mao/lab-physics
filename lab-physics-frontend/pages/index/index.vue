<template>
  <view class="page">
    <!-- 页面标题 -->
    <view class="page-title">请选择大物实验（二）</view>

    <!-- 列表样式：左侧图标 + 右侧名称 -->
    <view class="list">
      <view class="list-item" v-for="(item, idx) in experiments" :key="idx" @click="enter(item)">
        <image class="icon" :src="item.icon" mode="aspectFit" />
        <text class="name">{{ item.name }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      experiments: [
        { name: '光纤传感与通讯', icon: '/static/test/fibre-optics.svg' },
        { name: '弗兰克赫兹', icon: '/static/test/fulanke.svg' },
        { name: '超声波', icon: '/static/test/ultrasonic.svg' },
        { name: '太阳能电池', icon: '/static/test/sunelec.svg' },
        { name: '热学综合', icon: '/static/test/heat.svg' },
        { name: '光电器件性能', icon: '/static/test/sunenergy.svg' },
        { name: '密里根油滴', icon: '/static/test/milikon.svg' },
        { name: '力学综合实验', icon: '/static/test/mechanics.svg' }
      ]
    }
  },
  onLoad() {
    // 仅在微信小程序端隐藏左上角的「返回/主页」按钮，保留系统导航栏
    // 避免用户回退到登录页
    // #ifdef MP-WEIXIN
    try {
      if (typeof wx !== 'undefined' && wx.hideHomeButton) {
        wx.hideHomeButton()
      }
    } catch (e) {
      // ignore
    }
    // #endif
  },
  methods: {
    enter(item) {
      const name = item.name
      let url = ''
      if (name === '光纤传感与通讯') url = '/pages/experiments/fiber'
      else if (name === '弗兰克赫兹') url = '/pages/experiments/frank'
      else if (name === '密里根油滴') url = '/pages/experiments/millikan'
      else if (name === '力学综合实验' || name === '力学实验') url = '/pages/experiments/mechanics'
      else if (name === '超声波') url = '/pages/experiments/ultrasound'
      else if (name === '太阳能电池') url = '/pages/experiments/solar-cell'
      else if (name === '热学综合') url = '/pages/experiments/thermal'
      else if (name === '光电器件性能') url = '/pages/experiments/photo-devices'
      if (url) {
        uni.navigateTo({ url })
      } else {
        uni.showToast({ title: `暂未实现：${name}`, icon: 'none' })
      }
    },
    goAdmin() {
      uni.navigateTo({ url: '/pages/admin/index' })
    }
  },
  computed: {
    isAdmin() {
      const user = uni.getStorageSync('user')
      return user && user.role === 'admin'
    }
  }
}
</script>

<style>
  .page {
    padding: 24rpx;
  }

  .page-title {
    font-size: 28rpx;
    margin: 24rpx 12rpx;
  }

  .list {
    display: flex;
    flex-direction: column;
  }

  .list-item {
    display: flex;
    align-items: center;
    padding: 24rpx;
    background: #ffffff;
    border-radius: 20rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.06);
  }

  .icon {
    width: 72rpx;
    height: 72rpx;
    margin-right: 20rpx;
  }

  .name {
    font-size: 28rpx;
    color: #333;
  }
</style>
