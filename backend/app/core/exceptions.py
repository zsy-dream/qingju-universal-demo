"""
全局异常处理器

NOTE: 统一捕获各类异常并返回标准格式的 JSON 响应，
      避免在每个端点中重复 try/except。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger("app")


class AppException(Exception):
    """业务自定义异常基类"""

    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器到 FastAPI 实例

    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        """处理业务自定义异常"""
        logger.warning(f"业务异常：{exc.message}，路径：{request.url.path}")
        return JSONResponse(
            status_code=exc.code,
            content={"success": False, "code": exc.code, "message": exc.message},
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
        """处理 Pydantic 校验异常"""
        logger.warning(f"入参校验失败：{request.url.path}，详情：{exc.error_count()}个错误")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "code": 422,
                "message": "输入参数校验失败",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """兜底：捕获所有未处理的异常"""
        logger.error(f"未处理异常：{type(exc).__name__}: {str(exc)}，路径：{request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": 500,
                "message": "服务器内部错误，请稍后重试",
            },
        )
