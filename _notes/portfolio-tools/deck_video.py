"""出品G（提案書・営業資料の制作）の紹介動画を書き出す。

出力
  _notes/portfolio-tools/videowork/deck-movie.mp4   1920x1080 / 24fps / 約58秒 / 無音

静止画3枚では見せられないものが1つだけある。「並べ替え」そのもの。
よくある並びと、組み立て直した並びを、順に組み上がるところまで見せる。
それ以外のシーンは静止画と同じ話をしているので、長さより短さを優先する。

音は入れない。BGMは権利の確認が要るし、ナレーションは本人の声で
入れたほうが良い。必要になったらこの mp4 に後から重ねる。

ココナラの動画欄はYouTubeのURLしか受け付けない。書き出した mp4 を
YouTubeへ上げてから、そのURLを貼る。
"""
import functools
import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

JP = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "videowork")

VW, VH, FPS = 1920, 1080, 24

# ── 配色（静止画 deck_images.py と揃える）──────────────────
BG        = (244, 247, 251)
CARD      = (255, 255, 255)
LINE      = (222, 229, 238)
SHADOW    = (214, 222, 233)
INK       = (24, 36, 56)
SUB       = (108, 124, 145)
BODY      = (70, 84, 104)
ACCENT    = (0, 112, 214)
ACCENT_BG = (232, 241, 252)
WARN      = (206, 88, 74)
WARN_BG   = (253, 238, 236)
GOOD      = (20, 142, 102)
GOOD_BG   = (232, 247, 240)


@functools.lru_cache(maxsize=64)
def font(sz):
    return ImageFont.truetype(JP, sz)


def A(rgb, a):
    """色に不透明度を付ける。a は 0.0〜1.0。"""
    return rgb + (max(0, min(255, int(a * 255))),)


def ease(x):
    """0→1 を滑らかに。行き過ぎない素直なカーブにする。"""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def app(t, t0, dur=0.45):
    """t0 秒から dur 秒かけて現れる量を返す。"""
    return ease((t - t0) / dur)


def fade(t, dur, tin=0.40, tout=0.35):
    """シーンの入りと終わりの不透明度。"""
    return min(ease(t / tin), ease((dur - t) / tout))


# ── 描画の部品 ───────────────────────────────────────────
def text(d, xy, s, sz, col, a=1.0):
    d.text(xy, s, font=font(sz), fill=A(col, a))


def ctext(d, cx, y, s, sz, col, a=1.0):
    f = font(sz)
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=A(col, a))


def rtext(d, x_right, y, s, sz, col, a=1.0):
    f = font(sz)
    d.text((x_right - d.textlength(s, font=f), y), s, font=f, fill=A(col, a))


def card(d, x, y, w, h, a=1.0, accent=ACCENT, r=14, bar=True):
    """白いカード。右下に影、左端に色の帯。"""
    d.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=r, fill=A(SHADOW, a))
    d.rounded_rectangle([x, y, x + w, y + h], radius=r,
                        fill=A(CARD, a), outline=A(LINE, a), width=1)
    if bar:
        d.rounded_rectangle([x, y + 8, x + 7, y + h - 8], radius=4, fill=A(accent, a))


def head(d, s, sub, a=1.0, dy=0):
    """画面上部の見出し。"""
    text(d, (110, 74 + dy), s, 62, INK, a)
    if sub:
        text(d, (112, 164 + dy), sub, 32, SUB, a)
    d.rounded_rectangle([112, 216 + dy, 202, 223 + dy], radius=4, fill=A(ACCENT, a))


