"""
AI 能力接口

对应接口清单：
- POST /api/ai/summary_notes
- POST /api/ai/recommend_book
"""
from fastapi import APIRouter

from app.schemas.ai import RecommendBookRequest, RecommendationResponse, SummaryNotesRequest
from app.schemas.weread import ApiResponse
from app.services import ai_service

router = APIRouter()


@router.post("/summary_notes", response_model=ApiResponse, summary="笔记总结")
async def summary_notes(payload: SummaryNotesRequest) -> ApiResponse:
    """调用 DeepSeek 对选中的笔记生成总结文本。"""
    summary = await ai_service.summarize_notes(
        weread_key=payload.weread_key,
        notes=payload.notes,
        instruction=payload.instruction,
    )
    return ApiResponse(data={"summary": summary})


@router.post("/recommend_book", response_model=RecommendationResponse, summary="智能推荐书单")
async def recommend_book(payload: RecommendBookRequest) -> RecommendationResponse:
    """读取用户阅读偏好，调用 DeepSeek 生成标准 JSON 推荐书单。"""
    result = await ai_service.recommend_books(
        weread_key=payload.weread_key,
        limit=payload.limit,
        preferences=payload.preferences,
    )
    return result
