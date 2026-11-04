"""
书单推荐接口

对应接口清单：
- POST /recommend/stream（SSE 流式推荐）
- POST /books/list（全部书单）
- POST /books/detail（单本书详情）
- POST /books/notes（书籍笔记）
- POST /books/statistics（书单统计）
"""
import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.books import ApiResponse, BookDetailRequest, BookNotesRequest, RecommendRequest
from app.services import books_service

router = APIRouter()


def _sse_event(payload: dict) -> str:
    """把 JSON 包装成 SSE data 事件（前端 msgParser 按 data: 解析）。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/recommend/stream", summary="SSE 流式书单推荐")
async def recommend_stream(payload: RecommendRequest) -> StreamingResponse:
    """
    SSE 流式推荐：
    依次推送 thinking -> tool_call -> book_recommend xN -> done
    出错时推送 error 事件。
    推荐筛选逻辑全部在后端实现，前端只接收、解析、渲染。
    """

    async def event_stream():
        try:
            # 1. 思考事件
            yield _sse_event({"type": "thinking", "content": "正在检索书单库"})
            await asyncio.sleep(0.4)

            # 2. 工具调用事件
            yield _sse_event({"type": "tool_call", "content": "查询书籍数据库"})
            await asyncio.sleep(0.4)

            # 3. 后端推荐逻辑：按标签 + 偏好筛选排序
            books = books_service.recommend_books(
                tags=payload.tags,
                preference=payload.preference,
                count=payload.count,
            )
            for book in books:
                yield _sse_event({"type": "book_recommend", "data": book})
                await asyncio.sleep(0.3)

            # 4. 结束事件
            yield _sse_event({"type": "done"})
        except Exception as err:
            yield _sse_event({"type": "error", "msg": str(err)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/books/list", response_model=ApiResponse, summary="获取全部书单")
async def books_list() -> ApiResponse:
    """返回内置的全部书籍列表。"""
    return ApiResponse(data={"books": books_service.get_all_books()})


@router.post("/books/detail", response_model=ApiResponse, summary="获取单本书详情")
async def book_detail(payload: BookDetailRequest) -> ApiResponse:
    """根据 bookId 返回书籍详情。"""
    book = books_service.get_book_detail(payload.bookId)
    if not book:
        return ApiResponse(success=False, message="书籍不存在", data=None)
    return ApiResponse(data={"book": book})


@router.post("/books/notes", response_model=ApiResponse, summary="获取书籍笔记")
async def book_notes(payload: BookNotesRequest) -> ApiResponse:
    """根据 bookId 返回书籍笔记列表。"""
    notes = books_service.get_book_notes(payload.bookId)
    return ApiResponse(data={"notes": notes})


@router.post("/books/statistics", response_model=ApiResponse, summary="获取书单统计")
async def book_statistics() -> ApiResponse:
    """返回书单统计：总数、标签数、笔记数、平均评分。"""
    return ApiResponse(data={"stats": books_service.get_statistics()})