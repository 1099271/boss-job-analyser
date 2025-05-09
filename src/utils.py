"""
Utility functions for the web scraper project.
"""

import json
import os
import time
from datetime import datetime
from loguru import logger
from config.settings import COOKIE_FILE, COOKIE_EXPIRY_MARGIN


# 配置loguru
def setup_logging(log_file=None):
    """
    设置更详细的日志配置

    Args:
        log_file: 日志文件路径(可选)，若不提供则仅输出到控制台
    """
    # 移除默认处理器
    logger.remove()

    # 添加控制台处理器
    logger.add(
        sink=lambda msg: print(msg),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # 如果提供了日志文件路径，添加文件处理器
    if log_file:
        logger.add(
            sink=log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",  # 日志文件大小达到10MB时轮转
            retention="30 days",  # 保留30天的日志
            level="DEBUG",
        )

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
    # 默认休眠60秒，除非指定了其他时间
    sleep_time = retry_after if retry_after else 60
    logger.warning(f"遇到速率限制，将休眠 {sleep_time} 秒")
    time.sleep(sleep_time)


def load_cookies():
    """
    从文件加载Cookie

    Returns:
        dict: Cookie字典，如果文件不存在返回空字典
    """
    if os.path.exists(COOKIE_FILE):
        cookies = load_from_json(COOKIE_FILE)
        if cookies:
            logger.info("已加载Cookie")
            return cookies
    logger.info("没有找到Cookie文件或文件为空")
    return {}


def save_cookies(cookies):
    """
    将Cookie保存到文件

    Args:
        cookies: Cookie字典

    Returns:
        bool: 操作是否成功
    """
    return save_to_json(cookies, COOKIE_FILE)


def update_cookies_from_response(response, current_cookies=None):
    """
    从响应中更新Cookie

    Args:
        response: 请求响应对象
        current_cookies: 当前的Cookie字典，如果为None则从文件加载

    Returns:
        dict: 更新后的Cookie字典
    """
    if current_cookies is None:
        current_cookies = load_cookies() or {}

    if "set-cookie" in response.headers:
        # requests库使用getlist或get_all获取所有同名header
        try:
            # 尝试使用getlist方法（requests库新版本）
            raw_cookies = response.headers.getlist("set-cookie")
        except AttributeError:
            # 如果getlist不存在，尝试获取单个值
            set_cookie = response.headers.get("set-cookie")
            if set_cookie:
                raw_cookies = [set_cookie]
            else:
                raw_cookies = []
                logger.warning("无法从响应中获取set-cookie头")

        for cookie_str in raw_cookies:
            try:
                # 简单解析set-cookie字符串
                parts = cookie_str.split(";")[0].strip().split("=", 1)
                if len(parts) == 2:
                    name, value = parts
                    current_cookies[name] = value
                    logger.debug(f"已更新Cookie: {name}")
            except Exception as e:
                logger.error(f"解析Cookie时出错: {e}")

    save_cookies(current_cookies)
    return current_cookies


def cookies_dict_to_str(cookies_dict):
    """
    将Cookie字典转换为请求头所需的字符串格式

    Args:
        cookies_dict: Cookie字典

    Returns:
        str: Cookie字符串
    """
    return "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
