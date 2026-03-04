import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

process.on('uncaughtException', (err) => {
  console.error("UNCATCHED EXCEPTION:", err);
});
process.on('unhandledRejection', (reason, promise) => {
  console.error("UNHANDLED REJECTION:", reason);
});
process.on('exit', (code) => {
  console.log("PROCESS EXIT CODE:", code);
});


export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          echarts: ['echarts']
        }
      },
      onwarn(warning, warn) {
        if (warning.code === 'CIRCULAR_DEPENDENCY') return;
        warn(warning);
      },
    }
  }

})