# ── シーン ───────────────────────────────────────────────
def s_title(d, t, dur):
    dy = int(22 * (1 - app(t, 0.0, 0.9)))
    text(d, (150, 386 - dy), "提案書・営業資料を、", 84, INK, app(t, 0.05, 0.7))
    text(d, (150, 502 - dy), "構成から組み立てます", 84, INK, app(t, 0.30, 0.7))
    a2 = app(t, 0.95, 0.7)
    d.rounded_rectangle([152, 640, 242, 648], radius=4, fill=A(ACCENT, a2))
    text(d, (152, 684), "公共案件の技術提案書を15年", 40, SUB, a2)
    text(d, (152, 748), "PowerPoint形式でお渡しします", 34, SUB, app(t, 1.35, 0.7))


def s_problem(d, t, dur):
    head(d, "よくいただくご相談", "", app(t, 0.0, 0.5))
    quotes = ["「作った資料が、読んでもらえない」",
              "「見た目は整えたのに、話が前に進まない」"]
    y = 380
    for i, q in enumerate(quotes):
        a = app(t, 0.45 + i * 0.85, 0.55)
        if a <= 0:
            continue
        dy = int(18 * (1 - a))
        card(d, 150, y + dy, VW - 300, 160, a)
        text(d, (222, y + 54 + dy), q, 48, INK, a)
        y += 230
    text(d, (152, 900), "資料そのものは、きちんと作られていることが多いです。",
         36, SUB, app(t, 2.6, 0.6))


def s_claim(d, t, dur):
    head(d, "原因は、並び順にあることが多いです",
         "デザインの巧拙より先に、ここを見ます", app(t, 0.0, 0.5))
    items = [
        "相手が知りたい順に並んでいない",
        "判断に必要な情報が抜けている",
        "自分の話から始まっていて、読む理由が作られていない",
    ]
    y = 392
    for i, s in enumerate(items):
        a = app(t, 0.4 + i * 0.55, 0.5)
        if a <= 0:
            continue
        dy = int(16 * (1 - a))
        card(d, 190, y + dy, VW - 380, 126, a, accent=WARN)
        d.rounded_rectangle([228, y + 38 + dy, 282, y + 88 + dy], radius=10, fill=A(WARN_BG, a))
        ctext(d, 255, y + 44 + dy, "!", 34, WARN, a)
        text(d, (312, y + 42 + dy), s, 42, INK, a)
        y += 172
    text(d, (192, 952), "デザインを整えても、ここが直っていないと止まったままです。",
         36, SUB, app(t, 2.3, 0.6))


REORDER_L = ["会社の紹介", "これまでの実績", "サービス一覧", "料金表", "お問い合わせ先"]
REORDER_R = ["あなたの現状", "放っておくとどうなるか", "こうしませんか（提案）",
             "できる根拠", "進め方と費用", "次にすること"]


RE_Y0, RE_PITCH, RE_CH = 246, 96, 82


def _column(d, x, w, y0, title, items, col, soft, t, t0, pitch=RE_PITCH, ch=RE_CH):
    a = app(t, t0, 0.45)
    if a <= 0:
        return
    d.rounded_rectangle([x, y0, x + w, y0 + 70], radius=12, fill=A(col, a))
    ctext(d, x + w / 2, y0 + 16, title, 36, (255, 255, 255), a)
    y = y0 + 96
    for i, s in enumerate(items):
        ai = app(t, t0 + 0.35 + i * 0.30, 0.42)
        if ai <= 0:
            break
        dx = int(26 * (1 - ai))
        card(d, x + dx, y, w, ch, ai, accent=col)
        d.rounded_rectangle([x + dx + 26, y + 22, x + dx + 78, y + 66], radius=9, fill=A(soft, ai))
        ctext(d, x + dx + 52, y + 28, str(i + 1), 28, col, ai)
        text(d, (x + dx + 100, y + 24), s, 33, INK, ai)
        y += pitch


