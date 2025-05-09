"""
JSON文件导入模块：从本地文件夹导入JSON数据到数据库。
这是一种绕过网络爬虫的方法，通过手动保存浏览器响应数据来导入。
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from loguru import logger

from src.database import insert_job_data
from src.utils import get_timestamp


def scan_json_directory(directory_path):
    """
    扫描指定目录，获取所有JSON文件的路径

    Args:
        directory_path: 要扫描的目录路径

    Returns:
        list: 所有JSON文件的路径列表
    """
    json_files = []
    try:
        # 将路径转换为Path对象以提高可靠性
        directory = Path(directory_path)

        if not directory.exists():
            logger.error(f"目录不存在: {directory_path}")
            return []

        if not directory.is_dir():
            logger.error(f"指定路径不是目录: {directory_path}")
            return []

        # 查找所有.json文件
        json_files = list(directory.glob("*.json"))
        logger.info(f"在目录 {directory_path} 中找到 {len(json_files)} 个JSON文件")

        return json_files
    except Exception as e:
        logger.error(f"扫描目录时出错: {e}")
        return []


def parse_json_file(file_path):
    """
    解析JSON文件内容

    Args:
        file_path: JSON文件路径

    Returns:
        dict: 解析后的JSON数据，失败时返回None
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"成功解析文件: {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"解析JSON文件 {file_path} 时出错: {e}")
        return None
    except Exception as e:
        logger.error(f"读取文件 {file_path} 时出错: {e}")
        return None


def process_boss_json_file(file_path, file_info=None):
    """
    处理BOSS直聘格式的JSON文件并将数据导入数据库

    Args:
        file_path: JSON文件路径
        file_info: 文件相关信息字典，可包含search_term和page_number等

    Returns:
        tuple: (成功计数, 总数)
    """
    if file_info is None:
        file_info = {}

    search_term = file_info.get("search_term")
    page_number = file_info.get("page_number")

    json_data = parse_json_file(file_path)
    if not json_data:
        return 0, 0

    code = json_data.get("code")
    if code != 0:
        error_msg = json_data.get("message", "未知错误")
        logger.error(f"JSON文件中API返回错误: 代码 {code}, 消息: {error_msg}")
        return 0, 0

    # 提取职位列表
    zpData = json_data.get("zpData", {})
    job_list = zpData.get("jobList", [])

    if not job_list:
        logger.warning(f"文件 {file_path} 中的职位列表为空")
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
            logger.error(f"出错的文件: {file_path}")

    logger.info(
        f"从文件 {file_path} 中成功导入 {success_count}/{total_count} 条职位数据"
    )
    return success_count, total_count


def extract_file_info(file_path):
    """
    尝试从文件名提取搜索关键词和页码等信息
    假设文件名格式为: search_term_pX.json 或类似格式

    Args:
        file_path: 文件路径

    Returns:
        dict: 包含提取信息的字典
    """
    try:
        # 获取不带扩展名的文件名
        filename = Path(file_path).stem
        info = {}

        # 尝试提取页码 (假设以 _p1, _p2 等结尾)
        if "_p" in filename:
            parts = filename.split("_p")
            if len(parts) > 1 and parts[-1].isdigit():
                info["page_number"] = int(parts[-1])
                # 剩余部分可能是搜索词
                info["search_term"] = "_".join(parts[:-1])
        else:
            # 如果没有明确的页码标记，可以将整个文件名作为搜索词
            info["search_term"] = filename

        return info
    except Exception as e:
        logger.warning(f"从文件名提取信息时出错: {e}")
        return {}


def import_all_json_files(directory_path, process_file_callback=None):
    """
    处理目录中的所有JSON文件

    Args:
        directory_path: JSON文件所在目录
        process_file_callback: 处理单个文件的回调函数，默认使用process_boss_json_file

    Returns:
        dict: 导入结果统计
    """
    if process_file_callback is None:
        process_file_callback = process_boss_json_file

    json_files = scan_json_directory(directory_path)
    if not json_files:
        return {
            "status": "error",
            "message": "未找到JSON文件或目录不存在",
            "processed": 0,
        }

    start_time = datetime.now()
    total_success = 0
    total_jobs = 0
    files_processed = 0

    for file_path in json_files:
        # 尝试从文件名提取信息
        file_info = extract_file_info(file_path)

        # 处理文件
        success, total = process_file_callback(file_path, file_info)
        total_success += success
        total_jobs += total
        files_processed += 1

        # 短暂暂停，避免数据库压力
        time.sleep(0.5)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    result = {
        "status": "success" if files_processed > 0 else "warning",
        "message": f"成功处理 {files_processed} 个文件，导入 {total_success}/{total_jobs} 条数据",
        "processed": files_processed,
        "successful_imports": total_success,
        "total_jobs": total_jobs,
        "duration_seconds": duration,
    }

    logger.info(f"导入完成，耗时 {duration:.2f} 秒")
    return result
