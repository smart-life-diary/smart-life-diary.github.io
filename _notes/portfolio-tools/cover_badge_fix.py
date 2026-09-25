# -*- coding: utf-8 -*-
"""カバー画像のバッジ2行目を描き直す。

ChatGPTが出したカバーは全体として良いが、バッジ2行目が
「建設 / ?コンサルタント / 15年」と、余計な壊れた字を1つ含んでいる。
画像全体を作り直すと他が変わってしまうので、**この1行だけ**直す。

背景の復元は縦方向の補間で行う。実測すると文字の帯は y=116〜138 で、
その上（104〜115）と下（139〜152）は文字の無いきれいな青。
バッジのグラデーションはこの範囲で緩やか（平均 (3,100,174)→(3,94,167)）なので、
列ごとに上下から線形に埋めれば継ぎ目が出ない。

文字は Noto Sans CJK JP Bold で描き、元の字幅（横に詰まった形）に合わせて
横方向だけ縮める。
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, DST = "cover.jpg", "cover_fixed.png"

CX, CY, R = 1132, 172, 132        # バッジの中心と半径
X0, X1 = 1035, 1255               # 塗り直す横の範囲
TOP_SRC = (106, 114)              # 上側の参照行
BOT_SRC = (141, 149)              # 下側の参照行
Y0, Y1 = 114, 140                 # 塗り直す縦の範囲
TEXT = "コンサルタント"
TEXT_BOX = (172, 23)              # 元の文字の見た目の幅・高さ
TEXT_TOP = 116
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def column_profile(a, y_from, y_to):
    """列ごとの、文字でない青の中央値。無ければ左右から埋める。"""
    prof = np.full((a.shape[1], 3), np.nan)
    for x in range(X0 - 4, X1 + 5):
        col = a[y_from:y_to, x]
        keep = col[(col[:, 2] > col[:, 0] + 30) & (col[:, 2] > 60) & (col[:, 0] < 150)]
        if len(keep):
            prof[x] = np.median(keep, axis=0)
    xs = np.arange(a.shape[1])
    ok = ~np.isnan(prof[:, 0])
    for c in range(3):
        prof[:, c] = np.interp(xs, xs[ok], prof[ok, c])
    return prof


def text_layer():
    """元の字幅に合わせて、横に詰めた文字を作る。"""
    f = ImageFont.truetype(NOTO_B, 120, index=0)
    tmp = Image.new("L", (1400, 260), 0)
    ImageDraw.Draw(tmp).text((20, 20), TEXT, font=f, fill=255)
    return tmp.crop(tmp.getbbox()).resize(TEXT_BOX, Image.LANCZOS)


def main():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(float)
    top = column_profile(a, *TOP_SRC)
    bot = column_profile(a, *BOT_SRC)

    out = a.copy()
    yy = np.arange(Y0, Y1 + 1)
    t = (yy - (TOP_SRC[1] - 1)) / ((BOT_SRC[0] + 1) - (TOP_SRC[1] - 1))
    for x in range(X0, X1 + 1):
        if (x - CX) ** 2 > (R * 0.95) ** 2:
            continue
        half = np.sqrt(max((R * 0.95) ** 2 - (x - CX) ** 2, 0))
        for i, y in enumerate(yy):
            if abs(y - CY) > half:
                continue
            out[y, x] = top[x] * (1 - t[i]) + bot[x] * t[i]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    mask = text_layer()
    tx = CX - TEXT_BOX[0] // 2
    # 元の文字と同じく、わずかな影を先に置く
    sh = Image.new("RGB", TEXT_BOX, (12, 52, 100))
    img.paste(sh, (tx + 1, TEXT_TOP + 1), mask)
    img.paste(Image.new("RGB", TEXT_BOX, (255, 255, 255)), (tx, TEXT_TOP), mask)

    img.save(DST)
    print(DST, img.size)


if __name__ == "__main__":
    main()
