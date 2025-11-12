<template>
  <view class="page">
    <view class="title">用户管理</view>
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else>
      <view v-if="error" class="error">{{ error }}</view>
      <view v-else class="list">
        <view class="item" v-for="u in users" :key="u.user_id">
          <text>UID: {{u.user_id}}</text>
          <text> OpenID: {{u.openid}}</text>
          <text> 角色: {{u.role}}</text>
          <text> 创建: {{u.created_at}}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
  import { API_BASE, apiRequest } from '../../utils/request.js'
  export default {
    data() {
      return { users: [], loading: true, error: '' }
    },
    onLoad() {
      apiRequest({ url: API_BASE + '/api/admin/users' })
        .then(data => { this.users = data.items || [] })
        .catch(err => { this.error = (err?.data?.detail) || '没有权限或请求失败' })
        .finally(() => { this.loading = false })
      if (typeof wx !== 'undefined' && wx.showShareMenu) {
        wx.showShareMenu({ withShareTicket: true, menus: ['shareAppMessage','shareTimeline'] })
      }
    },
    onShareAppMessage() {
      return { title: '用户管理', path: '/pages/admin/index', imageUrl: '/static/logo.png' }
    },
    onShareTimeline() {
      return { title: '用户管理', query: 'from=timeline', imageUrl: '/static/logo.png' }
    }
  }
</script>

<style>
  .page { padding: 24rpx; }
  .title { font-size: 34rpx; font-weight: 600; margin-bottom: 24rpx; }
  .loading, .error { color: #999; }
  .list { display: flex; flex-direction: column; gap: 12rpx; }
  .item { padding: 16rpx; border-radius: 12rpx; background: #f5f5f7; }
</style>