def s_reorder(d, t, dur):
    head(d, "同じ材料でも、順番で伝わり方が変わります",
         "自分の話から始めるか、相手の話から始めるか", app(t, 0.0, 0.5))
    cw, gap = 700, 150
    x0 = (VW - cw * 2 - gap) // 2
    y0 = RE_Y0
    _column(d, x0, cw, y0, "よくある並び", REORDER_L, WARN, WARN_BG, t, 0.55)
    _column(d, x0 + cw + gap, cw, y0, "組み立て直した並び", REORDER_R, GOOD, GOOD_BG, t, 5.10)

    a = app(t, 3.10, 0.5)
    if a > 0:
        text(d, (x0 + 6, y0 + 96 + RE_PITCH * 5 + 24), "自分の話から始まっている", 30, WARN, a)
    a = app(t, 8.40, 0.5)
    if a > 0:
        text(d, (x0 + cw + gap + 6, y0 + 96 + RE_PITCH * 6 + 24),
             "相手の話から始まっている", 30, GOOD, a)

    # 中央の矢印。左が組み上がってから出す。
    a = app(t, 4.40, 0.5)
    if a > 0:
        cx, cy = x0 + cw + gap / 2, y0 + 320
        d.polygon([(cx - 34, cy - 26), (cx + 16, cy - 26), (cx + 16, cy - 48),
                   (cx + 52, cy), (cx + 16, cy + 48), (cx + 16, cy + 26), (cx - 34, cy + 26)],
                  fill=A(ACCENT, a * 0.9))

    # 組み上がった右の列を、上から順になぞる。
    if t >= 9.60:
        k = (t - 9.60) / 0.85
        i = int(k)
        if i < len(REORDER_R):
            ring = min(1.0, (k - i) * 2.4) * min(1.0, (len(REORDER_R) - k) * 1.6)
            bx = x0 + cw + gap
            by = y0 + 96 + i * RE_PITCH
            d.rounded_rectangle([bx - 6, by - 6, bx + cw + 6, by + RE_CH + 6],
                                radius=18, outline=A(ACCENT, ring * 0.85), width=5)

    text(d, (x0 + 6, y0 + 96 + RE_PITCH * 6 + 76),
         "材料は同じです。並べ替えただけで、相手が読む理由が変わります。",
         36, SUB, app(t, 10.60, 0.6))


STRUCTURE = [
    ("1", "表紙", ""),
    ("2", "相手がいま置かれている状況", "ここを外すと最後まで読まれません"),
    ("3", "そのままにすると何が起きるか", ""),
    ("4", "こちらの提案", ""),
    ("5-7", "その根拠", "実績・数字・事例"),
    ("8", "進め方と期間", ""),
    ("9", "費用", ""),
    ("10", "次にしていただきたいこと", "問い合わせ／面談／承認"),
]


def s_structure(d, t, dur):
    head(d, "本文を作る前に、構成案をお出しします",
         "何を、どの順番で、何枚で伝えるか。ここで方向を確認してから作ります",
         app(t, 0.0, 0.5))
    x, w = 150, VW - 300
    y = 272
    for i, (no, name, note) in enumerate(STRUCTURE):
        a = app(t, 0.45 + i * 0.30, 0.45)
        if a <= 0:
            break
        dy = int(16 * (1 - a))
        card(d, x, y + dy, w, 78, a)
        d.rounded_rectangle([x + 30, y + 17 + dy, x + 116, y + 61 + dy],
                            radius=10, fill=A(ACCENT_BG, a))
        ctext(d, x + 73, y + 23 + dy, no, 28, ACCENT, a)
        text(d, (x + 146, y + 21 + dy), name, 36, INK, a)
        if note:
            rtext(d, x + w - 34, y + 29 + dy, note, 26, SUB, a)
        y += 88
    text(d, (152, 272 + 88 * 8 + 18),
         "順番はご依頼内容によって変わります。作り始めてから大きく直す、を減らせます。",
         36, SUB, app(t, 3.40, 0.6))


