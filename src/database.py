"""
Database operation module for handling connections and CRUD operations with MySQL.
"""

import mysql.connector
from mysql.connector import Error
import logging
from config.db_config import DB_CONFIG

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_connection():
    """
    创建与MySQL数据库的连接

    Returns:
        conn: MySQL连接对象，如果连接失败则返回None
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            logger.info("成功连接到MySQL数据库")
            return conn
    except Error as e:
        logger.error(f"连接到MySQL时出错: {e}")
        return None


def create_tables():
    """
    创建数据表（如果不存在）
    这个函数应该根据您的实际数据结构来定义表结构
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 这里定义您的表结构，下面是一个示例
        # 您需要根据实际的数据结构修改这部分
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            content TEXT,
            url VARCHAR(512),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source VARCHAR(100)
        )
        """
        )

        logger.info("数据表创建成功或已存在")
        conn.commit()
        return True
    except Error as e:
        logger.error(f"创建表时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            logger.info("MySQL连接已关闭")


def insert_data(data_dict):
    """
    将抓取的数据插入数据库

    Args:
        data_dict: 包含要插入数据的字典，字段应与表结构对应

    Returns:
        bool: 操作是否成功
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 下面是一个示例，您需要根据实际表结构和数据修改
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))

        query = f"INSERT INTO scraped_data ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data_dict.values()))

        conn.commit()
        logger.info(f"成功插入数据，ID: {cursor.lastrowid}")
        return True
    except Error as e:
        logger.error(f"插入数据时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def batch_insert(data_list):
    """
    批量插入多条数据

    Args:
        data_list: 包含多个数据字典的列表

    Returns:
        bool: 操作是否成功
    """
    if not data_list:
        logger.warning("没有数据需要插入")
        return False

    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 假设所有字典有相同的键
        first_item = data_list[0]
        columns = ", ".join(first_item.keys())
        placeholders = ", ".join(["%s"] * len(first_item))

        query = f"INSERT INTO scraped_data ({columns}) VALUES ({placeholders})"

        # 准备批处理数据
        batch_data = [tuple(item.values()) for item in data_list]
        cursor.executemany(query, batch_data)

        conn.commit()
        logger.info(f"成功批量插入 {len(data_list)} 条数据")
        return True
    except Error as e:
        logger.error(f"批量插入数据时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def query_data(query, params=None):
    """
    执行查询并返回结果

    Args:
        query: SQL查询字符串
        params: 查询参数（可选）

    Returns:
        results: 查询结果列表，失败时返回None
    """
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor(dictionary=True)  # 结果以字典形式返回

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        results = cursor.fetchall()
        return results
    except Error as e:
        logger.error(f"查询数据时出错: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
