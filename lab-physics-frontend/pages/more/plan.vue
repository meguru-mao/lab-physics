<template>
  <view class="page">
    <view class="section">
      <text class="title">后续计划一：</text>
      <view class="content">
        <text>增加大学物理实验——</text>
        <text class="desc">能做，不确定何时做</text>
      </view>
    </view>

    <view class="section">
      <text class="title">后续计划二：</text>
      <view class="content">
        <text>集成学习通</text>
        <text class="desc">能做，不确定何时做</text>
      </view>
    </view>

    <view class="section">
      <text class="title">后续计划三：</text>
      <view class="content">
        <text>集成词达人</text>
        <text class="desc">能做，但不想做</text>
      </view>
    </view>

    <view class="section">
      <text class="title">后续计划四：</text>
      <view class="content">
        <text>增加拍照录入实验数据</text>
        <text class="desc">不好做，想做</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {}
</script>

<style>
  .page { padding: 24rpx; }
  .section { background: #fff; border-radius: 20rpx; padding: 28rpx 32rpx; margin-bottom: 20rpx; box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.06); }
  .title { font-size: 32rpx; color: #222; font-weight: 600; }
  .content { margin-top: 16rpx; }
  .desc { display: block; margin-top: 8rpx; color: #666; font-size: 26rpx; }
</style>