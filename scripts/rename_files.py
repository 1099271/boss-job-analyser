#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import re

# 目标目录
json_dir = "/www/htdocs/boss/json_responses"

# 获取目录中的所有JSON文件
json_files = glob.glob(os.path.join(json_dir, "*.json"))

print(f"找到 {len(json_files)} 个文件需要重命名")

# 为每个文件分配一个编号
# 我们要按照从大到小的顺序重命名
page_number = len(json_files)

for file_path in json_files:
    try:
        # 获取文件名和扩展名
        dir_path, old_filename = os.path.split(file_path)

        # 创建新的文件名
        new_filename = f"ai-tech-leader_p{page_number}.json"
        new_file_path = os.path.join(dir_path, new_filename)

        # 重命名文件
        os.rename(file_path, new_file_path)
        print(f"已重命名: {old_filename} -> {new_filename}")

        # 递减页码
        page_number -= 1
    except Exception as e:
        print(f"重命名文件 {os.path.basename(file_path)} 时出错: {e}")

print("所有文件重命名完成")
