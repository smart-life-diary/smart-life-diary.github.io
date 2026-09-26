"""出品Gの1枚目（AI生成のヒーロー画像）の金バッジを、事実だけの文言に直す。

元のバッジは **「実績豊富な / プロが対応」＋王冠＋★★★**。これは出せない。

  - この出品の販売実績は 0件。アカウント全体でも1件（別の出品）。
    ココナラで「実績」と言えば販売実績のことなので、買い手は必ずそう読む。
  - 王冠つきの金バッジで「プロ」は、運営が審査して付ける **PRO認定** に見える。
    持っていない。
  - ★★★ は評価に見える。根拠が無い。

画像全体を作り直すと他の部分まで変わるので、**円盤の中だけ**を描き直す。
やり方は cover_badge_fix.py と同じ（文字の上下にあるきれいな金の行を
列ごとに拾って、あいだを縦に線形補間で埋める）。金はグラデーションなので、
上下の参照帯を文字のすぐ近くに取れば継ぎ目が出ない。

入力は、公開中の出品ページから落とした1枚目（1220×1017）。

出力
  portfolio/deck-hero-fix.png
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P

NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

SRC = os.path.join(OUT_P, "deck-hero-ai.png")
DST = os.path.join(OUT_P, "deck-hero-fix.png")

CX, CY, R = 1060, 705, 96        # 金の円盤（月桂樹の内側）
SAFE = 0.90                      # 端の月桂樹に掛からない範囲だけ触る

# 実測した帯。CLEAN は文字の無いきれいな金、PAINT は塗り直す範囲。
C1, C2, C3, C4 = (654, 668), (701, 707), (743, 757), (781, 793)
BANDS = [((669, 700), C1, C2),   # 1行目
         ((708, 742), C2, C3),   # 2行目
         ((758, 780), C3, C4)]   # ★★★

INK = (16, 34, 74)               # 元の文字と同じ濃紺
LINES = [("公共案件の", 673, 142, 30),   # (文字, 上端y, 幅, 高さ)
         ("提案書15年", 711, 152, 34)]
DROP_STARS = True                # ★★★ は評価に見えるので消す


def column_profile(a, y0, y1):
    """列ごとの、文字でない金の中央値。取れない列は左右から埋める。"""
    prof = np.full((a.shape[1], 3), np.nan)
    x0, x1 = CX - R, CX + R
    for x in range(x0, x1 + 1):
        col = a[y0:y1 + 1, x]
        keep = col[(col[:, 0] > 120) & (col[:, 0] > col[:, 2] + 40)]
        if len(keep):
            prof[x] = np.median(keep, axis=0)
    xs = np.arange(a.shape[1])
    ok = ~np.isnan(prof[:, 0])
    for c in range(3):
        prof[:, c] = np.interp(xs, xs[ok], prof[ok, c])
    return prof


def repaint(out, a, band, top, bot):
    y0, y1 = band
    ptop, pbot = column_profile(a, *top), column_profile(a, *bot)
    ya, yb = top[1], bot[0]
    rr = (R * SAFE) ** 2
    for x in range(CX - R, CX + R + 1):
        d = rr - (x - CX) ** 2
        if d <= 0:
            continue
        half = np.sqrt(d)
        for y in range(y0, y1 + 1):
            if abs(y - CY) > half:
                continue
            t = (y - ya) / (yb - ya)
            out[y, x] = ptop[x] * (1 - t) + pbot[x] * t


def text_mask(s, box):
    """元の字幅に合わせて、描いた字を箱いっぱいに詰める。"""
    f = ImageFont.truetype(NOTO_B, 140, index=0)
    tmp = Image.new("L", (1800, 300), 0)
    ImageDraw.Draw(tmp).text((30, 30), s, font=f, fill=255)
    return tmp.crop(tmp.getbbox()).resize(box, Image.LANCZOS)


def main(src=SRC, dst=DST):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(float)

    out = a.copy()
    for band, top, bot in BANDS:
        if band == BANDS[2][0] and not DROP_STARS:
            continue
        repaint(out, a, band, top, bot)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    for s, ty, w, h in LINES:
        m = text_mask(s, (w, h))
        tx = CX - w // 2
        img.paste(Image.new("RGB", (w, h), (196, 158, 60)), (tx + 1, ty + 2), m)
        img.paste(Image.new("RGB", (w, h), INK), (tx, ty), m)

    img.save(dst)
    print(dst, img.size, os.path.getsize(dst) // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:])
