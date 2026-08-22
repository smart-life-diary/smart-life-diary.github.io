"""美容サロン向け 日報・売上集計・現金管理シートのサンプルを作る。

日報に入力すると、集計と現金管理へ自動で反映される構成。
提案に添付する見本なので、そのまま使える完成度で作る。
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "samples")
os.makedirs(OUT, exist_ok=True)
PATH = os.path.join(OUT, "サロン日次管理シート_サンプル.xlsx")

F = "Meiryo"
HEAD_BG = PatternFill("solid", fgColor="1F3864")
SUB_BG = PatternFill("solid", fgColor="D9E2F3")
INPUT_BG = PatternFill("solid", fgColor="FFF7D6")   # 入力する場所
CALC_BG = PatternFill("solid", fgColor="F2F2F2")    # 自動計算
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

YEN = '¥#,##0'
PCT = '0.0%'
DATE = 'yyyy/m/d'

ROW0, ROWN = 7, 206          # 日報の入力範囲（見本1行＋199行）
CASH0, CASHN = 7, 66         # 現金管理の入力範囲

wb = Workbook()


def head(ws, row, cols, widths=None):
    for i, c in enumerate(cols, start=1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = Font(name=F, size=10, bold=True, color="FFFFFF")
        cell.fill = HEAD_BG
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 28


def title(ws, text, sub=""):
    ws["A1"] = text
    ws["A1"].font = Font(name=F, size=14, bold=True, color="1F3864")
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(name=F, size=9, color="595959")


# ============================================================ はじめに
ws = wb.active
ws.title = "はじめに"
ws.sheet_view.showGridLines = False
title(ws, "サロン日次管理シート", "入力するのは「日報」と「現金管理」の2枚だけです。集計は自動で更新されます。")
ws.column_dimensions["A"].width = 22
ws.column_dimensions["B"].width = 78

rows = [
    ("シートの構成", ""),
    ("① 日報", "毎日の来店・売上をここに入力します。単価と売上は自動で計算されます。"),
    ("② 集計", "入力不要。年と月を指定すると、その月の数字が自動で出ます。"),
    ("③ 現金管理", "現金の残高を管理します。現金売上は日報から自動で拾います。"),
    ("④ マスタ", "担当者名とメニュー・単価を登録します。日報の選択肢がここから作られます。"),
    ("", ""),
    ("色の意味", ""),
    ("薄い黄色", "入力する場所です。ここだけ触れば動きます。"),
    ("薄いグレー", "自動計算です。書き換えないでください。"),
    ("", ""),
    ("使いはじめる手順", ""),
    ("1", "「マスタ」に担当者名とメニュー・単価を登録します。"),
    ("2", "「日報」の見本の行（7行目）を見て、8行目から実データを入力します。"),
    ("3", "「集計」の年と月を指定します。数字が自動で出ます。"),
    ("", ""),
    ("用語の定義", ""),
    ("契約率", "新規のお客様のうち、成約に至った方の割合です。日報の「成約」列に○を入れた件数で計算します。"),
    ("リピート率", "その月の来店のうち、リピートのお客様が占める割合です。"),
    ("客単価", "売上合計 ÷ 来店数です。"),
    ("", ""),
    ("補足", "行が足りなくなった場合は、最終行をコピーして下に貼り付けてください。数式も一緒に増えます。"),
]
r = 4
for k, v in rows:
    a = ws.cell(row=r, column=1, value=k)
    b = ws.cell(row=r, column=2, value=v)
    a.font = Font(name=F, size=10, bold=(v == "" and k != ""))
    b.font = Font(name=F, size=10)
    b.alignment = Alignment(wrap_text=True, vertical="top")
    if v == "" and k != "":
        a.fill = SUB_BG
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    if k == "薄い黄色":
        a.fill = INPUT_BG
    if k == "薄いグレー":
        a.fill = CALC_BG
    ws.row_dimensions[r].height = 20
    r += 1

# ============================================================ マスタ
ws = wb.create_sheet("マスタ")
ws.sheet_view.showGridLines = False
title(ws, "マスタ", "ここに登録した内容が、日報のプルダウンに反映されます。")
head(ws, 4, ["担当者", "", "メニュー", "単価"], [16, 3, 30, 12])

staff = ["佐藤", "鈴木", "高橋", "田中"]
menu = [("カット", 5500), ("カラー", 8800), ("パーマ", 11000),
        ("トリートメント", 4400), ("ヘッドスパ", 6600), ("縮毛矯正", 16500)]

for i in range(20):
    c = ws.cell(row=5 + i, column=1, value=staff[i] if i < len(staff) else None)
    c.font = Font(name=F, size=10); c.fill = INPUT_BG; c.border = BOX
for i in range(20):
    m = ws.cell(row=5 + i, column=3, value=menu[i][0] if i < len(menu) else None)
    p = ws.cell(row=5 + i, column=4, value=menu[i][1] if i < len(menu) else None)
    for c in (m, p):
        c.font = Font(name=F, size=10); c.fill = INPUT_BG; c.border = BOX
    p.number_format = YEN

# ============================================================ 日報
ws = wb.create_sheet("日報")
ws.sheet_view.showGridLines = False
title(ws, "日報", "7行目は入力例です。8行目から実際のデータを入力してください。単価・売上は自動計算です。")
head(ws, 6,
     ["日付", "担当者", "区分", "メニュー", "単価", "数量", "売上",
      "支払方法", "成約", "備考"],
     [12, 12, 11, 20, 12, 8, 13, 13, 8, 26])

ws.freeze_panes = "A7"

for r in range(ROW0, ROWN + 1):
    for col in range(1, 11):
        c = ws.cell(row=r, column=col)
        c.font = Font(name=F, size=10)
        c.border = BOX
        c.alignment = Alignment(horizontal="center" if col in (1, 3, 6, 8, 9) else "left")
        c.fill = CALC_BG if col in (5, 7) else INPUT_BG
    ws.cell(row=r, column=1).number_format = DATE
    # 単価はメニューから引く
    ws.cell(row=r, column=5,
            value=f'=IFERROR(INDEX(マスタ!$D$5:$D$24,MATCH(D{r},マスタ!$C$5:$C$24,0)),"")')
    ws.cell(row=r, column=5).number_format = YEN
    # 売上 = 単価 × 数量
    ws.cell(row=r, column=7, value=f'=IF(OR(E{r}="",F{r}=""),"",E{r}*F{r})')
    ws.cell(row=r, column=7).number_format = YEN

# 入力例
ex = [("2026-08-18", "佐藤", "新規", "カラー", None, 1, None, "現金", "○", "SNSを見てご来店")]
from datetime import date
ws.cell(row=ROW0, column=1, value=date(2026, 8, 18)).number_format = DATE
for col, val in ((2, "佐藤"), (3, "新規"), (4, "カラー"), (6, 1),
                 (8, "現金"), (9, "○"), (10, "SNSを見てご来店")):
    ws.cell(row=ROW0, column=col, value=val)
for col in range(1, 11):
    ws.cell(row=ROW0, column=col).font = Font(name=F, size=10, italic=True, color="7F7F7F")

# プルダウン
dvs = [
    (DataValidation(type="list", formula1="マスタ!$A$5:$A$24", allow_blank=True), "B"),
    (DataValidation(type="list", formula1='"新規,リピート"', allow_blank=True), "C"),
    (DataValidation(type="list", formula1="マスタ!$C$5:$C$24", allow_blank=True), "D"),
    (DataValidation(type="list", formula1='"現金,カード,電子マネー,その他"', allow_blank=True), "H"),
    (DataValidation(type="list", formula1='"○"', allow_blank=True), "I"),
]
for dv, col in dvs:
    ws.add_data_validation(dv)
    dv.add(f"{col}{ROW0}:{col}{ROWN}")

# ============================================================ 集計
ws = wb.create_sheet("集計")
ws.sheet_view.showGridLines = False
title(ws, "集計", "入力するのは年と月だけです。ほかはすべて自動で計算されます。")
for col, w in ((1, 16), (2, 14), (3, 14), (4, 14), (5, 4), (6, 14), (7, 12), (8, 14), (9, 12)):
    ws.column_dimensions[get_column_letter(col)].width = w

ws["A4"] = "対象年"; ws["A5"] = "対象月"
for a in ("A4", "A5"):
    ws[a].font = Font(name=F, size=10, bold=True)
ws["C4"] = 2026; ws["C5"] = 8
for a in ("C4", "C5"):
    ws[a].font = Font(name=F, size=11, bold=True, color="0000FF")
    ws[a].fill = INPUT_BG; ws[a].border = BOX
    ws[a].alignment = Alignment(horizontal="center")

D0 = f"DATE($C$4,$C$5,1)"
D1 = f"DATE($C$4,$C$5+1,1)"
RNG_D = "'日報'!$A$7:$A$206"
RNG_KB = "'日報'!$C$7:$C$206"
RNG_UR = "'日報'!$G$7:$G$206"
RNG_ST = "'日報'!$B$7:$B$206"
RNG_SK = "'日報'!$I$7:$I$206"
IN_MONTH = f'{RNG_D},">="&{D0},{RNG_D},"<"&{D1}'

head(ws, 7, ["月間サマリー", "来店数", "新規", "リピート", "", "売上合計", "客単価", "契約率", "リピート率"])
vals = {
    "B8": f'=COUNTIFS({IN_MONTH})',
    "C8": f'=COUNTIFS({IN_MONTH},{RNG_KB},"新規")',
    "D8": f'=COUNTIFS({IN_MONTH},{RNG_KB},"リピート")',
    "F8": f'=SUMIFS({RNG_UR},{IN_MONTH})',
    "G8": '=IFERROR(F8/B8,0)',
    "H8": f'=IFERROR(COUNTIFS({IN_MONTH},{RNG_KB},"新規",{RNG_SK},"○")/C8,0)',
    "I8": '=IFERROR(D8/B8,0)',
}
ws["A8"] = "当月合計"
ws["A8"].font = Font(name=F, size=10, bold=True)
for k, v in vals.items():
    ws[k] = v
    ws[k].font = Font(name=F, size=11, bold=True)
    ws[k].fill = CALC_BG; ws[k].border = BOX
    ws[k].alignment = Alignment(horizontal="center")
for k in ("F8", "G8"):
    ws[k].number_format = YEN
for k in ("H8", "I8"):
    ws[k].number_format = PCT
ws["E8"].fill = CALC_BG; ws["E8"].border = BOX
ws.row_dimensions[8].height = 24

# 日別
head(ws, 11, ["日", "日付", "来店数", "売上"])
for i in range(31):
    r = 12 + i
    ws.cell(row=r, column=1, value=i + 1)
    ws.cell(row=r, column=2,
            value=f'=IF(MONTH(DATE($C$4,$C$5,A{r}))<>$C$5,"",DATE($C$4,$C$5,A{r}))')
    ws.cell(row=r, column=3,
            value=f'=IF($B{r}="","",COUNTIFS({RNG_D},$B{r}))')
    ws.cell(row=r, column=4,
            value=f'=IF($B{r}="","",SUMIFS({RNG_UR},{RNG_D},$B{r}))')
    for col in range(1, 5):
        c = ws.cell(row=r, column=col)
        c.font = Font(name=F, size=10); c.border = BOX; c.fill = CALC_BG
        c.alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=2).number_format = DATE
    ws.cell(row=r, column=4).number_format = YEN

# 担当者別
head(ws, 11, [""] * 5 + ["担当者", "来店数", "売上", "契約率"])
for i in range(10):
    r = 12 + i
    ws.cell(row=r, column=6, value=f'=IF(マスタ!A{5+i}="","",マスタ!A{5+i})')
    ws.cell(row=r, column=7,
            value=f'=IF($F{r}="","",COUNTIFS({IN_MONTH},{RNG_ST},$F{r}))')
    ws.cell(row=r, column=8,
            value=f'=IF($F{r}="","",SUMIFS({RNG_UR},{IN_MONTH},{RNG_ST},$F{r}))')
    ws.cell(row=r, column=9,
            value=f'=IF($F{r}="","",IFERROR(COUNTIFS({IN_MONTH},{RNG_ST},$F{r},'
                  f'{RNG_KB},"新規",{RNG_SK},"○")/COUNTIFS({IN_MONTH},{RNG_ST},$F{r},'
                  f'{RNG_KB},"新規"),0))')
    for col in range(6, 10):
        c = ws.cell(row=r, column=col)
        c.font = Font(name=F, size=10); c.border = BOX; c.fill = CALC_BG
        c.alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=8).number_format = YEN
    ws.cell(row=r, column=9).number_format = PCT

ws["A44"] = "※ 契約率は「新規のお客様のうち、日報の成約列に○を入れた件数の割合」です。"
ws["A44"].font = Font(name=F, size=9, color="595959")

# ============================================================ 現金管理
ws = wb.create_sheet("現金管理")
ws.sheet_view.showGridLines = False
title(ws, "現金管理", "現金売上は日報から自動で拾います。入力するのは入金・出金・実査残高だけです。")
head(ws, 6,
     ["日付", "前日繰越", "現金売上", "その他入金", "出金", "理論残高", "実査残高", "差異", "備考"],
     [12, 14, 14, 14, 12, 14, 14, 12, 26])
ws.freeze_panes = "A7"

for i in range(CASHN - CASH0 + 1):
    r = CASH0 + i
    ws.cell(row=r, column=1).number_format = DATE
    if i == 0:
        ws.cell(row=r, column=1, value=date(2026, 8, 18))
        ws.cell(row=r, column=2, value=30000)
    else:
        ws.cell(row=r, column=2, value=f'=IF(G{r-1}="","",G{r-1})')
    ws.cell(row=r, column=3,
            value=f'=IF($A{r}="","",SUMIFS(\'日報\'!$G$7:$G$206,'
                  f'\'日報\'!$A$7:$A$206,$A{r},\'日報\'!$H$7:$H$206,"現金"))')
    ws.cell(row=r, column=6,
            value=f'=IF($A{r}="","",N(B{r})+N(C{r})+N(D{r})-N(E{r}))')
    ws.cell(row=r, column=8,
            value=f'=IF(OR($A{r}="",G{r}=""),"",G{r}-F{r})')
    for col in range(1, 10):
        c = ws.cell(row=r, column=col)
        c.font = Font(name=F, size=10); c.border = BOX
        c.alignment = Alignment(horizontal="center" if col == 1 else "right")
        c.fill = CALC_BG if col in (3, 6, 8) or (col == 2 and i > 0) else INPUT_BG
        if col in (2, 3, 4, 5, 6, 7, 8):
            c.number_format = YEN

# 入力例
for col, val in ((4, 0), (5, 3000), (7, 32000), (9, "釣銭準備金 30,000円から開始")):
    ws.cell(row=CASH0, column=col, value=val)
for col in range(1, 10):
    ws.cell(row=CASH0, column=col).font = Font(name=F, size=10, italic=True, color="7F7F7F")

ws["A69"] = "※ 差異がマイナスなら現金が不足、プラスなら過剰です。0以外が続く場合は運用の見直しが必要です。"
ws["A69"].font = Font(name=F, size=9, color="595959")

wb.save(PATH)
print(PATH)
