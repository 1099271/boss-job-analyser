"""
Utility functions for the web scraper project.
"""

import logging
import json
import os
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_logging(log_file=None):
    """
    设置更详细的日志配置

    Args:
        log_file: 日志文件路径(可选)，若不提供则仅输出到控制台
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # 如果提供了日志文件路径，创建文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)

    logger.info("日志设置完成")


def save_to_json(data, filename):
    """
    将数据保存为JSON文件（作为数据备份或调试用）

    Args:
        data: 要保存的数据
        filename: 文件名

    Returns:
        bool: 操作是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f"数据已保存至 {filename}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件时出错: {e}")
        return False


def load_from_json(filename):
    """
    从JSON文件加载数据

    Args:
        filename: 文件名

    Returns:
        data: 加载的数据，错误时返回None
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"从 {filename} 加载了数据")
        return data
    except Exception as e:
        logger.error(f"加载JSON文件时出错: {e}")
        return None


def get_timestamp():
    """
    获取当前时间戳，用于文件名或日志

    Returns:
        str: 格式化的时间戳
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def handle_rate_limit(retry_after=None):
    """
    处理API速率限制，如果需要则休眠

    Args:
        retry_after: 头部中的重试时间(秒)，如果没有则使用默认值

    Returns:
        None
    """
    import time

    # 默认休眠60秒，除非指定了其他时间
    sleep_time = retry_after if retry_after else 60
    logger.warning(f"遇到速率限制，将休眠 {sleep_time} 秒")
    time.sleep(sleep_time)
