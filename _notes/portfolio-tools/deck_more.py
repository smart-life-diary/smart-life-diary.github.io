"""出品「選ばれる提案書・営業資料を構成から作ります」の画像を5枚増やす。

出力
  portfolio/deck-m1.png 〜 deck-m5.png   1560×1300（1.20:1）

すでに登録してある5枚（deck-h1 / h2 / deck-2 / deck-1 / deck-3）に足して、
上限の10枚にする。

中身は deck_hero.py が作るサンプルスライドだが、**あれは 1920×1080 なので
そのまま上げると比率が合わない。** 1枚ずつ 1.20:1 の台紙に大きく置き直し、
「なぜその作りなのか」を1行添える。スライドを並べるだけでは、
作れることは伝わっても、何を考えて作っているかが伝わらない。

受注実績ではないので、**各画像にサンプルである旨を必ず入れる。**
"""
import os

from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P

NOTO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

W, H = 1560, 1300

BG     = (244, 247, 251)
CARD   = (255, 255, 255)
LINE   = (222, 229, 238)
SHADOW = (214, 222, 233)
INK    = (24, 36, 56)
SUB    = (108, 124, 145)
BODY   = (70, 84, 104)
ACCENT = (0, 112, 214)

# (元のサンプル, 見出し, 補足, 説明2行)
PAGES = [
    ("deck-sample-01.png", "1枚目に、してほしいことを書きます",
     "表紙",
     ["誰に向けた資料で、何を決めてほしいのかを最初に置きます。",
      "ここが曖昧なまま始まる資料は、最後まで読まれません。"]),
    ("deck-sample-03.png", "変化は、並べて見せます",
     "導入前と導入後",
     ["文章で説明するより、左右に並べたほうが差が一目で伝わります。",
      "相手が社内で説明するときも、この1枚がそのまま使えます。"]),
    ("deck-sample-05.png", "数字は、大きく3つまで",
     "実績・効果",
     ["並べすぎると、どれも印象に残りません。",
      "相手が覚えて帰る数字だけに絞り、出どころも添えます。"]),
    ("deck-sample-06.png", "いつ終わるかを、先に見せます",
     "スケジュール",
     ["期間が見えないと、良い提案でも社内で検討が止まります。",
      "着手から完了までを、月単位ではなく「工程」で並べます。"]),
    ("deck-sample-07.png", "費用は、内訳まで出します",
     "費用",
     ["総額だけでは決裁できません。何にいくらかかるかを分けて示します。",
      "初年度と次年度以降を並べ、続けたときの負担まで見えるようにします。"]),
]

NOTE = "※ 掲載しているスライドは、この出品のために作成したサンプルです。"


def font(sz, bold=False):
    return ImageFont.truetype(NOTO_B if bold else NOTO_R, sz, index=0)


def build(src, title, tag, lines):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((84, 62), title, font=font(52, True), fill=INK)
    d.text((86, 142), tag, font=font(30), fill=SUB)
    d.rounded_rectangle([86, 192, 176, 199], radius=4, fill=ACCENT)

    # スライド本体。影を付けて紙らしく見せる。
    sl = Image.open(os.path.join(OUT_P, src)).convert("RGB")
    sw = W - 160
    sh = int(sw * sl.height / sl.width)
    sl = sl.resize((sw, sh), Image.LANCZOS)
    x, y = 80, 236
    d.rounded_rectangle([x + 4, y + 6, x + sw + 4, y + sh + 6], radius=10, fill=SHADOW)
    img.paste(sl, (x, y))
    d.rectangle([x, y, x + sw - 1, y + sh - 1], outline=LINE, width=1)

    # 説明。ここが本体で、スライドはその例。
    cy = y + sh + 42
    d.rounded_rectangle([84, cy, W - 84, cy + 148], radius=16,
                        fill=CARD, outline=LINE, width=1)
    d.rounded_rectangle([84, cy + 12, 91, cy + 136], radius=4, fill=ACCENT)
    ty = cy + 30
    for t in lines:
        d.text((126, ty), t, font=font(31), fill=BODY)
        ty += 52

    d.text((86, H - 62), NOTE, font=font(25), fill=SUB)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    for i, (src, title, tag, lines) in enumerate(PAGES, 1):
        p = os.path.join(OUT_P, f"deck-m{i}.png")
        im = build(src, title, tag, lines)
        im.save(p)
        print(p, im.size, f"{im.size[0]/im.size[1]:.2f}:1",
              os.path.getsize(p) // 1024, "KB")
