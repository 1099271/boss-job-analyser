"""
Web scraper module for fetching and processing JSON data from target URLs.
"""

import requests
import json
import logging
import time
from datetime import datetime
from config.settings import TARGET_URLS, DEFAULT_HEADERS
from src.database import insert_data, batch_insert

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_data(url, headers=None, params=None):
    """
    从指定URL获取JSON数据

    Args:
        url: 目标URL
        headers: HTTP请求头(可选)
        params: URL参数(可选)

    Returns:
        data: 解析后的JSON数据，错误时返回None
    """
    if headers is None:
        headers = DEFAULT_HEADERS

    try:
        logger.info(f"正在从 {url} 获取数据")
        response = requests.get(url, headers=headers, params=params, timeout=30)

        # 检查HTTP状态码
        response.raise_for_status()

        # 解析JSON
        data = response.json()
        logger.info(f"成功获取数据 ({len(str(data))} 字节)")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        return None


def process_json_data(json_data):
    """
    处理JSON数据并将其转换为适合存储的格式

    Args:
        json_data: 从API获取的原始JSON数据

    Returns:
        processed_data: 处理后的数据列表
    """
    if not json_data:
        return []

    processed_data = []

    # 这里的处理逻辑取决于您的实际数据结构
    # 以下是一个示例，您需要根据实际JSON结构修改
    try:
        # 假设json_data是一个字典，含有'items'键，它的值是一个数据列表
        items = json_data.get("items", [])

        for item in items:
            # 根据实际数据结构提取所需字段
            processed_item = {
                "title": item.get("title", ""),
                "content": item.get("description", ""),
                "url": item.get("link", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "api",
            }
            processed_data.append(processed_item)

        logger.info(f"成功处理 {len(processed_data)} 条数据")
        return processed_data
    except Exception as e:
        logger.error(f"处理数据时出错: {e}")
        return []


def scrape_all_targets():
    """
    爬取所有目标URL并存储数据

    Returns:
        bool: 操作是否成功
    """
    if not TARGET_URLS:
        logger.warning("没有目标URL配置")
        return False

    success = True

    for url in TARGET_URLS:
        try:
            # 获取数据
            raw_data = fetch_data(url)
            if not raw_data:
                logger.warning(f"无法从 {url} 获取数据，跳过")
                continue

            # 处理数据
            processed_data = process_json_data(raw_data)
            if not processed_data:
                logger.warning(f"处理来自 {url} 的数据时没有结果，跳过")
                continue

            # 存储数据
            if len(processed_data) == 1:
                success = insert_data(processed_data[0]) and success
            else:
                success = batch_insert(processed_data) and success

            # 如果有多个URL，适当休眠以避免请求过于频繁
            if len(TARGET_URLS) > 1:
                time.sleep(2)  # 休眠2秒

        except Exception as e:
            logger.error(f"处理URL {url} 时发生未预期的错误: {e}")
            success = False

    return success
