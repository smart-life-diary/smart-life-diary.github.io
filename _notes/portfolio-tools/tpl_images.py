"""出品D（テンプレート販売）用の画像を作る。

テンプレート3種を実際に操作して撮影し、ココナラの表示枠（約1.20:1）に
合わせた出品画像を書き出す。
"""
import os
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "..", "templates")
SHOTS = os.path.join(HERE, "tplshots")
OUT = os.path.join(HERE, "..", "..", "portfolio")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

BG, PANEL, LINE = (14, 20, 36), (22, 32, 58), (43, 57, 88)
GOLD, INK, MUT = (232, 196, 119), (238, 242, 251), (150, 163, 192)
RATIO = 1.20

TYPES = [
    ("type-a-4types",  "タイプ判定型",      "回答の傾向から4タイプ前後を判定",
     ["もっとも汎用的な型", "集客用の診断に向く", "サブタイプも同時に表示"]),
    ("type-b-score",   "スコア％表示型",    "回答を点数化し0〜100%で表示",
     ["セルフチェックに向く", "数字がカウントアップする演出", "判定の段階は自由に増減"]),
    ("type-c-multi",   "多分岐型",          "複数の評価軸から1タイプを選出",
     ["レーダーチャート付き", "6〜12タイプまで対応", "SNS拡散を狙う診断に向く"]),
]

