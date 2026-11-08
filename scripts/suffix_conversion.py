"""生成「后缀词性变化关系」图（内联 SVG）。

用法：python3 scripts/suffix_conversion.py out.svg
然后把输出的 <svg> 替换到 docs/vocabulary/word-formation/suffix.md 中。
"""
import sys

COLS = {"adj": 165, "noun": 495, "verb": 825}          # 三列的中心 x
NAMES = {"adj": "形容词", "noun": "名词", "verb": "动词"}
COLORS = {"adj": "#3b82f6", "noun": "#16a34a", "verb": "#e11d48"}

# 分组：(源词性, 目标词性, [(源后缀, 目标后缀), ...])
GROUPS = [
    ("adj", "noun", [("-able/-ible", "-ability/-ibility"), ("-ant/-ent", "-ance/-ence"),
                     ("-al", "-ity/-ation"), ("-ic", "-ism/-ity"),
                     ("-ive", "-ion/-ity"), ("-ous", "-ion/-osity")]),
    ("verb", "noun", [("-ate", "-ation"), ("-ify", "-ification"), ("-ize", "-ization")]),
    ("noun", "adj", [("-or/-er", "-ory/-ary"), ("-ist", "-istic")]),
    ("noun", "verb", [("-th", "-en")]),
    ("verb", "adj", [("-e/-ate", "-able/-ible")]),
]

W = 990
FONT = 20
ROW_H = 46
GROUP_GAP = 22
TOP = 90                     # 第一行的 y
PAD_X, PILL_H = 14, 32

def text_w(s):
    return len(s) * FONT * 0.6

def pill(col, y, text):
    w = text_w(text) + PAD_X * 2
    x = COLS[col] - w / 2
    c = COLORS[col]
    return (x, x + w), (
        f'<rect x="{x:.0f}" y="{y - PILL_H / 2:.0f}" width="{w:.0f}" height="{PILL_H}" rx="8" '
        f'fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-opacity="0.6"/>'
        f'<text class="sfx" x="{COLS[col]}" y="{y}">{text}</text>')

rows, y = [], TOP
for gi, (src, dst, pairs) in enumerate(GROUPS):
    if gi:
        y += GROUP_GAP
    for a, b in pairs:
        (sx0, sx1), s_svg = pill(src, y, a)
        (dx0, dx1), d_svg = pill(dst, y, b)
        # 箭头从源框边缘指向目标框边缘
        if COLS[src] < COLS[dst]:
            x1, x2 = sx1 + 12, dx0 - 14
        else:
            x1, x2 = sx0 - 12, dx1 + 14
        rows.append(f'<line class="arrow" x1="{x1:.0f}" y1="{y}" x2="{x2:.0f}" y2="{y}" marker-end="url(#pos-arrow)"/>')
        rows += [s_svg, d_svg]
        y += ROW_H
H = y - ROW_H + 40

head = []
for k, x in COLS.items():
    head.append(f'<text class="col-name" x="{x}" y="38" fill="{COLORS[k]}">{NAMES[k]}</text>')
    head.append(f'<line x1="{x - 60}" y1="58" x2="{x + 60}" y2="58" stroke="{COLORS[k]}" stroke-width="3" stroke-linecap="round"/>')

total = sum(len(p) for *_, p in GROUPS)
svg = (
    f'<svg class="suffix-conv" viewBox="0 0 {W} {H:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" '
    f'aria-label="后缀词性变化关系图：{total} 组后缀在形容词、名词、动词之间的转换，箭头指向变化后的词性">'
    '<style>'
    '.suffix-conv{width:100%;height:auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif}'
    f'.suffix-conv .sfx{{fill:var(--md-default-fg-color,#1f2937);font-size:{FONT}px;text-anchor:middle;dominant-baseline:central}}'
    '.suffix-conv .col-name{font-weight:700;font-size:25px;text-anchor:middle}'
    '.suffix-conv .arrow{stroke:var(--md-default-fg-color--light,#6b7280);stroke-width:2}'
    '.suffix-conv .arrow-head{fill:var(--md-default-fg-color--light,#6b7280)}'
    '</style>\n'
    '<defs><marker id="pos-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path class="arrow-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>\n'
    + "\n".join(head + rows) + "\n</svg>"
)
open(sys.argv[1], "w", encoding="utf-8").write(svg)
print(f"ok: {total} rows, height {H:.0f}")
