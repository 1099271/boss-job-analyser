# settings.py
# This file will store configurations for the scraper, such as target URLs, API keys, headers, etc.
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 目标URL
TARGET_URLS = ["https://www.zhipin.com/wapi/zpgeek/search/joblist.json"]

# 默认请求参数
DEFAULT_PARAMS = {
    "page": 1,
    "pageSize": 15,
    "city": "101020100",
    "query": "AI技术总监",
    "scene": 1,
}

# 默认请求头
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# 请求重试配置
RETRY_TIMES = 3
RETRY_DELAY = 5  # 秒

# Cookie更新配置
COOKIE_FILE = os.getenv("COOKIE_FILE", "cookies.secret.json")
COOKIE_EXPIRY_MARGIN = 3600  # 提前1小时视为过期

# 数据备份配置
BACKUP_DIR = "data_backup"
