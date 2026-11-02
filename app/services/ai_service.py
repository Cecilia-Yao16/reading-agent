"""
AI 业务层

作用：组合 DeepSeek 客户端和微信读书数据，提供笔记总结、智能推荐书单。
"""
from app.clients.deepseek_client import DeepSeekClient
from app.core.exceptions import DeepSeekError
from app.schemas.ai import RecommendBookItem, RecommendationResponse
from app.services.weread_service import build_reading_preferences

deepseek_client = DeepSeekClient()


async def summarize_notes(weread_key: str, notes: str, instruction: str = "") -> str:
    """
    对选中的微信读书笔记做总结。

    :param weread_key: 前端传入，仅作接口参数保留，不会发给 DeepSeek
    :param notes: 用户选中的笔记内容
    :param instruction: 用户可选的额外要求，例如“请用 200 字总结”
    """
    # 隐私说明：weread_key 不写入给模型的 prompt
    extra_line = f"额外要求：{instruction}\n" if instruction else ""
    user_prompt = f"""请对以下微信读书笔记进行整理和总结，要求：
1. 提炼核心观点和主题
2. 用清晰、简洁的中文输出
3. 可以分点列出

{extra_line}
以下是用户选中的笔记内容：
{notes}"""

    messages = [
        {
            "role": "system",
            "content": "你是一位擅长读书笔记整理的阅读助手，输出要结构化、有洞察力。",
        },
        {"role": "user", "content": user_prompt},
    ]
    return await deepseek_client.chat(messages, temperature=0.3)


async def recommend_books(
    weread_key: str,
    limit: int = 5,
    preferences: str | None = None,
) -> RecommendationResponse:
    """
    根据用户阅读偏好生成标准 JSON 推荐书单。

    :param weread_key: 用于读取微信读书用户的书架和阅读统计
    :param limit: 推荐数量
    :param preferences: 可选的用户自述偏好，优先使用
    """
    # 如果前端没有传偏好文本，就自动读取微信读书数据
    preference_text = preferences or await build_reading_preferences(weread_key)

    prompt = f"""请根据用户的阅读偏好，推荐 {limit} 本值得阅读的书籍。

用户阅读偏好：
{preference_text}

要求：
1. 只返回一个标准 JSON 对象，不要输出 Markdown 代码块，不要输出任何解释文字。
2. JSON 结构必须为：
{{
  "summary": "对推荐书单的整体说明",
  "recommendations": [
    {{
      "title": "书名",
      "author": "作者",
      "category": "分类",
      "reason": "推荐理由，要结合用户偏好具体说明",
      "tags": ["标签1", "标签2"]
    }}
  ]
}}
3. 推荐理由要具体、真诚，不要空泛。"""

    messages = [
        {
            "role": "system",
            "content": "你是专业的读书推荐顾问，擅长根据用户偏好推荐高质量书籍。",
        },
        {"role": "user", "content": prompt},
    ]

    raw = await deepseek_client.chat_json(messages, temperature=0.4)
    return _parse_recommendation(raw)


def _parse_recommendation(raw: dict) -> RecommendationResponse:
    """把 DeepSeek 返回的 JSON 校验成标准结构，字段缺失时给出清晰错误。"""
    items = raw.get("recommendations")
    if not isinstance(items, list):
        raise DeepSeekError("DeepSeek 返回的推荐列表不是数组")

    recommendation_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("书名")
        if not title:
            raise DeepSeekError("推荐书籍缺少 title 字段")
        recommendation_items.append(
            RecommendBookItem(
                title=str(title),
                author=str(item.get("author") or item.get("作者") or ""),
                category=str(item.get("category") or item.get("分类") or ""),
                reason=str(item.get("reason") or item.get("推荐理由") or ""),
                tags=[str(t) for t in (item.get("tags") or [])],
            )
        )

    if not recommendation_items:
        raise DeepSeekError("DeepSeek 推荐列表为空")

    return RecommendationResponse(
        summary=str(raw.get("summary") or raw.get("整体说明") or ""),
        recommendations=recommendation_items,
    )
