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
  methods: {
    goPlan() {
      uni.navigateTo({ url: '/pages/more/plan' })
    },
    joinUs() {
      uni.showModal({
        title: '加入我（们）',
        content: '内容待定。欢迎通过页面中的联系方式或项目仓库与作者联系。',
        confirmText: '知道了',
        showCancel: true
      })
    },
    feedback() {
      uni.showModal({
        title: '反馈与建议',
        content: '内容待定。您可以通过 GitHub Issue 或邮件提出建议与反馈。',
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