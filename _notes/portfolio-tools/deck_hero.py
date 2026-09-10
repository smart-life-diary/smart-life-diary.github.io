"""出品Gの1枚目・2枚目に置く、目を引かせるための画像を書き出す。

出力
  portfolio/deck-h1.png   ヒーロー（何の出品か・誰が作るか・何で届くか）
  portfolio/deck-h2.png   このサービスは（材料整理 → 構成 → スライド）

上位出品者の画像が効いているのは、受注した資料のサムネイルを敷き詰めている
ところであって、グラデーションや極太フォントではない。こちらに受注実績は
まだ無いので、**架空の顧客名やロゴを載せた「実績風」は作らない。**
代わりに、この出品のために実際に作ったサンプルスライドを並べ、画像の中に
サンプルであることを書く。肩書きも事実だけを置く（建設コンサルタント15年）。

日本語のボールド書体がこの環境に無いため、stroke_width で太らせている。
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from koji_sheet import OUT_P, W, H, font

# ── 配色 ─────────────────────────────────────────────────
G0 = (104, 206, 210)      # 地のグラデーション（左上）
G1 = (58, 170, 196)
G2 = (30, 118, 168)
G3 = (16, 74, 124)        # 右下
YEL = (247, 232, 74)      # 差し色
WHT = (255, 255, 255)
DIM = (206, 228, 238)
INK = (24, 36, 56)
SUB = (108, 124, 145)
ACC = (0, 112, 214)
WARN = (206, 88, 74)
GOOD = (20, 142, 102)
SLATE = (238, 242, 247)


def btext(d, xy, s, sz, fill, bold=0, anchor=None):
    """日本語の太字が無いので、輪郭を重ねて太らせる。"""
    f = font(sz)
    if bold:
        d.text(xy, s, font=f, fill=fill, stroke_width=bold, stroke_fill=fill, anchor=anchor)
    else:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)


def tw(d, s, sz, bold=0):
    return d.textlength(s, font=font(sz)) + bold * 2


def runs(d, x, y, parts, sz, bold=0):
    """[(文字列, 色), ...] を横に continuous に描く。語ごとに色を変えるため。"""
    for s, col in parts:
        btext(d, (x, y), s, sz, col, bold)
        x += tw(d, s, sz, bold)
    return x


def gradient(w, h):
    """四隅の色を補間した地を作る。小さく作って引き伸ばすと滑らかになる。"""
    seed = Image.new("RGB", (2, 2))
    seed.putdata([G0, G1, G2, G3])
    return seed.resize((w, h), Image.BICUBIC)


def glow(img, cx, cy, r, strength=0.30):
    """指定の位置に白い光を落として、平坦なグラデーションに奥行きを出す。"""
    layer = Image.new("L", img.size, 0)
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.55))
    layer = layer.point(lambda v: int(v * strength))
    return Image.composite(Image.new("RGB", img.size, WHT), img, layer)


def shadow_paste(base, im, x, y, blur=16, alpha=110, spread=8):
    """影付きで貼る。回転済みの画像でも輪郭に沿った影になる。"""
    a = im.getchannel("A") if im.mode == "RGBA" else Image.new("L", im.size, 255)
    sh = Image.new("L", (im.width + spread * 4, im.height + spread * 4), 0)
    sh.paste(a, (spread * 2, spread * 2))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha / 255))
    base.paste(Image.new("RGB", sh.size, (6, 30, 52)),
               (x - spread * 2, y - spread * 2 + spread), sh)
    base.paste(im, (x, y), a)


# ── サンプルスライド（16:9）─────────────────────────────
SW, SH = 1024, 576


def _base(title, tag=None):
    im = Image.new("RGB", (SW, SH), WHT)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SW, 8], fill=ACC)
    d.rectangle([56, 52, 66, 92], fill=ACC)
    btext(d, (86, 50), title, 40, INK, 1)
    d.line([56, 118, SW - 56, 118], fill=(222, 229, 238), width=2)
    if tag:
        btext(d, (SW - 56 - tw(d, tag, 22), 62), tag, 22, SUB)
    return im, d


def _box(d, x, y, w, h, fill=SLATE, outline=None, r=10):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                        outline=outline, width=2 if outline else 0)


def sl_cover():
    im = Image.new("RGB", (SW, SH), (16, 74, 124))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, SH], fill=YEL)
    btext(d, (86, 200), "現場の残業を減らす", 60, WHT, 1)
    btext(d, (86, 284), "施工管理アプリのご提案", 60, WHT, 1)
    d.rounded_rectangle([88, 392, 178, 400], radius=4, fill=YEL)
    btext(d, (86, 432), "2026年9月　営業本部", 28, DIM)
    return im


def sl_issue():
    im, d = _base("いま起きていること", "2")
    xs = [56, 386, 716]
    for i, (t, s) in enumerate([("残業が減らない", "月平均 42時間"),
                                ("紙の日報", "転記に1日1時間"),
                                ("若手が辞める", "3年で4割")]):
        _box(d, xs[i], 170, 252, 300, fill=(253, 238, 236))
        d.rounded_rectangle([xs[i], 170, xs[i] + 252, 178], radius=4, fill=WARN)
        btext(d, (xs[i] + 26, 216), t, 32, INK, 1)
        btext(d, (xs[i] + 26, 288), s, 26, WARN)
    btext(d, (56, 502), "どれも現場側では止められない", 26, SUB)
    return im


def sl_compare():
    im, d = _base("導入前と導入後", "5")
    for i, (t, col, soft, rows) in enumerate([
            ("導入前", WARN, (253, 238, 236), ["紙の日報を持ち帰る", "事務所で転記", "集計は月末にまとめて"]),
            ("導入後", GOOD, (232, 247, 240), ["現場でその場に入力", "転記なし", "集計は自動"])]):
        x = 56 + i * 484
        d.rounded_rectangle([x, 158, x + 428, 214], radius=10, fill=col)
        btext(d, (x + 214 - tw(d, t, 30, 1) / 2, 168), t, 30, WHT, 1)
        y = 240
        for r in rows:
            _box(d, x, y, 428, 74, fill=soft)
            btext(d, (x + 28, y + 20), r, 28, INK)
            y += 88
    d.polygon([(500, 330), (500, 366), (524, 348)], fill=ACC)
    return im


def sl_flow():
    im, d = _base("導入の進め方", "8")
    names = ["現状の確認", "設定", "現場で試す", "全社展開"]
    x = 56
    for i, n in enumerate(names):
        _box(d, x, 240, 194, 130, fill=(232, 241, 252))
        d.rounded_rectangle([x, 240, x + 194, 248], radius=4, fill=ACC)
        btext(d, (x + 97 - tw(d, n, 28, 1) / 2, 286), n, 28, INK, 1)
        btext(d, (x + 97 - tw(d, f"STEP {i+1}", 20) / 2, 392), f"STEP {i + 1}", 20, SUB)
        if i < 3:
            d.polygon([(x + 208, 292), (x + 208, 318), (x + 230, 305)], fill=ACC)
        x += 242
    btext(d, (56, 470), "1〜4 でおよそ 2か月", 26, SUB)
    return im


def sl_number():
    im, d = _base("導入した3社の変化", "6")
    for i, (v, u, t) in enumerate([("20", "時間", "1社あたりの残業削減／月"),
                                   ("0", "件", "日報の転記ミス"),
                                   ("3", "社", "導入企業")]):
        x = 56 + i * 330
        _box(d, x, 170, 252, 290, fill=(232, 241, 252))
        btext(d, (x + 40, 206), v, 96, ACC, 2)
        btext(d, (x + 40 + tw(d, v, 96, 2) + 10, 282), u, 30, ACC)
        btext(d, (x + 40, 352), t, 22, SUB)
    return im


def sl_gantt():
    im, d = _base("スケジュール", "9")
    rows = [("要件の確認", 0, 2), ("初期設定", 1, 3), ("試験運用", 3, 5), ("全社展開", 5, 8)]
    x0, cw = 300, 84
    for i in range(8):
        btext(d, (x0 + i * cw + 20, 150), f"{i + 1}月", 20, SUB)
    y = 196
    for name, s, e in rows:
        btext(d, (56, y + 12), name, 26, INK)
        d.rounded_rectangle([x0, y, x0 + cw * 8, y + 48], radius=6, fill=SLATE)
        d.rounded_rectangle([x0 + s * cw, y, x0 + e * cw, y + 48], radius=6, fill=ACC)
        y += 68
    return im


def sl_cost():
    im, d = _base("費用", "10")
    heads = ["項目", "初年度", "次年度以降"]
    ws = [430, 240, 240]
    x = 56
    for i, h in enumerate(heads):
        d.rectangle([x, 168, x + ws[i], 226], fill=(31, 59, 87))
        btext(d, (x + 20, 182), h, 26, WHT, 1)
        x += ws[i]
    rows = [("利用料（20名）", "720,000円", "720,000円"),
            ("初期設定", "150,000円", "—"),
            ("合計", "870,000円", "720,000円")]
    y = 226
    for j, r in enumerate(rows):
        x = 56
        bg = (232, 241, 252) if j == 2 else WHT
        for i, c in enumerate(r):
            d.rectangle([x, y, x + ws[i], y + 62], fill=bg, outline=(214, 220, 228))
            btext(d, (x + 20, y + 16), c, 26, INK, 1 if j == 2 else 0)
            x += ws[i]
        y += 62
    return im


def sl_close():
    im = Image.new("RGB", (SW, SH), (232, 241, 252))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, SW, 10], fill=ACC)
    btext(d, (86, 194), "まずは30分の説明会から", 56, INK, 1)
    d.rounded_rectangle([88, 296, 178, 304], radius=4, fill=ACC)
    btext(d, (86, 336), "御社の現場に合うかどうかを、実際の画面でご確認ください", 28, (70, 84, 104))
    d.rounded_rectangle([86, 412, 470, 486], radius=12, fill=ACC)
    btext(d, (126, 432), "お申し込みはこちら", 30, WHT, 1)
    return im


SLIDES = [sl_cover, sl_issue, sl_compare, sl_flow, sl_number, sl_gantt, sl_cost, sl_close]


def thumb(i, w, angle=0.0):
    """サンプルスライドを縮小し、必要なら傾けて返す（RGBA）。"""
    im = SLIDES[i]().resize((w, int(w * SH / SW)), Image.LANCZOS)
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width - 1, im.height - 1], outline=(255, 255, 255, 255), width=3)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


# ── 1枚目：ヒーロー ──────────────────────────────────────
def hero():
    img = gradient(W, H)
    img = glow(img, 1180, 230, 620, 0.34)
    img = glow(img, 180, 1120, 520, 0.16)

    # 右上にサンプルを散らす。読ませるものではないので密度だけ作る。
    for i, (x, y, w, a) in enumerate([
            (952, 92, 470, -7.0), (1236, 330, 430, 5.0), (868, 470, 400, 3.5),
            (1188, 690, 440, -5.5), (900, 872, 420, 6.0), (1300, 1010, 400, -4.0)]):
        shadow_paste(img, thumb(i, w, a), x, y, blur=18, alpha=120)

    d = ImageDraw.Draw(img, "RGBA")
    # 左側を少し沈めて文字を乗せる
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(veil).rectangle([0, 0, 930, H], fill=(10, 52, 90, 96))
    veil = veil.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img.convert("RGBA"), veil).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    d.rounded_rectangle([84, 92, 470, 148], radius=28, fill=(255, 255, 255, 46))
    btext(d, (112, 100), "建設コンサルタント 15年", 32, WHT, 1)

    btext(d, (84, 192), "読まれる資料は、", 46, DIM)
    btext(d, (84, 262), "順番が違います", 46, DIM)

    runs(d, (84), 366, [("提案書", YEL), ("・", WHT), ("営業資料", YEL)], 88, 3)
    btext(d, (84, 516), "を構成から作ります", 64, WHT, 2)

    d.rounded_rectangle([88, 632, 178, 642], radius=5, fill=YEL)
    btext(d, (84, 674), "頭の中の材料を、相手が知りたい順に組み直します。", 33, WHT)
    btext(d, (84, 726), "作るのは見た目より先に、話の並びです。", 33, WHT)

    # 事実だけのバッジ
    for i, (t, s) in enumerate([("公共案件の", "技術提案書"), ("構成案を", "先にお出し"),
                                ("修正", "2回まで")]):
        x = 84 + i * 268
        d.rounded_rectangle([x, 800, x + 240, 952], radius=16, fill=(255, 255, 255, 34),
                            outline=(255, 255, 255, 90), width=2)
        btext(d, (x + 120 - tw(d, t, 28) / 2, 830), t, 28, DIM)
        btext(d, (x + 120 - tw(d, s, 32, 1) / 2, 874), s, 32, YEL, 1)

    # 対応形式
    x = 84
    for t in ["PowerPoint", "Word", "PDF"]:
        w_ = tw(d, t, 34, 1) + 64
        d.rounded_rectangle([x, 1024, x + w_, 1090], radius=33, fill=(255, 255, 255, 232))
        btext(d, (x + 32, 1038), t, 34, (16, 74, 124), 1)
        x += w_ + 18
    btext(d, (x + 8, 1038), "でお渡し", 32, WHT)

    btext(d, (84, 1176), "※ 掲載しているスライドは、この出品のために作成したサンプルです。",
          24, (214, 232, 240))
    return img


# ── 2枚目：このサービスは ────────────────────────────────
def what():
    img = gradient(W, H)
    img = glow(img, 780, 180, 700, 0.34)
    d = ImageDraw.Draw(img, "RGBA")

    d.rounded_rectangle([580, 62, 980, 122], radius=30, fill=(255, 255, 255, 52))
    btext(d, (780 - tw(d, "このサービスは", 36, 1) / 2, 70), "このサービスは", 36, WHT, 1)

    y = 166
    steps = [("材料を出す", "メモ・既存資料・話した内容"),
             ("構成に組む", "何を、どの順番で、何枚で"),
             ("スライドにする", "PowerPoint でお渡し")]
    bw, gap = 426, 60
    x = 80
    for i, (t, s) in enumerate(steps):
        btext(d, (x + bw / 2 - tw(d, t, 54, 3) / 2, y + 6), t, 54, YEL, 3)
        btext(d, (x + bw / 2 - tw(d, s, 26) / 2, y + 92), s, 26, DIM)
        if i < 2:
            cx = x + bw + 14
            d.polygon([(cx, y + 22), (cx, y + 70), (cx + 32, y + 46)], fill=(255, 255, 255, 210))
        x += bw + gap

    btext(d, (780 - tw(d, "見た目を整える前に、話の並びを決めます。", 36) / 2, 304),
          "見た目を整える前に、話の並びを決めます。", 36, WHT)

    # サンプルを3枚、大きめに見せる
    for i, (idx, xx, yy, w_, a) in enumerate([(0, 106, 396, 460, -3.0),
                                              (2, 556, 372, 470, 2.0),
                                              (4, 1022, 396, 452, -2.5)]):
        shadow_paste(img, thumb(idx, w_, a), xx, yy, blur=16, alpha=110)
    d = ImageDraw.Draw(img, "RGBA")

    btext(d, (780 - tw(d, "※ サンプルとして作成したスライドです", 24) / 2, 700),
          "※ サンプルとして作成したスライドです", 24, (214, 232, 240))

    d.rounded_rectangle([92, 776, W - 92, 986], radius=20, fill=(255, 255, 255, 40),
                        outline=(255, 255, 255, 92), width=2)
    btext(d, (136, 808), "作れるもの", 32, YEL, 1)
    items = ["営業資料", "提案書", "会社案内", "事業計画書", "社内説明資料", "登壇資料"]
    x, yy = 136, 876
    for t in items:
        w_ = tw(d, t, 32, 1) + 52
        if x + w_ > W - 136:
            x, yy = 136, yy + 74
        d.rounded_rectangle([x, yy, x + w_, yy + 62], radius=31, fill=(255, 255, 255, 226))
        btext(d, (x + 26, yy + 12), t, 32, (16, 74, 124), 1)
        x += w_ + 16

    d.rounded_rectangle([96, 1058, 186, 1068], radius=5, fill=YEL)
    btext(d, (92, 1108), "建設コンサルタントとして15年、公共案件の技術提案書を書いてきました。",
          34, WHT)
    btext(d, (92, 1162), "専門用語の多い話を、専門外の相手に伝わる形へ置き換える作業が中心です。",
          34, WHT)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    for name, fn in [("deck-h1", hero), ("deck-h2", what)]:
        p = os.path.join(OUT_P, f"{name}.png")
        im = fn()
        im.save(p)
        print(p, im.size, f"{im.size[0] / im.size[1]:.2f}:1", os.path.getsize(p) // 1024, "KB")

    # ヒーローに散らしているサンプルを、ポートフォリオ登録用に単体でも書き出す。
    # 登録するときは説明文に「この出品のために作成したサンプル」と明記すること。
    for i, fn in enumerate(SLIDES, start=1):
        p = os.path.join(OUT_P, f"deck-sample-{i:02d}.png")
        fn().resize((1920, 1080), Image.LANCZOS).save(p)
        print(p, os.path.getsize(p) // 1024, "KB")
