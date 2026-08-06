"""4カットを1枚の横並び合成画像にまとめる（ココナラ ポートフォリオ用）。"""
import os
from PIL import Image, ImageDraw, ImageFont

SHOTS = os.path.join(os.path.dirname(__file__), "shots")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "portfolio")
FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"

BG = (14, 20, 36)
PANEL = (22, 32, 58)
LINE = (43, 57, 88)
GOLD = (232, 196, 119)
INK = (238, 242, 251)
MUT = (138, 151, 181)

DEMOS = [
    ("isekai",   "異世界転生 職業診断",            "7問 → 12タイプ分岐 ／ レーダーチャート付き", "④ 拡散の仕掛け"),
    ("side-biz", "副業タイプ診断",                 "7問 → 4タイプ ／ 集客導線の標準構成",       "④ シェアで拡散"),
    ("ai-level", "AI活用レベル診断",               "5問 → スコア採点でレベル判定",             "④ 次の行動へ誘導"),
    ("shachiku", "隠れ社畜度チェック",             "7問 → 度合いを％で可視化",                 "④ シェアで拡散"),
    ("golf",     "ゴルフ・スコア伸び悩みタイプ診断", "7問 → 4タイプ ／ 専門領域 × 診断",         "④ シェアで拡散"),
]
STEPS = [("1-start", "① スタート"), ("2-question", "② 設問に答える"),
         ("3-result", "③ 結果が出る"), ("4-share", "④ シェアで拡散")]

CUT_W, GAP, MARGIN = 430, 66, 52
HEAD_H, LABEL_H = 150, 62


def font(sz):
    return ImageFont.truetype(FONT, sz)


def bold(d, xy, text, f, fill, anchor="la"):
    """IPAGothicに太字がないため、微小オフセットの重ね描きで太さを出す。"""
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        d.text((xy[0] + dx, xy[1] + dy), text, font=f, fill=fill, anchor=anchor)


def rounded(d, box, r, fill, outline=None):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2)


def trim_tail(im, keep=28, tol=6):
    """下端に続く単色の余白（ページ背景）を削る。"""
    px = im.load()
    base = px[4, im.height - 4]
    w = im.width
    y = im.height - 1
    while y > im.height // 3:
        row = (px[x, y] for x in range(0, w, 7))
        if all(abs(p[0]-base[0]) <= tol and abs(p[1]-base[1]) <= tol and abs(p[2]-base[2]) <= tol
               for p in row):
            y -= 1
        else:
            break
    return im.crop((0, 0, w, min(im.height, y + keep)))


def build(slug, title, subtitle, step4):
    cuts = []
    for key, _ in STEPS:
        im = trim_tail(Image.open(f"{SHOTS}/{slug}-{key}.png").convert("RGB"))
        h = round(im.height * CUT_W / im.width)
        cuts.append(im.resize((CUT_W, h), Image.LANCZOS))

    body_h = max(c.height for c in cuts) + 40          # パネル内余白
    W = MARGIN * 2 + CUT_W * 4 + GAP * 3
    H = HEAD_H + LABEL_H + body_h + MARGIN

    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # ヘッダー
    bold(d, (MARGIN, 44), title, font(46), INK)
    d.text((MARGIN, 104), subtitle, font=font(26), fill=MUT)
    d.text((W - MARGIN, 52), "スマートフォン最適化", font=font(24), fill=GOLD, anchor="ra")
    d.text((W - MARGIN, 92), "HTML1ファイルで納品", font=font(24), fill=MUT, anchor="ra")
    d.line([(MARGIN, HEAD_H - 12), (W - MARGIN, HEAD_H - 12)], fill=LINE, width=2)

    labels = [l for _, l in STEPS[:3]] + [step4]
    for i, (cut, label) in enumerate(zip(cuts, labels)):
        x = MARGIN + i * (CUT_W + GAP)
        # ステップ名
        d.text((x + CUT_W // 2, HEAD_H + 18), label, font=font(28), fill=GOLD, anchor="ma")
        # パネル
        top = HEAD_H + LABEL_H
        rounded(d, (x - 10, top, x + CUT_W + 10, top + body_h), 20, PANEL, LINE)
        # 画像は縦中央に配置
        y = top + (body_h - cut.height) // 2
        canvas.paste(cut, (x, y))
        # 矢印
        if i < 3:
            ax = x + CUT_W + GAP // 2
            ay = top + body_h // 2
            d.polygon([(ax - 13, ay - 19), (ax + 15, ay), (ax - 13, ay + 19)], fill=GOLD)

    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{slug}-flow.png"
    canvas.save(path, optimize=True)
    return path, canvas.size


for slug, title, sub, s4 in DEMOS:
    p, size = build(slug, title, sub, s4)
    print(f"{p}  {size[0]}x{size[1]}  {os.path.getsize(p)//1024}KB")
    # 結果画面の単体画像も書き出す
    r = trim_tail(Image.open(f"{SHOTS}/{slug}-3-result.png").convert("RGB"))
    rp = f"{OUT}/{slug}-result.png"
    r.save(rp, optimize=True)
    print(f"{rp}  {r.width}x{r.height}  {os.path.getsize(rp)//1024}KB")
