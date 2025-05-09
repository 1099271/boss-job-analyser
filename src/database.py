"""
Database operation module for handling connections and CRUD operations with MySQL.
"""

import mysql.connector
from mysql.connector import Error
from loguru import logger
from config.db_config import DB_CONFIG, TABLE_PREFIX, CHARSET, COLLATION
import json


def get_connection():
    """
    创建与MySQL数据库的连接

    Returns:
        conn: MySQL连接对象，如果连接失败则返回None
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        logger.error(f"连接到MySQL时出错: {e}")
        return None


def create_tables():
    """
    创建数据表（如果不存在）
    根据BOSS直聘的数据结构创建相应的表
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 创建工作岗位表
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}jobs (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID（encryptJobId）',
            job_name VARCHAR(100) NOT NULL COMMENT '岗位名称',
            salary_desc VARCHAR(50) COMMENT '薪资描述',
            job_experience VARCHAR(50) COMMENT '工作经验要求',
            job_degree VARCHAR(50) COMMENT '学历要求',
            city_name VARCHAR(50) COMMENT '城市名称',
            city_code VARCHAR(20) COMMENT '城市代码',
            area_district VARCHAR(50) COMMENT '区域',
            business_district VARCHAR(50) COMMENT '商圈',
            lid VARCHAR(100) COMMENT '岗位标识符',
            item_id INT COMMENT '列表中的项目ID',
            security_id VARCHAR(255) COMMENT '安全ID',
            job_type INT DEFAULT 0 COMMENT '岗位类型',
            proxy_job TINYINT(1) DEFAULT 0 COMMENT '是否为代理岗位',
            anonymous TINYINT(3) DEFAULT 0 COMMENT '匿名状态',
            outland TINYINT(1) DEFAULT 0 COMMENT '是否为外地岗位',
            longitude DECIMAL(10, 6) COMMENT '经度',
            latitude DECIMAL(10, 6) COMMENT '纬度',
            is_shield TINYINT(1) DEFAULT 0 COMMENT '是否被屏蔽',
            show_top_position TINYINT(1) DEFAULT 0 COMMENT '是否置顶显示', 
            ats_direct_post TINYINT(1) DEFAULT 0 COMMENT 'ATS直接发布标志',
            days_per_week_desc VARCHAR(50) COMMENT '每周工作天数描述',
            least_month_desc VARCHAR(50) COMMENT '最短工作月数描述',
            optimal TINYINT(1) DEFAULT 0 COMMENT '是否为优质岗位',
            search_term VARCHAR(100) COMMENT '搜索关键词',
            page_number INT COMMENT '页码',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            UNIQUE KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='BOSS直聘岗位信息表';
        """
        )

        # 创建岗位标签表（多对多关系）
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}job_labels (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            label VARCHAR(50) NOT NULL COMMENT '标签内容',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='岗位标签表';
        """
        )

        # 创建岗位技能表（多对多关系）
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}job_skills (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            skill VARCHAR(50) NOT NULL COMMENT '技能内容',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='岗位技能要求表';
        """
        )

        # 创建岗位图标标志表（多对多关系）
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}job_icon_flags (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            icon_flag INT NOT NULL COMMENT '图标标志值',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='岗位图标标志表';
        """
        )

        # 创建公司（品牌）表
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}companies (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            brand_id VARCHAR(50) COMMENT '公司ID（encryptBrandId）',
            brand_name VARCHAR(100) NOT NULL COMMENT '公司名称',
            brand_logo TEXT COMMENT '公司logo URL',
            brand_stage_name VARCHAR(50) COMMENT '融资阶段',
            brand_industry VARCHAR(100) COMMENT '行业',
            industry_code INT COMMENT '行业代码',
            brand_scale_name VARCHAR(50) COMMENT '公司规模',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            UNIQUE KEY (brand_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='公司信息表';
        """
        )

        # 创建公司福利表（多对多关系）
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}company_welfare (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            welfare VARCHAR(50) NOT NULL COMMENT '福利内容',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='公司福利表';
        """
        )

        # 创建招聘者（Boss）表
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}recruiters (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            boss_id VARCHAR(50) NOT NULL COMMENT 'Boss ID（encryptBossId）',
            boss_name VARCHAR(50) COMMENT 'Boss姓名',
            boss_title VARCHAR(100) COMMENT 'Boss职位',
            boss_avatar TEXT COMMENT 'Boss头像URL',
            boss_cert TINYINT DEFAULT 0 COMMENT 'Boss认证状态',
            gold_hunter TINYINT(1) DEFAULT 0 COMMENT '是否为金牌猎头',
            boss_online TINYINT(1) DEFAULT 0 COMMENT 'Boss是否在线',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            UNIQUE KEY (boss_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='招聘者信息表';
        """
        )

        # 创建岗位-公司-招聘者关系表
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}job_company_recruiter (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            brand_id VARCHAR(50) COMMENT '公司ID',
            boss_id VARCHAR(50) COMMENT 'Boss ID',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            UNIQUE KEY (job_id),
            KEY (brand_id),
            KEY (boss_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='岗位-公司-招聘者关系表';
        """
        )

        # 创建请求记录表
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}request_logs (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            url TEXT NOT NULL COMMENT '请求URL',
            params TEXT COMMENT '请求参数',
            status_code INT COMMENT 'HTTP状态码',
            response_time DECIMAL(10,3) COMMENT '响应时间（秒）',
            total_results INT COMMENT '总结果数',
            has_more TINYINT(1) COMMENT '是否有更多结果',
            cookies TEXT COMMENT '请求使用的Cookie',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='API请求日志表';
        """
        )

        # 创建图标URL表（名称前后图标）
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {TABLE_PREFIX}name_icons (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            job_id VARCHAR(50) NOT NULL COMMENT '岗位ID',
            icon_url TEXT NOT NULL COMMENT '图标URL',
            position ENUM('before', 'after') NOT NULL COMMENT '图标位置：名称前/名称后',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            KEY (job_id)
        ) ENGINE=InnoDB DEFAULT CHARSET={CHARSET} COLLATE={COLLATION} COMMENT='名称图标表';
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


def insert_job_data(job_data, search_term=None, page_number=None):
    """
    将工作岗位数据插入数据库
    如果岗位已存在，则直接返回不做修改

    Args:
        job_data: 岗位数据字典
        search_term: 搜索关键词
        page_number: 页码

    Returns:
        bool: 操作是否成功
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # 首先检查岗位是否已存在
        job_id = job_data.get("encryptJobId")
        if not job_id:
            logger.error("岗位数据缺少encryptJobId字段")
            return False

        # 检查岗位是否已存在
        cursor.execute(
            f"SELECT 1 FROM {TABLE_PREFIX}jobs WHERE job_id = %s LIMIT 1", (job_id,)
        )
        exists = cursor.fetchone()

        if exists:
            # 岗位已存在，直接返回成功
            logger.info(f"岗位 {job_id} 已存在，跳过处理")
            return True

        # 岗位不存在，继续插入数据
        # 1. 处理招聘者数据
        if "encryptBossId" in job_data:
            boss_values = {
                "boss_id": job_data.get("encryptBossId"),
                "boss_name": job_data.get("bossName"),
                "boss_title": job_data.get("bossTitle"),
                "boss_avatar": job_data.get("bossAvatar"),
                "boss_cert": job_data.get("bossCert"),
                "gold_hunter": job_data.get("goldHunter"),
                "boss_online": int(job_data.get("bossOnline", False)),
            }

            boss_columns = ", ".join(boss_values.keys())
            boss_placeholders = ", ".join(["%s"] * len(boss_values))

            # 使用ON DUPLICATE KEY UPDATE进行更新
            boss_update = ", ".join(
                [f"{k}=VALUES({k})" for k in boss_values.keys() if k != "boss_id"]
            )

            query = f"""
                INSERT INTO {TABLE_PREFIX}recruiters ({boss_columns}) 
                VALUES ({boss_placeholders})
                ON DUPLICATE KEY UPDATE {boss_update}
            """
            cursor.execute(query, tuple(boss_values.values()))

        # 2. 处理公司数据
        brand_id = job_data.get("encryptBrandId")
        if brand_id:
            company_values = {
                "brand_id": brand_id,
                "brand_name": job_data.get("brandName"),
                "brand_logo": job_data.get("brandLogo"),
                "brand_stage_name": job_data.get("brandStageName"),
                "brand_industry": job_data.get("brandIndustry"),
                "industry_code": job_data.get("industry"),
                "brand_scale_name": job_data.get("brandScaleName"),
            }

            company_columns = ", ".join(company_values.keys())
            company_placeholders = ", ".join(["%s"] * len(company_values))

            # 使用ON DUPLICATE KEY UPDATE进行更新
            company_update = ", ".join(
                [f"{k}=VALUES({k})" for k in company_values.keys() if k != "brand_id"]
            )

            query = f"""
                INSERT INTO {TABLE_PREFIX}companies ({company_columns}) 
                VALUES ({company_placeholders})
                ON DUPLICATE KEY UPDATE {company_update}
            """
            cursor.execute(query, tuple(company_values.values()))

        # 3. 处理工作岗位基本数据
        gps = job_data.get("gps", {})
        job_values = {
            "job_id": job_data.get("encryptJobId"),
            "job_name": job_data.get("jobName"),
            "salary_desc": job_data.get("salaryDesc"),
            "job_experience": job_data.get("jobExperience"),
            "job_degree": job_data.get("jobDegree"),
            "city_name": job_data.get("cityName"),
            "city_code": job_data.get("city"),
            "area_district": job_data.get("areaDistrict"),
            "business_district": job_data.get("businessDistrict"),
            "lid": job_data.get("lid"),
            "item_id": job_data.get("itemId"),
            "security_id": job_data.get("securityId"),
            "job_type": job_data.get("jobType", 0),
            "proxy_job": job_data.get("proxyJob", 0),
            "anonymous": job_data.get("anonymous", 0),
            "outland": job_data.get("outland", 0),
            "longitude": gps.get("longitude"),
            "latitude": gps.get("latitude"),
            "is_shield": job_data.get("isShield", 0),
            "show_top_position": int(job_data.get("showTopPosition", False)),
            "ats_direct_post": int(job_data.get("atsDirectPost", False)),
            "days_per_week_desc": job_data.get("daysPerWeekDesc"),
            "least_month_desc": job_data.get("leastMonthDesc"),
            "optimal": job_data.get("optimal", 0),
            "search_term": search_term,
            "page_number": page_number,
        }

        # 过滤掉None值，避免覆盖已有数据
        job_values = {k: v for k, v in job_values.items() if v is not None}

        job_columns = ", ".join(job_values.keys())
        job_placeholders = ", ".join(["%s"] * len(job_values))

        # 使用ON DUPLICATE KEY UPDATE进行更新
        job_update = ", ".join(
            [f"{k}=VALUES({k})" for k in job_values.keys() if k != "job_id"]
        )

        query = f"""
            INSERT INTO {TABLE_PREFIX}jobs ({job_columns}) 
            VALUES ({job_placeholders})
            ON DUPLICATE KEY UPDATE {job_update}
        """
        cursor.execute(query, tuple(job_values.values()))

        job_id = job_data.get("encryptJobId")

        # 4. 处理岗位公司招聘者关系
        relation_values = {
            "job_id": job_id,
            "brand_id": brand_id,
            "boss_id": job_data.get("encryptBossId"),
        }

        relation_columns = ", ".join(relation_values.keys())
        relation_placeholders = ", ".join(["%s"] * len(relation_values))

        query = f"""
            INSERT INTO {TABLE_PREFIX}job_company_recruiter ({relation_columns}) 
            VALUES ({relation_placeholders})
            ON DUPLICATE KEY UPDATE brand_id=VALUES(brand_id), boss_id=VALUES(boss_id)
        """
        cursor.execute(query, tuple(relation_values.values()))

        # 5. 处理所有的多对多关系表

        # 5.1 岗位标签
        if "jobLabels" in job_data and job_data["jobLabels"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}job_labels WHERE job_id = %s", (job_id,)
            )

            # 插入新数据
            labels_data = [(job_id, label) for label in job_data["jobLabels"]]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}job_labels (job_id, label) VALUES (%s, %s)",
                labels_data,
            )

        # 5.2 岗位技能
        if "skills" in job_data and job_data["skills"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}job_skills WHERE job_id = %s", (job_id,)
            )

            # 插入新数据
            skills_data = [(job_id, skill) for skill in job_data["skills"]]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}job_skills (job_id, skill) VALUES (%s, %s)",
                skills_data,
            )

        # 5.3 岗位图标标志
        if "iconFlagList" in job_data and job_data["iconFlagList"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}job_icon_flags WHERE job_id = %s", (job_id,)
            )

            # 插入新数据
            icon_flags_data = [(job_id, flag) for flag in job_data["iconFlagList"]]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}job_icon_flags (job_id, icon_flag) VALUES (%s, %s)",
                icon_flags_data,
            )

        # 5.4 公司福利
        if "welfareList" in job_data and job_data["welfareList"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}company_welfare WHERE job_id = %s",
                (job_id,),
            )

            # 插入新数据
            welfare_data = [(job_id, welfare) for welfare in job_data["welfareList"]]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}company_welfare (job_id, welfare) VALUES (%s, %s)",
                welfare_data,
            )

        # 5.5 处理名称前后图标
        # 名称前图标
        if "beforeNameIcons" in job_data and job_data["beforeNameIcons"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}name_icons WHERE job_id = %s AND position = 'before'",
                (job_id,),
            )

            # 插入新数据
            icons_data = [
                (job_id, icon, "before") for icon in job_data["beforeNameIcons"]
            ]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}name_icons (job_id, icon_url, position) VALUES (%s, %s, %s)",
                icons_data,
            )

        # 名称后图标
        if "afterNameIcons" in job_data and job_data["afterNameIcons"]:
            # 先删除旧数据
            cursor.execute(
                f"DELETE FROM {TABLE_PREFIX}name_icons WHERE job_id = %s AND position = 'after'",
                (job_id,),
            )

            # 插入新数据
            icons_data = [
                (job_id, icon, "after") for icon in job_data["afterNameIcons"]
            ]
            cursor.executemany(
                f"INSERT INTO {TABLE_PREFIX}name_icons (job_id, icon_url, position) VALUES (%s, %s, %s)",
                icons_data,
            )

        conn.commit()
        logger.info(f"成功插入/更新岗位数据，ID: {job_id}")
        return True
    except Error as e:
        logger.error(f"插入数据时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def insert_request_log(
    url, params, status_code, response_time, total_results, has_more, cookies
):
    """
    记录API请求日志

    Args:
        url: 请求的URL
        params: 请求参数
        status_code: HTTP状态码
        response_time: 响应时间（秒）
        total_results: 总结果数
        has_more: 是否有更多结果
        cookies: 请求使用的Cookie

    Returns:
        bool: 操作是否成功
    """
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        params_json = json.dumps(params, ensure_ascii=False) if params else None
        cookies_json = json.dumps(cookies, ensure_ascii=False) if cookies else None

        query = f"""
            INSERT INTO {TABLE_PREFIX}request_logs 
            (url, params, status_code, response_time, total_results, has_more, cookies)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (
                url,
                params_json,
                status_code,
                response_time,
                total_results,
                has_more,
                cookies_json,
            ),
        )

        conn.commit()
        logger.info(f"成功记录API请求日志，ID: {cursor.lastrowid}")
        return True
    except Error as e:
        logger.error(f"记录API请求日志时出错: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
