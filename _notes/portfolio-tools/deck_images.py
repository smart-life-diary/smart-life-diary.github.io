"""出品G（提案書・営業資料の制作）で使う画像3枚を書き出す。

  portfolio/deck-1.png  構成案の実物
  portfolio/deck-2.png  並び順で伝わり方が変わること
  portfolio/deck-3.png  メモ書きから納品までの流れ

この出品で見せるべきなのは完成スライドの美しさではない。競合はデザインの
上手さで並んでいるので、そこで比べられると評価数の差がそのまま出る。
見せるのは「どう組み立てるか」のほう。
"""
import os
from PIL import Image, ImageDraw

from koji_sheet import board, font, OUT_P, W, H, ACCENT

CARD_BG = (24, 33, 54)
MUTED = (150, 172, 200)
PALE = (214, 226, 242)
WARN = (206, 84, 74)
GOOD = (70, 160, 120)


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
    x, w_ = 120, W - 240
    yy = y
    for no, name, note in rows:
        d.rectangle([x, yy, x + w_, yy + 100], fill=CARD_BG)
        d.rectangle([x, yy, x + 10, yy + 100], fill=ACCENT)
        nf = font(30)
        d.text((x + 36, yy + 34), no, font=nf, fill=ACCENT)
        d.text((x + 132, yy + 30), name, font=font(34), fill=(255, 255, 255))
        if note:
            tl = d.textlength(note, font=font(24))
            d.text((x + w_ - 32 - tl, yy + 38), note, font=font(24), fill=MUTED)
        yy += 112
    d.text((x, yy + 26),
           "順番はご依頼内容によって変わります。作ってから大きく直す、が起きません。",
           font=font(29), fill=PALE)
    return img


def img2():
    """同じ材料でも並べ方で変わる、を左右で見せる。"""
    img, d, y = board("同じ材料でも、順番で伝わり方が変わります",
                      "自分の話から始めるか、相手の話から始めるか")
    left = ["会社の紹介", "これまでの実績", "サービス一覧", "料金表", "お問い合わせ先"]
    right = ["あなたの現状", "放っておくとどうなるか", "こうしませんか（提案）",
             "できる根拠", "進め方と費用", "次にすること"]
    cw, gap = 620, 80
    x0 = (W - cw * 2 - gap) // 2
    for k, (title, items, col, note) in enumerate([
            ("よくある並び", left, WARN, "自分の話から始まっている"),
            ("組み立て直した並び", right, GOOD, "相手の話から始まっている")]):
        bx = x0 + k * (cw + gap)
        d.rectangle([bx, y, bx + cw, y + 62], fill=col)
        tl = d.textlength(title, font=font(32))
        d.text((bx + cw / 2 - tl / 2, y + 12), title, font=font(32), fill=(255, 255, 255))
        yy = y + 86
        for i, it in enumerate(items, 1):
            d.rectangle([bx, yy, bx + cw, yy + 96], fill=CARD_BG)
            d.text((bx + 28, yy + 32), f"{i}", font=font(26), fill=col)
            d.text((bx + 78, yy + 28), it, font=font(31), fill=(255, 255, 255))
            yy += 106
        note_y = y + 86 + 106 * 6 + 20      # 長いほうの列にそろえる
        d.text((bx + 4, note_y), note, font=font(26), fill=MUTED)
    d.text((x0, y + 86 + 106 * 6 + 84),
           "材料は同じです。並べ替えただけで、相手が読む理由が変わります。",
           font=font(30), fill=PALE)
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
    x, w_ = 110, W - 220
    yy = y
    for i, (title, items, note) in enumerate(steps, 1):
        h = 74 + len(items) * 40 + 34
        d.rectangle([x, yy, x + w_, yy + h], fill=CARD_BG)
        d.rectangle([x, yy, x + 10, yy + h], fill=ACCENT)
        d.text((x + 36, yy + 22), f"{i}", font=font(32), fill=ACCENT)
        d.text((x + 86, yy + 20), title, font=font(34), fill=(255, 255, 255))
        tl = d.textlength(note, font=font(24))
        d.text((x + w_ - 30 - tl, yy + 28), note, font=font(24), fill=MUTED)
        ty = yy + 76
        for it in items:
            d.text((x + 96, ty), it, font=font(26), fill=PALE)
            ty += 40
        yy += h + 26
        if i < len(steps):
            cx = x + w_ / 2
            d.polygon([(cx - 16, yy - 20), (cx + 16, yy - 20), (cx, yy - 2)], fill=ACCENT)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    for i, fn in enumerate([img1, img2, img3], start=1):
        im = fn()
        p = os.path.join(OUT_P, f"deck-{i}.png")
        im.save(p)
        print(p, im.size, f"{im.size[0]/im.size[1]:.2f}:1", os.path.getsize(p) // 1024, "KB")
