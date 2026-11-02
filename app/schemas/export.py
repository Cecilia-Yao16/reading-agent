"""
Markdown 导出接口请求/响应模型
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ExportNote(BaseModel):
    """一条可导出的笔记数据。"""

    book_title: str = Field(..., description="书名")
    chapter: Optional[str] = Field(None, description="章节名称")
    note_type: str = Field("note", description="笔记类型：highlight/note/annotation 或 划线/笔记/批注")
    content: str = Field(..., description="笔记内容")
    created_time: Optional[str] = Field(None, description="笔记创建时间")


class MarkdownExportRequest(BaseModel):
    """导出 Markdown 报告请求参数。"""

    title: str = Field("微信读书笔记报告", description="报告标题")
    notes: List[ExportNote] = Field(..., description="要导出的笔记列表")


class MarkdownExportResponse(BaseModel):
    """导出 Markdown 报告返回结构。"""

    markdown: str