CONTENT_BOX = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width>4 && r.height>4 && s.display!=='none' && s.visibility!=='hidden'
           && +s.opacity>0.05 && r.bottom>0 && r.top < innerHeight; };
  let top=1e9,left=1e9,right=0,bottom=0,found=false;
  document.querySelectorAll('body *').forEach(e => {
    if (!vis(e)) return;
    const r = e.getBoundingClientRect();
    if (r.height > innerHeight * 2) return;
    found = true;
    top=Math.min(top,r.top); left=Math.min(left,r.left);
    right=Math.max(right,r.right); bottom=Math.max(bottom,r.bottom);
  });
  if (!found) return null;
  const p = 14;
  return { x:Math.max(0,left-p), y:Math.max(0,top-p),
           width:Math.min(innerWidth,right+p)-Math.max(0,left-p),
           height:Math.min(innerHeight,bottom+p)-Math.max(0,top-p) };
}"""


def capture():
    os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for slug, *_ in TYPES:
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
            pg.goto("file://" + os.path.abspath(os.path.join(TPL, slug + ".html")))
            pg.wait_for_timeout(400)

            def shot(name):
                box = pg.evaluate(CONTENT_BOX)
                path = f"{SHOTS}/{slug}-{name}.png"
                if box and box["width"] > 100 and box["height"] > 100:
                    pg.screenshot(path=path, clip=box)
                else:
                    pg.screenshot(path=path)

            shot("1")
            pg.click("#startBtn"); pg.wait_for_timeout(350)
            shot("2")
            for i in range(40):
                if pg.is_visible("#result"):
                    break
                opts = pg.query_selector_all(".opt")
                if not opts:
                    break
                opts[i % len(opts)].click(); pg.wait_for_timeout(150)
            pg.wait_for_timeout(800)
            pg.evaluate("() => window.scrollTo(0,0)"); pg.wait_for_timeout(250)
            shot("3")
            pg.close()
        b.close()


def font(sz, mono=False):
    return ImageFont.truetype(MONO if mono else FONT, sz)


def bold(d, xy, text, f, fill, anchor="la"):
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        d.text((xy[0] + dx, xy[1] + dy), text, font=f, fill=fill, anchor=anchor)


def trim_tail(im, keep=26, tol=6):
    px = im.load(); base = px[4, im.height - 4]; y = im.height - 1
    while y > im.height // 3:
        if all(abs(px[x, y][c] - base[c]) <= tol for x in range(0, im.width, 7) for c in range(3)):
            y -= 1
        else:
            break
    return im.crop((0, 0, im.width, min(im.height, y + keep)))


def canvas43(w):
    h = round(w / RATIO)
    im = Image.new("RGB", (w, h), BG)
    return im, ImageDraw.Draw(im), h


def header(d, w, title, sub, right1="1ファイルで完結", right2="編集は1か所だけ", margin=150):
    bold(d, (margin, 62), title, font(46), INK)
    d.text((margin, 122), sub, font=font(26), fill=MUT)
    d.text((w - margin, 70), right1, font=font(24), fill=GOLD, anchor="ra")
    d.text((w - margin, 110), right2, font=font(24), fill=MUT, anchor="ra")
    d.line([(margin, 166), (w - margin, 166)], fill=LINE, width=2)


def pill_row(d, cx, y, items, size=29):
    f = font(size)
    widths = [d.textlength(t, font=f) + 52 for t in items]
    total = sum(widths) + 22 * (len(items) - 1)
    x = cx - total / 2
    for t, wd in zip(items, widths):
        d.rounded_rectangle((x, y, x + wd, y + 60), radius=30, outline=(60, 78, 116), width=2)
        d.text((x + wd / 2, y + 14), t, font=f, fill=MUT, anchor="ma")
        x += wd + 22


def build_cover():
    W = 2100
    im, d, H = canvas43(W)
    header(d, W, "診断ツール テンプレート 3種", "設問を差し替えるだけ。HTML1ファイルで完結します")

    cut_w, gap = 430, 70
    shots = [trim_tail(Image.open(f"{SHOTS}/{s}-3.png").convert("RGB")) for s, *_ in TYPES]
    shots = [s.resize((cut_w, round(s.height * cut_w / s.width)), Image.LANCZOS) for s in shots]
    body = max(s.height for s in shots) + 44
    total_w = cut_w * 3 + gap * 2
    x0 = (W - total_w) // 2
    top = 300
    for i, (s, (_, name, use, _)) in enumerate(zip(shots, TYPES)):
        x = x0 + i * (cut_w + gap)
        d.text((x + cut_w // 2, top - 92), name, font=font(31), fill=GOLD, anchor="ma")
        d.text((x + cut_w // 2, top - 48), use, font=font(23), fill=MUT, anchor="ma")
        d.rounded_rectangle((x - 10, top, x + cut_w + 10, top + body), radius=20,
                            fill=PANEL, outline=LINE, width=2)
        im.paste(s, (x, top + (body - s.height) // 2))

    pill_row(d, W // 2, H - 250, ["スマートフォン最適化", "X／LINEシェア機能", "使い方ガイド付き"])
    d.text((W // 2, H - 150), "サーバーに置くだけで動きます。データベースも追加ファイルも不要です。",
           font=font(27), fill=MUT, anchor="ma")
    p = os.path.join(OUT, "tpl-cover.png")
    im.save(p, optimize=True)
    return p


def build_type(slug, name, use, points, idx):
    W = 2100
    im, d, H = canvas43(W)
    header(d, W, name, use)

    labels = ["① スタート", "② 設問に答える", "③ 結果が出る"]
    cut_w, gap = 470, 80
    shots = [trim_tail(Image.open(f"{SHOTS}/{slug}-{n}.png").convert("RGB")) for n in (1, 2, 3)]
    shots = [s.resize((cut_w, round(s.height * cut_w / s.width)), Image.LANCZOS) for s in shots]
    body = max(s.height for s in shots) + 44
    total_w = cut_w * 3 + gap * 2
    x0 = (W - total_w) // 2
    band = 150
    band_y = H - 150 - band
    top = 210 + (band_y - 210 - 66 - body) // 2

    for i, (s, lb) in enumerate(zip(shots, labels)):
        x = x0 + i * (cut_w + gap)
        d.text((x + cut_w // 2, top + 14), lb, font=font(29), fill=GOLD, anchor="ma")
        pt = top + 66
        d.rounded_rectangle((x - 10, pt, x + cut_w + 10, pt + body), radius=20,
                            fill=PANEL, outline=LINE, width=2)
        im.paste(s, (x, pt + (body - s.height) // 2))
        if i < 2:
            ax, ay = x + cut_w + gap // 2, pt + body // 2
            d.polygon([(ax - 13, ay - 19), (ax + 15, ay), (ax - 13, ay + 19)], fill=GOLD)

    d.line([(150, band_y), (W - 150, band_y)], fill=LINE, width=2)
    col = (W - 300) // 3
    for i, t in enumerate(points):
        bx, by = 150 + i * col, band_y + 58
        d.ellipse((bx, by + 12, bx + 15, by + 27), fill=GOLD)
        d.text((bx + 32, by), t, font=font(29), fill=INK)

    p = os.path.join(OUT, f"tpl-{idx}.png")
    im.save(p, optimize=True)
    return p


CODE = [
    ("/* ▼ ここから編集してください ▼ */", GOLD),
    ("", INK),
    ("const CONFIG = {", INK),
    ('  title: \'あなたに向いてる<span class="hi">タイプ</span>\',', INK),
    ('  lead:  "ここに導入文を書きます。",', INK),
    ('  hashtag: "#サンプル診断",', INK),
    ("};", INK),
    ("", INK),
    ("const TYPES = {", INK),
    ('  write: { name:"発信タイプ", color:"#5ec6c0",', INK),
    ('           desc:"ここに人物像を書きます。" },', INK),
    ('  plan:  { name:"設計タイプ", color:"#7c8cf0",', INK),
    ('           desc:"ここに人物像を書きます。" },', INK),
    ("};", INK),
    ("", INK),
    ("const QUESTIONS = [", INK),
    ('  { q:"自分の考えを伝えるとき、ラクなのは？",', INK),
    ("    a:[", INK),
    ('      ["文章にまとめる",     { write:2 }],', INK),
    ('      ["図や手順に整理する", { plan:2  }],', INK),
    ("    ]},", INK),
    ("];", INK),
    ("", INK),
    ("/* ▲ 編集はここまでです ▲ */", GOLD),
]


def build_edit():
    W = 2100
    im, d, H = canvas43(W)
    header(d, W, "編集するのは、この1か所だけ", "設問・結果・配色すべてがこのブロックに入っています")

    bx, bw = 150, 1150
    bh = 34 * 2 + 40 * len(CODE)
    by = 240 + (H - 150 - 240 - bh) // 2
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=18, fill=(9, 13, 24), outline=LINE, width=2)
    f = font(26, mono=True)
    fj = font(25)
    y = by + 34
    for text, col in CODE:
        # 日本語を含む行は日本語フォントで描く
        use = fj if any(ord(c) > 0x2E80 for c in text) else f
        d.text((bx + 34, y), text, font=use, fill=col)
        y += 40

    tx = bx + bw + 90
    notes = [
        ("2行のコメントで挟んであります",
         "この外側は動作させている部分です。触る必要はありません。"),
        ("サンプル文が全項目に入っています",
         "「ここに〜を書きます」を自分の言葉に置き換えるだけで完成します。"),
        ("記号は消さないでください",
         "書き換えるのは引用符で囲まれた日本語だけです。"),
        ("配色は :root{} の1か所",
         "色コードを変えると全体に反映されます。"),
    ]
    ny = by + 20
    for t, s in notes:
        d.ellipse((tx, ny + 13, tx + 16, ny + 29), fill=GOLD)
        bold(d, (tx + 36, ny), t, font(32), INK)
        # 説明文は折り返して描く
        words, line = list(s), ""
        lines = []
        for ch in words:
            if d.textlength(line + ch, font=font(25)) > 590:
                lines.append(line); line = ch
            else:
                line += ch
        lines.append(line)
        for i, l in enumerate(lines):
            d.text((tx + 36, ny + 48 + i * 38), l, font=font(25), fill=MUT)
        ny += 62 + len(lines) * 38 + 34

    p = os.path.join(OUT, "tpl-edit.png")
    im.save(p, optimize=True)
    return p


if __name__ == "__main__":
    capture()
    os.makedirs(OUT, exist_ok=True)
    print(build_cover())
    for i, (slug, name, use, pts) in enumerate(TYPES, start=1):
        print(build_type(slug, name, use, pts, i))
    print(build_edit())
