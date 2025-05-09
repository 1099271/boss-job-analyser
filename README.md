# BOSS 直聘爬虫项目

这个项目是一个 Python 爬虫系统，用于获取 BOSS 直聘网站的招聘数据并存储到 MySQL 数据库中。

## 功能特点

- 从 BOSS 直聘 API 获取招聘数据
- 将数据存储到 MySQL 数据库中进行分析
- 支持多页数据爬取和断点续传
- 支持 Cookie 设置和自动更新
- 日志记录和数据备份功能
- 从本地 JSON 文件导入数据（绕过反爬限制）

## 环境要求

- Python 3.7+
- MySQL 5.7+

## 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置数据库

1. 编辑 `config/db_config.py` 文件，设置数据库连接信息：

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "your_database",
    "port": 3306,
}
```

2. 或者设置环境变量（推荐）：

创建 `.env` 文件，添加以下内容：

```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_PORT=3306
```

### 数据库初始化

```bash
python main.py --setup-db
```

## 使用方法

### 1. 标准网络爬取方式

```bash
# 基本使用
python main.py

# 指定搜索关键词和城市
python main.py --query "Python开发" --city "101020100"

# 限制爬取页数
python main.py --max-pages 5

# 备份JSON数据
python main.py --backup

# 保存详细日志
python main.py --log scraper.log
```

### 2. 本地 JSON 文件导入方式（规避反爬限制）

当网站有反爬机制时，可以使用浏览器手动获取数据，然后导入到数据库：

1. 浏览器中打开 BOSS 直聘，登录账号
2. 使用浏览器开发者工具 > 网络 > XHR 请求
3. 找到以下 API 请求: `https://www.zhipin.com/wapi/zpgeek/search/joblist.json`
4. 在查看响应内容后，右键保存为 JSON 文件
5. 将 JSON 文件放入 `json_responses` 目录（默认）
6. 运行导入命令：

```bash
# 从默认目录导入
python main.py --import-json

# 从指定目录导入
python main.py --import-json --json-dir /path/to/your/json/files
```

#### JSON 文件命名建议

为了更好地记录搜索条件和页码信息，建议按以下格式命名 JSON 文件：

```
搜索关键词_p页码.json
```

例如：

- `Python开发_p1.json` - 搜索"Python 开发"的第 1 页结果
- `AI技术总监_p2.json` - 搜索"AI 技术总监"的第 2 页结果

程序会尝试从文件名中提取搜索关键词和页码信息。

## 常见问题

### 遇到反爬措施

如果在使用网络爬取模式时遇到反爬限制，建议尝试以下方法：

1. 使用本地 JSON 文件导入功能
2. 设置新的 Cookie：
   ```bash
   python main.py --set-cookie cookies.json
   ```
3. 减少请求频率，增加请求间隔时间

## 许可证

MIT
