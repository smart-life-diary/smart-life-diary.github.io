"""建設帳票5点セットのうち、原価管理表以外の4点を生成する。

出力先は samples/建設帳票5点セット/ 。原価管理表は koji_sheet.py が作る。

  1. 工事別原価管理表.xlsx   ← koji_sheet.py
  2. 工程管理表.xlsx
  3. 工事日報.xlsx
  4. 資材発注・受入管理表.xlsx
  5. 見積・請求・入金管理表.xlsx

共通の約束
  ・入力する欄は FFF3CC（黄）、数式の欄は EEF2F6（グレー）で塗り分ける
  ・工事名や取引先はマスタに登録し、入力欄は入力規則のプルダウンにする
  ・マクロは使わない。Googleスプレッドシートでも同じように動く
  ・入力行は200行目まで数式を入れておく
"""
import os
import re
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from koji_sheet import BORDER, head, SITE

OUT = os.path.join(SITE, "samples", "建設帳票5点セット")
IN_F = PatternFill("solid", fgColor="FFF3CC")     # 入力欄
CA_F = PatternFill("solid", fgColor="EEF2F6")     # 自動計算欄
MEI = "Meiryo"


def title(ws, name, note):
    ws["A1"] = name
    ws["A1"].font = Font(name=MEI, size=14, bold=True, color="1F3B57")
    ws["A2"] = note
    ws["A2"].font = Font(name=MEI, size=10, color="6E7A8A")


def d8(v):
    """'2026/04/02' を日付として書き込む。文字列のままだと日付計算ができない。"""
    if isinstance(v, str) and re.fullmatch(r"\d{4}/\d{1,2}/\d{1,2}", v):
        y, m, d = (int(x) for x in v.split("/"))
        return datetime.date(y, m, d)
    return v


def cell(ws, r, c, value=None, calc=False, fmt=None, align=None):
    x = ws.cell(row=r, column=c, value=d8(value))
    x.font = Font(name=MEI, size=10)
    x.fill = CA_F if calc else IN_F
    x.border = BORDER
    if fmt:
        x.number_format = fmt
    if align:
        x.alignment = Alignment(horizontal=align, vertical="center")
    return x


def intro(wb, name, lines):
    ws = wb.active
    ws.title = "はじめに"
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 88
    ws["B2"] = name
    ws["B2"].font = Font(name=MEI, size=18, bold=True, color="1F3B57")
    body = lines + [
        "",
        "■ 共通のルール",
        "　 入力するのは黄色の欄だけです。グレーの欄には数式が入っています。",
        "　 上書きすると集計が止まります。",
        "",
        "■ 行を増やすとき",
        "　 200行目まで数式が入っています。足りなくなったら、",
        "　 最終行をコピーして下に貼り付けてください。",
        "",
        "■ このファイルについて",
        "　 サンプルです。工事名・金額・氏名・会社名はすべて架空のものです。",
    ]
    for i, t in enumerate(body, start=3):
        ws.cell(row=i, column=2, value=t).font = Font(name=MEI, size=11)
    return ws


def koji_master(wb, kojis):
    """どの帳票でも使う工事マスタ。"""
    ws = wb.create_sheet("マスタ")
    title(ws, "マスタ", "ここに登録した内容が、入力欄のプルダウンに出ます。")
    head(ws, 4, [("工事番号", 12), ("工事名", 34)])
    for i, (no, nm) in enumerate(kojis, start=5):
        cell(ws, i, 1, no)
        cell(ws, i, 2, nm)
    return ws


KOJIS = [
    ("K-101", "市道1号線 舗装補修工事"),
    ("K-102", "○○川 護岸ブロック工事"),
    ("K-103", "××排水路 改修工事"),
    ("K-104", "県道2号線 側溝設置工事"),
]


