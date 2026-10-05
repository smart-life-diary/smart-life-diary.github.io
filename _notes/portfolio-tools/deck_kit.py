"""出品Gの画像の残り3枠を埋める。

出力
  portfolio/deck-k1.png  購入から納品までの流れ
  portfolio/deck-k2.png  8,000円に含まれるもの／有料オプション
  portfolio/deck-k3.png  お受けできること・できないこと／資料の扱い

すでに登録してある7枚は「何を作るか」と「どんな出来か」しか見せていない。
**買う直前に止まる理由は、そこではない。**
どう進むのか、総額はいくらになるのか、頼んでいいものなのか。
この3つを画像で先に潰す。

中身はすべて出品ページに書いてあることの引き写しで、新しい約束はしていない。
金額・オプション名・納期・修正回数は、公開中のページから取ったそのままの値。
**ここを画像側で盛ると、購入後に必ず食い違う。**

見た目は deck-m1〜m5 と同じ。ヒーローだけ濃色で、以降は明るい面で揃える。
"""
import os

from PIL import Image, ImageDraw, ImageFont

from koji_sheet import OUT_P

NOTO_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
NOTO_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

W, H = 1560, 1300
M = 84                                   # 左右の余白

BG     = (244, 247, 251)
CARD   = (255, 255, 255)
LINE   = (222, 229, 238)
INK    = (24, 36, 56)
SUB    = (108, 124, 145)
BODY   = (70, 84, 104)
ACCENT = (0, 112, 214)
SOFT   = (233, 241, 251)
OK     = (14, 132, 92)
OKBG   = (232, 246, 240)
NG     = (192, 58, 58)
NGBG   = (253, 238, 238)
GOLD   = (168, 130, 38)
GOLDBG = (252, 246, 231)


def font(sz, bold=False):
    return ImageFont.truetype(NOTO_B if bold else NOTO_R, sz, index=0)


def head(d, title, sub):
    d.text((M, 60), title, font=font(52, True), fill=INK)
    d.text((M + 2, 140), sub, font=font(29), fill=SUB)
    d.rounded_rectangle([M + 2, 190, M + 92, 197], radius=4, fill=ACCENT)


def card(d, y0, y1, fill=CARD, outline=LINE):
    d.rounded_rectangle([M, y0, W - M, y1], radius=18, fill=fill, outline=outline, width=1)


