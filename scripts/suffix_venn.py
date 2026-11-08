"""生成「后缀与词性」韦恩图（内联 SVG），并校验每个后缀落在正确的区域。"""
import sys

W, H = 985, 640
# 集合：名称 -> (cx, cy, rx, ry, 颜色)
SETS = {
    "adj":  (300, 330, 280, 195, "#3b82f6"),
    "noun": (650, 320, 310, 210, "#16a34a"),
    "verb": (470, 530, 180, 85,  "#e11d48"),
    "adv":  (225, 105, 160, 65,  "#d97706"),
}
NAMES = {"adj": "形容词", "noun": "名词", "verb": "动词", "adv": "副词"}
# 集合名称标签位置（放在各自独有区域的边缘）
NAME_POS = {"adj": (70, 330), "noun": (650, 128), "verb": (470, 600), "adv": (110, 95)}

# 区域：所属集合, 后缀列表, 排版框 (x0, y0, x1, y1), 列数
REGIONS = [
    ({"adv"}, ["-wise"], (225, 75, 225, 75), 1),
    ({"adj", "adv"}, ["-ward"], (255, 152, 255, 152), 1),
    ({"adj"}, ["-able/-ible", "-less", "-ish", "-ous", "-ly", "-ive", "-some", "-ed", "-y"],
     (180, 215, 290, 440), 2),
    ({"adj", "noun"}, ["-ic", "-ory", "-ary", "-al/-ial/-ical/-ual", "-ar/-ular/-icular",
                       "-ant", "-ent", "-ful"],
     (462, 215, 462, 425), 1),
    ({"adj", "noun", "verb"}, ["-ate"], (464, 464, 464, 464), 1),
    ({"adj", "verb"}, ["-en"], (372, 492, 372, 492), 1),
    ({"verb"}, ["-ize/-ise", "-fy/-ify/-efy"], (470, 543, 470, 570), 1),
    ({"noun"}, ["-ion", "-ity/-ty/-ety", "-ment",
                "-ness", "-ance/-ancy", "-ist",
                "-er", "-ence/-ency", "-or",
                "-ee", "-our/-or", "-ism",
                "-logy", "-ship", "-hood",
                "-dom", "-age", "-ure",
                "-ery", "-ry", "-th",
                "-ite", "-y"],
     (645, 200, 868, 458), 3),
]

def inside(name, x, y):
    cx, cy, rx, ry, _ = SETS[name]
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1

def text_w(s, size):
    return sum(size * (0.6 if c.isascii() else 1.0) for c in s)

def layout(box, items, cols):
    x0, y0, x1, y1 = box
    rows = -(-len(items) // cols)
    out = []
    for i, s in enumerate(items):
        r, c = divmod(i, cols)
        x = x0 + (x1 - x0) * (c / (cols - 1) if cols > 1 else 0.5) if cols > 1 else (x0 + x1) / 2
        y = y0 + (y1 - y0) * (r / (rows - 1) if rows > 1 else 0)
        out.append((s, x, y))
    return out

FONT = 18
errors, labels, total = [], [], 0
for members, items, box, cols in REGIONS:
    for s, x, y in layout(box, items, cols):
        total += 1
        size = FONT
        hw = text_w(s, size) / 2
        # 检查文字左右两端和中心都落在正确的区域
        for px, py in [(x - hw, y - 5), (x, y - 5), (x + hw, y - 5), (x - hw, y + 3), (x + hw, y + 3)]:
            got = {n for n in SETS if inside(n, px, py)}
            if got != members:
                errors.append(f"{s}: ({px:.0f},{py:.0f}) 在 {sorted(got)}，应在 {sorted(members)}")
                break
        labels.append((s, x, y, size))
# 检查同一行的标签之间至少留 12px 空隙
for i, (a, ax, ay, asz) in enumerate(labels):
    for b, bx, by, bsz in labels[i + 1:]:
        if abs(ay - by) < 16 and abs(ax - bx) < (text_w(a, asz) + text_w(b, bsz)) / 2 + 12:
            errors.append(f"{a} 与 {b} 重叠")
for n, (x, y) in NAME_POS.items():
    got = {k for k in SETS if inside(k, x, y)}
    if got != {n}:
        errors.append(f"标签 {NAMES[n]} 落在 {sorted(got)}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)

# ---------- 输出 SVG ----------
order = ["adj", "noun", "verb", "adv"]
svg = [f'<svg class="suffix-venn" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
       f'aria-label="后缀与词性韦恩图：共 {total} 个后缀，按能构成的词性归入形容词、名词、动词、副词四个集合及其交集">',
       '<style>'
       '.suffix-venn{width:100%;height:auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif}'
       '.suffix-venn .sfx{fill:var(--md-default-fg-color,#1f2937);text-anchor:middle;dominant-baseline:middle}'
       '.suffix-venn .set-name{font-weight:700;font-size:25px;text-anchor:middle;dominant-baseline:middle}'
       '</style>']
for n in order:
    cx, cy, rx, ry, col = SETS[n]
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" fill-opacity="0.14" '
               f'stroke="{col}" stroke-width="2"/>')
for n in order:
    x, y = NAME_POS[n]
    svg.append(f'<text class="set-name" x="{x}" y="{y}" fill="{SETS[n][4]}">{NAMES[n]}</text>')
for s, x, y, size in labels:
    bold = ' font-weight="700"' if s == "-ate" else ""
    svg.append(f'<text class="sfx" x="{x:.0f}" y="{y:.0f}" font-size="{size}"{bold}>{s}</text>')
svg.append("</svg>")
out = "".join(svg[:2]) + "\n" + "\n".join(svg[2:])
open(sys.argv[1], "w", encoding="utf-8").write(out)
print(f"ok: {total} suffixes")
