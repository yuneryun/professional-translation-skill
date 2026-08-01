#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成项目版本清单 README + 修改日志模板。

用法:
    python3 make_version_readme.py <project_dir> [--md-backup <backup.md>]

产出:
    1. VERSION_README.md — 每个文件的名称/状态/说明（防"终极版是哪个"）
    2. CHANGELOG.md — 修改日志模板（时间/位置/原因/依据页码）

来源: 《World War C》翻译项目复盘教训 #6/#9 (版本管理混乱)
"""
import os
import sys
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    d = sys.argv[1]
    md_backup = None
    if '--md-backup' in sys.argv:
        i = sys.argv.index('--md-backup')
        md_backup = sys.argv[i+1]

    files = sorted(os.listdir(d))
    lines = ['# 版本清单', '', f'生成时间: {datetime.now().isoformat(timespec="minutes")}', '',
             '| 文件 | 大小 | 状态 | 说明 |', '|---|---|---|---|']
    for f in files:
        fp = os.path.join(d, f)
        if os.path.isdir(fp):
            size = 'dir'
        else:
            size = f'{os.path.getsize(fp)/1024:.0f}KB'
        lines.append(f'| {f} | {size} | ? | 待填 |')
    with open(os.path.join(d, 'VERSION_README.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    print(f'✅ VERSION_README.md 已生成: {d}')

    clog = ['# 修改日志', '',
            '| 时间 | 文件 | 位置(段/页) | 修改内容 | 原因 | 依据页码 |', '|---|---|---|---|---|---|']
    with open(os.path.join(d, 'CHANGELOG.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(clog) + '\n')
    print('✅ CHANGELOG.md 模板已生成')

    if md_backup and os.path.exists(md_backup):
        print(f'ℹ️ 提示: md 备份 {md_backup} 需在每次主文件修改后重新导出')


if __name__ == '__main__':
    main()
