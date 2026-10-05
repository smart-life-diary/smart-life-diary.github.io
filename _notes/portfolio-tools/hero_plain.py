"""出品の1枚目を、ChatGPT を待たずに仮で作る。

出力
  portfolio/<slug>-hero-plain.png   1560×1300（1.20:1）

listing_kits.py の各出品の hero（見出し・サブ・補足・チップ4つ）をそのまま描く。
写真は無く、濃紺＋金の面構成だけ。ChatGPT 版が出来たら差し替える前提の「仮」だが、
文字はプロンプトと同じものしか入れていないので、そのまま使っても嘘にはならない。

使い方
  python3 hero_plain.py            # 6本すべて
  python3 hero_plain.py 01-tensaku # 1本だけ
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P
from listing_kits import KITS

NOTO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

W, H = 1560, 1300
NAVY_T = (22, 36, 68)
NAVY_B = (9, 18, 42)
GOLD = (214, 172, 72)
GOLD_D = (168, 128, 38)
WHITE = (255, 255, 255)
PALE = (205, 214, 232)
INK = (18, 30, 58)
CARD = (246, 248, 252)
LINE = (214, 222, 236)


NOTES = {
    "01-tensaku": "お返しするもの：ページごとのコメント／45項目のチェック表／組み替えの構成案",
    "02-ai": "お渡しするもの：組み替えて書き直したスライド／変更箇所と理由の一覧",
    "03-kenshu": "含まれるもの：構成案／スライド10枚まで／修正2回",
    "04-kaisha": "含まれるもの：構成案／スライド10枚まで／修正2回",
    "05-ichimai": "お渡しするもの：A4一枚（PowerPoint または Word、編集できる状態）",
    "06-gijutsu": "含まれるもの：構成案／スライド10枚まで／修正2回",
}


def font(sz, bold=False):
    return ImageFont.truetype(NOTO_B if bold else NOTO_R, sz, index=0)


def gradient(img):
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(NAVY_T[i] * (1 - t) + NAVY_B[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)


def wrap(d, text, f, maxw):
    """日本語は単語境界が無いので、1文字ずつ詰めて折り返す。"""
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def slides_motif(img, x, y):
    """右側の主役。3枚のスライドを少しずらして重ね、番号を振る。"""
    d = ImageDraw.Draw(img, "RGBA")
    cw, ch = 440, 280
    for i in range(3):
        ox, oy = x + i * 60, y + i * 110
        d.rounded_rectangle([ox + 8, oy + 10, ox + cw + 8, oy + ch + 10], radius=14,
                            fill=(0, 0, 0, 90))
        d.rounded_rectangle([ox, oy, ox + cw, oy + ch], radius=14, fill=CARD, outline=LINE, width=2)
        # 見出し帯と本文の線
        d.rounded_rectangle([ox + 28, oy + 28, ox + 180, oy + 44], radius=6, fill=INK)
        for k in range(3):
            w = 300 - k * 60
            d.rounded_rectangle([ox + 28, oy + 76 + k * 34, ox + 28 + w, oy + 88 + k * 34],
                                radius=5, fill=(190, 200, 220))
        d.rounded_rectangle([ox + 28, oy + 190, ox + 150, oy + 220], radius=8, fill=GOLD)
        # 番号
        d.ellipse([ox + cw - 70, oy + 18, ox + cw - 22, oy + 66], fill=GOLD)
        f = font(30, True)
        s = str(i + 1)
        d.text((ox + cw - 46 - d.textlength(s, font=f) / 2, oy + 24), s, font=f, fill=INK)


def chip(d, x, y, text):
    f = font(30, True)
    w = int(d.textlength(text, font=f)) + 56
    d.rounded_rectangle([x, y, x + w, y + 70], radius=35, fill=WHITE, outline=GOLD, width=3)
    d.text((x + 28, y + 15), text, font=f, fill=INK)
    return w


def medallion(d, cx, cy, r, lines):
    for k in range(6, 0, -1):
        d.ellipse([cx - r - k, cy - r - k, cx + r + k, cy + r + k], fill=(0, 0, 0, 40))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], outline=GOLD_D, width=3)
    f = font(32, True)
    y = cy - 38
    for s in lines:
        d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=INK)
        y += 46


def build(kit):
    hp = kit["hero"]
    img = Image.new("RGB", (W, H))
    gradient(img)
    d = ImageDraw.Draw(img, "RGBA")

    # 左上の細い金線と、小さな肩書き
    d.rounded_rectangle([90, 96, 190, 103], radius=4, fill=GOLD)
    d.text((90, 122), "提案書・営業資料", font=font(28), fill=PALE)

    # 見出し（折り返しあり）
    f_h = font(74, True)
    y = 190
    for ln in wrap(d, hp["headline"], f_h, 900):
        d.text((88, y), ln, font=f_h, fill=WHITE)
        y += 96
    d.rounded_rectangle([90, y + 14, 250, y + 22], radius=4, fill=GOLD)
    y += 56

    f_s = font(40, True)
    for ln in wrap(d, hp["sub"], f_s, 880):
        d.text((90, y), ln, font=f_s, fill=GOLD)
        y += 56
    y += 14
    f_l = font(30)
    for ln in wrap(d, hp["lead"], f_l, 780):
        d.text((92, y), ln, font=f_l, fill=PALE)
        y += 46

    # 右の主役
    slides_motif(img, 940, 250)
    d = ImageDraw.Draw(img, "RGBA")

    # チップ4つ
    x, cy = 90, 900
    for c in hp["chips"]:
        x += chip(d, x, cy, c) + 22

    # 右下の帯
    medallion(d, 1372, 1110, 118, ["公共案件の", "提案書15年"])
    # 下の余白に、納品物を1行（本文と同じ内容。約束を増やさない）。出品ごとに違う
    note = NOTES.get(kit["slug"])
    if note:
        d.text((92, 1040), note, font=font(27), fill=PALE)
    return img


if __name__ == "__main__":
    want = set(sys.argv[1:])
    os.makedirs(OUT_P, exist_ok=True)
    for k in KITS:
        if want and k["slug"] not in want:
            continue
        p = os.path.join(OUT_P, f"{k['slug']}-hero-plain.png")
        im = build(k)
        im.save(p)
        print(p, im.size, os.path.getsize(p) // 1024, "KB")
