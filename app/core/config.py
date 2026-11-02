"""
全局配置模块

作用：统一从 backend/.env 读取配置，避免散落在各个文件里。
提示：.env 已加入 .gitignore，绝不会提交到 Git 仓库。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 找到 backend 项目根目录（config.py 位于 app/core/，向上两级就是 backend/）
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 backend/.env；文件不存在也不会报错，只是走默认值
load_dotenv(BACKEND_DIR / ".env")


def _parse_cors_origins(value: str | None) -> list[str]:
    """把 CORS_ORIGINS 字符串解析成列表，逗号分隔。"""
    if not value or value.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings:
    """集中管理项目配置的类，后续前端对接时可直接引用。"""

    # 微信读书 Skill 官方网关地址
    WEREAD_GATEWAY_URL: str = os.getenv(
        "WEREAD_GATEWAY_URL",
        "https://i.weread.qq.com/api/agent/gateway",
    )

    # DeepSeek API 配置
    # 注意：API Key 只从 .env 读取，禁止写死在代码里
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    # 模型名以 DeepSeek 控制台为准；如官方提供 V4 Flash，请把 .env 中的模型名改成对应值
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096"))
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

    # 对外请求统一超时时间（秒），避免接口长时间卡住
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "30"))

    # CORS 允许的来源列表，默认放开所有来源，方便本地前端调试
    CORS_ORIGINS: list[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))


# 模块级单例，其他文件通过 from app.core.config import settings 使用
settings = Settings()
