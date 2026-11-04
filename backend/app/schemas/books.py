"""
书单推荐接口请求/响应模型
"""
from typing import Any, List

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """SSE 流式推荐请求参数。"""

    tags: List[str] = Field(default_factory=list, description="标签数组")
    preference: str = Field("", description="偏好文本，如：喜欢心理学")
    count: int = Field(5, ge=1, le=20, description="返回推荐数量")


class BookDetailRequest(BaseModel):
    """单本书详情请求参数。"""

    bookId: str = Field(..., description="书籍 id")


class BookNotesRequest(BaseModel):
    """书籍笔记请求参数。"""

    bookId: str = Field(..., description="书籍 id")


class ApiResponse(BaseModel):
    """统一响应结构，前端只认这一个格式。"""

    success: bool = True
    message: str = "ok"
    data: Any = None