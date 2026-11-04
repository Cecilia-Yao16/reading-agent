"""
日志模块

作用：统一配置控制台日志，方便后端调试和排查问题。
"""
import logging
import sys

# 设置日志格式：时间、级别、模块、消息
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str = "weread-agent") -> logging.Logger:
    """获取一个带统一格式的日志器。"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
