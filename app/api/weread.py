"""
微信读书数据接口

对应接口清单：
- POST /api/weread/fetch_books
- POST /api/weread/fetch_statistics
- POST /api/weread/fetch_notes
"""
from fastapi import APIRouter

from app.schemas.weread import (
    ApiResponse,
    FetchBooksRequest,
    FetchNotesRequest,
    FetchStatisticsRequest,
)
from app.services import weread_service

router = APIRouter()


@router.post("/fetch_books", response_model=ApiResponse, summary="获取书架书籍列表")
async def fetch_books(payload: FetchBooksRequest) -> ApiResponse:
    """根据前端传入的 weread_key，获取微信读书书架书籍列表。"""
    data = await weread_service.fetch_books(weread_key=payload.weread_key)
    return ApiResponse(data=data)


@router.post("/fetch_statistics", response_model=ApiResponse, summary="获取阅读统计")
async def fetch_statistics(payload: FetchStatisticsRequest) -> ApiResponse:
    """获取阅读时长、阅读天数、阅读进度等统计数据。"""
    data = await weread_service.fetch_statistics(weread_key=payload.weread_key)
    return ApiResponse(data=data)


@router.post("/fetch_notes", response_model=ApiResponse, summary="获取划线/批注/笔记")
async def fetch_notes(payload: FetchNotesRequest) -> ApiResponse:
    """获取用户笔记，支持分页和按书筛选。"""
    data = await weread_service.fetch_notes(
        weread_key=payload.weread_key,
        page=payload.page,
        page_size=payload.page_size,
        book_id=payload.book_id,
    )
    return ApiResponse(data=data)
