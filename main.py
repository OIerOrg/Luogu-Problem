import requests
import gzip
import shutil
import json
import os
from tqdm import tqdm

# 下载文件
url = "https://cdn.luogu.com.cn/problemset-open/latest.ndjson.gz"
response = requests.get(url, stream=True)

# 保存压缩文件
with open("latest.ndjson.gz", "wb") as f:
    total_size = int(response.headers.get('content-length', 0))
    with tqdm(total=total_size, unit='B', unit_scale=True, desc='下载中') as bar:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)
            bar.update(len(data))

# 解压缩文件
with gzip.open("latest.ndjson.gz", "rb") as f_in:
    with open("latest.ndjson", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

# 难度映射表
difficulty_mapping = {
    1: "入门",
    2: "普及-",
    3: "普及/提高-",
    4: "普及+/提高",
    5: "提高+/省选-",
    6: "省选/NOI-",
    7: "NOI/NOI+/CTSC"
}

# 创建一个文件夹用来存放题目
os.makedirs("problems", exist_ok=True)

# 读取 NDJSON 文件
with open("latest.ndjson", "r", encoding="utf-8") as file:
    lines = file.readlines()

# 处理每一行并生成 Markdown 文件
for line in tqdm(lines, desc="生成中", unit="题"):
    problem = json.loads(line)
    
    # 构建 Markdown 文件的内容
    pid = problem["pid"]
    title = problem["title"]
    difficulty = difficulty_mapping.get(problem["difficulty"], "暂无评定")  # 默认未知
    
    # 添加样例内容
    samples_content = ""
    for index, sample in enumerate(problem.get("samples", [])):
        samples_content += f"### 样例输入 #{index + 1}\n```\n{sample[0]}\n```\n"
        samples_content += f"### 样例输出 #{index + 1}\n```\n{sample[1]}\n```\n"

    # 创建 Markdown 文件的内容
    content = f"""---
title: "{title}"
layout: "post"
diff: {difficulty}
pid: {pid}
tag: {problem['tags']}
---

<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>

# {title}
"""

    # 检查并添加每个部分
    if problem.get("background"):
        content += f"## 题目背景\n\n{problem['background']}\n"

    if problem.get("description"):
        content += f"## 题目描述\n\n{problem['description']}\n"

    if problem.get("inputFormat"):
        content += f"## 输入格式\n\n{problem['inputFormat']}\n"

    if problem.get("outputFormat"):
        content += f"## 输出格式\n\n{problem['outputFormat']}\n"

    if samples_content:
        content += f"## 样例\n\n{samples_content}"

    if problem.get("hint"):
        content += f"## 提示\n\n{problem['hint']}\n"

    if problem.get("translation"):
        content += f"## 题目翻译\n\n{problem['translation']}\n"

    # 写入 Markdown 文件
    filename = f"problems/{pid}.md"
    with open(filename, "w", encoding="utf-8") as md_file:
        md_file.write(content)
