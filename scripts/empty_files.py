#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob

# 目标目录
json_dir = "/www/htdocs/boss/json_responses"

# 获取目录中的所有JSON文件
json_files = glob.glob(os.path.join(json_dir, "*.json"))

print(f"找到 {len(json_files)} 个JSON文件")

# 清空每个文件的内容
for file_path in json_files:
    try:
        # 打开文件进行写操作，这会清空文件内容
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")  # 写入空字符串
        print(f"已清空文件: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"清空文件 {os.path.basename(file_path)} 时出错: {e}")

print("所有文件清空完成")
