"""
全局配置模块

作用：从 backend/.env 读取配置，避免散落在各个文件里。
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
    """集中管理项目配置。"""

    # CORS 允许的来源列表，默认放开所有来源，方便本地前端调试
    CORS_ORIGINS: list[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))

    # 火山方舟（Volcano Ark）
    ARK_API_KEY: str = os.getenv("ARK_API_KEY", "")
    ARK_BASE_URL: str = os.getenv("ARK_BASE_URL", "")
    ARK_MODEL: str = os.getenv("ARK_MODEL", "")


# 模块级单例，其他文件通过 from app.core.config import settings 使用
settings = Settings()
