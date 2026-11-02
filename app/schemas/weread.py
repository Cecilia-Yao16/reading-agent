"""
微信读书接口请求/响应模型

作用：用 Pydantic 声明接口入参，FastAPI 会自动校验参数。
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class WereadKeyRequest(BaseModel):
    """所有微信读书接口都需要的公共参数：weread_key。"""

    weread_key: str = Field(
        ...,
        min_length=1,
        description="微信读书 Key，由前端传入，后端作为 Bearer Token 转发给官方网关",
    )


class FetchBooksRequest(WereadKeyRequest):
    """获取书架书籍列表请求参数。"""

    page: Optional[int] = Field(1, ge=1, description="页码")
    page_size: Optional[int] = Field(50, ge=1, le=100, description="每页数量")


class FetchStatisticsRequest(WereadKeyRequest):
    """获取阅读统计请求参数。"""


class FetchNotesRequest(WereadKeyRequest):
    """获取划线、批注、笔记请求参数，支持分页。"""

    book_id: Optional[str] = Field(None, description="可选：只获取某本书的笔记")
    page: int = Field(1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    note_type: Optional[str] = Field(None, description="可选：划线/批注/笔记")


class ApiResponse(BaseModel):
    """统一的接口返回结构，前端只认这一个格式。"""

    success: bool = True
    message: str = "ok"
    data: Any = None
