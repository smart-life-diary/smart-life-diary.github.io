"""提案書チェック45 の検索結果表示画像を書き出す。

出力
  portfolio/check45-cover.png   1200×1200

コンテンツマーケットの表紙画像に決まった比率は無い。実測すると 1.91:1 が11件、
1:1 が7件（上位40件）で、CDN側は幅1000pxに正規化するだけだった。
ただし一覧のカードでは切り取られ、出品画面にも「画像が見切れていると購入率が
下がる傾向があります」と書かれている。**正方形にして、文字を中央に寄せる。**

一覧では小さく表示される。読ませるのは「45」と「3軸」だけで、
細い説明文は入れない。
"""
import os

from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P

# Noto Sans CJK JP。太字が実体として入っているので、輪郭を重ねて太らせる必要がない。
# .ttc の index=0 が JP（fc-list の並び）。SC/TC を引くと中国字体になるので固定する。
NOTO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(sz, bold=False):
    return ImageFont.truetype(NOTO_B if bold else NOTO_R, sz, index=0)

W = H = 1200

BG      = (244, 247, 251)
CARD    = (255, 255, 255)
LINE    = (222, 229, 238)
SHADOW  = (214, 222, 233)
INK     = (24, 36, 56)
SUB     = (108, 124, 145)
ACCENT  = (0, 112, 214)
ACC_BG  = (232, 241, 252)
WARN    = (206, 88, 74)
GOOD    = (20, 142, 102)
AMBER   = (217, 119, 6)


def tw(d, s, sz, bold=0):
    return d.textlength(s, font=font(sz, bool(bold)))


def bt(d, xy, s, sz, fill, bold=0):
    d.text(xy, s, font=font(sz, bool(bold)), fill=fill)


def ct(d, cx, y, s, sz, fill, bold=0):
    bt(d, (cx - tw(d, s, sz, bold) / 2, y), s, sz, fill, bold)


def card(d, x, y, w, h, r=16, bar=None):
    d.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=r, fill=SHADOW)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=CARD, outline=LINE, width=1)
    if bar:
        d.rounded_rectangle([x, y + 10, x + 7, y + h - 10], radius=4, fill=bar)


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # 上の帯。ここは切り取られても惜しくない位置に置く。
    d.rounded_rectangle([0, 0, W, 12], fill=ACCENT)

    ct(d, cx, 96, "その資料は、なぜ通らないのか", 42, SUB)

    # 主役。一覧で小さくなっても読める大きさにする。
    ct(d, cx, 170, "提案書チェック", 86, INK, 1)
    ct(d, cx, 300, "45", 170, ACCENT, 1)

    d.rounded_rectangle([cx - 60, 562, cx + 60, 570], radius=4, fill=ACCENT)

    ct(d, cx, 598, "3つの軸で、自動採点", 44, INK, 1)

    # 3軸。色は結果画面のバーと揃える。
    axes = [("構成", "話の並び", ACCENT), ("情報", "判断材料", GOOD), ("表現", "伝わり方", AMBER)]
    cw, gap = 300, 24
    x0 = cx - (cw * 3 + gap * 2) // 2
    for i, (name, note, col) in enumerate(axes):
        x = x0 + i * (cw + gap)
        card(d, x, 668, cw, 168, bar=col)
        ct(d, x + cw / 2 + 4, 692, name, 50, INK, 1)
        ct(d, x + cw / 2 + 4, 762, note, 26, SUB)
        d.rounded_rectangle([x + 40, 808, x + cw - 40, 814], radius=3, fill=col)

    # 何が届くか。ここが購入判断に効く。
    card(d, 108, 862, W - 216, 176)
    rows = ["45項目に3択で答えるだけ",
            "できていない項目が自動で一覧になる",
            "Excel／Googleスプレッドシート対応"]
    y = 892
    for t in rows:
        # チェックは線で描く。記号のグリフは小さいと潰れる。
        d.ellipse([152, y + 10, 176, y + 34], fill=ACCENT)
        d.line([(158, y + 22), (163, y + 28), (170, y + 16)],
               fill=(255, 255, 255), width=3, joint="curve")
        bt(d, (198, y), t, 33, INK)
        y += 46

    ct(d, cx, 1078, "建設コンサルタント15年／公共案件の技術提案書", 30, SUB)
    d.rounded_rectangle([0, H - 12, W, H], fill=ACCENT)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    p = os.path.join(OUT_P, "check45-cover.png")
    im = build()
    im.save(p)
    print(p, im.size, f"{im.size[0]/im.size[1]:.2f}:1", os.path.getsize(p) // 1024, "KB")
