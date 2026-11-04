/**
 * 应用入口：注册 Pinia，挂载根组件
 * 说明：当前挂载的是极简聊天组件 ChatView（方便直接运行调试）；
 *      整套网站页面由成员 A 在 components / views 中开发替换。
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia()) // 注册 Pinia（store 依赖它）
app.mount('#app')