<template>
  <view class="page">
    <!-- 使用系统导航栏，移除自定义顶部栏 -->
    <!-- 页面标题 -->
    <view class="page-title">请选择大物实验（二）</view>

    <!-- 九宫格卡片 -->
    <view class="grid">
      <view class="card" v-for="(item, idx) in experiments" :key="idx" @click="enter(item)">
        <text class="card-text">{{ item.name }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      experiments: [
        { name: '光纤传感与通讯' },
        { name: '弗兰克赫兹' },
        { name: '超声波' },
        { name: '太阳能电池' },
        { name: '热学综合' },
        { name: '光电器件性能' },
        { name: '密里根油滴' },
        { name: '力学综合实验' }
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

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 24rpx;
  }

  .card {
    height: 180rpx;
    border-radius: 30rpx;
    background: #f5f5f7;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.06);
  }

  .card-text {
    font-size: 28rpx;
    color: #333;
    text-align: center;
    line-height: 42rpx;
  }
</style>
