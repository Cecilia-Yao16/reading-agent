# 书单推荐系统后端

基于标签与偏好筛选的书单推荐后端（FastAPI + SSE 流式）。推荐逻辑全部在后端实现，前端只接收、解析、渲染。

## 启动方式

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 接口清单

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |
| `/recommend/stream` | POST | SSE 流式推荐（thinking → tool_call → book_recommend×N → done / error） |
| `/books/list` | POST | 获取全部书单 |
| `/books/detail` | POST | 单本书详情，入参 `bookId` |
| `/books/notes` | POST | 书籍笔记，入参 `bookId` |
| `/books/statistics` | POST | 书单统计 |

## SSE 事件格式

```json
{"type":"thinking","content":"正在检索书单库"}
{"type":"tool_call","content":"查询书籍数据库"}
{"type":"book_recommend","data":{"id":"","title":"","author":"","cover":"","desc":"","tags":[]}}
{"type":"done"}
{"type":"error","msg":"错误信息"}
```

## 目录结构

```text
backend
├── main.py                     # FastAPI 入口、CORS、健康检查
├── requirements.txt
├── .env                        # CORS 配置
└── app
    ├── api
    │   ├── router.py           # 路由汇总
    │   └── books.py            # 书单推荐接口（SSE + 书单查询）
    ├── core
    │   ├── config.py           # 全局配置
    │   ├── exceptions.py       # 异常类型与全局异常处理
    │   └── logger.py           # 日志
    ├── schemas
    │   └── books.py            # 请求/响应模型
    └── services
        └── books_service.py    # 内置书单数据 + 推荐逻辑
```