# ── 2. 工程管理表 ───────────────────────────────────────
def build_kotei():
    wb = Workbook()
    intro(wb, "工程管理表", [
        "",
        "■ 使う順番",
        "　 1. 「マスタ」に工事と工種を登録します",
        "　 2. 「工程表」の対象年月と、工種ごとの予定・実績を入力します",
        "　 3. 右側の日付欄に、予定＝■ 実績＝□ が自動で並びます",
        "",
        "■ 見方",
        "　 ■ だけの日は、予定より遅れています。",
        "　 □ だけの日は、予定より早く進んでいます。",
    ])
    ws = koji_master(wb, KOJIS)
    head(ws, 11, [("工種", 16)])
    for i, k in enumerate(["準備工", "土工", "仮設工", "舗装工",
                           "コンクリート工", "付帯工", "片付け"], start=12):
        cell(ws, i, 1, k)

    ws = wb.create_sheet("工程表")
    title(ws, "工程表", "対象年月と、工種ごとの予定・実績の日付を入力してください。")
    cell(ws, 2, 6, "対象年月", calc=True, align="center")
    cell(ws, 2, 7, "2026/04/01", fmt="yyyy年m月", align="center")
    cell(ws, 3, 6, "工事番号", calc=True, align="center")
    cell(ws, 3, 7, "K-101", align="center")

    cols = [("工種", 18), ("予定開始", 12), ("予定終了", 12),
            ("実績開始", 12), ("実績終了", 12), ("進捗率", 10)]
    head(ws, 5, cols)
    # 日付の見出し。$G$2 の月の1日から31日ぶん
    for d in range(1, 32):
        c = ws.cell(row=5, column=6 + d, value=f"=$G$2+{d - 1}")
        c.fill = PatternFill("solid", fgColor="1F3B57")
        c.font = Font(name=MEI, size=9, bold=True, color="FFFFFF")
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = BORDER
        c.number_format = "d"
        ws.column_dimensions[get_column_letter(6 + d)].width = 3.4

    plan = [("準備工", "2026/04/01", "2026/04/03", "2026/04/01", "2026/04/03"),
            ("仮設工", "2026/04/04", "2026/04/08", "2026/04/04", "2026/04/09"),
            ("土工", "2026/04/09", "2026/04/16", "2026/04/10", ""),
            ("舗装工", "2026/04/17", "2026/04/24", "", ""),
            ("付帯工", "2026/04/25", "2026/04/28", "", ""),
            ("片付け", "2026/04/29", "2026/04/30", "", "")]
    R0, RN = 6, 45
    for r in range(R0, RN + 1):
        i = r - R0
        src = plan[i] if i < len(plan) else ("", "", "", "", "")
        for c, v in enumerate(src, start=1):
            cell(ws, r, c, v or None, fmt="m/d" if c > 1 else None,
                 align="center" if c > 1 else None)
        # 進捗率＝実績が終わっていれば100%、始まっていれば50%、未着手は0%
        cell(ws, r, 6,
             f'=IF($A{r}="","",IF($E{r}<>"",1,IF($D{r}<>"",0.5,0)))',
             calc=True, fmt="0%", align="center")
        for d in range(1, 32):
            col = 6 + d
            ref = f"{get_column_letter(col)}$5"
            f = (f'=IF($A{r}="","",'
                 f'IF(AND($D{r}<>"",{ref}>=$D{r},{ref}<=IF($E{r}="",{ref},$E{r})),"□",'
                 f'IF(AND($B{r}<>"",{ref}>=$B{r},{ref}<=$C{r}),"■","")))')
            x = ws.cell(row=r, column=col, value=f)
            x.font = Font(name=MEI, size=10)
            x.fill = CA_F
            x.border = BORDER
            x.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "G6"
    for dv, col, rng in [
        (DataValidation(type="list", formula1="マスタ!$A$5:$A$8", allow_blank=True),
         "G", f"G3:G3"),
        (DataValidation(type="list", formula1="マスタ!$A$12:$A$18", allow_blank=True),
         "A", f"A{R0}:A{RN}"),
    ]:
        ws.add_data_validation(dv)
        dv.add(rng)
    return wb


