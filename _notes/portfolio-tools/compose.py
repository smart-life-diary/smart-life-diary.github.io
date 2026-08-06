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

# ココナラの画像表示枠は約1.20:1。これ以外の比率は中央だけが残り、左右または
# 上下が切り落とされる。実測では片側4.8%が失われたため、比率を合わせたうえで
# 余白も7%確保し、多少ずれても文字が欠けないようにしている。
RATIO = 1.20
CUT_W, GAP, MARGIN = 405, 60, 150
HEAD_H, LABEL_H, BAND_H = 178, 66, 150


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


RESULT_POINTS = {
    "isekai":   ["12タイプから1つを判定", "6軸のレーダーチャートを自動描画", "画像生成プロンプトを自動発行"],
    "side-biz": ["4タイプから1つを判定", "タイプごとに配色を出し分け", "シェアを促す一文で拡散へ"],
    "ai-level": ["回答をスコア化し4段階で判定", "次にとる行動を3つ提示", "CTAでリード獲得へつなぐ"],
    "shachiku": ["度合いを％で可視化", "3段階のスケールで位置を表示", "結果に寄り添う解説文"],
    "golf":     ["4タイプから課題を特定", "タイプ共通の改善ヒントを提示", "シェアを促す一文で拡散へ"],
}


def build_result(slug, title, subtitle):
    """結果画面の単体画像。縦長のままだと4:3で上下を切られるため、台紙に載せる。"""
    W, H = 1560, 1300
    shot = trim_tail(Image.open(f"{SHOTS}/{slug}-3-result.png").convert("RGB"))
    ph = H - 190
    pw = round(shot.width * ph / shot.height)
    shot = shot.resize((pw, ph), Image.LANCZOS)

    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    x = W - 110 - pw
    canvas.paste(shot, (x, (H - ph) // 2))

    # 左側にテキスト。作品名が長いとスマホ画像に重なるので幅に収まるまで縮める
    tx, ty = 110, 390
    avail = x - tx - 44
    tf = font(52)
    while tf.size > 30 and d.textlength(title, font=tf) > avail:
        tf = font(tf.size - 2)
    d.text((tx, ty), "RESULT", font=font(26), fill=GOLD)
    bold(d, (tx, ty + 52), title, tf, INK)
    d.text((tx, ty + 130), subtitle, font=font(27), fill=MUT)
    for i, p in enumerate(RESULT_POINTS[slug]):
        y = ty + 220 + i * 62
        d.ellipse((tx + 4, y + 13, tx + 18, y + 27), fill=GOLD)
        d.text((tx + 36, y), p, font=font(29), fill=INK)

    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{slug}-result.png"
    canvas.save(path, optimize=True)
    return path


def build(slug, title, subtitle, step4):
    cuts = []
    for key, _ in STEPS:
        im = trim_tail(Image.open(f"{SHOTS}/{slug}-{key}.png").convert("RGB"))
        h = round(im.height * CUT_W / im.width)
        cuts.append(im.resize((CUT_W, h), Image.LANCZOS))

    W = MARGIN * 2 + CUT_W * 4 + GAP * 3
    body_h = max(c.height for c in cuts) + 44           # パネルは中身に合わせる
    H = max(HEAD_H + LABEL_H + body_h + BAND_H + MARGIN, round(W / RATIO))
    # スマホ画面4枚を横に並べると1.20:1の枠には縦が余る。下端に訴求文の帯を置き、
    # 残りをヘッダーと帯のあいだで均等に配分してパネル列を収める。
    band_y = H - MARGIN - BAND_H
    block_top = HEAD_H + 30 + (band_y - HEAD_H - 30 - LABEL_H - body_h) // 2

    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # ヘッダー
    bold(d, (MARGIN, 62), title, font(46), INK)
    d.text((MARGIN, 122), subtitle, font=font(26), fill=MUT)
    d.text((W - MARGIN, 70), "スマートフォン最適化", font=font(24), fill=GOLD, anchor="ra")
    d.text((W - MARGIN, 110), "HTML1ファイルで納品", font=font(24), fill=MUT, anchor="ra")
    d.line([(MARGIN, HEAD_H - 12), (W - MARGIN, HEAD_H - 12)], fill=LINE, width=2)

    labels = [l for _, l in STEPS[:3]] + [step4]
    for i, (cut, label) in enumerate(zip(cuts, labels)):
        x = MARGIN + i * (CUT_W + GAP)
        # ステップ名
        d.text((x + CUT_W // 2, block_top + 18), label, font=font(28), fill=GOLD, anchor="ma")
        # パネル
        top = block_top + LABEL_H
        rounded(d, (x - 10, top, x + CUT_W + 10, top + body_h), 20, PANEL, LINE)
        # 画像は縦中央に配置
        y = top + (body_h - cut.height) // 2
        canvas.paste(cut, (x, y))
        # 矢印
        if i < 3:
            ax = x + CUT_W + GAP // 2
            ay = top + body_h // 2
            d.polygon([(ax - 13, ay - 19), (ax + 15, ay), (ax - 13, ay + 19)], fill=GOLD)

    # 下部の帯：この作品でできることを3点
    d.line([(MARGIN, band_y), (W - MARGIN, band_y)], fill=LINE, width=2)
    col = (W - MARGIN * 2) // 3
    for i, p in enumerate(RESULT_POINTS[slug]):
        bx = MARGIN + i * col
        by = band_y + 58
        d.ellipse((bx, by + 12, bx + 15, by + 27), fill=GOLD)
        d.text((bx + 32, by), p, font=font(29), fill=INK)

    os.makedirs(OUT, exist_ok=True)
    path = f"{OUT}/{slug}-flow.png"
    canvas.save(path, optimize=True)
    return path, canvas.size


for slug, title, sub, s4 in DEMOS:
    p, size = build(slug, title, sub, s4)
    print(f"{p}  {size[0]}x{size[1]}  {os.path.getsize(p)//1024}KB")
    # 結果画面の単体画像も4:3の台紙に載せて書き出す
    rp = build_result(slug, title, sub)
    r = Image.open(rp)
    print(f"{rp}  {r.width}x{r.height}  {os.path.getsize(rp)//1024}KB")
