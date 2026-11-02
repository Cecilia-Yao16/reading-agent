"""
微信读书阅读 Agent 后端入口

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
    title="微信读书阅读 Agent API",
    description="对接微信读书 Skill 官方网关与 DeepSeek 大模型的阅读助手后端",
    version="1.0.0",
)

# 自动处理跨域 CORS，方便后续 Vue 前端直接对接
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 允许的来源列表
    allow_credentials=False,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册全局异常处理器，统一返回清晰的中文错误信息
register_exception_handlers(app)

# 注册所有业务路由，统一挂在 /api 前缀下
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """健康检查接口，方便确认后端是否启动成功。"""
    return {"message": "微信读书阅读 Agent 后端运行中", "docs": "/docs"}


if __name__ == "__main__":
    # 本地开发时也可以直接运行 python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
