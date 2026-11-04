"""
全局异常处理

作用：统一返回 { success, message, detail, status_code } 结构。
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """业务异常：由接口主动抛出。"""

    def __init__(self, message: str = "业务异常", detail: str = "", status_code: int = 400):
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        logger.exception("未捕获异常: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "服务器内部错误",
                "detail": str(exc),
                "status_code": 500,
            },
        )