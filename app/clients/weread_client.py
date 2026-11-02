"""
微信读书 Skill 官方网关客户端

作用：统一封装对 https://i.weread.qq.com/api/agent/gateway 的请求，
处理 Bearer Token 鉴权、超时、网关错误解析。
"""
import httpx

from app.core.config import settings
from app.core.exceptions import WereadAuthError, WereadGatewayError, WereadTimeoutError
from app.core.logger import get_logger

logger = get_logger(__name__)


class WereadClient:
    """负责调用微信读书 Skill 官方网关的客户端。"""

    def __init__(
        self,
        gateway_url: str | None = None,
        timeout: float | None = None,
    ):
        self.gateway_url = gateway_url or settings.WEREAD_GATEWAY_URL
        self.timeout = timeout or settings.REQUEST_TIMEOUT

    async def call(self, weread_key: str, action: str, params: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {weread_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "api_name": action,
            "skill_version": "1.0.3",
            **(params or {})
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(self.gateway_url, json=payload, headers=headers)
        except httpx.TimeoutException:
            logger.error("微信读书网关请求超时, action=%s", action)
            raise WereadTimeoutError(f"请求微信读书网关超时 (action={action})")
        except httpx.HTTPError as exc:
            logger.error("微信读书网关网络错误: %s", exc)
            raise WereadGatewayError(f"微信读书网关网络错误: {exc}")

        if response.status_code in (401, 403):
            logger.error("微信读书鉴权失败, status=%s", response.status_code)
            raise WereadAuthError()
        if response.status_code >= 400:
            logger.error("微信读书网关 HTTP 错误, status=%s", response.status_code)
            raise WereadGatewayError(f"微信读书网关返回 HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError:
            raise WereadGatewayError("微信读书网关返回的不是合法 JSON")

        if isinstance(data, dict):
            errcode = data.get("errcode") or data.get("code") or data.get("errno")
            errmsg = data.get("errmsg") or data.get("message") or data.get("msg")
            if errcode is not None and errcode != 0:
                logger.error("微信读书网关业务错误: %s, %s", errcode, errmsg)
                raise WereadGatewayError(errmsg or "微信读书网关业务错误")
        if "data" in data:
            return data["data"]
        return data


