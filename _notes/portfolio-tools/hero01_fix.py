"""出品01の1枚目（ChatGPT生成）を、登録できる状態に直す。

直すのは3点。絵の良し悪しではなく、事実と規格の問題だけ。

1. バッジの「捷設」→「建設」。1文字化け（9/25 のプロフィールのカバーと同じ事故）。
2. 「最大10枚まで」（流れの枠と、下の帯の2か所）→「10枚まで」。
   本文は「10枚までを基本」で、11〜20枚目はオプションで受ける。
   「最大」と書くと12枚の人が開く前に帰る。
3. 比率。ChatGPT は 1536×1024（3:2）で出す。ココナラの表示は 1.20:1 なので、
   上下を足して 1536×1280 にする。切らずに足す（左右の端まで文字があるため）。

文字の塗り直しは、文字のすぐ横のきれいな地色を行ごとに拾って埋める。
バッジの中は濃紺のグラデーションだが、20px 幅なら横方向の変化は無視できる。

入力  portfolio/01-tensaku-hero-chatgpt.png（ChatGPT の出力をそのまま置く）
出力  portfolio/01-tensaku-hero.png
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P

NOTO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SRC = os.path.join(OUT_P, "01-tensaku-hero-chatgpt.png")
DST = os.path.join(OUT_P, "01-tensaku-hero.png")


def font(sz, bold=True):
    return ImageFont.truetype(NOTO_B if bold else NOTO_R, sz, index=0)


def bbox_of(a, win, pred):
    """win=(x0,y0,x1,y1) の中で pred を満たす画素の外接矩形。"""
    x0, y0, x1, y1 = win
    sub = a[y0:y1, x0:x1]
    m = pred(sub)
    ys, xs = np.where(m)
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)


def fill_from_side(a, box, src_x0, src_x1, pad=2):
    """box を、同じ行の src_x0..src_x1 の中央値で塗る（行ごと）。"""
    x0, y0, x1, y1 = box
    for y in range(y0 - pad, y1 + pad):
        row = a[y, src_x0:src_x1]
        a[y, x0 - pad:x1 + pad] = np.median(row, axis=0)


def draw_text(img, xy, s, sz, fill, bold=True, box_w=None):
    """左上 xy に描く。box_w を渡すと、その幅に横方向だけ合わせる。"""
    f = font(sz, bold)
    tmp = Image.new("L", (sz * len(s) * 2 + 40, sz * 2 + 40), 0)
    ImageDraw.Draw(tmp).text((20, 20), s, font=f, fill=255)
    bb = tmp.getbbox()
    mask = tmp.crop(bb)
    if box_w and abs(mask.width - box_w) > 2:
        mask = mask.resize((box_w, mask.height), Image.LANCZOS)
    img.paste(Image.new("RGB", mask.size, fill), xy, mask)
    return mask.size


def main():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(np.uint8).copy()

    # 1. バッジ「捷設」。白い画素を探す。
    white = lambda s: (s.min(axis=2) > 200)
    box = bbox_of(a, (860, 62, 925, 96), white)
    print("badge text bbox", box)
    x0, y0, x1, y1 = box
    # 「捷」は左半分。文字間の谷で切る：列ごとの白画素数が0になる列を探す
    cols = white(a[y0:y1, x0:x1]).sum(axis=0)
    gaps = [i for i, c in enumerate(cols) if c == 0 and 5 < i < len(cols) - 5]
    split = x0 + (gaps[len(gaps) // 2] if gaps else (x1 - x0) // 2)
    print("split at", split)
    fill_from_side(a, (x0, y0, split, y1), x0 - 14, x0 - 4)
    img = Image.fromarray(a)
    w, h = y1 - y0, y1 - y0
    draw_text(img, (x0, y0), "建", h + 2, (255, 255, 255), box_w=split - x0)

    # 2a. 流れの枠「（最大10枚まで）」。濃紺の文字を探す。
    a = np.asarray(img).astype(np.uint8).copy()
    dark = lambda s: (s.max(axis=2) < 120)
    box = bbox_of(a, (60, 780, 230, 816), dark)
    print("flow text bbox", box)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    fill_from_side(a, box, 40, 58, pad=3)
    img = Image.fromarray(a)
    sz = y1 - y0 + 4
    tw = int(ImageDraw.Draw(img).textlength("（10枚まで）", font=font(sz)))
    draw_text(img, (cx - tw // 2, y0), "（10枚まで）", sz, (24, 36, 72))

    # 2b. 下の帯「最大10枚まで」。白い文字を探す。
    a = np.asarray(img).astype(np.uint8).copy()
    box = bbox_of(a, (170, 952, 330, 986), white)
    print("bar text bbox", box)
    x0, y0, x1, y1 = box
    fill_from_side(a, box, 340, 390, pad=3)
    img = Image.fromarray(a)
    draw_text(img, (x0, y0), "10枚まで（追加可）", (y1 - y0) + 2, (255, 255, 255), bold=False)

    # 3. 上下に足して 1.20:1
    W, H = img.size
    newH = int(round(W / 1.2))
    top = 64
    bot = newH - H - top
    out = Image.new("RGB", (W, newH))
    arr = np.asarray(img)
    out.paste(Image.fromarray(np.repeat(arr[:1], top, axis=0)), (0, 0))
    out.paste(img, (0, top))
    out.paste(Image.fromarray(np.repeat(arr[-1:], bot, axis=0)), (0, top + H))
    out.save(DST)
    print(DST, out.size, f"{out.size[0]/out.size[1]:.2f}:1", os.path.getsize(DST) // 1024, "KB")


if __name__ == "__main__":
    main()
