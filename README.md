# 微信读书阅读 Agent 后端

基于 Python FastAPI 的后端服务，对接微信读书 Skill 官方网关与 DeepSeek 大模型。

## 目录结构

```text
backend
├── main.py                  # FastAPI 入口
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
├── .gitignore
└── app
    ├── core                 # 配置、日志、异常
    ├── clients              # 微信读书网关、DeepSeek 客户端
    ├── schemas              # 请求/响应模型
    ├── services             # 业务逻辑
    └── api                  # 路由
```

## 快速开始

1. 进入项目目录并创建虚拟环境：

```powershell
cd E:\weread-reading-agent\backend
python -m venv .venv
.venv\Scripts\activate
```

2. 安装依赖：

```powershell
pip install -r requirements.txt
```

3. 创建并配置 `.env`：

```powershell
Copy-Item .env.example .env
```

至少把 `DEEPSEEK_API_KEY` 填成你自己的密钥；如果 DeepSeek 官方提供 V4 Flash，把 `DEEPSEEK_MODEL` 改成控制台里的模型名。

4. 启动服务：

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Swagger 接口文档：<http://127.0.0.1:8000/docs>

## 接口清单与测试

所有接口都使用 POST + JSON。`weread_key` 由前端传入，后端不保存、不写死。

### 1. 获取书架书籍

```text
POST /api/weread/fetch_books
```

```json
{"weread_key": "你的微信读书Key"}
```

### 2. 获取阅读统计

```text
POST /api/weread/fetch_statistics
```

```json
{"weread_key": "你的微信读书Key"}
```

### 3. 获取划线、批注、笔记（分页）

```text
POST /api/weread/fetch_notes
```

```json
{
  "weread_key": "你的微信读书Key",
  "book_id": "可选，只取某本书",
  "page": 1,
  "page_size": 20
}
```

### 4. 笔记总结

```text
POST /api/ai/summary_notes
```

```json
{
  "weread_key": "你的微信读书Key",
  "notes": "用户选中的笔记内容，可多段",
  "instruction": "可选，例如：请用 200 字总结"
}
```

### 5. 智能推荐书单

```text
POST /api/ai/recommend_book
```

```json
{
  "weread_key": "你的微信读书Key",
  "limit": 5,
  "preferences": "可选，用户自述偏好；不传则自动读取书架和阅读统计"
}
```

### 6. 导出 Markdown 报告

```text
POST /api/export/markdown
```

```json
{
  "title": "我的读书报告",
  "notes": [
    {
      "book_title": "书名",
      "chapter": "章节",
      "note_type": "highlight",
      "content": "划线内容",
      "created_time": "2026-01-01"
    }
  ]
}
```

## 错误处理

接口统一返回如下错误格式，前端可以直接展示 `message` 和 `detail`：

```json
{
  "success": false,
  "message": "错误标题",
  "detail": "详细原因",
  "status_code": 401
}
```

常见错误：`weread_key` 无效、DeepSeek API Key 缺失、外部接口超时、微信读书网关业务错误。
