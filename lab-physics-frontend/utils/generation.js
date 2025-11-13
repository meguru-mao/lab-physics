export function clearPolling(ctx) {
  if (ctx.pollTimer) { clearInterval(ctx.pollTimer); ctx.pollTimer = null }
}

export async function startGeneration(ctx, apiRequest, startUrl, payload, toWxFileFromDataUri) {
  if (ctx.generating) return
  try {
    ctx.generating = true
    ctx.images = []
    const start = await apiRequest({ url: startUrl, method: 'POST', data: payload })
    const tid = start && start.task_id
    if (!tid) { ctx.generating = false; uni.showToast({ title: '任务创建失败', icon: 'none' }); return }
    ctx.taskId = tid
    if (ctx.pollTimer) clearPolling(ctx)
    ctx.pollTimer = setInterval(async () => {
      try {
        const res = await apiRequest({ url: `/api/plots/status/${ctx.taskId}`, method: 'GET' })
        if (!res || !res.status) return
        if (res.status === 'completed') {
          let imgs = (res.images_data && res.images_data.length) ? res.images_data : (res.images || [])
          if (typeof wx !== 'undefined') {
            if (imgs && imgs.length && String(imgs[0]).startsWith('data:')) {
              try {
                const files = await Promise.all(imgs.map((d) => toWxFileFromDataUri(d)))
                imgs = files
              } catch (e) {}
            }
          }
          ctx.images = imgs
          ctx.generating = false
          ctx.taskId = ''
          clearPolling(ctx)
          if (!ctx.images.length) uni.showToast({ title: '未返回图像', icon: 'none' })
        } else if (res.status === 'failed') {
          ctx.generating = false
          ctx.taskId = ''
          clearPolling(ctx)
          uni.showToast({ title: res.message || '生成失败', icon: 'none' })
        }
      } catch (e) {}
    }, 1500)
  } catch (e) { ctx.generating = false }
}

