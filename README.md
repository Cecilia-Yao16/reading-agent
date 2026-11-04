[README.md](https://github.com/user-attachments/files/34362966/README.md)
# Reading Agent（书单推荐 + 3D 星球 + AI 对话）

一个完整的读书项目：内置 100 本书的推荐系统、Vue 前端和 3D 星球网站。后端用 FastAPI 提供书单推荐与 AI 对话，前端用 Vue3 + Vite + Pinia，3D 网站用 Three.js 实现可交互的星球。

## 功能

- 书单推荐：按标签和偏好关键词加权筛选，内置 100 本书、60 个标签、100 条读书笔记
- 书单列表、书籍详情、书籍笔记、统计接口
- AI 对话：对接火山方舟（Volcano Ark）OpenAI 兼容接口，支持多轮历史
- 3D 星球网站：线稿地球、建筑模块、书单推荐面板、对话助手
- Mock / Real 一键切换，不启动后端也能演示

## 目录结构

```text
reading-agent-project
├── backend/       # FastAPI 后端：书单推荐 + AI 对话
├── frontend/      # Vue3 + Vite + Pinia 前端
├── website-3d/    # 3D 星球网站（Three.js 单文件页面）
└── 变更说明.md     # 项目改造说明
```

## 快速启动

### 1. 后端（端口 8000）

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# 编辑 .env，填入火山方舟 API Key 和模型 ID
.venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

- 健康检查：http://127.0.0.1:8000/
- Swagger 文档：http://127.0.0.1:8000/docs

### 2. Vue 前端（端口 5173）

```powershell
cd frontend
npm install
npm run dev
```

- 页面：http://localhost:5173
- 默认 mock 模式，页面右上角可切换 Mock / Real

### 3. 3D 星球网站（端口 5199）

```powershell
cd website-3d
node serve.mjs . 5199
```

- 页面：http://127.0.0.1:5199/reading-agent-3d.html
- 加载到 100% 后点击 Enter the planet 进入星球
- 01 Studio = 书单推荐、02 Projects = 书单列表、03 Journal = 读书笔记、04 Contact = 对话助手
- 注意：不要直接双击 HTML 打开，ES Module 在 file:// 下会被浏览器拦截，必须通过本地服务访问

## 后端配置（backend/.env）

```env
# 火山方舟（Volcano Ark）
ARK_API_KEY=你的火山方舟API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/plan/v3
ARK_MODEL=你的模型ID，例如 deepseek-v4-flash

# CORS 允许来源，* 表示允许所有来源
CORS_ORIGINS=*
```

API Key 只放在后端 `.env`，已被 `.gitignore` 忽略，不要提交到 GitHub。

## API 一览

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/recommend/stream` | POST | SSE 流式书单推荐 |
| `/books/list` | POST | 全部书单 |
| `/books/detail` | POST | 单本书详情 |
| `/books/notes` | POST | 书籍笔记 |
| `/books/statistics` | POST | 书单统计 |
| `/api/ai/chat` | POST | AI 对话（火山方舟） |

## Mock / Real 说明

- 默认 mock：`frontend/src/api/agent.js` 与 `website-3d/lib/api/agent.js` 中 `mockEnabled = true`
- mock 用静态样例，不实现推荐算法；推荐算法在 `backend/app/services/books_service.py`
- 切换真实后端：页面按钮切换，或在控制台调用 `setMock(false)`
- 3D 页面对话助手默认也是 Mock，切到 Real 后调用 `/api/ai/chat`

## 书单数据

后端内置 100 本书 / 60 个标签 / 100 条笔记，平均评分 8.9；推荐按「标签 + 偏好关键词」加权，同分按查询种子错序。
