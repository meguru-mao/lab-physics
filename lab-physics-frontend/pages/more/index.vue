<template>
  <view class="page">
    <view class="list">
      <view class="item" @click="goPlan">
        <text class="label">后续计划</text>
        <text class="arrow">></text>
      </view>
      <view class="item" @click="joinUs">
        <text class="label">加入我（们）</text>
        <text class="arrow">></text>
      </view>
      <view class="item" @click="feedback">
        <text class="label">反馈与建议</text>
        <text class="arrow">></text>
      </view>
      <view class="item" @click="goAuthor">
        <text class="label">作者与权益</text>
        <text class="arrow">></text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  onLoad() {
    if (typeof wx !== 'undefined' && wx.showShareMenu) {
      wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
    }
  },
  onShareAppMessage() {
    return { title: '了解更多', path: '/pages/more/index', imageUrl: '/static/logo.png' }
  },
  onShareTimeline() {
    return { title: '了解更多', query: 'from=timeline', imageUrl: '/static/logo.png' }
  },
  methods: {
    goPlan() {
      uni.navigateTo({ url: '/pages/more/plan' })
    },
    joinUs() {
      uni.showModal({
        title: '加入我（们）',
        content: '欢迎通过邮箱 huiwen.mao@pondrobotics.com 联系作者',
        confirmText: '知道了',
        showCancel: true
      })
    },
    feedback() {
      uni.showModal({
        title: '反馈与建议',
        content: '您可以在github上找到该开源项目，项目地址 https://github.com/meguru-mao/lab-physics.git\n通过 issue 提出您宝贵的建议，也可以通过邮箱联系作者\nhuiwen.mao@pondrobotics.com',
        confirmText: '好的',
        showCancel: false
      })
    },
    goAuthor() {
      uni.navigateTo({ url: '/pages/more/author' })
    }
  }
}
</script>

<style>
  .page { padding: 16rpx; }
  .list { background: #fff; border-radius: 24rpx; overflow: hidden; box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.06); }
  .item { display: flex; align-items: center; justify-content: space-between; padding: 28rpx 32rpx; border-bottom: 1rpx solid #f0f0f0; }
  .item:last-child { border-bottom: none; }
  .label { font-size: 28rpx; color: #333; }
  .arrow { font-size: 28rpx; color: #bbb; }
</style>
