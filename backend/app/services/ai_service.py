"""
AI 对话业务逻辑：调用火山方舟（Volcano Ark）OpenAI 兼容接口。
"""
import json
import urllib.error
import urllib.request
from typing import List, Optional

from app.core.config import settings
from app.core.exceptions import AppError


def chat_with_ai(
    question: str,
    history: Optional[List[dict]] = None,
) -> str:
    """
    调用火山方舟 /chat/completions 获取 AI 回答。

    Args:
        question: 用户当前提问
        history: 可选多轮历史 [{"role":"user","content":"..."}]

    Returns:
        AI 回复文本
    """
    if not settings.ARK_API_KEY:
        raise AppError("火山方舟 API Key 未配置", "请在 backend/.env 中配置 ARK_API_KEY", 500)
    if not settings.ARK_BASE_URL:
        raise AppError("火山方舟接口地址未配置", "请在 backend/.env 中配置 ARK_BASE_URL", 500)
    if not settings.ARK_MODEL:
        raise AppError("火山方舟模型 ID 未配置", "请在 backend/.env 中配置 ARK_MODEL", 500)

    messages = [{"role": "user", "content": question}]
    for item in history or []:
        if isinstance(item, dict) and item.get("role") and item.get("content"):
            messages.append({"role": item["role"], "content": item["content"]})

    url = settings.ARK_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.ARK_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.ARK_API_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = str(exc)
        raise AppError("火山方舟接口请求失败", detail, 502) from exc
    except Exception as exc:
        raise AppError("火山方舟连接失败", str(exc), 504) from exc

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AppError("火山方舟返回格式异常", json.dumps(data, ensure_ascii=False), 502) from exc