FLOW = [
    ("お送りいただくもの",
     ["・うちは施工管理アプリを売っている",
      "・現場監督の残業を減らせる",
      "・導入は3社",
      "・1社は残業が月20時間減った",
      "・料金は月3万円から"],
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


def s_flow(d, t, dur):
    head(d, "メモ書きからでも作れます",
         "整った原稿は要りません。何を伝えたいかさえあれば組み立てます",
         app(t, 0.0, 0.5))
    cw, gap = 540, 60
    x0 = (VW - cw * 3 - gap * 2) // 2
    y0 = 300
    for i, (title, items, note) in enumerate(FLOW):
        a = app(t, 0.5 + i * 1.15, 0.55)
        if a <= 0:
            break
        x = x0 + i * (cw + gap)
        dy = int(20 * (1 - a))
        card(d, x, y0 + dy, cw, 500, a)
        d.rounded_rectangle([x + 28, y0 + 26 + dy, x + 82, y0 + 74 + dy],
                            radius=10, fill=A(ACCENT_BG, a))
        ctext(d, x + 55, y0 + 32 + dy, str(i + 1), 30, ACCENT, a)
        text(d, (x + 100, y0 + 32 + dy), title, 30, INK, a)
        ty = y0 + 108 + dy
        for it in items:
            text(d, (x + 40, ty), it, 27, BODY, a)
            ty += 42
        # 補足は3枚とも同じ高さに置く。項目数がいちばん多い列に合わせる。
        text(d, (x + 40, y0 + 456 + dy), note, 25, SUB, a)
        if i < 2:
            aa = app(t, 1.15 + i * 1.15, 0.4)
            cx, cy = x + cw + gap / 2, y0 + 250
            d.polygon([(cx - 16, cy - 20), (cx + 16, cy), (cx - 16, cy + 20)],
                      fill=A(ACCENT, aa))
    text(d, (152, 866), "原稿がまとまっていない段階のご相談で構いません。",
         36, SUB, app(t, 4.20, 0.6))


def s_close(d, t, dur):
    dy = int(20 * (1 - app(t, 0.0, 0.9)))
    text(d, (150, 372 - dy), "構成から、お引き受けします", 76, INK, app(t, 0.05, 0.7))
    a2 = app(t, 0.75, 0.7)
    d.rounded_rectangle([152, 500, 242, 508], radius=4, fill=A(ACCENT, a2))
    text(d, (152, 548), "箇条書きのメモ、既存の資料、打ち合わせの書き起こし。",
         38, SUB, a2)
    text(d, (152, 608), "どの形からでも組み立てます。", 38, SUB, app(t, 1.05, 0.7))
    a3 = app(t, 1.70, 0.7)
    card(d, 150, 700, 980, 128, a3)
    text(d, (206, 742), "まずはメッセージでご相談ください", 44, INK, a3)


SCENES = [
    (4.5, s_title),
    (5.0, s_problem),
    (4.5, s_claim),
    (15.0, s_reorder),
    (13.0, s_structure),
    (10.0, s_flow),
    (6.0, s_close),
]


def frame(tg):
    """全体時刻 tg 秒の1枚を返す。"""
    img = Image.new("RGB", (VW, VH), BG)
    acc = 0.0
    for dur, fn in SCENES:
        if acc <= tg < acc + dur:
            layer = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer, "RGBA")
            fn(d, tg - acc, dur)
            a = fade(tg - acc, dur)
            if a < 1.0:
                layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
            img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
            break
        acc += dur
    return img


if __name__ == "__main__":
    total = sum(d for d, _ in SCENES)
    frames = os.path.join(WORK, "frames")
    shutil.rmtree(frames, ignore_errors=True)
    os.makedirs(frames, exist_ok=True)

    n = int(total * FPS)
    for i in range(n):
        frame(i / FPS).save(os.path.join(frames, f"f{i:05d}.png"))
        if i % 120 == 0:
            print(f"{i}/{n}")

    out = os.path.join(WORK, "deck-movie.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        check=True)
    shutil.rmtree(frames, ignore_errors=True)
    print(out, f"{total:.1f}s", os.path.getsize(out) // 1024, "KB")
