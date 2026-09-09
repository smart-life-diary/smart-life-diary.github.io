"""工事別原価管理表のサンプル（.xlsx）と、ココナラ出品用の画像を生成する。

出力
  samples/工事別原価管理表_サンプル.xlsx
  portfolio/koji-1.png  日報入力シート（入力欄と自動計算欄の色分け）
  portfolio/koji-2.png  工事別集計シート（粗利が出ている画面）
  portfolio/koji-3.png  シート構成の一覧

画像はココナラの表示比率 1.20:1 に合わせて 1560×1300 で書き出す。
LibreOffice はこの環境で動かないため、xlsx を画像化するのではなく
同じデータから PIL で描画している。

日報入力の画像（koji-1）は xlsx の中身とそのまま一致する。
工事別集計の画像（koji-2）の発生原価は、日報が数百行たまった運用時の
イメージであり、サンプル8行を集計した値ではない。KOJI の第5要素が
その表示用の値で、xlsx 側は SUMIFS で実際の合計を出している。
"""
import os
from PIL import Image, ImageDraw, ImageFont
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_X = os.path.join(SITE, "samples")
OUT_P = os.path.join(SITE, "portfolio")
JP = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# ── 見た目 ───────────────────────────────────────────────
BG      = (14, 20, 36)        # 台紙
CARD    = (255, 255, 255)
GRID    = (214, 220, 228)
HEAD_BG = (31, 59, 87)        # 見出し行
HEAD_FG = (255, 255, 255)
IN_BG   = (255, 243, 204)     # 入力欄（黄）
CALC_BG = (238, 242, 246)     # 自動計算欄（グレー）
INK     = (26, 32, 44)
SUB     = (110, 122, 138)
ACCENT  = (0, 122, 204)
GOOD    = (22, 138, 92)

W, H = 1560, 1300             # 1.20:1


def font(sz, mono=False):
    return ImageFont.truetype(MONO if mono else JP, sz)


# ── サンプルデータ（xlsx と画像で共有する）─────────────────
KOJI = [
    ("K-101", "市道1号線 舗装補修工事",  4800000, 3900000, 2145000),
    ("K-102", "○○川 護岸ブロック工事", 12600000, 10250000, 7810000),
    ("K-103", "××排水路 改修工事",      3200000, 2640000,  510000),
    ("K-104", "県道2号線 側溝設置工事",   2450000, 1980000, 1924000),
]

NIPPO = [
    # 日付, 工事番号, 工種, 作業員, 人工, 単価, 材料費, 外注費
    ("04/01", "K-101", "舗装",   "佐藤", 1.0, 21000, 48000,      0),
    ("04/01", "K-101", "舗装",   "鈴木", 1.0, 19000,     0,      0),
    ("04/02", "K-102", "土工",   "佐藤", 1.0, 21000,     0, 180000),
    ("04/02", "K-102", "土工",   "高橋", 0.5, 18000, 22000,      0),
    ("04/03", "K-103", "仮設",   "鈴木", 1.0, 19000, 15000,      0),
    ("04/03", "K-101", "舗装",   "高橋", 1.0, 18000, 96000,      0),
    ("04/04", "K-102", "コンクリート", "佐藤", 1.0, 21000, 134000, 0),
    ("04/04", "K-102", "コンクリート", "鈴木", 1.0, 19000,      0, 240000),
]

SHEETS = [
    ("はじめに",   "入力のルールと、触ってはいけない欄の説明"),
    ("マスタ",     "工事・工種・作業員を登録。入力欄のプルダウンになります"),
    ("日報入力",   "1日1行。色の付いた欄だけ入力します"),
    ("工事別集計", "工事ごとの発生原価・予算消化率・粗利を自動計算"),
    ("出面集計",   "作業員別・月別の人工数を自動集計"),
]


def rome(v):
    return f"{v:,}"


# ── xlsx ────────────────────────────────────────────────
THIN = Side(style="thin", color="D6DCE4")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def head(ws, row, cols):
    for i, (name, width) in enumerate(cols, start=1):
        c = ws.cell(row=row, column=i, value=name)
        c.fill = PatternFill("solid", fgColor="1F3B57")
        c.font = Font(name="Meiryo", size=10, bold=True, color="FFFFFF")
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[row].height = 26


