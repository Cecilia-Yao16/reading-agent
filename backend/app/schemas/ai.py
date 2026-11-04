"""
AI 对话接口请求/响应模型
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """一条对话历史消息。"""

    role: str = Field(..., description="user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """AI 对话请求参数。"""

    question: str = Field(..., min_length=1, description="用户提问内容")
    history: Optional[List[ChatMessage]] = Field(
        None,
        description="可选：多轮对话历史，按时间顺序从旧到新传入",
    )