# ── 3. 工事日報（A4印刷用）──────────────────────────────
def build_nippo():
    wb = Workbook()
    intro(wb, "工事日報", [
        "",
        "■ 使い方",
        "　 「日報」シートの黄色い欄を埋めて、そのまま印刷してください。",
        "　 A4縦1枚に収まるよう設定してあります。",
        "",
        "■ 現場に持ち出す場合",
        "　 空欄のまま印刷して、手書きで記入する使い方もできます。",
    ])
    koji_master(wb, KOJIS)

    ws = wb.create_sheet("日報")
    for c, w in zip("ABCDEFGH", [10, 14, 12, 10, 10, 12, 12, 14]):
        ws.column_dimensions[c].width = w
    ws["A1"] = "工 事 日 報"
    ws["A1"].font = Font(name=MEI, size=18, bold=True, color="1F3B57")
    ws.merge_cells("A1:H1")
    ws["A1"].alignment = Alignment(horizontal="center")

    def label(r, c, text):
        x = ws.cell(row=r, column=c, value=text)
        x.font = Font(name=MEI, size=10, bold=True, color="FFFFFF")
        x.fill = PatternFill("solid", fgColor="1F3B57")
        x.alignment = Alignment(horizontal="center", vertical="center")
        x.border = BORDER

    label(3, 1, "工事番号"); cell(ws, 3, 2, "K-101", align="center")
    label(3, 3, "工事名")
    ws.merge_cells("D3:F3")
    cell(ws, 3, 4, "=IFERROR(VLOOKUP($B$3,マスタ!$A$5:$B$8,2,FALSE),\"\")", calc=True)
    label(3, 7, "日付"); cell(ws, 3, 8, "2026/04/10", fmt="yyyy/m/d", align="center")
    label(4, 1, "天候"); cell(ws, 4, 2, "晴", align="center")
    label(4, 3, "気温"); cell(ws, 4, 4, "18", fmt='0"℃"', align="center")
    label(4, 5, "作業時間"); ws.merge_cells("F4:H4"); cell(ws, 4, 6, "8:00〜17:00")

    label(6, 1, "本日の作業内容")
    ws.merge_cells("B6:H6"); cell(ws, 6, 2, "路盤工 t=150 施工　L=45m")
    label(7, 1, "翌日の予定")
    ws.merge_cells("B7:H7"); cell(ws, 7, 2, "表層工 施工準備")

    label(9, 1, "作業員")
    for c, t in zip(range(2, 5), ["氏名", "職種", "人工"]):
        label(9, c, t)
    label(9, 5, "使用機械・車両")
    for c, t in zip(range(6, 9), ["名称", "規格", "台数"]):
        label(9, c, t)
    crew = [("佐藤", "土工", 1.0), ("鈴木", "土工", 1.0),
            ("高橋", "運転手", 1.0), ("", "", None), ("", "", None), ("", "", None)]
    mach = [("バックホウ", "0.45m3", 1), ("ローラー", "10t", 1),
            ("ダンプ", "10t", 2), ("", "", None), ("", "", None), ("", "", None)]
    for i in range(6):
        r = 10 + i
        cell(ws, r, 1, None)
        for c, v in enumerate(crew[i], start=2):
            cell(ws, r, c, v or None, fmt="0.0" if c == 4 else None,
                 align="center" if c >= 3 else None)
        cell(ws, r, 5, None)
        for c, v in enumerate(mach[i], start=6):
            cell(ws, r, c, v or None, align="center" if c >= 7 else None)
    label(16, 3, "人工計")
    cell(ws, 16, 4, "=SUM($D$10:$D$15)", calc=True, fmt="0.0", align="center")

    label(18, 1, "使用資材")
    for c, t in zip(range(2, 5), ["品名", "規格", "数量"]):
        label(18, c, t)
    label(18, 5, "安全・特記事項")
    ws.merge_cells("F18:H18")
    zai = [("再生砕石", "RC-40", "80t"), ("加熱アスファルト", "密粒13", "24t"),
           ("", "", "")]
    for i, (a, b, c_) in enumerate(zai):
        r = 19 + i
        cell(ws, r, 1, None)
        cell(ws, r, 2, a or None); cell(ws, r, 3, b or None)
        cell(ws, r, 4, c_ or None, align="center")
        cell(ws, r, 5, None)
        ws.merge_cells(f"F{r}:H{r}")
        cell(ws, r, 6, "KY実施。重機後方に誘導員配置。" if i == 0 else None)

    label(23, 1, "記入者"); cell(ws, 23, 2, "山田", align="center")
    label(23, 3, "確認者"); cell(ws, 23, 4, None, align="center")

    ws.print_area = "A1:H24"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1

    dv = DataValidation(type="list", formula1="マスタ!$A$5:$A$8", allow_blank=True)
    ws.add_data_validation(dv)
    dv.add("B3:B3")
    return wb