def cap(d, x, y, text, bg, fg, pad=18, sz=27):
    f = font(sz, True)
    w = int(d.textlength(text, font=f))
    d.rounded_rectangle([x, y, x + w + pad * 2, y + sz + 18], radius=(sz + 18) // 2, fill=bg)
    d.text((x + pad, y + 8), text, font=f, fill=fg)
    return x + w + pad * 2


NOTE = "※ 記載の金額・日数・回数は、この出品ページに登録しているものと同じです。"


# ---------------------------------------------------------------- k1 流れ

STEPS = [
    ("ご購入前に、この4つをメッセージでお知らせください",
     "誰に見せる資料か／相手にどうしてほしいか／盛り込みたい内容／希望納期"),
    ("構成案をお出しします",
     "何を、どの順番で、何枚で伝えるか。本文を作る前に、ここで方向を確認します"),
    ("ご承認をいただいてから、作成に入ります",
     "方向が違うと感じられた場合は、構成の段階で組み直せます"),
    ("スライドを作成します（10枚まで）",
     "PowerPoint（.pptx）で、編集できる状態のままお渡しします"),
    ("ご要望を2回まで反映します",
     "無料修正2回。お届け日数は5日（予定）です"),
]


def k1():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    head(d, "購入してから、納品までの流れ", "お届け日数 5日（予定）／無料修正 2回")

    y = 236
    for i, (t, s) in enumerate(STEPS, 1):
        card(d, y, y + 128)
        d.ellipse([M + 30, y + 34, M + 90, y + 94], fill=SOFT)
        n = str(i)
        f = font(34, True)
        d.text((M + 60 - d.textlength(n, font=f) / 2, y + 47), n, font=f, fill=ACCENT)
        d.text((M + 120, y + 32), t, font=font(33, True), fill=INK)
        d.text((M + 120, y + 80), s, font=font(26), fill=BODY)
        if i < len(STEPS):
            d.polygon([(M + 60, y + 144), (M + 46, y + 132), (M + 74, y + 132)],
                      fill=(206, 216, 229))
        y += 152

    card(d, y + 8, y + 158, fill=GOLDBG, outline=(238, 226, 194))
    d.text((M + 34, y + 34), "作業できる時間について", font=font(29, True), fill=GOLD)
    d.text((M + 34, y + 80),
           "平日は19時以降、土日は日中に作業しています。一次返信は24時間以内を目安に。",
           font=font(26), fill=BODY)
    d.text((M + 34, y + 114),
           "予定日に間に合わない見込みが立った時点で、早めにご連絡します。",
           font=font(26), fill=BODY)

    d.text((M + 2, H - 52), NOTE, font=font(24), fill=SUB)
    return img


# ---------------------------------------------------------------- k2 料金

INCLUDED = [
    "構成案の作成（何を、どの順番で、何枚で）",
    "スライド10枚までの作成",
    "PowerPoint（.pptx）で納品",
    "無料修正 2回",
]

OPTIONS = [
    ("スライド5枚追加", "＋2,000円"),
    ("図解を1点作成", "＋1,500円"),
    ("発表用の読み原稿（スピーカーノート）", "＋2,000円"),
    ("配布用PDFの作成", "＋500円"),
    ("既存資料の書き起こし・整理", "＋3,000円"),
    ("Word版もあわせて作成", "＋2,000円"),
    ("お急ぎ対応（3日以内）", "＋3,000円"),
]


def k2():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    head(d, "8,000円に、どこまで含まれるか", "追加したい分だけ、オプションで足せます")

    card(d, 236, 496, fill=OKBG, outline=(206, 231, 220))
    d.text((M + 34, 262), "基本料金 8,000円 に含まれるもの", font=font(31, True), fill=OK)
    for i, t in enumerate(INCLUDED):
        x = M + 34 + (i % 2) * 690
        y = 324 + (i // 2) * 74
        d.ellipse([x, y + 6, x + 28, y + 34], outline=OK, width=3)
        d.line([(x + 7, y + 20), (x + 12, y + 27), (x + 21, y + 13)], fill=OK, width=4)
        d.text((x + 44, y), t, font=font(28), fill=BODY)

    top = 540
    card(d, top, top + 560)
    f = font(31, True)
    d.text((M + 34, top + 26), "有料オプション", font=f, fill=INK)
    d.text((M + 34 + d.textlength("有料オプション", font=f) + 24, top + 33),
           "必要なものだけお選びいただけます", font=font(25), fill=SUB)
    y = top + 90
    for i, (name, price) in enumerate(OPTIONS):
        if i:
            d.line([(M + 34, y), (W - M - 34, y)], fill=(238, 242, 248), width=1)
        d.text((M + 34, y + 16), name, font=font(29), fill=BODY)
        f = font(29, True)
        d.text((W - M - 34 - d.textlength(price, font=f), y + 16), price, font=f, fill=ACCENT)
        y += 66

    card(d, 1128, 1236, fill=SOFT, outline=(210, 226, 245))
    d.text((M + 34, 1148), "見積り相談は無料です", font=font(29, True), fill=ACCENT)
    d.text((M + 34, 1190),
           "枚数や内容が決まっていない段階でも、総額の目安をお出しできます。",
           font=font(26), fill=BODY)

    d.text((M + 2, H - 38), NOTE, font=font(24), fill=SUB)
    return img


# ---------------------------------------------------------------- k3 範囲

CAN = ["サービス紹介資料", "提案書", "会社紹介資料",
       "社内の決裁を通す説明資料", "展示会・セミナーの配布資料"]

CANNOT = [
    ("イラスト・写真の描き起こし", "図解の作成は有料オプションで承ります"),
    ("ブランドガイドラインの策定", "既存のガイドラインに沿わせることは可能です"),
    ("税務・法務・労務の判断を伴う内容", "士業の業務にあたるため、お受けできません"),
]

CARE = [
    "社名・個人名・金額など、伏せたい部分はマスキングのうえお送りください。伏せたままでも構成は作れます。",
    "ご提供いただいた資料と完成ファイルは、納品完了から2週間を目安に削除します。",
    "機密保持契約（NDA）の締結に対応しています。",
]


def k3():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    head(d, "お受けできること、できないこと", "先に線を引いておきます")

    card(d, 236, 430, fill=OKBG, outline=(206, 231, 220))
    d.text((M + 34, 260), "対応できる資料", font=font(31, True), fill=OK)
    x, y = M + 34, 318
    for i, t in enumerate(CAN):
        if i == 3:
            x, y = M + 34, 368
        x = cap(d, x, y, t, (255, 255, 255), OK, sz=26) + 14

    card(d, 462, 800, fill=NGBG, outline=(243, 214, 214))
    d.text((M + 34, 486), "お受けできないこと", font=font(31, True), fill=NG)
    y = 548
    for t, s in CANNOT:
        d.line([(M + 36, y + 18), (M + 62, y + 18)], fill=NG, width=4)
        d.text((M + 78, y), t, font=font(29, True), fill=INK)
        d.text((M + 78, y + 44), s, font=font(25), fill=BODY)
        y += 84

    card(d, 832, 1080)
    d.text((M + 34, 856), "お預かりした資料の扱い", font=font(31, True), fill=INK)
    y = 916
    for t in CARE:
        d.ellipse([M + 36, y + 10, M + 50, y + 24], fill=ACCENT)
        d.text((M + 70, y), t, font=font(26), fill=BODY)
        y += 52

    card(d, 1112, 1250, fill=SOFT, outline=(210, 226, 245))
    d.text((M + 34, 1132), "原稿がまとまっていなくても大丈夫です",
           font=font(29, True), fill=ACCENT)
    d.text((M + 34, 1174),
           "箇条書きのメモ、既存の資料、話した内容の書き起こし。どの形でも構いません。",
           font=font(26), fill=BODY)
    d.text((M + 34, 1210),
           "何を伝えたいかさえあれば、順番と言葉はこちらで組み立てます。",
           font=font(26), fill=BODY)
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    for i, fn in enumerate((k1, k2, k3), 1):
        p = os.path.join(OUT_P, f"deck-k{i}.png")
        im = fn()
        im.save(p)
        print(p, im.size, f"{im.size[0]/im.size[1]:.2f}:1",
              os.path.getsize(p) // 1024, "KB")
