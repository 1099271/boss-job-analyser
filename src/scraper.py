"""
Web scraper module for fetching and processing JSON data from target URLs.
"""

import requests
import json
import time
import traceback
import random
from datetime import datetime
from loguru import logger
from config.settings import (
    TARGET_URLS,
    DEFAULT_HEADERS,
    DEFAULT_PARAMS,
    RETRY_TIMES,
    RETRY_DELAY,
)
from src.database import insert_job_data, insert_request_log
from src.utils import load_cookies, update_cookies_from_response, cookies_dict_to_str


def fetch_data(url, headers=None, params=None, cookies=None):
    """
    从指定URL获取JSON数据

    Args:
        url: 目标URL
        headers: HTTP请求头(可选)
        params: URL参数(可选)
        cookies: Cookie字典(可选)

    Returns:
        tuple: (data, response), 解析后的JSON数据和原始响应对象，出错时data为None
    """
    if headers is None:
        headers = DEFAULT_HEADERS.copy()

    if cookies:
        # 将cookie字典转为字符串
        cookie_str = cookies_dict_to_str(cookies)
        headers["Cookie"] = cookie_str

    start_time = time.time()

    try:
        logger.info(f"正在从 {url} 获取数据")
        response = requests.get(url, headers=headers, params=params, timeout=30)

        # 计算响应时间
        response_time = time.time() - start_time

        # 更新Cookie
        updated_cookies = update_cookies_from_response(response, cookies)

        # 检查HTTP状态码
        response.raise_for_status()

        # 解析JSON
        data = response.json()
        logger.info(
            f"成功获取数据 ({len(str(data))} 字节), 耗时: {response_time:.3f}秒"
        )

        # 记录请求
        try:
            # 检查是否有错误代码
            code = data.get("code", -1)
            message = data.get("message", "")

            if code != 0:
                logger.error(f"API返回错误代码: {code}, 消息: {message}")

            total_results = (
                data.get("zpData", {}).get("resCount", 0) if code == 0 else 0
            )
            has_more = (
                data.get("zpData", {}).get("hasMore", False) if code == 0 else False
            )
            insert_request_log(
                url=url,
                params=params,
                status_code=response.status_code,
                response_time=response_time,
                total_results=total_results,
                has_more=has_more,
                cookies=cookies,
            )
        except Exception as e:
            logger.error(f"记录请求日志时出错: {e}")

        return data, response, updated_cookies
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None, None, cookies
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        return None, None, cookies


def process_boss_zhipin_data(json_data, search_term=None, page_number=None):
    """
    处理BOSS直聘的JSON数据并存储到数据库

    Args:
        json_data: 从API获取的原始JSON数据
        search_term: 搜索关键词
        page_number: 页码

    Returns:
        tuple: (成功计数, 总数)
    """
    if not json_data:
        logger.error("无数据返回")
        return 0, 0

    code = json_data.get("code")
    if code != 0:
        error_msg = json_data.get("message", "未知错误")
        logger.error(f"API返回错误: 代码 {code}, 消息: {error_msg}")
        return 0, 0

    # 提取职位列表
    zpData = json_data.get("zpData", {})
    job_list = zpData.get("jobList", [])

    if not job_list:
        logger.warning("返回的职位列表为空")
        return 0, 0

    success_count = 0
    total_count = len(job_list)

    for job in job_list:
        try:
            if insert_job_data(job, search_term, page_number):
                success_count += 1
            time.sleep(0.1)  # 添加短暂延迟，避免数据库压力过大
        except Exception as e:
            logger.error(f"处理职位数据时出错: {e}")
            logger.error(traceback.format_exc())

    logger.info(f"成功处理 {success_count}/{total_count} 条职位数据")
    return success_count, total_count


def fetch_all_pages(url, params=None, max_pages=None):
    """
    爬取所有分页数据

    Args:
        url: 目标URL
        params: 基础请求参数，会被修改用于分页
        max_pages: 最大爬取页数(可选)，默认无限制直到没有更多数据

    Returns:
        bool: 操作是否成功
    """
    if params is None:
        params = DEFAULT_PARAMS.copy()
    else:
        params = params.copy()  # 创建副本，避免修改原始对象

    # 确保page从1开始
    params["page"] = 1

    # 记录搜索关键词
    search_term = params.get("query")

    cookies = load_cookies()
    current_page = 1
    total_success = 0
    total_jobs = 0

    while True:
        logger.info(f"获取第 {current_page} 页数据")
        params["page"] = current_page

        # 添加时间戳，避免缓存
        params["_"] = int(time.time() * 1000)

        success = False
        retry_count = 0

        # 重试机制
        while retry_count < RETRY_TIMES and not success:
            data, response, cookies = fetch_data(url, params=params, cookies=cookies)

            if data and data.get("code") == 0 and "zpData" in data:
                success = True

                # 处理数据
                page_success, page_total = process_boss_zhipin_data(
                    data, search_term, current_page
                )
                total_success += page_success
                total_jobs += page_total

                # 检查是否还有更多页
                has_more = data.get("zpData", {}).get("hasMore", False)
                if not has_more:
                    logger.info(f"没有更多数据，爬取完成，共 {current_page} 页")
                    return True
            else:
                retry_count += 1
                if data:
                    logger.warning(
                        f"第 {retry_count} 次重试获取第 {current_page} 页数据，响应码: {data.get('code')}, 消息: {data.get('message', '无错误信息')}"
                    )
                else:
                    logger.warning(
                        f"第 {retry_count} 次重试获取第 {current_page} 页数据"
                    )
                time.sleep(RETRY_DELAY)

        if not success:
            logger.error(f"获取第 {current_page} 页失败，达到最大重试次数")
            return False

        # 检查是否达到最大页数限制
        if max_pages and current_page >= max_pages:
            logger.info(f"已达到最大页数限制 {max_pages}，爬取停止")
            return True

        # 下一页
        current_page += 1

        # 添加随机间隔，避免请求频率过高
        random_sleep_time = random.uniform(5, 10)  # 生成5-10之间的随机数
        logger.info(f"等待 {random_sleep_time:.2f} 秒后获取下一页数据")
        time.sleep(random_sleep_time)

    return True


def scrape_all_targets(max_pages=None):
    """
    爬取所有目标URL并存储数据

    Args:
        max_pages: 每个URL最大爬取页数

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
            fetch_success = fetch_all_pages(url, DEFAULT_PARAMS, max_pages)
            if not fetch_success:
                logger.warning(f"从 {url} 获取数据失败")
                success = False
                continue

            # 如果有多个URL，适当休眠以避免请求过于频繁
            if len(TARGET_URLS) > 1:
                time.sleep(5)  # 休眠5秒

        except Exception as e:
            logger.error(f"处理URL {url} 时发生未预期的错误: {e}")
            logger.error(traceback.format_exc())
            success = False

    return success
