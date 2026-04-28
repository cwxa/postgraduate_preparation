"""
FlowShop日志配置模块
集中管理项目日志，支持：
- 控制台输出：只显示WARNING及以上级别（关键信息）
- 文件输出：记录DEBUG及以上级别（完整执行流程）
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "flowshop.log"
CONSOLE_LEVEL = logging.WARNING
FILE_LEVEL = logging.DEBUG
FORMATTER = logging.Formatter(
    fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def setup_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger实例

    Args:
        name: logger名称，通常使用模块名

    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(CONSOLE_LEVEL)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(FILE_LEVEL)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取logger的便捷方法"""
    return setup_logger(name)