"""
AI 对话接口

- POST /api/ai/chat：火山方舟对话
"""
from fastapi import APIRouter

from app.schemas.ai import ChatRequest
from app.schemas.books import ApiResponse
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI 对话"])


@router.post("/chat", response_model=ApiResponse, summary="AI 对话")
async def chat(payload: ChatRequest) -> ApiResponse:
    """调用火山方舟回答用户问题。"""
    reply = ai_service.chat_with_ai(
        question=payload.question,
        history=[item.model_dump() for item in payload.history] if payload.history else None,
    )
    return ApiResponse(data={"reply": reply})
