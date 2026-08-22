"""ココナラ プロフィールのカバー画像を作る。

アイコンがカバーの左下に重なるため、文字は横中央・やや上寄せに置く。
背景にはデモ5本の実画面を薄く敷き、何を作る人かが一目で伝わるようにしている。
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(__file__)
SHOTS = os.path.join(HERE, "shots")
OUT = os.path.join(HERE, "..", "..", "portfolio")
FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"

W, H = 2000, 500
BG = (14, 20, 36)
GOLD = (232, 196, 119)
INK = (238, 242, 251)
MUT = (150, 163, 192)

DEMOS = ["isekai", "side-biz", "ai-level", "shachiku", "golf"]
TITLE = "スマホで動く診断コンテンツを、企画から実装まで"
POINTS = ["HTML1ファイルで納品", "実物デモ5点", "12タイプ分岐まで対応"]


def font(sz):
    return ImageFont.truetype(FONT, sz)


def bold(d, xy, text, f, fill, anchor="la"):
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        d.text((xy[0] + dx, xy[1] + dy), text, font=f, fill=fill, anchor=anchor)


# 背景：デモ5本の画面を等間隔に敷く
layer = Image.new("RGB", (W, H), BG)
slot = W // 5
for i, slug in enumerate(DEMOS):
    im = Image.open(f"{SHOTS}/{slug}-3-result.png").convert("RGB")
    w = round(im.width * H / im.height)
    im = im.resize((w, H), Image.LANCZOS)
    layer.paste(im, (i * slot + (slot - w) // 2, 0))

# 実画面と分かる程度に残しつつ、文字の邪魔をしないところまでぼかして沈める
layer = layer.filter(ImageFilter.GaussianBlur(5))
canvas = Image.blend(Image.new("RGB", (W, H), BG), layer, 0.34)
veil = Image.new("RGBA", (W, H), (14, 20, 36, 150))
vd = ImageDraw.Draw(veil)
# 文字が乗る中央帯はさらに濃く落とす
for i in range(90):
    a = int(150 + 88 * (1 - abs(i - 45) / 45))
    vd.line([(0, 90 + i * 3), (W, 90 + i * 3)], fill=(14, 20, 36, a), width=3)
canvas = Image.alpha_composite(canvas.convert("RGBA"), veil).convert("RGB")

d = ImageDraw.Draw(canvas)
cx = W // 2

# 見出し（横中央・やや上寄せ。左下はアイコンが重なるので使わない）
d.text((cx, 118), "DIAGNOSTIC  CONTENT", font=font(26), fill=GOLD, anchor="ma")
bold(d, (cx, 172), TITLE, font(58), INK, anchor="ma")

# 訴求3点をピルで横並び
f = font(27)
pads, gap = 26, 22
widths = [d.textlength(p, font=f) + pads * 2 for p in POINTS]
total = sum(widths) + gap * (len(POINTS) - 1)
x = cx - total / 2
y = 288
for p, w in zip(POINTS, widths):
    d.rounded_rectangle((x, y, x + w, y + 56), radius=28, outline=(60, 78, 116), width=2)
    d.text((x + w / 2, y + 13), p, font=f, fill=MUT, anchor="ma")
    x += w + gap

os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "cover.png")
canvas.save(path, optimize=True)
print(path, canvas.size, f"{os.path.getsize(path)//1024}KB")