def build_xlsx():
    os.makedirs(OUT_X, exist_ok=True)
    wb = Workbook()

    # はじめに
    ws = wb.active
    ws.title = "はじめに"
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 88
    ws["B2"] = "工事別原価管理表"
    ws["B2"].font = Font(name="Meiryo", size=18, bold=True, color="1F3B57")
    lines = [
        "",
        "■ 入力するのは、黄色の欄だけです",
        "　 グレーの欄は数式が入っています。上書きすると集計が止まります。",
        "",
        "■ 使う順番",
        "　 1. 「マスタ」に工事・工種・作業員を登録します",
        "　 2. 「日報入力」に1日1行、その日の作業を入力します",
        "　 3. 「工事別集計」「出面集計」は自動で更新されます",
        "",
        "■ 行を増やすとき",
        "　 200行目まで数式が入っています。足りなくなったら、",
        "　 最終行をコピーして下に貼り付けてください。",
        "",
        "■ このファイルについて",
        "　 サンプルです。工事名・金額・氏名はすべて架空のものです。",
    ]
    for i, t in enumerate(lines, start=3):
        ws.cell(row=i, column=2, value=t).font = Font(name="Meiryo", size=11)

    # マスタ
    ws = wb.create_sheet("マスタ")
    ws["A1"] = "マスタ"
    ws["A1"].font = Font(name="Meiryo", size=14, bold=True, color="1F3B57")
    ws["A2"] = "ここに登録した内容が、日報入力のプルダウンに出ます。"
    ws["A2"].font = Font(name="Meiryo", size=10, color="6E7A8A")
    head(ws, 4, [("工事番号", 12), ("工事名", 34), ("請負金額", 14), ("実行予算", 14)])
    for r, (no, name, uke, yosan, _) in enumerate(KOJI, start=5):
        for col, v in enumerate([no, name, uke, yosan], start=1):
            c = ws.cell(row=r, column=col, value=v)
            c.font = Font(name="Meiryo", size=10)
            c.fill = PatternFill("solid", fgColor="FFF3CC")
            c.border = BORDER
            if col >= 3:
                c.number_format = "#,##0"

    head(ws, 11, [("工種", 12), ("作業員", 14), ("労務単価", 14)])
    kousyu = ["土工", "舗装", "コンクリート", "仮設", "運搬"]
    sagyou = [("佐藤", 21000), ("鈴木", 19000), ("高橋", 18000), ("田中", 20000)]
    for i, k in enumerate(kousyu, start=12):
        c = ws.cell(row=i, column=1, value=k)
        c.font = Font(name="Meiryo", size=10); c.fill = PatternFill("solid", fgColor="FFF3CC"); c.border = BORDER
    for i, (n, t) in enumerate(sagyou, start=12):
        for col, v in enumerate([n, t], start=2):
            c = ws.cell(row=i, column=col, value=v)
            c.font = Font(name="Meiryo", size=10); c.fill = PatternFill("solid", fgColor="FFF3CC"); c.border = BORDER
            if col == 3:
                c.number_format = "#,##0"

    # 日報入力
    ws = wb.create_sheet("日報入力")
    ws["A1"] = "日報入力"
    ws["A1"].font = Font(name="Meiryo", size=14, bold=True, color="1F3B57")
    ws["A2"] = "黄色の欄だけ入力してください。労務費と原価計は自動で出ます。"
    ws["A2"].font = Font(name="Meiryo", size=10, color="6E7A8A")
    cols = [("日付", 11), ("工事番号", 11), ("工種", 14), ("作業員", 11),
            ("人工", 8), ("労務単価", 12), ("労務費", 13),
            ("材料費", 12), ("外注費", 12), ("原価計", 14)]
    head(ws, 4, cols)
    R0, RN = 5, 204
    for r in range(R0, RN + 1):
        i = r - R0
        src = NIPPO[i] if i < len(NIPPO) else None
        vals = list(src) if src else [None] * 8
        d, no, ks, sg, nin, tan, zai, gai = vals
        ws.cell(row=r, column=1, value=d)
        ws.cell(row=r, column=2, value=no)
        ws.cell(row=r, column=3, value=ks)
        ws.cell(row=r, column=4, value=sg)
        ws.cell(row=r, column=5, value=nin)
        # 労務単価はマスタから引く
        ws.cell(row=r, column=6,
                value=f'=IF($D{r}="","",IFERROR(VLOOKUP($D{r},マスタ!$B$12:$C$15,2,FALSE),""))')
        ws.cell(row=r, column=7, value=f'=IF($E{r}="","",$E{r}*$F{r})')
        ws.cell(row=r, column=8, value=zai)
        ws.cell(row=r, column=9, value=gai)
        ws.cell(row=r, column=10,
                value=f'=IF($A{r}="","",SUM($G{r},$H{r},$I{r}))')
        for col in range(1, 11):
            c = ws.cell(row=r, column=col)
            c.font = Font(name="Meiryo", size=10)
            c.border = BORDER
            auto = col in (6, 7, 10)
            c.fill = PatternFill("solid", fgColor="EEF2F6" if auto else "FFF3CC")
            if col in (6, 7, 8, 9, 10):
                c.number_format = "#,##0"
            if col == 5:
                c.number_format = "0.0"
    ws.freeze_panes = "A5"
    for dv, col in [
        (DataValidation(type="list", formula1="マスタ!$A$5:$A$8", allow_blank=True), "B"),
        (DataValidation(type="list", formula1="マスタ!$A$12:$A$16", allow_blank=True), "C"),
        (DataValidation(type="list", formula1="マスタ!$B$12:$B$15", allow_blank=True), "D"),
    ]:
        ws.add_data_validation(dv)
        dv.add(f"{col}{R0}:{col}{RN}")

    # 工事別集計
    ws = wb.create_sheet("工事別集計")
    ws["A1"] = "工事別集計"
    ws["A1"].font = Font(name="Meiryo", size=14, bold=True, color="1F3B57")
    ws["A2"] = "この画面はすべて自動計算です。入力する欄はありません。"
    ws["A2"].font = Font(name="Meiryo", size=10, color="6E7A8A")
    head(ws, 4, [("工事番号", 11), ("工事名", 30), ("請負金額", 14), ("実行予算", 14),
                 ("発生原価", 14), ("予算消化率", 12), ("粗利見込", 14), ("粗利率", 10)])
    rng = "'日報入力'!$J$5:$J$204"
    key = "'日報入力'!$B$5:$B$204"
    for i, (no, name, uke, yosan, _) in enumerate(KOJI):
        r = 5 + i
        m = 5 + i          # マスタの行
        ws.cell(row=r, column=1, value=f"=マスタ!A{m}")
        ws.cell(row=r, column=2, value=f"=マスタ!B{m}")
        ws.cell(row=r, column=3, value=f"=マスタ!C{m}")
        ws.cell(row=r, column=4, value=f"=マスタ!D{m}")
        ws.cell(row=r, column=5, value=f'=SUMIFS({rng},{key},$A{r})')
        ws.cell(row=r, column=6, value=f'=IFERROR($E{r}/$D{r},0)')
        ws.cell(row=r, column=7, value=f'=$C{r}-$D{r}')
        ws.cell(row=r, column=8, value=f'=IFERROR($G{r}/$C{r},0)')
        for col in range(1, 9):
            c = ws.cell(row=r, column=col)
            c.font = Font(name="Meiryo", size=10)
            c.fill = PatternFill("solid", fgColor="EEF2F6")
            c.border = BORDER
            if col in (3, 4, 5, 7):
                c.number_format = "#,##0"
            if col in (6, 8):
                c.number_format = "0.0%"

    # 出面集計
    ws = wb.create_sheet("出面集計")
    ws["A1"] = "出面集計"
    ws["A1"].font = Font(name="Meiryo", size=14, bold=True, color="1F3B57")
    ws["A2"] = "作業員別の人工数です。日報入力から自動で集まります。"
    ws["A2"].font = Font(name="Meiryo", size=10, color="6E7A8A")
    head(ws, 4, [("作業員", 14), ("人工数 計", 14), ("労務費 計", 16)])
    for i, (n, _t) in enumerate(sagyou):
        r = 5 + i
        ws.cell(row=r, column=1, value=f"=マスタ!B{12+i}")
        ws.cell(row=r, column=2,
                value=f"=SUMIFS('日報入力'!$E$5:$E$204,'日報入力'!$D$5:$D$204,$A{r})")
        ws.cell(row=r, column=3,
                value=f"=SUMIFS('日報入力'!$G$5:$G$204,'日報入力'!$D$5:$D$204,$A{r})")
        for col in range(1, 4):
            c = ws.cell(row=r, column=col)
            c.font = Font(name="Meiryo", size=10)
            c.fill = PatternFill("solid", fgColor="EEF2F6")
            c.border = BORDER
            c.number_format = "0.0" if col == 2 else ("#,##0" if col == 3 else "General")

    # 生成直後の .xlsx には計算結果が入らない。開いた時点で必ず再計算させる。
    wb.calculation.fullCalcOnLoad = True
    path = os.path.join(OUT_X, "工事別原価管理表_サンプル.xlsx")
    wb.save(path)
    return path


