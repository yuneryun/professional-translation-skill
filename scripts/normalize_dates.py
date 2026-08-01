#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日期规范化：中文数字年月日 → 阿拉伯数字；阿拉伯世纪 → 中文数字。

用法:
    python3 normalize_dates.py <input.docx> [output.docx]
    不指定 output 时原地修改。

规则（来自《World War C》项目）:
    1. 4位中文数字年份（1700-2100）→ 阿拉伯: 二〇二〇年 → 2020年
    2. 中文数字月份（1-12月）→ 阿拉伯: 三月 → 3月（排除"个月"时长、"月份"）
    3. 中文数字日期（1-31日）→ 阿拉伯: 三十日 → 30日
    4. 阿拉伯数字世纪 → 中文: 21世纪 → 二十一世纪
    5. 阿拉伯数字年代 → 中文: 1990年代 → 二十世纪九十年代

保护项:
    - 时长表达: 一年/十年/几十年（不匹配）
    - 专有名词: 《失落的二月》通过占位符保护
    - 逐 run 处理，保留格式
"""
import re
import sys
from docx import Document

CN = {'零':'0','〇':'0','一':'1','二':'2','两':'2','三':'3','四':'4','五':'5',
      '六':'6','七':'7','八':'8','九':'9','十':'10'}

def cn2arab(s):
    if not s: return ''
    if not any(c in '十百千万' for c in s):
        return ''.join(CN.get(c, '') for c in s)
    total, cur = 0, 0
    for c in s:
        if c in '零〇': continue
        elif c in '一二三四五六七八九': cur = int(CN[c])
        elif c == '十': total += (cur if cur else 1) * 10; cur = 0
        elif c == '百': total += (cur if cur else 1) * 100; cur = 0
        elif c == '千': total += (cur if cur else 1) * 1000; cur = 0
    total += cur
    return str(total)

def arab2cn(n):
    n = int(n); digits = '零一二三四五六七八九'
    if n == 0: return '零'
    if n < 10: return digits[n]
    if n < 20: return '十' + (digits[n-10] if n > 10 else '')
    if n < 100: return digits[n//10] + '十' + (digits[n%10] if n%10 else '')
    if n < 1000:
        s = digits[n//100] + '百'; r = n % 100
        if r == 0: return s
        if r < 10: return s + '零' + digits[r]
        return s + arab2cn(r)
    s = digits[n//1000] + '千'; r = n % 1000
    if r == 0: return s
    if r < 100: return s + '零' + arab2cn(r)
    return s + arab2cn(r)

# 专有名词保护：这些词中的数字不转换
PROTECTED = ['失落的二月', '迷失之月']

def normalize_text(text):
    for p in PROTECTED:
        text = text.replace(p, '<<PROTECTED>>')
    def fix_year(m):
        v = int(cn2arab(m.group(1)))
        return f'{v}年' if 1700 <= v <= 2100 else m.group(0)
    text = re.sub(r'([零〇一二三四五六七八九十百千]{4})年', fix_year, text)
    def fix_month(m):
        v = int(cn2arab(m.group(1)))
        return f'{v}月' if 1 <= v <= 12 else m.group(0)
    text = re.sub(r'(?<!个)(?<!月)([零〇一二三四五六七八九十]{1,3})月(?!份)', fix_month, text)
    def fix_day(m):
        v = int(cn2arab(m.group(1)))
        return f'{v}日' if 1 <= v <= 31 else m.group(0)
    text = re.sub(r'([零〇一二三四五六七八九十]{1,3})日', fix_day, text)
    def fix_century(m):
        return f'{arab2cn(m.group(1))}世纪'
    text = re.sub(r'(\d{1,2})\s*世纪', fix_century, text)
    def fix_decade(m):
        y = int(m.group(1)); century = (y - 1) // 100 + 1; decade = (y % 100) // 10 * 10
        if y >= 1000:
            s = f'{arab2cn(century)}世纪'
            if decade: s += arab2cn(decade) + '年代'
            return s
        return m.group(0)
    text = re.sub(r'(\d{4})\s*年代', fix_decade, text)
    for p in PROTECTED:
        text = text.replace('<<PROTECTED>>', p)
    return text

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else path
    doc = Document(path)
    total = 0
    for p in doc.paragraphs:
        for r in p.runs:
            if not r.text: continue
            new = normalize_text(r.text)
            if new != r.text:
                r.text = new
                total += 1
    doc.save(out)
    print(f'✅ 日期规范化完成，共 {total} 处修改: {path} → {out}')

if __name__ == '__main__':
    main()
