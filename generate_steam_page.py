# -*- coding: utf-8 -*-
import re
import os

def markdown_to_steam(md_content):
    # 将 Markdown 转换为 Steam BBCode
    content = md_content
    
    # 标题转换: # H1 -> [h1], ## H2 -> [h2], ### H3 -> [h3]
    content = re.sub(r'^# (.+)$', r'[h1]\1[/h1]', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'[h2]\1[/h2]', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'[h3]\1[/h3]', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'[b]\1[/b]', content, flags=re.MULTILINE)
    
    # 粗体: **text** -> [b]text[/b]
    content = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', content)
    
    # 列表: - item -> [b]·[/b] item (Steam 不直接支持标准列表标签，常用粗体圆点代替)
    content = re.sub(r'^- (.+)$', r'[b]·[/b] \1', content, flags=re.MULTILINE)
    
    # 分割线: --- -> [hr][/hr]
    content = re.sub(r'^---+$', r'[hr][/hr]', content, flags=re.MULTILINE)
    
    # 链接: [text](url) -> [url=url]text[/url]
    content = re.sub(r'\[(.+?)\]\((.+?)\)', r'[url=\2]\1[/url]', content)
    
    # 移除代码块标记
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'`(.+?)`', r'[i]\1[/i]', content) # 行内代码转斜体表示强调

    return content


def keep_latest_changelog_entries(md_content, keep=2, section_title="## 最近更新日志"):
    """在指定更新日志章节中仅保留最新的若干条。

    - 通过标题截取更新日志区域
    - 使用粗体版本号/日期行作为分隔符拆分条目
    """
    pattern = rf"({section_title})([\s\S]*?)(\n## |\Z)"
    match = re.search(pattern, md_content)
    if not match:
        return md_content

    title, body = match.group(1), match.group(2)

    # 使用包含粗体的行作为每条更新日志的开头进行拆分
    entries = re.split(r"(?=^[^\s-].*\*\*.*\*\*.*$)", body, flags=re.MULTILINE)
    entries = [entry.strip() for entry in entries if entry.strip()]
    if not entries:
        return md_content

    latest_entries = entries[-keep:]
    note = "完整更新日志见 GitHub"
    new_body = "\n\n".join(latest_entries + [note])

    prefix = md_content[: match.start(1)]
    suffix = md_content[match.end(2) :].lstrip("\n")
    rebuilt_section = f"{title}\n\n{new_body}\n\n"
    return prefix + rebuilt_section + suffix

def generate_steam_page():
    root_path = r'c:\Users\Estelle\Documents\Paradox Interactive\Stellaris\mod\better_colony_manage'
    zh_path = os.path.join(root_path, 'README.md')
    output_path = os.path.join(root_path, 'steam_page.txt')

    with open(zh_path, 'r', encoding='utf-8') as f:
        zh_content = f.read()

    zh_trimmed = keep_latest_changelog_entries(zh_content)
    final_content = markdown_to_steam(zh_trimmed)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Success! Steam page content generated at: {output_path}")

if __name__ == "__main__":
    generate_steam_page()