# ── 4. 資材発注・受入管理表 ─────────────────────────────
def build_zaizai():
    wb = Workbook()
    intro(wb, "資材発注・受入管理表", [
        "",
        "■ 使う順番",
        "　 1. 「マスタ」に工事・資材・仕入先を登録します",
        "　 2. 「発注入力」に1件1行、発注した内容を入力します",
        "　 3. 納品されたら受入日と受入数量を入れます",
        "　 4. 残数と未受入の金額が自動で出ます",
    ])
    ws = koji_master(wb, KOJIS)
    head(ws, 11, [("資材名", 20), ("単位", 8), ("仕入先", 22)])
    zaisai = [("再生砕石 RC-40", "t"), ("加熱アスファルト 密粒13", "t"),
              ("生コン 24-8-20", "m3"), ("U字側溝 300", "本"),
              ("鉄筋 D13", "t"), ("型枠 コンパネ", "枚")]
    shiire = ["○○建材", "△△生コン", "□□工業", "各社"]
    for i, (n, u) in enumerate(zaisai, start=12):
        cell(ws, i, 1, n); cell(ws, i, 2, u, align="center")
    for i, s in enumerate(shiire, start=12):
        cell(ws, i, 3, s)

    ws = wb.create_sheet("発注入力")
    title(ws, "発注入力", "黄色の欄だけ入力してください。金額と残数は自動で出ます。")
    cols = [("発注日", 11), ("工事番号", 11), ("資材名", 24), ("仕入先", 16),
            ("単位", 7), ("発注数量", 11), ("単価", 11), ("発注金額", 13),
            ("納品予定日", 12), ("受入日", 11), ("受入数量", 11),
            ("残数", 10), ("未受入金額", 13)]
    head(ws, 4, cols)
    data = [
        ("2026/04/02", "K-101", "再生砕石 RC-40", "○○建材", 120, 3800,
         "2026/04/08", "2026/04/08", 120),
        ("2026/04/05", "K-101", "加熱アスファルト 密粒13", "○○建材", 40, 12500,
         "2026/04/17", "", None),
        ("2026/04/06", "K-102", "生コン 24-8-20", "△△生コン", 85, 18200,
         "2026/04/12", "2026/04/12", 85),
        ("2026/04/09", "K-104", "U字側溝 300", "□□工業", 150, 4200,
         "2026/04/15", "2026/04/15", 140),
        ("2026/04/10", "K-102", "鉄筋 D13", "□□工業", 6, 128000,
         "2026/04/20", "", None),
    ]
    R0, RN = 5, 204
    for r in range(R0, RN + 1):
        i = r - R0
        d = data[i] if i < len(data) else None
        v = d if d else ("", "", "", "", None, None, "", "", None)
        cell(ws, r, 1, v[0] or None, fmt="m/d", align="center")
        cell(ws, r, 2, v[1] or None, align="center")
        cell(ws, r, 3, v[2] or None)
        cell(ws, r, 4, v[3] or None)
        cell(ws, r, 5,
             f'=IF($C{r}="","",IFERROR(VLOOKUP($C{r},マスタ!$A$12:$B$17,2,FALSE),""))',
             calc=True, align="center")
        cell(ws, r, 6, v[4], fmt="#,##0.0", align="right")
        cell(ws, r, 7, v[5], fmt="#,##0")
        cell(ws, r, 8, f'=IF($F{r}="","",$F{r}*$G{r})', calc=True, fmt="#,##0")
        cell(ws, r, 9, v[6] or None, fmt="m/d", align="center")
        cell(ws, r, 10, v[7] or None, fmt="m/d", align="center")
        cell(ws, r, 11, v[8], fmt="#,##0.0", align="right")
        cell(ws, r, 12, f'=IF($F{r}="","",$F{r}-N($K{r}))', calc=True, fmt="#,##0.0")
        cell(ws, r, 13, f'=IF($F{r}="","",$L{r}*$G{r})', calc=True, fmt="#,##0")
    ws.freeze_panes = "A5"
    for f1, col in [("マスタ!$A$5:$A$8", "B"), ("マスタ!$A$12:$A$17", "C"),
                    ("マスタ!$C$12:$C$15", "D")]:
        dv = DataValidation(type="list", formula1=f1, allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}{R0}:{col}{RN}")

    ws = wb.create_sheet("工事別集計")
    title(ws, "工事別集計", "この画面はすべて自動計算です。入力する欄はありません。")
    head(ws, 4, [("工事番号", 12), ("工事名", 30), ("発注金額", 15),
                 ("未受入金額", 15), ("受入済み金額", 15)])
    for i in range(4):
        r, m = 5 + i, 5 + i
        cell(ws, r, 1, f"=マスタ!A{m}", calc=True, align="center")
        cell(ws, r, 2, f"=マスタ!B{m}", calc=True)
        cell(ws, r, 3, f"=SUMIFS('発注入力'!$H$5:$H$204,'発注入力'!$B$5:$B$204,$A{r})",
             calc=True, fmt="#,##0")
        cell(ws, r, 4, f"=SUMIFS('発注入力'!$M$5:$M$204,'発注入力'!$B$5:$B$204,$A{r})",
             calc=True, fmt="#,##0")
        cell(ws, r, 5, f"=$C{r}-$D{r}", calc=True, fmt="#,##0")
    return wb


