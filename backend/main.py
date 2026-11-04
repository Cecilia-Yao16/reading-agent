"""
书单推荐系统后端入口

启动方式（在 backend 目录下执行）：
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

# 创建 FastAPI 实例
app = FastAPI(
    title="书单推荐系统 API",
    description="基于标签与偏好筛选的书单推荐后端（SSE 流式推荐，推荐逻辑全部在后端）",
    version="1.0.0",
)

# 跨域 CORS：默认允许所有来源，方便前端本地调试
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器，统一返回清晰的中文错误信息
register_exception_handlers(app)

# 注册业务路由（接口无 /api 前缀，见需求：POST /recommend/stream、/books/*）
app.include_router(api_router)


@app.get("/")
async def root():
    """健康检查接口，方便确认后端是否启动成功。"""
    return {"message": "书单推荐系统后端运行中", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)