<template>
  <view class="page">
    <view class="card">
      <text class="title">作者与权益</text>
    </view>
    <view class="card">
      <text class="p">本项目作者为泥盘某24级菜鸟</text>
    </view>
    <view class="card">
      <text class="p">你可以在 GitHub 上找到该开源项目，项目地址：</text>
      <text class="link">https://github.com/meguru-mao/lab-physics.git</text>
      <text class="p">也可以通过邮箱联系作者：huiwen.mao@pondrobotics.com</text>
    </view>
    <view class="card">
      <text class="p">未经授权严禁任何商业用途。</text>
      <text class="p">因误用、滥用造成的学术问题与作者本人无关，请注意甄别。</text>
    </view>
  </view>
</template>

<script>
export default {}
</script>

<style>
  .page { padding: 24rpx; }
  .card { background: #fff; border-radius: 20rpx; padding: 28rpx 32rpx; margin-bottom: 20rpx; box-shadow: 0 6rpx 16rpx rgba(0,0,0,0.06); }
  .title { font-size: 32rpx; font-weight: 600; color: #222; }
  .p { display: block; margin-top: 8rpx; font-size: 28rpx; color: #333; line-height: 40rpx; }
  .link { display: block; margin-top: 8rpx; font-size: 28rpx; color: #1677ff; word-break: break-all; }
</style>