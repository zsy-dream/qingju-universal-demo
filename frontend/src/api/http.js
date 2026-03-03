import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 15000
})

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

http.interceptors.response.use(
  (res) => res,
  (error) => {
    // 智能格式化错误信息，避免显示原始JSON
    let msg = error?.response?.data?.detail || error.message || '请求失败'
    
    // 如果detail是数组（FastAPI验证错误），提取第一条可读信息
    if (Array.isArray(msg)) {
      const firstError = msg[0]
      if (typeof firstError === 'object' && firstError !== null) {
        // FastAPI验证错误格式: [{"loc":["body","field"],"msg":"...","type":"..."}]
        const field = firstError.loc?.slice(-1)[0] || '字段'
        const errMsg = firstError.msg || '验证失败'
        msg = `${field}: ${errMsg}`
      } else {
        msg = msg.join('；')
      }
    }
    
    // 如果detail是对象，尝试提取可读的字符串
    if (typeof msg === 'object' && msg !== null && !Array.isArray(msg)) {
      msg = msg.message || msg.error || JSON.stringify(msg)
    }
    
    // 截断过长的错误信息
    if (typeof msg === 'string' && msg.length > 100) {
      msg = msg.substring(0, 100) + '...'
    }
    
    window.dispatchEvent(new CustomEvent('app:toast', { detail: { type: 'error', message: msg } }))
    return Promise.reject(error)
  }
)

export default http
