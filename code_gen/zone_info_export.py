#!/usr/bin/env python3
"""
从指定目录下的 PDX 脚本文件中提取顶级对象名和 icon，导出为 YAML。
用法示例：
    python export_zones.py -s "D:\SteamLibrary\steamapps\common\Stellaris\common\zones" -o zones_info.yaml
"""
import argparse
import os
import re
from typing import List, Dict

ID_RE = re.compile(r'([A-Za-z0-9_.-]+)\s*=\s*{', re.ASCII)
ICON_RE = re.compile(r'icon\s*=\s*(?:"([^"]+)"|([A-Za-z0-9_.-]+))', re.IGNORECASE)

def _strip_comments_keep_strings(text: str) -> str:
    """去除 # 行注释 和 /* .. */ 块注释，保留字符串原样（避免字符串内的花括号干扰）。"""
    res = []
    i = 0
    n = len(text)
    in_block = False
    in_line = False
    while i < n:
        if in_block:
            if text.startswith('*/', i):
                in_block = False
                i += 2
            else:
                i += 1
            continue
        if in_line:
            if text[i] == '\n':
                in_line = False
                res.append('\n')
            i += 1
            continue
        if text.startswith('/*', i):
            in_block = True
            i += 2
            continue
        if text[i] == '#':
            in_line = True
            i += 1
            continue
        if text[i] in ('"', "'"):
            # copy entire string including escapes
            q = text[i]
            res.append(q)
            i += 1
            while i < n:
                ch = text[i]
                res.append(ch)
                i += 1
                if ch == '\\' and i < n:
                    res.append(text[i]); i += 1
                elif ch == q:
                    break
            continue
        res.append(text[i])
        i += 1
    return ''.join(res)
# ...existing code...
def extract_top_level_objects(text: str) -> List[Dict[str, str]]:
    """
    从文件文本中提取顶层对象名和其第一个 icon（若有）。
    修正了 open_brace_pos 的计算，保证正确匹配对象范围（避免把内部键当作顶层对象）。
    """
    clean = _strip_comments_keep_strings(text)
    results = []
    n = len(clean)
    i = 0
    depth = 0
    while i < n:
        ch = clean[i]
        if ch == '{':
            depth += 1
            i += 1
            continue
        if ch == '}':
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0:
            # 跳过空白后尝试匹配顶层对象定义
            j = i
            while j < n and clean[j].isspace():
                j += 1
            m = ID_RE.match(clean, j)
            if m:
                name = m.group(1)
                # m.end() 已是绝对位置，直接使用（不要再加 j）
                open_brace_pos = m.end() - 1
                if open_brace_pos < j or clean[open_brace_pos] != '{':
                    i = j + 1
                    continue
                # 向后找匹配的闭括号（考虑嵌套）
                k = open_brace_pos + 1
                d = 1
                while k < n:
                    if clean[k] == '{':
                        d += 1
                    elif clean[k] == '}':
                        d -= 1
                        if d == 0:
                            break
                    elif clean[k] in ('"', "'"):
                        # 跳过字符串内容
                        q = clean[k]
                        k += 1
                        while k < n:
                            if clean[k] == '\\':
                                k += 2
                            elif clean[k] == q:
                                k += 1
                                break
                            else:
                                k += 1
                        continue
                    k += 1
                obj_text = clean[open_brace_pos+1:k] if k > open_brace_pos else ''
                icon_m = ICON_RE.search(obj_text)
                icon = (icon_m.group(1) or icon_m.group(2)) if icon_m else ''
                results.append({'id': name, 'icon': icon})
                i = k + 1
                continue
        i += 1
    return results
# ...existing code...

def scan_dir_for_zones(base_dir: str) -> List[Dict[str,str]]:
    items = []
    for root, _, files in os.walk(base_dir):
        for fn in files:
            if not fn.lower().endswith('.txt'):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                items.extend(extract_top_level_objects(text))
            except Exception as e:
                print(f"Warning: failed to read {path}: {e}")
    return items

def to_yaml(zones: List[Dict[str,str]]) -> str:
    lines = ["zones_info:"]
    for z in zones:
        idv = z['id'].replace('"', '\\"')
        iconv = z['icon'].replace('"', '\\"') if z['icon'] else ''
        lines.append('  - id: "{}"'.format(idv))
        if iconv:
            lines.append('    icon: "{}"'.format(iconv))
        else:
            lines.append('    icon: ""')
    return "\n".join(lines) + "\n"

def main():
    p = argparse.ArgumentParser(description="导出 zones 的 id 和 icon 到 YAML")
    p.add_argument('-s', '--source', required=False,
                   default="""D:\SteamLibrary\steamapps\common\Stellaris\common\zones""",
                   help="源目录（递归搜索 .txt 文件）")
    p.add_argument('-o', '--output', required=False, default="zones_info.yaml", help="输出 YAML 文件")
    args = p.parse_args()
    zones = scan_dir_for_zones(args.source)
    # 去重并保持出现顺序
    seen = set()
    uniq = []
    for z in zones:
        if z['id'] not in seen:
            seen.add(z['id'])
            uniq.append(z)
    yaml_text = to_yaml(uniq)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(yaml_text)
    print(f"Wrote {len(uniq)} entries to {args.output}")

if __name__ == '__main__':
    main()