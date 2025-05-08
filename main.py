#!/usr/bin/env python3
"""
主程序入口，用于启动爬虫和数据处理任务。
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# 添加项目根目录到路径，以便能够正确导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import create_tables
from src.scraper import scrape_all_targets
from src.utils import setup_logging, get_timestamp, save_to_json

# 设置基本日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """
    主函数：解析命令行参数并执行相应的操作
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="网页爬虫和数据存储程序")
    parser.add_argument("--log", help="保存日志到指定文件")
    parser.add_argument(
        "--backup", action="store_true", help="备份抓取的数据为JSON文件"
    )
    parser.add_argument("--setup-db", action="store_true", help="仅设置数据库表结构")
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

    # 如果只需设置数据库
    if args.setup_db:
        logger.info("正在设置数据库表结构...")
        if create_tables():
            logger.info("数据库表设置成功")
        else:
            logger.error("数据库表设置失败")
        return

    # 确保数据库表已创建
    logger.info("检查数据库表结构...")
    if not create_tables():
        logger.error("无法设置数据库表，程序终止")
        return

    # 开始爬取数据
    logger.info("开始爬取目标...")
    start_time = datetime.now()

    success = scrape_all_targets()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    if success:
        logger.info(f"爬取任务完成，耗时 {duration:.2f} 秒")
    else:
        logger.warning(f"爬取任务完成，但有一些错误发生，耗时 {duration:.2f} 秒")

    logger.info("========== 爬虫程序结束 ==========")


if __name__ == "__main__":
    main()
