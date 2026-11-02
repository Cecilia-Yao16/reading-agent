"""
DeepSeek 大模型客户端

作用：调用 DeepSeek 的 OpenAI 兼容 Chat Completions 接口。
API Key 从 backend/.env 读取，禁止硬编码。
"""
import json

import httpx

from app.core.config import settings
from app.core.exceptions import DeepSeekError, DeepSeekTimeoutError
from app.core.logger import get_logger

logger = get_logger(__name__)


class DeepSeekClient:
    """负责调用 DeepSeek 模型的客户端。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = timeout or settings.REQUEST_TIMEOUT

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """
        发送聊天请求，返回模型生成的文本。

        :param messages: OpenAI 风格的 messages 列表
        :param temperature: 生成温度，越低越稳定
        :param max_tokens: 最大生成 token 数
        """
        if not self.api_key:
            raise DeepSeekError("未配置 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填写")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or settings.DEEPSEEK_MAX_TOKENS,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=body, headers=headers)
        except httpx.TimeoutException:
            logger.error("DeepSeek 请求超时")
            raise DeepSeekTimeoutError("DeepSeek 请求超时，请稍后重试")
        except httpx.HTTPError as exc:
            logger.error("DeepSeek 网络错误: %s", exc)
            raise DeepSeekError(f"DeepSeek 网络错误: {exc}")

        # 常见错误码给出清晰提示
        if response.status_code == 401:
            raise DeepSeekError("DeepSeek API Key 无效，请检查 .env 中的 DEEPSEEK_API_KEY")
        if response.status_code == 429:
            raise DeepSeekError("DeepSeek 请求过于频繁，请稍后重试")
        if response.status_code >= 400:
            logger.error("DeepSeek HTTP 错误，status=%s", response.status_code)
            raise DeepSeekError(f"DeepSeek 返回 HTTP {response.status_code}")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content
        except (KeyError, IndexError, ValueError) as exc:
            logger.error("DeepSeek 返回格式异常: %s", exc)
            raise DeepSeekError("DeepSeek 返回格式异常")

    async def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict:
        """
        让模型返回 JSON，并自动解析成 dict。
        如果模型输出了 ```json 代码块，也会自动清理。
        """
        text = await self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        return self.parse_json(text)

    @staticmethod
    def parse_json(text: str) -> dict:
        """从模型输出中提取 JSON 对象，兼容 Markdown 代码块。"""
        if not text:
            raise DeepSeekError("DeepSeek 返回内容为空")
        cleaned = text.strip()
        # 去掉 ```json ... ``` 代码块
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            cleaned = cleaned.removeprefix("json").strip()
        # 找第一个 { 和最后一个 }，防止模型输出多余文字
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise DeepSeekError("DeepSeek 返回内容中没有 JSON 对象")
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise DeepSeekError(f"DeepSeek 返回的 JSON 解析失败: {exc}")