# ── 5. 見積・請求・入金管理表 ───────────────────────────
def build_seikyu():
    wb = Workbook()
    intro(wb, "見積・請求・入金管理表", [
        "",
        "■ 使う順番",
        "　 1. 「マスタ」に取引先を登録します",
        "　 2. 「案件管理」に1件1行、見積を出した案件を入力します",
        "　 3. 受注・請求・入金の日付を、進むたびに埋めていきます",
        "　 4. 未入金額と、入金予定日からの経過日数が自動で出ます",
        "",
        "■ 督促の判断",
        "　 「経過日数」が赤字になっていなくても、数字が大きい行は",
        "　 入金予定日を過ぎています。上から順に確認してください。",
    ])
    ws = wb.create_sheet("マスタ")
    title(ws, "マスタ", "ここに登録した内容が、入力欄のプルダウンに出ます。")
    head(ws, 4, [("取引先", 28), ("担当者", 16)])
    for i, (a, b) in enumerate([("○○建設 株式会社", "田中"),
                                ("株式会社 △△組", "佐々木"),
                                ("□□土木 株式会社", "渡辺"),
                                ("市役所 建設課", "—")], start=5):
        cell(ws, i, 1, a); cell(ws, i, 2, b)
    head(ws, 11, [("状況", 14)])
    for i, s in enumerate(["見積中", "受注", "失注", "請求済", "入金済"], start=12):
        cell(ws, i, 1, s, align="center")

    ws = wb.create_sheet("案件管理")
    title(ws, "案件管理", "黄色の欄だけ入力してください。未入金額と経過日数は自動です。")
    cols = [("見積日", 11), ("取引先", 24), ("件名", 30), ("状況", 11),
            ("見積金額", 14), ("受注金額", 14), ("請求日", 11), ("請求金額", 14),
            ("入金予定日", 12), ("入金日", 11), ("入金額", 14),
            ("未入金額", 14), ("経過日数", 11)]
    head(ws, 4, cols)
    data = [
        ("2026/03/02", "○○建設 株式会社", "市道1号線 舗装補修", "入金済",
         4800000, 4800000, "2026/03/31", 4800000, "2026/04/30", "2026/04/28", 4800000),
        ("2026/03/10", "株式会社 △△組", "○○川 護岸ブロック", "請求済",
         13200000, 12600000, "2026/04/30", 6300000, "2026/05/31", "", None),
        ("2026/03/22", "□□土木 株式会社", "××排水路 改修", "受注",
         3400000, 3200000, "", None, "", "", None),
        ("2026/04/05", "市役所 建設課", "県道2号線 側溝設置", "受注",
         2450000, 2450000, "", None, "", "", None),
        ("2026/04/12", "○○建設 株式会社", "駐車場 舗装打替え", "見積中",
         1850000, None, "", None, "", "", None),
    ]
    R0, RN = 5, 204
    for r in range(R0, RN + 1):
        i = r - R0
        d = data[i] if i < len(data) else None
        v = d if d else ("", "", "", "", None, None, "", None, "", "", None)
        cell(ws, r, 1, v[0] or None, fmt="m/d", align="center")
        cell(ws, r, 2, v[1] or None)
        cell(ws, r, 3, v[2] or None)
        cell(ws, r, 4, v[3] or None, align="center")
        for c, val in [(5, v[4]), (6, v[5])]:
            cell(ws, r, c, val, fmt="#,##0")
        cell(ws, r, 7, v[6] or None, fmt="m/d", align="center")
        cell(ws, r, 8, v[7], fmt="#,##0")
        cell(ws, r, 9, v[8] or None, fmt="m/d", align="center")
        cell(ws, r, 10, v[9] or None, fmt="m/d", align="center")
        cell(ws, r, 11, v[10], fmt="#,##0")
        cell(ws, r, 12, f'=IF($H{r}="","",N($H{r})-N($K{r}))', calc=True, fmt="#,##0")
        cell(ws, r, 13,
             f'=IF(OR($I{r}="",$J{r}<>""),"",TODAY()-$I{r})',
             calc=True, fmt="#,##0", align="center")
    ws.freeze_panes = "A5"
    for f1, col in [("マスタ!$A$5:$A$8", "B"), ("マスタ!$A$12:$A$16", "D")]:
        dv = DataValidation(type="list", formula1=f1, allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}{R0}:{col}{RN}")

    ws = wb.create_sheet("集計")
    title(ws, "集計", "この画面はすべて自動計算です。")
    head(ws, 4, [("項目", 26), ("金額・件数", 18)])
    rows = [
        ("見積提出額 合計", '=SUM(\'案件管理\'!$E$5:$E$204)', "#,##0"),
        ("受注額 合計", '=SUM(\'案件管理\'!$F$5:$F$204)', "#,##0"),
        ("受注率（件数）",
         '=IFERROR(COUNTIF(\'案件管理\'!$D$5:$D$204,"受注")'
         '/COUNTA(\'案件管理\'!$D$5:$D$204),0)', "0.0%"),
        ("請求済み 合計", '=SUM(\'案件管理\'!$H$5:$H$204)', "#,##0"),
        ("入金済み 合計", '=SUM(\'案件管理\'!$K$5:$K$204)', "#,##0"),
        ("未入金 合計", '=SUM(\'案件管理\'!$L$5:$L$204)', "#,##0"),
        ("入金予定を過ぎている件数",
         '=COUNTIF(\'案件管理\'!$M$5:$M$204,">0")', "#,##0"),
    ]
    for i, (name, f, fmt) in enumerate(rows, start=5):
        cell(ws, i, 1, name, calc=True)
        cell(ws, i, 2, f, calc=True, fmt=fmt)
    return wb


