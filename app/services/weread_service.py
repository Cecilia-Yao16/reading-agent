"""
微信读书业务层

作用：把微信读书网关的原始调用整理成接口层直接可用的方法，
同时提供读取用户阅读偏好给 AI 使用的能力。
"""
import json
from typing import Any

from app.clients.weread_client import WereadClient

# 全局复用同一个网关客户端
weread_client = WereadClient()


async def fetch_books(weread_key: str) -> dict[str, Any]:
    """获取书架书籍列表。"""
    return await weread_client.call(weread_key=weread_key, action="/shelf/sync")


async def fetch_statistics(weread_key: str) -> dict[str, Any]:
    """获取阅读时长、阅读天数、阅读进度统计数据。"""
    return await weread_client.call(weread_key=weread_key, action="/readdata/detail")


async def fetch_notes(
    weread_key: str,
    page: int = 1,
    page_size: int = 20,
    book_id: str | None = None,
) -> dict[str, Any]:
    """获取划线、批注、笔记，支持分页。"""
    params: dict[str, Any] = {"page": page, "page_size": page_size}
    if book_id:
        params["book_id"] = book_id
    return await weread_client.call(weread_key=weread_key, action="/book/bookmarklist", params=params)


async def build_reading_preferences(weread_key: str) -> str:
    """
    读取用户书架和阅读统计，拼成一段给 DeepSeek 的阅读偏好描述。

    说明：weread_key 只用于调用微信读书网关，绝不传给 DeepSeek，保证隐私。
    """
    try:
        books_data = await fetch_books(weread_key)
        stats_data = await fetch_statistics(weread_key)
    except Exception:
        # 拉取失败不阻断推荐，让 AI 基于现有信息继续
        books_data = {}
        stats_data = {}

    # 尽量从返回数据中提取书名列表
    book_titles = _extract_book_titles(books_data)
    preference_parts = ["用户的书架书籍："]
    if book_titles:
        preference_parts.append("、".join(book_titles[:50]))
    else:
        preference_parts.append("（未能获取到书架书籍）")

    preference_parts.append("用户的阅读统计：")
    preference_parts.append(_format_data(stats_data))
    return "\n".join(preference_parts)


def _extract_book_titles(data: Any) -> list[str]:
    """从网关返回的书架数据中尝试提取书名，兼容多种常见字段名。"""
    titles: list[str] = []
    if not isinstance(data, dict):
        return titles
    # 常见列表字段：books / items / list / data
    for key in ("books", "items", "list", "data"):
        raw_list = data.get(key)
        if isinstance(raw_list, list):
            for item in raw_list:
                if not isinstance(item, dict):
                    continue
                title = (
                    item.get("title")
                    or item.get("bookTitle")
                    or item.get("name")
                    or item.get("book_name")
                )
                if title:
                    titles.append(str(title))
    return titles


def _format_data(data: Any) -> str:
    """把统计/书籍数据转成可读文本，防止 None 导致报错。"""
    if data is None:
        return "（无数据）"
    return json.dumps(data, ensure_ascii=False, indent=2)
