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

def generate_steam_page():
    root_path = r'c:\Users\Estelle\Documents\Paradox Interactive\Stellaris\mod\better_colony_manage'
    zh_path = os.path.join(root_path, 'README.md')
    en_path = os.path.join(root_path, 'README_EN.md')
    output_path = os.path.join(root_path, 'steam_page.txt')

    with open(zh_path, 'r', encoding='utf-8') as f:
        zh_content = f.read()
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read()

    steam_zh = markdown_to_steam(zh_content)
    steam_en = markdown_to_steam(en_content)

    final_content = "[h1]Chinese / 中文[/h1]\n" + steam_zh + "\n\n[hr][/hr]\n\n" + "[h1]English / 英文[/h1]\n" + steam_en

    with open(output_path, 'w', encoding='utf-8') as f:
        f.read = f.write(final_content)
    
    print(f"Success! Steam page content generated at: {output_path}")

if __name__ == "__main__":
    generate_steam_page()
