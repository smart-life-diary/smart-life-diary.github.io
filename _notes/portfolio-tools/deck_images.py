"""出品G（提案書・営業資料の制作）で使う画像3枚を書き出す。

  portfolio/deck-1.png  構成案の実物
  portfolio/deck-2.png  並び順で伝わり方が変わること
  portfolio/deck-3.png  メモ書きから納品までの流れ

この出品で見せるべきなのは完成スライドの美しさではない。競合はデザインの
上手さで並んでいるので、そこで比べられると評価数の差がそのまま出る。
見せるのは「どう組み立てるか」のほう。

ただし資料制作の出品である以上、画像そのものの見栄えが信用になる。
明るい地に白いカードを置き、影と角丸で立体を作る。
"""
import os
from PIL import Image, ImageDraw

from koji_sheet import font, OUT_P, W, H

# ── 配色 ─────────────────────────────────────────────────
BG        = (244, 247, 251)      # 地
CARD      = (255, 255, 255)
LINE      = (222, 229, 238)      # カードの縁
SHADOW    = (214, 222, 233)      # 影
INK       = (24, 36, 56)         # 本文
SUB       = (108, 124, 145)      # 補足
ACCENT    = (0, 112, 214)
ACCENT_BG = (232, 241, 252)
WARN      = (206, 88, 74)
WARN_BG   = (253, 238, 236)
GOOD      = (20, 142, 102)
GOOD_BG   = (232, 247, 240)


