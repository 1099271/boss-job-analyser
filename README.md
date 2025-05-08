# Python 网页爬虫和数据存储项目

这是一个用 Python 编写的网页爬虫项目，专注于爬取 JSON 格式的 API 数据，并将其存储到 MySQL 数据库中以便后续分析。

## 功能特性

- 从配置的 URL 获取 JSON 格式的数据
- 解析和处理 JSON 数据
- 将数据存储到 MySQL 数据库
- 提供命令行参数控制程序行为
- 完整的日志记录系统
- 错误处理和异常管理

## 项目结构

```
project_root/
├── config/                     # 配置文件目录
│   ├── settings.py             # 爬虫设置（URL、请求头等）
│   └── db_config.py            # 数据库连接配置
├── src/                        # 源代码目录
│   ├── database.py             # 数据库操作
│   ├── scraper.py              # 爬虫逻辑
│   └── utils.py                # 工具函数
├── logs/                       # 日志目录（自动创建）
├── .cursor/docs/               # 项目文档目录
├── venv/                       # Python虚拟环境
├── main.py                     # 主程序入口
└── requirements.txt            # 项目依赖
```

## 文档

详细的项目设计与使用说明请参阅 [../.cursor/docs/README.md](./.cursor/docs/README.md)

## 安装和配置

1. 克隆或下载此项目
2. 创建并激活 Python 虚拟环境:

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
# 或者
venv\Scripts\activate       # Windows
```

3. 安装项目依赖:

```bash
pip install -r requirements.txt
```

4. 配置数据库:

   - 在 `config/db_config.py` 中设置你的 MySQL 数据库连接信息
   - 根据需要修改表结构（在 `src/database.py` 的 `create_tables()` 函数中）

5. 配置爬虫目标:
   - 在 `config/settings.py` 中添加目标 URL 及其他设置

## 使用方法

### 基本用法

```bash
python main.py
```

### 命令行选项

- `--log FILE`: 指定日志文件路径
- `--backup`: 备份爬取的数据为 JSON 文件
- `--setup-db`: 仅设置数据库表结构，不爬取数据

示例:

```bash
# 仅创建数据库表
python main.py --setup-db

# 爬取数据并指定日志文件
python main.py --log ./my_custom_log.log
```

## 开发注意事项

- 请确保遵守网站的爬取规则和服务条款
- 控制请求频率，避免对目标服务器造成过大压力
- 请在生产环境中妥善保护数据库凭证等敏感信息

## 许可证

[根据需要添加许可证信息]
