"""
异常与全局异常处理模块

作用：
1. 定义后端自己的异常类型；
2. 注册 FastAPI 全局异常处理器；
3. 让前端收到统一、清晰的中文错误 JSON。
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """后端业务异常基类，其他异常都继承它。"""

    def __init__(self, message: str = "请求处理失败", detail: str = "", status_code: int = 500):
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)


class WereadAuthError(AppError):
    """微信读书鉴权失败：weread_key 无效或已过期。"""

    def __init__(self, detail: str = "weread_key 无效或已过期"):
        super().__init__(message="微信读书鉴权失败", detail=detail, status_code=401)


class WereadGatewayError(AppError):
    """微信读书网关返回错误。"""

    def __init__(self, detail: str = "微信读书网关返回错误"):
        super().__init__(message="微信读书网关错误", detail=detail, status_code=502)


class WereadTimeoutError(AppError):
    """微信读书网关请求超时。"""

    def __init__(self, detail: str = "微信读书网关请求超时"):
        super().__init__(message="微信读书网关请求超时", detail=detail, status_code=504)


class DeepSeekError(AppError):
    """DeepSeek 接口调用失败。"""

    def __init__(self, detail: str = "DeepSeek 接口调用失败"):
        super().__init__(message="AI 服务错误", detail=detail, status_code=502)


class DeepSeekTimeoutError(AppError):
    """DeepSeek 接口请求超时。"""

    def __init__(self, detail: str = "DeepSeek 接口请求超时"):
        super().__init__(message="AI 服务请求超时", detail=detail, status_code=504)


def register_exception_handlers(app: FastAPI) -> None:
    """把全局异常处理器注册到 FastAPI 应用上。"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """所有自定义业务异常统一走这里。"""
        logger.error("业务异常: %s - %s", exc.message, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求参数校验失败（FastAPI 自动校验）统一返回中文错误。"""
        errors = exc.errors()
        detail = "; ".join(
            f"{'.'.join(str(x) for x in err.get('loc', []))}: {err.get('msg', '参数错误')}"
            for err in errors
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "请求参数错误",
                "detail": detail or "请检查请求参数",
                "status_code": 422,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """兜底捕获所有未预料的异常，避免把堆栈直接返回给前端。"""
        logger.exception("未捕获异常: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "服务器内部错误",
                "detail": "请稍后重试或联系开发者",
                "status_code": 500,
            },
        )
