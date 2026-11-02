"""
API 路由汇总模块

作用：把 weread、ai、export 三组接口统一注册到 /api 前缀下。
"""
from fastapi import APIRouter

from app.api import ai, export, weread

api_router = APIRouter()

# 微信读书数据接口
api_router.include_router(weread.router, prefix="/weread", tags=["微信读书数据"])

# AI 能力接口
api_router.include_router(ai.router, prefix="/ai", tags=["AI 能力"])

# 导出接口
api_router.include_router(export.router, prefix="/export", tags=["导出"])