BOOKS = [
    ("工程管理表.xlsx", build_kotei),
    ("工事日報.xlsx", build_nippo),
    ("資材発注・受入管理表.xlsx", build_zaizai),
    ("見積・請求・入金管理表.xlsx", build_seikyu),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in BOOKS:
        p = os.path.join(OUT, name)
        wb = fn()
        # 生成直後の .xlsx には計算結果が入らない。開いた時点で必ず再計算させる。
        wb.calculation.fullCalcOnLoad = True
        wb.save(p)
        print(f"{p}  {os.path.getsize(p) // 1024}KB")


# ── 出品用の画像（1.20:1）───────────────────────────────
def images():
    from koji_sheet import board, table, font, OUT_P, IN_BG, CALC_BG, ACCENT, W, H
    from PIL import ImageDraw
    import os as _os
    _os.makedirs(OUT_P, exist_ok=True)
    out = []

    # 1枚目：セットの中身
    img, d, y = board("帳票5点。買ったその日に届きます",
                      "受注生産ではありません。完成しているものをお渡しします")
    items = [
        ("① 工事別原価管理表", "日報から工事ごとの発生原価・予算消化率・粗利率まで"),
        ("② 工程管理表", "工種ごとの予定と実績を並べて表示。遅れが一目で分かります"),
        ("③ 工事日報", "A4縦1枚。印刷して現場に持ち出せます"),
        ("④ 資材発注・受入管理表", "発注と受入の差から、未受入の金額が出ます"),
        ("⑤ 見積・請求・入金管理表", "未入金額と、入金予定日からの経過日数が出ます"),
    ]
    x, w_ = 120, W - 240
    for i, (name, desc) in enumerate(items):
        yy = y + i * 172
        d.rectangle([x, yy, x + w_, yy + 142], fill=(24, 33, 54))
        d.rectangle([x, yy, x + 12, yy + 142], fill=ACCENT)
        d.text((x + 46, yy + 24), name, font=font(42), fill=(255, 255, 255))
        d.text((x + 46, yy + 84), desc, font=font(27), fill=(150, 172, 200))
    p = _os.path.join(OUT_P, "fset-1.png"); img.save(p); out.append(p)

    # 2枚目：工程管理表（実物どおり ■＝予定 / □＝実績 のセル表示）
    img, d, y = board("予定と実績が、同じ行に並びます",
                      "■が予定、□が実績。ずれている工種がその場で分かります")
    days = list(range(1, 21))
    plan = [("準備工", 1, 3, 1, 3, "100%"), ("仮設工", 4, 8, 4, 9, "100%"),
            ("土工", 9, 16, 10, 0, "50%"), ("舗装工", 17, 20, 0, 0, "0%")]
    TODAY = 12
    cols = [("工種", 190, "l"), ("進捗率", 120, "c")] + \
           [(str(dd), 52, "c") for dd in days]
    fills = [IN_BG, CALC_BG] + [CALC_BG] * len(days)
    rows = []
    for name, ps, pe, rs, re_, pr in plan:
        row = [name, pr]
        for dd in days:
            end = re_ if re_ else (TODAY if rs else 0)
            if rs and rs <= dd <= end:
                row.append("□")
            elif ps <= dd <= pe:
                row.append("■")
            else:
                row.append("")
        rows.append(row)
    x = (W - sum(c[1] for c in cols)) // 2
    yy = table(d, x, y, cols, rows, fills, rowh=112)

    d.text((x, yy + 46), "■ 予定", font=font(32), fill=(255, 255, 255))
    d.text((x + 200, yy + 46), "□ 実績", font=font(32), fill=(255, 255, 255))

    bx, bw = x, sum(c[1] for c in cols)
    d.rectangle([bx, yy + 118, bx + bw, yy + 268], fill=(24, 33, 54))
    d.rectangle([bx, yy + 118, bx + 12, yy + 268], fill=ACCENT)
    d.text((bx + 44, yy + 146),
           "土工は予定より1日遅れて着手し、まだ終わっていません。",
           font=font(34), fill=(214, 226, 242))
    d.text((bx + 44, yy + 202),
           "日付の欄は自動です。予定と実績の日付を入れるだけで並びます。",
           font=font(29), fill=(150, 172, 200))
    p = _os.path.join(OUT_P, "fset-2.png"); img.save(p); out.append(p)

    # 3枚目：見積・請求・入金
    img, d, y = board("入金されていない金額が、常に出ています",
                      "請求したまま忘れる、が起きません")
    cols = [("取引先", 330, "l"), ("件名", 350, "l"), ("請求金額", 200, "r"),
            ("入金額", 200, "r"), ("未入金額", 200, "r"), ("経過日数", 160, "r")]
    fills = [IN_BG, IN_BG, IN_BG, IN_BG, CALC_BG, CALC_BG]
    rows = [
        ["○○建設 株式会社", "市道1号線 舗装補修", "4,800,000", "4,800,000", "0", "—"],
        ["株式会社 △△組", "○○川 護岸ブロック", "6,300,000", "0", "6,300,000", "12"],
        ["□□土木 株式会社", "××排水路 改修", "1,600,000", "0", "1,600,000", "3"],
        ["市役所 建設課", "県道2号線 側溝設置", "2,450,000", "2,450,000", "0", "—"],
        ["○○建設 株式会社", "駐車場 舗装打替え", "—", "—", "—", "—"],
    ]
    x = (W - sum(c[1] for c in cols)) // 2
    yy = table(d, x, y, cols, rows, fills, rowh=88)
    d.text((x, yy + 74), "未入金 合計", font=font(36), fill=(196, 210, 228))
    d.text((x + 320, yy + 62), "7,900,000 円", font=font(58), fill=(214, 226, 242))
    d.text((x, yy + 166),
           "入金予定日を過ぎた案件は、経過日数が積み上がっていきます。",
           font=font(31), fill=(196, 210, 228))
    d.text((x, yy + 216),
           "請求したまま放置されている案件が、一覧の上から順に見つかります。",
           font=font(29), fill=(150, 172, 200))
    p = _os.path.join(OUT_P, "fset-3.png"); img.save(p); out.append(p)
    return out
