#!/usr/bin/env python3
"""
主程序入口，用于启动爬虫和数据处理任务。
"""
import os
import sys
import argparse
import json
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径，以便能够正确导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import create_tables
from src.scraper import scrape_all_targets
from src.import_json import import_all_json_files
from src.utils import (
    setup_logging,
    get_timestamp,
    save_to_json,
    load_cookies,
    save_cookies,
)
from config.settings import DEFAULT_PARAMS, BACKUP_DIR, COOKIE_FILE, JSON_RESPONSES_DIR


def main():
    """
    主函数：解析命令行参数并执行相应的操作
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="BOSS直聘网页爬虫和数据存储程序")
    parser.add_argument("--log", help="保存日志到指定文件")
    parser.add_argument(
        "--backup", action="store_true", help="备份抓取的数据为JSON文件"
    )
    parser.add_argument("--setup-db", action="store_true", help="仅设置数据库表结构")
    parser.add_argument("--max-pages", type=int, help="每个URL最大爬取页数")
    parser.add_argument("--query", help="搜索关键词，默认使用配置文件中的设置")
    parser.add_argument("--city", help="城市代码，默认使用配置文件中的设置")
    parser.add_argument(
        "--set-cookie", help="设置Cookie，格式为JSON字符串或JSON文件路径"
    )
    # 添加从本地JSON文件导入数据的参数
    parser.add_argument(
        "--import-json", action="store_true", help="从本地JSON文件导入数据"
    )
    parser.add_argument(
        "--json-dir", help=f"JSON文件所在目录，默认为 {JSON_RESPONSES_DIR}"
    )
    args = parser.parse_args()

    # 设置日志
    if args.log:
        log_file = args.log
    else:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"scraper_{get_timestamp()}.log")

    setup_logging(log_file)
    logger.info("========== 爬虫程序启动 ==========")
    logger.debug(f"Cookie文件路径: {COOKIE_FILE}")

    # 如果需要设置Cookie
    if args.set_cookie:
        try:
            if os.path.exists(args.set_cookie):
                # 如果是文件路径
                with open(args.set_cookie, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            else:
                # 如果是JSON字符串
                cookies = json.loads(args.set_cookie)

            if save_cookies(cookies):
                logger.success("成功设置Cookie")
            else:
                logger.error("设置Cookie失败")
                return
        except Exception as e:
            logger.error(f"解析Cookie时出错: {e}")
            return

    # 如果只需设置数据库
    if args.setup_db:
        logger.info("正在设置数据库表结构...")
        if create_tables():
            logger.success("数据库表设置成功")
        else:
            logger.error("数据库表设置失败")
        return

    # 确保数据库表已创建
    logger.info("检查数据库表结构...")
    if not create_tables():
        logger.error("无法设置数据库表，程序终止")
        return

    # 如果是导入本地JSON文件
    if args.import_json:
        logger.info("开始从本地JSON文件导入数据...")
        json_dir = args.json_dir if args.json_dir else JSON_RESPONSES_DIR

        # 确保目录存在
        if not os.path.exists(json_dir):
            logger.error(f"JSON响应目录不存在: {json_dir}")
            return

        start_time = datetime.now()
        result = import_all_json_files(json_dir)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if result["status"] == "success":
            logger.success(f"JSON导入任务完成，耗时 {duration:.2f} 秒")
            logger.info(f"导入结果: {result['message']}")
        else:
            logger.warning(f"JSON导入任务未完全成功: {result['message']}")

        logger.info("========== 导入程序结束 ==========")
        return

    # 准备查询参数
    params = DEFAULT_PARAMS.copy()
    if args.query:
        params["query"] = args.query
        logger.info(f"使用自定义搜索关键词: {args.query}")
    if args.city:
        params["city"] = args.city
        logger.info(f"使用自定义城市代码: {args.city}")

    # 开始爬取数据
    logger.info("开始爬取目标...")
    logger.info(f"查询参数: {params}")
    start_time = datetime.now()

    # 根据需要备份数据
    if args.backup:
        os.makedirs(BACKUP_DIR, exist_ok=True)

    success = scrape_all_targets(args.max_pages)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    if success:
        logger.success(f"爬取任务完成，耗时 {duration:.2f} 秒")
    else:
        logger.warning(f"爬取任务完成，但有一些错误发生，耗时 {duration:.2f} 秒")

    logger.info("========== 爬虫程序结束 ==========")


if __name__ == "__main__":
    main()
