"""建設帳票5点セットを1枚で見せる、ポートフォリオ登録用の画像を書き出す。

出力
  portfolio/fset-portfolio.png   1560×1300

出品用の画像（fset-1〜3 / koji-1〜3）は1枚につき1つの帳票しか映っておらず、
しかも売り文句の見出しが大きく入っている。ポートフォリオでは「5点セット」
であることが1枚で伝わってほしいので、既存の画像から**表の部分だけを切り出して**
並べ直す。見出しは持ち込まない。

切り出しは「明るい行が横に連続している範囲」を拾う。表は濃紺の地に対して
明るいので、行ごとの明るさで機械的に判定できる。見出しの白文字は行全体を
明るくしないため、この方法なら混ざらない。
"""
import os

from PIL import Image, ImageDraw

from koji_sheet import OUT_P, W, H, font

BG     = (244, 247, 251)
CARD   = (255, 255, 255)
LINE   = (222, 229, 238)
SHADOW = (214, 222, 233)
INK    = (24, 36, 56)
SUB    = (108, 124, 145)
BODY   = (70, 84, 104)
ACCENT = (0, 112, 214)
ACC_BG = (232, 241, 252)

# 切り出す元画像と、その帳票の名前
SRC = [
    ("koji-1.png", "工事別原価管理表 ／ 日報入力"),
    ("koji-2.png", "工事別原価管理表 ／ 集計"),
    ("fset-2.png", "工程管理表"),
    ("fset-3.png", "見積・請求・入金管理表"),
]

# 左に並べる説明は、カードの幅に収まる長さにする（およそ17字まで）
SHEETS = [
    ("工事別原価管理表", "日報から原価・粗利率まで"),
    ("工程管理表", "予定と実績を同じ行に"),
    ("工事日報", "A4縦1枚。印刷できます"),
    ("資材発注・受入管理表", "未受入の金額が出ます"),
    ("見積・請求・入金管理表", "未入金と経過日数が出ます"),
]


def table_box(path, thresh=170, ratio=0.55):
    """濃紺の地から、表の部分だけの矩形を返す。

    行の明るいピクセルが ratio 以上を占める行を「表の行」とみなす。
    見出しの白文字は行の一部しか占めないので拾われない。
    """
    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    step = 3
    rows = []
    for y in range(0, h, step):
        n = sum(1 for x in range(0, w, step) if px[x, y] > thresh)
        rows.append(n / len(range(0, w, step)) >= ratio)
    ys = [i * step for i, v in enumerate(rows) if v]
    if not ys:
        return (0, 0, w, h)
    top, bot = min(ys), max(ys) + step

    cols = []
    for x in range(0, w, step):
        n = sum(1 for y in range(top, bot, step) if px[x, y] > thresh)
        cols.append(n / max(1, len(range(top, bot, step))) >= 0.5)
    xs = [i * step for i, v in enumerate(cols) if v]
    left, right = (min(xs), max(xs) + step) if xs else (0, w)
    return (max(0, left - 4), max(0, top - 4), min(w, right + 4), min(h, bot + 4))


def card(d, x, y, w, h, r=14, bar=None):
    d.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=r, fill=SHADOW)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=CARD, outline=LINE, width=1)
    if bar:
        d.rounded_rectangle([x, y + 8, x + 7, y + h - 8], radius=4, fill=bar)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((84, 62), "建設業の管理帳票5点セット", font=font(60), fill=INK)
    d.text((86, 150), "Excel。数式が入った状態でお渡しします", font=font(31), fill=SUB)
    d.rounded_rectangle([86, 200, 176, 207], radius=4, fill=ACCENT)

    # 左：5点の名前。画面が無い帳票もここで拾う。
    lx, lw, pitch = 84, 456, 140
    y = 250
    for i, (name, note) in enumerate(SHEETS, 1):
        card(d, lx, y, lw, 128, bar=ACCENT)
        d.rounded_rectangle([lx + 26, y + 28, lx + 76, y + 74], radius=10, fill=ACC_BG)
        nf = font(26)
        d.text((lx + 51 - d.textlength(str(i), font=nf) / 2, y + 36), str(i), font=nf, fill=ACCENT)
        d.text((lx + 96, y + 30), name, font=font(29), fill=INK)
        d.text((lx + 96, y + 78), note, font=font(21), fill=SUB)
        y += pitch

    # 右：実際の画面を4枚。売り文句の見出しは持ち込まない。
    gx, gw, gap = 566, 452, 24
    gy, ih, lab = 250, 290, 46          # ih=画像の高さ, lab=ラベル帯
    for i, (fn, label) in enumerate(SRC):
        p = os.path.join(OUT_P, fn)
        src = Image.open(p).convert("RGB").crop(table_box(p))
        col, row = i % 2, i // 2
        x = gx + col * (gw + gap)
        yy = gy + row * (ih + lab + 28)
        card(d, x, yy, gw, ih + lab)
        iw, ihh = gw - 36, ih - 28
        sc = min(iw / src.width, ihh / src.height)
        th = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS)
        px = x + 18 + (iw - th.width) // 2
        py = yy + 14 + (ihh - th.height) // 2      # 縦にも中央へ寄せる
        img.paste(th, (px, py))
        d.rectangle([px, py, px + th.width - 1, py + th.height - 1], outline=LINE, width=1)
        d.text((x + 22, yy + ih + 4), label, font=font(22), fill=BODY)

    d.text((86, 1030),
           "黄色が入力する欄、グレーが自動で計算される欄です。開いた時点でどこを触ればよいかが分かります。",
           font=font(27), fill=SUB)
    d.text((86, 1078),
           "納品前に全ての数式を計算して検証しています。",
           font=font(27), fill=SUB)
    return img


if __name__ == "__main__":
    for fn, _ in SRC:
        p = os.path.join(OUT_P, fn)
        print(fn, "→ 表の範囲", table_box(p))
    im = build()
    p = os.path.join(OUT_P, "fset-portfolio.png")
    im.save(p)
    print(p, im.size, os.path.getsize(p) // 1024, "KB")
