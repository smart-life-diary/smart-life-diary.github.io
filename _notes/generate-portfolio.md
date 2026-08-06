# ポートフォリオ画像の生成手順

ココナラのポートフォリオは**画像のみ**登録できます（動画・GIF不可）。
そのため、デモを実際に自動操作してスクリーンショットを撮り、
操作の流れを4カット横並びに合成した画像を作ります。

生成物は `portfolio/` に出力されます。

## 必要なもの

- Chromium（`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`）
- `pip install playwright pillow`
- 日本語フォント（`/usr/share/fonts/truetype/fonts-japanese-gothic.ttf` / IPAGothic）

環境が変わってパスが違う場合は、各スクリプト冒頭の `CHROME` と `FONT` を書き換えてください。

## 実行

```bash
cd _notes/portfolio-tools
python3 shots.py     # デモ5本を自動操作して shots/ に撮影（20枚）
python3 compose.py   # 4カットを合成して portfolio/ に出力（10枚）
```

## 何をしているか

**`shots.py`** — 390×844（スマホ相当）／2倍解像度で各デモを開き、以下を撮ります。

| カット | 内容 | 取得方法 |
|---|---|---|
| ① start | スタート画面 | 読み込み直後 |
| ② question | 設問1問目 | スタートボタンを押した直後 |
| ③ result | 結果画面の上部 | 全問に回答したあと最上部へスクロール |
| ④ share | シェア導線のクローズアップ | `.share-hint` `.copy-btn` `.again` `.cta` `.promptbox` の外接矩形 |

セレクタは5本のデモで構造が違うため、クラス名を横断的に拾う作りにしています。
新しいデモを足したら `DEMOS` に slug を追加してください。既存のクラス命名
（`.opts` / `.options` / `.result` など）に合わせておけば、そのまま動きます。

**`compose.py`** — 各カットの下端の単色余白を削り、幅430pxに揃えて横並びに合成します。
ヘッダーに作品名・構成・訴求文を載せ、カット間に矢印を描きます。
作品名や「○問→○タイプ」の文言は `DEMOS` に定義しています。

## 出力

| ファイル | 用途 |
|---|---|
| `portfolio/<slug>-flow.png` | 4カット合成。ポートフォリオのメイン画像 |
| `portfolio/<slug>-result.png` | 結果画面の単体。2枚目以降に追加する |

slug: `isekai` / `side-biz` / `ai-level` / `shachiku` / `golf`

## 注意

`shots.py` は各設問で**常に最初の選択肢**を選びます。そのため結果は毎回同じ
タイプになります（例：隠れ社畜度チェックは100%）。別のタイプを見せたい場合は
`window.__opts[0]` の添字を変えてください。
