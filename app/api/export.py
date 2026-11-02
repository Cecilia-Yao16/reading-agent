"""
导出接口

对应接口清单：
- POST /api/export/markdown
"""
from fastapi import APIRouter

from app.schemas.export import MarkdownExportRequest, MarkdownExportResponse
from app.services.markdown_service import notes_to_markdown

router = APIRouter()


@router.post("/markdown", response_model=MarkdownExportResponse, summary="导出 Markdown 笔记报告")
async def export_markdown(payload: MarkdownExportRequest) -> MarkdownExportResponse:
    """把前端传入的笔记数据转换成 Markdown 文本，用于导出报告。"""
    markdown = notes_to_markdown(title=payload.title, notes=payload.notes)
    return MarkdownExportResponse(markdown=markdown)
