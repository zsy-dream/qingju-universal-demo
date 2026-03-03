"""
青居智算 · FastAPI 入口

NOTE: 应用启动时初始化日志系统、注册全局异常处理器、创建数据库表。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api_router import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import register_exception_handlers
from app.core.logger import setup_logger
from app.services.db_init_service import init_db

# 初始化日志（应用级别最先执行）
logger = setup_logger("app")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # 注册全局异常处理器
    register_exception_handlers(app)

    # 注册 API 路由
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def _startup() -> None:
        logger.info("青居智算服务启动中...")
        await init_db(engine)
        logger.info("数据库初始化完成")

    return app


app = create_app()