def board(title, sub):
    """明るい地にタイトルを置いて (img, draw, 本文の開始y) を返す。"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((84, 66), title, font=font(62), fill=INK)
    d.text((86, 156), sub, font=font(31), fill=SUB)
    d.rounded_rectangle([86, 206, 176, 213], radius=4, fill=ACCENT)
    return img, d, 254


def card(d, x, y, w, h, accent=ACCENT, r=14):
    """白いカード。右下に影を落とし、左端に色の帯を入れる。"""
    d.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=r, fill=SHADOW)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=CARD, outline=LINE, width=1)
    d.rounded_rectangle([x, y + 8, x + 7, y + h - 8], radius=4, fill=accent)


def right_text(d, x_right, y, text, f, fill):
    d.text((x_right - d.textlength(text, font=f), y), text, font=f, fill=fill)


def img1():
    """構成案そのものを見せる。10枚の並びが商品の中身。"""
    img, d, y = board("本文を作る前に、構成案をお出しします",
                      "何を、どの順番で、何枚で伝えるか。ここで方向を確認してから作ります")
    rows = [
        ("1", "表紙", ""),
        ("2", "相手がいま置かれている状況", "ここを外すと最後まで読まれません"),
        ("3", "そのままにすると何が起きるか", ""),
        ("4", "こちらの提案", ""),
        ("5-7", "その根拠", "実績・数字・事例"),
        ("8", "進め方と期間", ""),
        ("9", "費用", ""),
        ("10", "次にしていただきたいこと", "問い合わせ／面談／承認"),
    ]
    x, w_ = 110, W - 220
    yy = y
    for no, name, note in rows:
        card(d, x, yy, w_, 96)
        d.rounded_rectangle([x + 30, yy + 24, x + 108, yy + 72], radius=10, fill=ACCENT_BG)
        nf = font(28)
        d.text((x + 69 - d.textlength(no, font=nf) / 2, yy + 34), no, font=nf, fill=ACCENT)
        d.text((x + 136, yy + 28), name, font=font(35), fill=INK)
        if note:
            right_text(d, x + w_ - 32, yy + 36, note, font(24), SUB)
        yy += 108
    d.text((x + 4, yy + 24),
           "順番はご依頼内容によって変わります。作ってから大きく直す、が起きません。",
           font=font(29), fill=SUB)
    return img


def img2():
    """同じ材料でも並べ方で変わる、を左右で見せる。"""
    img, d, y = board("同じ材料でも、順番で伝わり方が変わります",
                      "自分の話から始めるか、相手の話から始めるか")
    cols = [
        ("よくある並び", ["会社の紹介", "これまでの実績", "サービス一覧", "料金表",
                     "お問い合わせ先"], WARN, WARN_BG, "自分の話から始まっている"),
        ("組み立て直した並び", ["あなたの現状", "放っておくとどうなるか", "こうしませんか（提案）",
                       "できる根拠", "進め方と費用", "次にすること"], GOOD, GOOD_BG,
         "相手の話から始まっている"),
    ]
    cw, gap = 626, 74
    x0 = (W - cw * 2 - gap) // 2
    pitch, ch = 100, 88
    for k, (title, items, col, soft, note) in enumerate(cols):
        bx = x0 + k * (cw + gap)
        d.rounded_rectangle([bx, y, bx + cw, y + 66], radius=12, fill=col)
        d.text((bx + cw / 2 - d.textlength(title, font=font(32)) / 2, y + 14),
               title, font=font(32), fill=(255, 255, 255))
        yy = y + 88
        for i, it in enumerate(items, 1):
            card(d, bx, yy, cw, ch, accent=col)
            d.rounded_rectangle([bx + 26, yy + 22, bx + 78, yy + 66], radius=9, fill=soft)
            d.text((bx + 52 - d.textlength(str(i), font=font(26)) / 2, yy + 30),
                   str(i), font=font(26), fill=col)
            d.text((bx + 100, yy + 26), it, font=font(31), fill=INK)
            yy += pitch
        note_y = y + 88 + pitch * 6 + 14
        d.text((bx + 6, note_y), note, font=font(26), fill=col)
    d.text((x0 + 6, y + 88 + pitch * 6 + 74),
           "材料は同じです。並べ替えただけで、相手が読む理由が変わります。",
           font=font(30), fill=SUB)
    return img


def img3():
    """原稿がなくてよい、を流れで見せる。"""
    img, d, y = board("メモ書きからでも作れます",
                      "整った原稿は要りません。何を伝えたいかさえあれば組み立てます")
    steps = [
        ("お送りいただくもの",
         ["・うちは施工管理アプリを売っている", "・現場監督の残業を減らせる",
          "・導入は3社。1社は残業が月20時間減った", "・料金は月3万円から"],
         "箇条書きのメモで構いません"),
        ("構成案をお出しします",
         ["1 表紙", "2 現場監督の残業という問題", "3 放置した場合の離職リスク",
          "4 提案：施工管理アプリ", "5-7 導入3社の実績", "8 導入の進め方",
          "9 費用", "10 まずは30分の説明会を"],
         "ここで方向を確認します"),
        ("PowerPointでお渡しします",
         ["・スライド10枚", "・編集できる .pptx 形式", "・修正2回まで"],
         "使用フォントもお伝えします"),
    ]
    x, w_ = 104, W - 208
    yy = y
    for i, (title, items, note) in enumerate(steps, 1):
        h = 78 + len(items) * 40 + 26
        card(d, x, yy, w_, h)
        d.rounded_rectangle([x + 30, yy + 22, x + 84, yy + 70], radius=10, fill=ACCENT_BG)
        d.text((x + 57 - d.textlength(str(i), font=font(30)) / 2, yy + 30),
               str(i), font=font(30), fill=ACCENT)
        d.text((x + 108, yy + 26), title, font=font(35), fill=INK)
        right_text(d, x + w_ - 30, yy + 34, note, font(24), SUB)
        ty = yy + 84
        for it in items:
            d.text((x + 116, ty), it, font=font(26), fill=(70, 84, 104))
            ty += 40
        yy += h + 24
        if i < len(steps):
            cx = x + w_ / 2
            d.polygon([(cx - 15, yy - 19), (cx + 15, yy - 19), (cx, yy - 3)], fill=ACCENT)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    for i, fn in enumerate([img1, img2, img3], start=1):
        im = fn()
        p = os.path.join(OUT_P, f"deck-{i}.png")
        im.save(p)
        print(p, im.size, f"{im.size[0]/im.size[1]:.2f}:1", os.path.getsize(p) // 1024, "KB")
