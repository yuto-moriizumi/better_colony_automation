#!/usr/bin/env python3
"""
按 icon 分组 zones_info.yaml 中的条目，输出 icons_info 格式的 YAML。
用法：
  python group_zones_by_icon.py            # 读取 zones_info.yaml，写入 zones_by_icon.yaml
  python group_zones_by_icon.py -i in.yaml -o out.yaml
"""
import argparse
import sys
import os

try:
    import yaml
except ImportError:
    print("需要安装 pyyaml：pip install pyyaml", file=sys.stderr)
    sys.exit(1)

def group_zones(zones_list):
    order = []
    groups = {}
    for item in zones_list:
        zid = item.get('id') or item.get('zone') or ''
        icon = (item.get('icon') or '').strip()
        if icon not in groups:
            groups[icon] = []
            order.append(icon)
        if zid and zid not in groups[icon]:
            groups[icon].append(zid)
    #using first zone as type:e.g. first zone is 'zone_urban' then type is 'urban'

    return [{'icon': ic,
             'zones': groups[ic],
             'type': str(ic).replace('GFX_district_specialization_', '')
             }
            for ic in order]

def main():
    input_default = 'zones_info.yaml'
    output_default = 'zones_by_icon.yaml'

    with open(input_default, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    zones = data.get('zones_info')
    grouped = {'icons_info': group_zones(zones)}

    with open(output_default, 'w', encoding='utf-8') as f:
        yaml.safe_dump(grouped, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    print(f"Wrote {len(grouped['icons_info'])} groups to {output_default}")

if __name__ == '__main__':
    main()