# ── 画像 ────────────────────────────────────────────────
def board(title, sub):
    """台紙とタイトル帯を描いて (img, draw, y) を返す。"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((66, 66), title, font=font(64), fill=(255, 255, 255))
    d.text((66, 158), sub, font=font(32), fill=(150, 172, 200))
    return img, d, 240


def table(d, x, y, cols, rows, fills, rowh=80, headh=76):
    """cols=[(見出し,幅,寄せ)] rows=[[値]] fills=[列ごとの背景色]"""
    tw = sum(c[1] for c in cols)
    d.rectangle([x, y, x + tw, y + headh], fill=HEAD_BG)
    cx = x
    for name, w_, al in cols:
        tx = cx + w_ / 2 - d.textlength(name, font=font(27)) / 2
        d.text((tx, y + headh / 2 - 18), name, font=font(27), fill=HEAD_FG)
        cx += w_
    yy = y + headh
    for row in rows:
        cx = x
        for i, ((name, w_, al), v) in enumerate(zip(cols, row)):
            d.rectangle([cx, yy, cx + w_, yy + rowh], fill=fills[i], outline=GRID)
            f = font(27, mono=al == "r")
            tl = d.textlength(str(v), font=f)
            tx = cx + w_ - 18 - tl if al == "r" else (
                cx + w_ / 2 - tl / 2 if al == "c" else cx + 18)
            d.text((tx, yy + rowh / 2 - 18), str(v), font=f, fill=INK)
            cx += w_
        yy += rowh
    return yy


def legend(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=IN_BG, outline=GRID)
    d.text((x + 54, y + 2), "入力する欄", font=font(29), fill=(255, 255, 255))
    x2 = x + 300
    d.rectangle([x2, y, x2 + 38, y + 38], fill=CALC_BG, outline=GRID)
    d.text((x2 + 54, y + 2), "自動で出る欄（触らない）", font=font(29), fill=(255, 255, 255))


def img1():
    img, d, y = board("入力するのは、色の付いた欄だけ",
                      "1日1行。人工を入れれば労務費と原価計は自動で出ます")
    cols = [("日付", 108, "c"), ("工事番号", 146, "c"), ("工種", 196, "l"),
            ("作業員", 124, "c"), ("人工", 96, "r"), ("労務単価", 148, "r"),
            ("労務費", 148, "r"), ("材料費", 142, "r"), ("外注費", 142, "r"),
            ("原価計", 170, "r")]
    fills = [IN_BG, IN_BG, IN_BG, IN_BG, IN_BG, CALC_BG, CALC_BG,
             IN_BG, IN_BG, CALC_BG]
    rows = []
    for (dt, no, ks, sg, nin, tan, zai, gai) in NIPPO:
        roumu = int(nin * tan)
        rows.append([dt, no, ks, sg, f"{nin:.1f}", rome(tan), rome(roumu),
                     rome(zai), rome(gai), rome(roumu + zai + gai)])
    x = (W - sum(c[1] for c in cols)) // 2
    yy = table(d, x, y, cols, rows, fills)
    legend(d, x, yy + 54)
    d.text((x, yy + 136),
           "工事番号・工種・作業員はプルダウン。手入力の打ち間違いが起きません。",
           font=font(30), fill=(196, 210, 228))
    return img


def img2():
    img, d, y = board("工事ごとの粗利が、その場で出る",
                      "日報を入れた時点で集計は終わっています。月末の集計作業はありません")
    cols = [("工事番号", 150, "c"), ("工事名", 380, "l"), ("請負金額", 184, "r"),
            ("実行予算", 184, "r"), ("発生原価", 184, "r"),
            ("予算消化率", 162, "r"), ("粗利率", 136, "r")]
    fills = [CALC_BG] * 7
    rows = []
    for no, name, uke, yosan, genka in KOJI:
        rows.append([no, name, rome(uke), rome(yosan), rome(genka),
                     f"{genka / yosan * 100:.1f}%",
                     f"{(uke - yosan) / uke * 100:.1f}%"])
    x = (W - sum(c[1] for c in cols)) // 2
    yy = table(d, x, y, cols, rows, fills, rowh=84)

    d.text((x, yy + 74), "予算の消化ぐあい", font=font(34), fill=(255, 255, 255))
    by = yy + 142
    for no, name, uke, yosan, genka in KOJI:
        ratio = genka / yosan
        d.text((x, by + 4), no, font=font(29), fill=(196, 210, 228))
        bx, bw = x + 150, 880
        d.rectangle([bx, by, bx + bw, by + 42], fill=(38, 50, 72))
        col = GOOD if ratio < 0.85 else (206, 84, 74)
        d.rectangle([bx, by, bx + int(bw * min(ratio, 1.0)), by + 42], fill=col)
        d.text((bx + bw + 26, by + 4), f"{ratio*100:.1f}%", font=font(29),
               fill=(255, 255, 255))
        by += 72
    d.text((x, by + 26), "実行予算を使い切りそうな工事が、月の途中で分かります。",
           font=font(30), fill=(196, 210, 228))
    return img


def img3():
    img, d, y = board("シート構成は5つだけ",
                      "増やしすぎると使われなくなります。必要なものに絞っています")
    x, w_ = 130, W - 260
    for i, (name, desc) in enumerate(SHEETS):
        yy = y + i * 182
        d.rectangle([x, yy, x + w_, yy + 150], fill=(24, 33, 54))
        d.rectangle([x, yy, x + 12, yy + 150], fill=ACCENT)
        d.text((x + 48, yy + 28), name, font=font(42), fill=(255, 255, 255))
        d.text((x + 48, yy + 88), desc, font=font(28), fill=(150, 172, 200))
    d.text((x, y + len(SHEETS) * 182 + 34),
           "Excel（.xlsx）とGoogleスプレッドシート、どちらでも同じように動きます。",
           font=font(30), fill=(196, 210, 228))
    return img


def thumb():
    """コンテンツ出品のサムネイル。正方形で、要素を中央に寄せて作る。

    検索結果の枠は縦横比が読めず、上下左右どちらにも切られうる。
    そのため文字と図は中央 78% の範囲に収め、端まで伸ばさない。
    """
    S = 1200
    M = int(S * 0.11)                       # 端の余白。ここは切られてよい
    img = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(img)

    d.text((M, M + 44), "工事別", font=font(52), fill=(150, 172, 200))
    d.text((M, M + 102), "原価管理表", font=font(96), fill=(255, 255, 255))
    d.text((M, M + 222), "Excel ／ 5シート ／ マクロなし",
           font=font(38), fill=ACCENT)

    # 色分けが伝わる最小の表。数字は読めなくてよい
    cols = [("日付", 116, "c"), ("工事番号", 168, "c"), ("人工", 108, "r"),
            ("労務費", 174, "r"), ("材料費", 174, "r"), ("原価計", 194, "r")]
    fills = [IN_BG, IN_BG, IN_BG, CALC_BG, IN_BG, CALC_BG]
    # 外注費の列を省くため、外注のない行だけを見本に使う。
    # 混ぜると「材料費0なのに原価計が大きい」と、計算違いに見えてしまう。
    rows = []
    for (dt, no, ks, sg, nin, tan, zai, gai) in [r for r in NIPPO if r[7] == 0][:5]:
        roumu = int(nin * tan)
        rows.append([dt, no, f"{nin:.1f}", rome(roumu), rome(zai),
                     rome(roumu + zai)])
    x = (S - sum(c[1] for c in cols)) // 2
    yy = table(d, x, M + 298, cols, rows, fills, rowh=72, headh=68)

    d.rectangle([x, yy + 46, x + 30, yy + 76], fill=IN_BG)
    d.text((x + 44, yy + 44), "入力", font=font(30), fill=(255, 255, 255))
    d.rectangle([x + 190, yy + 46, x + 220, yy + 76], fill=CALC_BG)
    d.text((x + 234, yy + 44), "自動計算", font=font(30), fill=(255, 255, 255))

    d.text((M, yy + 122), "日報を入れるだけで、工事ごとの粗利が出ます。",
           font=font(40), fill=(214, 226, 242))
    return img


if __name__ == "__main__":
    os.makedirs(OUT_P, exist_ok=True)
    p = build_xlsx()
    print(p, os.path.getsize(p) // 1024, "KB")
    im = thumb()
    dst = os.path.join(OUT_P, "koji-thumb.png")
    im.save(dst)
    print(dst, im.size, os.path.getsize(dst) // 1024, "KB")
    for i, fn in enumerate([img1, img2, img3], start=1):
        im = fn()
        dst = os.path.join(OUT_P, f"koji-{i}.png")
        im.save(dst)
        print(dst, im.size, f"{im.size[0]/im.size[1]:.2f}:1",
              os.path.getsize(dst) // 1024, "KB")
