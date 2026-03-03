"""
统一日志配置模块

NOTE: 使用 RotatingFileHandler 按大小切割日志，保留最近5份历史日志。
      生产环境建议日志级别设为 INFO，开发环境可用 DEBUG。
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "app", log_dir: str = "logs") -> logging.Logger:
    """
    初始化并返回统一日志实例

    Args:
        name: 日志名称
        log_dir: 日志文件目录

    Returns:
        配置完成的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 文件处理器：按大小切割，最大10MB，保留5份
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 统一日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
