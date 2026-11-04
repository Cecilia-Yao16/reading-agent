"""
路由汇总模块

作用：把书单推荐相关接口统一注册到应用（无 /api 前缀）。
"""
from fastapi import APIRouter

from app.api import ai, books

api_router = APIRouter()

# 书单推荐接口（SSE 流式 + 书单查询）
api_router.include_router(books.router, tags=["书单推荐"])

# AI 对话接口
api_router.include_router(ai.router)
