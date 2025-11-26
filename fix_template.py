#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

print("正在修复模板文件...")

with open('volunteer/templates/volunteer/message_wall.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有跨行的模板标签为单行
fixes = [
    (r'\{\{\s+msg\.content\s+\}\}', '{{ msg.content }}'),
    (r'\{\{\s+msg\.user\.first_name\|slice:":1"\s+\}\}', '{{ msg.user.first_name|slice:":1" }}'),
    (r'\{\{\s+msg\.user\.first_name\s+\}\}', '{{ msg.user.first_name }}'),
    (r'\{\{\s+msg\.created_at\|date:"m-d H:i"\s+\}\}', '{{ msg.created_at|date:"m-d H:i" }}'),
    (r'\{\{\s+msg\.color\s+\}\}', '{{ msg.color }}'),
    (r'\{\{\s+forloop\.\w+[^\}]*\}\}', lambda m: m.group(0).replace('\n', '').replace('  ', ' ')),
    (r'class="card-"', 'class="card-body"'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# 确保没有跨行的{{}}
content = re.sub(r'\{\{[^\}]*\n[^\}]*\}\}', lambda m: m.group(0).replace('\n', ' ').replace('  ', ' '), content)

with open('volunteer/templates/volunteer/message_wall.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("修复完成！")

# 验证
with open('volunteer/templates/volunteer/message_wall.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    has_issue = False
    for i, line in enumerate(lines, 1):
        if '{{' in line and '}}' not in line:
            print(f"警告: 第{i}行有未闭合的模板标签")
            has_issue = True
        if '}}' in line and '{{' not in line and i > 1 and '{{' in lines[i-2]:
            print(f"警告: 第{i}行可能是跨行模板标签的结尾")
            has_issue = True
    
    if not has_issue:
        print("✓ 所有模板标签都在单行内")
