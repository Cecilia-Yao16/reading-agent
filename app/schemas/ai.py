"""
AI 接口请求/响应模型
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class SummaryNotesRequest(BaseModel):
    """笔记总结请求参数。"""

    weread_key: str = Field(..., min_length=1, description="微信读书 Key")
    notes: str = Field(..., description="用户选中的笔记内容，支持多段文本")
    instruction: str = Field("", description="可选的额外总结要求")


class RecommendBookRequest(BaseModel):
    """智能推荐书单请求参数。"""

    weread_key: str = Field(..., min_length=1, description="微信读书 Key")
    limit: int = Field(5, ge=1, le=20, description="推荐书籍数量")
    preferences: Optional[str] = Field(None, description="可选：用户自述阅读偏好")


class RecommendBookItem(BaseModel):
    """推荐书单中的单本书。"""

    title: str
    author: str = ""
    category: str = ""
    reason: str = ""
    tags: List[str] = []


class RecommendationResponse(BaseModel):
    """DeepSeek 返回的标准推荐书单。"""

    summary: str = ""
    recommendations: List[RecommendBookItem]
