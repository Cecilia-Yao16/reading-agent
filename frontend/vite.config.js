import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置：Vue 插件 + 开发服务器端口
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
})