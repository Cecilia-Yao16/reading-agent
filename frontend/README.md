# 书单推荐前端（Vue3 + Vite + Pinia + SSE）

书单推荐系统前端。底层通信 / SSE 解析 / 状态托管由成员 B 封装，
推荐逻辑全部在后端，前端只做接口封装、SSE 解析、状态托管与页面渲染。

## 快速运行

```bash
npm install
npm run dev
```

默认是 **mock 模式**，无需启动后端即可调试页面：
点「开始推荐」会按 `thinking → tool_call → book_recommend×N → done` 每 600ms 推一条静态书单样例。

## 目录结构

```text
src
├─ main.js            # 应用入口（注册 Pinia）
├─ App.vue            # 根组件（挂载书单推荐页）
├─ api
│  └─ agent.js        # 底层通信：sendQuery / fetchBookList / fetchBookDetail / fetchBookNotes / fetchBookStats / stopGenerate（成员B）
├─ components
│  └─ ChatView.vue    # 书单推荐页面（筛选 + 流式卡片 + 详情 + 笔记 + 统计）
├─ store
│  └─ chat.js         # Pinia 全局状态（成员B）
├─ types
│  └─ message.js      # SSE 事件类型定义（成员B）
└─ utils
   ├─ request.js      # fetch 封装 + AbortController（成员B）
   ├─ mockStream.js   # mock SSE 流 + 开关（成员B）
   └─ msgParser.js    # SSE 分片解析器，只解析 thinking/tool_call/book_recommend/done/error（成员B）
```

## 后端地址

- 正式：`http://127.0.0.1:8000`
- 备选：`http://127.0.0.1:8001`（8000 被占用时，修改 `src/utils/request.js` 的 `BASE_URL`）
- Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`GET http://127.0.0.1:8000/`

## 接口对照

| 前端方法 | 后端接口 | 说明 |
| --- | --- | --- |
| `sendQuery({tags, preference, count})` | `POST /recommend/stream` | SSE 流式推荐 |
| `fetchBookList()` | `POST /books/list` | 全部书单 |
| `fetchBookDetail(bookId)` | `POST /books/detail` | 单本书详情 |
| `fetchBookNotes(bookId)` | `POST /books/notes` | 书籍笔记 |
| `fetchBookStats()` | `POST /books/statistics` | 书单统计 |

## mock / 真实后端切换

- 默认 mock：`src/api/agent.js` 里 `mockEnabled = true`
- 启动后端后，在页面控制台执行：
  - `chatStore.setMock(false)` → 切真实后端（SSE `POST /recommend/stream`）
  - `chatStore.setMock(true)` → 切回 mock

## 分工

- **页面**：筛选面板、流式书单卡片、详情弹窗、笔记面板、统计展示（绿色地球柔和主题）。
- **底层**：`src/api`、`src/store`、`src/utils`、`src/types`；页面不写 fetch / SSE / 解析逻辑。