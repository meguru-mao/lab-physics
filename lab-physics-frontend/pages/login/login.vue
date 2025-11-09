<template>
  <view class="login-page">
    <view class="content">
      <!-- 中间图标卡片 -->
      <view class="logo-card">
        <image class="logo" src="/static/logo.png" mode="aspectFit" />
      </view>

      <!-- 标语 -->
      <view class="slogan">别让绘图成为实验报告的障碍</view>

      <!-- 微信登录按钮：始终保持绿色，点击时由逻辑判断是否允许登录 -->
      <button class="wx-btn" @click="onLogin">微信登录</button>

      <!-- 协议勾选 -->
      <view class="agree">
        <checkbox-group @change="onChangeAgree">
          <checkbox value="agree" :checked="agree" />
        </checkbox-group>
        <text>我已阅读《用户协议》</text>
      </view>
    </view>
  </view>
</template>

<script>
  import { API_BASE, apiRequest } from '../../utils/request.js'

  export default {
    data() {
      return {
        agree: false
      }
    },
    methods: {
      onChangeAgree(e) {
        const val = (e && e.detail && e.detail.value) || []
        this.agree = val.includes('agree')
      },
      onLogin() {
        if (!this.agree) {
          uni.showToast({ title: '请先阅读并同意用户协议', icon: 'none' })
          return
        }
        // #ifdef MP-WEIXIN
        uni.login({
          provider: 'weixin',
          onlyAuthorize: true,
          success: (res) => {
            const code = res.code
            this.exchangeCode(code)
          },
          fail: (err) => {
            console.error('uni.login fail', err)
            uni.showToast({ title: '登录失败', icon: 'none' })
          }
        })
        // #endif

        // #ifndef MP-WEIXIN
        this.exchangeCode('DEV_CODE')
        // #endif
      },
      exchangeCode(code) {
        apiRequest({ url: API_BASE + '/api/auth/wechat', method: 'POST', data: { code } })
          .then((data) => {
            if (!data || !data.token) {
              uni.showToast({ title: '登录失败', icon: 'none' })
              return
            }
            uni.setStorageSync('token', data.token)
            uni.setStorageSync('user', data.user)
            uni.reLaunch({ url: '/pages/index/index' })
          })
          .catch((err) => {
            console.error('login request fail', err)
          })
      }
    }
  }
</script>

<style>
  .login-page {
    padding: 24rpx;
    background-color: #f4f6f9;
    min-height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center; /* 主体居中 */
  }

  .content {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    transform: translateY(-80rpx); /* 主体整体上移 */
  }

  .logo-card {
    background-color: #fff;
    margin: 36rpx auto 24rpx;
    width: 520rpx;   /* 正方形卡片 */
    height: 520rpx;  /* 正方形卡片 */
    border-radius: 24rpx;
    box-shadow: 0 8rpx 20rpx rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .logo { width: 360rpx; height: 360rpx; } /* 正方形图片 */

  .slogan {
    text-align: center;
    color: #666;
    margin: 16rpx 0 48rpx;
    font-size: 26rpx;
  }

  .wx-btn {
    width: 680rpx;
    height: 96rpx;
    line-height: 96rpx;
    margin: 0 auto;
    border-radius: 18rpx;
    background-color: #07c160; /* 微信绿色 */
    color: #fff;
    font-size: 32rpx;
    font-weight: 600;
  }

  .agree {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 28rpx;
    color: #666;
    font-size: 26rpx;
  }
</style>