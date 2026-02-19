# app/core/logger.py
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger():
    logger = logging.getLogger("nl2analysis")
    logger.setLevel(logging.DEBUG)  # 控制全局日志等级

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件输出（可滚动）
    file_handler = RotatingFileHandler(
        "logs/nl2analysis.log", maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[%(name)s] "
        "[%(filename)s:%(lineno)d] "
        "%(message)s"
        )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
