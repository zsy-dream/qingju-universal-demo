import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    toasts: []
  }),
  actions: {
    pushToast(t) {
      const message = t.message || ''
      const type = t.type || 'info'
      
      // 检查是否有相同消息正在显示（防止重复提示）
      const isDuplicate = this.toasts.some(toast => 
        toast.message === message && toast.type === type
      )
      if (isDuplicate) return
      
      const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
      this.toasts.push({ id, type, message })
      setTimeout(() => {
        this.toasts = this.toasts.filter((x) => x.id !== id)
      }, 3200)
    }
  }
})
