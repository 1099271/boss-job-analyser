# db_config.py
# This file will store MySQL database connection details.
# For production, consider using environment variables or a .env file for sensitive information.

"""
数据库配置模块，从.env文件加载配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "dev_user"),
    "password": os.getenv("DB_PASSWORD", "Dev#@#123"),
    "database": os.getenv("DB_NAME", "dev"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# 表前缀
TABLE_PREFIX = os.getenv("TABLE_PREFIX", "boss_")

# 数据库字符集配置
CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
COLLATION = os.getenv("DB_COLLATION", "utf8mb4_unicode_ci")
