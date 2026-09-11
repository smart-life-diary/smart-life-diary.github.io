"""提案書チェック45 の納品ファイルを書き出す。

出力（samples/ は .gitignore。販売物はリポジトリに置かない）
  samples/提案書チェック45/提案書チェック45.html        診断ツール（※出品はできない。下記）
  samples/提案書チェック45/提案書チェック45_印刷用.html  紙のチェックシート
  samples/提案書チェック45/提案書チェック45_印刷用.pdf   同上をPDF化したもの。これが納品物

**HTML版はココナラのコンテンツ出品では使えない。** 出品画面の対応形式にも無く、
実データ5,012件を数えても html は0件だった（zipも0件）。
納品物は **PDF（このスクリプト）と xlsx（check45_xlsx.py）** の2点。

HTML版は、自分のサイトに無料デモとして置く分には使える。
ただし**ココナラで売る物の中に外部リンクを入れてはいけない**ので、
PDFやxlsxからそのデモへ誘導することはしない。

守っていること
  - 外部の読み込みを一切しない。フォントもCDNも使わない。開けば動く
  - 外部サイトへのリンクを入れない。ココナラは外部でのやりとりを禁じている
  - 「必ず」「確実に」など、過度な期待を与える表現を入れない
"""
import html
import json
import os
import subprocess

from check45_items import AXES, ITEMS, BANDS, AXIS_ADVICE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "samples", "提案書チェック45"))

FONT = ("-apple-system,BlinkMacSystemFont,'Hiragino Kaku Gothic ProN',"
        "'Yu Gothic Medium','Meiryo',sans-serif")

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#F4F7FB; --card:#fff; --line:#E2E8F0; --ink:#182438; --sub:#6C7C91;
  --body:#46546 8; --accent:#0070D6; --accent-soft:#E8F1FC;
}
html,body{min-height:100%}
body{background:var(--bg);font-family:__FONT__;color:var(--ink);
  line-height:1.7;padding:20px 14px 56px;display:flex;justify-content:center;
  -webkit-text-size-adjust:100%}
.shell{width:100%;max-width:560px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;
  padding:24px 20px;box-shadow:0 10px 30px -18px rgba(24,36,56,.28)}
.hidden{display:none}
button{font-family:inherit;cursor:pointer}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.08em;color:var(--accent);margin-bottom:10px}
h1{font-size:25px;line-height:1.45;font-weight:700;margin-bottom:12px}
.lead{font-size:14.5px;color:var(--sub);margin-bottom:20px}
.axisrow{display:grid;gap:9px;margin-bottom:22px}
.axisrow div{display:flex;gap:10px;align-items:baseline;background:var(--bg);
  border:1px solid var(--line);border-radius:11px;padding:10px 13px;font-size:13.5px}
.axisrow b{font-size:14px}
.axisrow span{color:var(--sub);font-size:12.5px}
.primary{width:100%;background:var(--accent);color:#fff;border:none;border-radius:13px;
  padding:15px;font-size:16px;font-weight:700;box-shadow:0 8px 20px -10px rgba(0,112,214,.8)}
.ghost{width:100%;background:none;border:1px solid var(--line);border-radius:13px;
  padding:13px;font-size:14px;color:var(--sub);margin-top:10px}
.note{font-size:12px;color:var(--sub);margin-top:16px;line-height:1.65}

.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.back{background:none;border:none;color:var(--sub);font-size:13.5px;padding:0}
.step{font-size:13px;color:var(--sub)}
.bar{display:flex;gap:5px;margin-bottom:20px}
.bar i{flex:1;height:5px;border-radius:99px;background:var(--line)}
.bar i.on{background:var(--accent)}
h2{font-size:20px;font-weight:700;margin-bottom:4px}
h2 em{font-style:normal;font-size:13px;color:var(--sub);font-weight:500;margin-left:8px}
.axisdesc{font-size:13.5px;color:var(--sub);margin-bottom:18px}
.q{border-top:1px solid var(--line);padding:14px 0}
.q .t{font-size:14.5px;line-height:1.65;margin-bottom:10px;display:flex;gap:9px}
.q .n{flex:0 0 26px;font-size:12px;font-weight:700;color:var(--accent);
  background:var(--accent-soft);border-radius:7px;text-align:center;padding:2px 0;height:22px}
.opts{display:flex;gap:7px;padding-left:35px}
.opts button{flex:1;border:1.5px solid var(--line);background:#fff;border-radius:10px;
  padding:9px 4px;font-size:13px;color:var(--body);transition:.15s}
.opts button.sel{border-color:var(--accent);background:var(--accent-soft);
  color:var(--accent);font-weight:700}

.score{text-align:center;padding:6px 0 18px}
.score .big{font-size:52px;font-weight:700;line-height:1;color:var(--accent)}
.score .big small{font-size:20px;color:var(--sub);font-weight:500;margin-left:4px}
.band{font-size:19px;font-weight:700;margin:14px 0 8px}
.bandmsg{font-size:14.5px;color:var(--sub);margin-bottom:22px}
.axb{margin-bottom:14px}
.axb .h{display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:6px}
.axb .h b{font-weight:700}
.axb .h span{color:var(--sub)}
.axb .g{height:9px;background:var(--line);border-radius:99px;overflow:hidden}
.axb .g i{display:block;height:100%;border-radius:99px;transition:width .7s ease}
.sect{background:var(--bg);border:1px solid var(--line);border-radius:14px;
  padding:16px 15px;margin:22px 0}
.sect h3{font-size:14px;font-weight:700;margin-bottom:10px}
.sect ul{list-style:none;display:grid;gap:10px}
.sect li{display:flex;gap:9px;font-size:13.5px;line-height:1.6}
.sect li .d{flex:0 0 18px;height:18px;border-radius:99px;background:var(--accent);
  color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;
  justify-content:center;margin-top:3px}
.todo li .d{background:#CE584A}
.todo .cnt{font-size:12px;color:var(--sub);font-weight:500}
@media print{
  body{background:#fff;padding:0}
  .noprint{display:none !important}
  .card{box-shadow:none;border:none}
}
"""

JS = """
const AXES=__AXES__, ITEMS=__ITEMS__, BANDS=__BANDS__, ADVICE=__ADVICE__;
const LABELS=["できている","あいまい","できていない"], VALUES=[2,1,0];
const ans=new Array(ITEMS.length).fill(null);
let page=0;
const $=id=>document.getElementById(id);

function show(n){for(const s of ["intro","quiz","result"])$(s).classList.toggle("hidden",s!==n);
  window.scrollTo(0,0);}

function renderIntro(){
  const c=$("axisrow");c.innerHTML="";
  AXES.forEach(a=>{const d=document.createElement("div");
    d.innerHTML='<b>'+a[0]+'</b><span>'+a[1]+'　15項目</span>';c.appendChild(d);});
}

function renderQuiz(){
  const a=AXES[page];
  $("axisName").innerHTML=a[0]+'<em>'+a[1]+'</em>';
  $("axisDesc").textContent=a[3];
  $("stepNo").textContent=(page+1)+" / 3";
  const b=$("bar");b.innerHTML="";
  for(let i=0;i<3;i++){const e=document.createElement("i");if(i<=page)e.className="on";b.appendChild(e);}
  $("backBtn").style.visibility=page?"visible":"hidden";
  const list=$("list");list.innerHTML="";
  ITEMS.forEach((it,i)=>{
    if(it[0]!==page)return;
    const q=document.createElement("div");q.className="q";
    const t=document.createElement("div");t.className="t";
    t.innerHTML='<span class="n">'+(i+1)+'</span><span>'+it[1]+'</span>';
    const o=document.createElement("div");o.className="opts";
    LABELS.forEach((lb,k)=>{
      const btn=document.createElement("button");btn.textContent=lb;
      if(ans[i]===VALUES[k])btn.classList.add("sel");
      btn.onclick=()=>{ans[i]=VALUES[k];
        [...o.children].forEach(x=>x.classList.remove("sel"));btn.classList.add("sel");
        updateNext();};
      o.appendChild(btn);});
    q.appendChild(t);q.appendChild(o);list.appendChild(q);
  });
  updateNext();
}

function updateNext(){
  const left=ITEMS.filter((it,i)=>it[0]===page&&ans[i]===null).length;
  const b=$("nextBtn");
  b.disabled=left>0;
  b.style.opacity=left>0?.45:1;
  b.textContent=left>0?("未回答 あと"+left+"問"):(page<2?"次へ":"結果を見る");
}

function next(){ if(page<2){page++;renderQuiz();} else {renderResult();show("result");} }
function back(){ if(page>0){page--;renderQuiz();} }

function renderResult(){
  const per=[0,0,0];
  ITEMS.forEach((it,i)=>per[it[0]]+=ans[i]);
  const total=per.reduce((a,b)=>a+b,0);
  $("total").firstChild.textContent=total;
  const band=BANDS.find(b=>total>=b[0]);
  $("band").textContent=band[1];
  $("bandmsg").textContent=band[2];
  const bx=$("axbars");bx.innerHTML="";
  per.forEach((v,i)=>{
    const w=Math.round(v/30*100);
    const d=document.createElement("div");d.className="axb";
    d.innerHTML='<div class="h"><b>'+AXES[i][0]+'</b><span>'+v+' / 30</span></div>'+
      '<div class="g"><i style="width:0;background:'+AXES[i][2]+'"></i></div>';
    bx.appendChild(d);
    setTimeout(()=>{d.querySelector("i").style.width=w+"%";},60+i*120);
  });
  const weak=per.indexOf(Math.min(...per));
  $("weakName").textContent="いちばん低いのは「"+AXES[weak][0]+"」です";
  const ul=$("advice");ul.innerHTML="";
  ADVICE[weak].forEach(t=>{
    const li=document.createElement("li");
    li.innerHTML='<span class="d">→</span><span>'+t+'</span>';ul.appendChild(li);});
  const todo=[];
  ITEMS.forEach((it,i)=>{if(ans[i]===0)todo.push((i+1)+". "+it[1]);});
  $("todoCnt").textContent="（"+todo.length+"件）";
  const tl=$("todo");tl.innerHTML="";
  if(!todo.length){
    const li=document.createElement("li");
    li.innerHTML='<span class="d">✓</span><span>「できていない」を付けた項目はありませんでした。</span>';
    tl.appendChild(li);
  } else todo.forEach(t=>{
    const li=document.createElement("li");
    li.innerHTML='<span class="d">!</span><span>'+t+'</span>';tl.appendChild(li);});
}

function restart(){ans.fill(null);page=0;renderQuiz();show("quiz");}

renderIntro();
$("startBtn").onclick=()=>{renderQuiz();show("quiz");};
$("nextBtn").onclick=next;
$("backBtn").onclick=back;
$("againBtn").onclick=restart;
$("printBtn").onclick=()=>window.print();
"""

BODY = """
<div class="shell">
<section id="intro" class="card">
  <div class="eyebrow">45項目・3分</div>
  <h1>提案書・営業資料が<br>通らない理由を切り分けます</h1>
  <p class="lead">出来上がった資料を横に置いて、45項目に答えてください。3つの軸のどこで落ちているかが点数で出ます。最後に「今日直すところ」の一覧が出ます。</p>
  <div class="axisrow" id="axisrow"></div>
  <button class="primary" id="startBtn">はじめる</button>
  <p class="note">この診断は建設コンサルタントとして15年、公共案件の技術提案書を作成してきた経験から項目を起こしています。通信は行いません。入力した内容はこの端末の外に出ません。</p>
</section>

<section id="quiz" class="card hidden">
  <div class="top">
    <button class="back" id="backBtn">← 戻る</button>
    <span class="step" id="stepNo"></span>
  </div>
  <div class="bar" id="bar"></div>
  <h2 id="axisName"></h2>
  <p class="axisdesc" id="axisDesc"></p>
  <div id="list"></div>
  <button class="primary" id="nextBtn" style="margin-top:22px">次へ</button>
</section>

<section id="result" class="card hidden">
  <div class="score">
    <div class="big" id="total">0<small>/ 90</small></div>
  </div>
  <div class="band" id="band"></div>
  <p class="bandmsg" id="bandmsg"></p>
  <div id="axbars"></div>

  <div class="sect">
    <h3 id="weakName"></h3>
    <ul id="advice"></ul>
  </div>

  <div class="sect todo">
    <h3>今日直すところ <span class="cnt" id="todoCnt"></span></h3>
    <p class="cnt" style="margin:-4px 0 10px">「できていない」と答えた項目です。上から順に潰してください。</p>
    <ul id="todo"></ul>
  </div>

  <button class="ghost noprint" id="printBtn">この結果を印刷する</button>
  <button class="ghost noprint" id="againBtn">もう一度チェックする</button>
</section>
</div>
"""


def interactive():
    css = CSS.replace("__FONT__", FONT).replace("--body:#46546 8", "--body:#465468")
    js = (JS.replace("__AXES__", json.dumps(AXES, ensure_ascii=False))
            .replace("__ITEMS__", json.dumps(ITEMS, ensure_ascii=False))
            .replace("__BANDS__", json.dumps(BANDS, ensure_ascii=False))
            .replace("__ADVICE__", json.dumps(AXIS_ADVICE, ensure_ascii=False)))
    return ("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n"
            "<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
            "<title>提案書・営業資料チェック45</title>\n"
            f"<style>{css}</style>\n</head>\n<body>\n{BODY}\n"
            f"<script>{js}</script>\n</body>\n</html>\n")


PRINT_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:__FONT__;color:#182438;line-height:1.6;font-size:10.5pt;
  padding:14mm 12mm}
h1{font-size:17pt;margin-bottom:3mm}
.sub{font-size:9pt;color:#6C7C91;margin-bottom:6mm;line-height:1.7}
h2{font-size:12pt;margin:6mm 0 2mm;padding-left:3mm;border-left:4px solid #0070D6}
h2 span{font-size:9pt;color:#6C7C91;font-weight:400;margin-left:4mm}
table{width:100%;border-collapse:collapse;margin-bottom:2mm}
td,th{border:.4pt solid #C8D2E0;padding:1.6mm 2mm;font-size:9.5pt;vertical-align:middle}
th{background:#EEF3F9;font-size:8.5pt;font-weight:700}
td.n{width:8mm;text-align:center;color:#0070D6;font-weight:700}
td.c{width:13mm;text-align:center}
.tot{margin-top:5mm;border:.6pt solid #C8D2E0;border-radius:2mm;padding:3mm 4mm;font-size:9.5pt}
.tot b{font-size:11pt}
.tot .row{display:flex;justify-content:space-between;padding:1mm 0}
.foot{margin-top:5mm;font-size:8.5pt;color:#6C7C91;line-height:1.7}
@page{size:A4;margin:0}
"""


def printable():
    rows = []
    for ai, (name, note, color, desc) in enumerate(AXES):
        rows.append(f'<h2>{html.escape(name)}<span>{html.escape(note)}　15項目・30点</span></h2>')
        rows.append('<table><tr><th></th><th>チェック項目</th>'
                    '<th>できて<br>いる<br>2点</th><th>あいまい<br>1点</th>'
                    '<th>できて<br>いない<br>0点</th></tr>')
        for i, (a, t) in enumerate(ITEMS, 1):
            if a != ai:
                continue
            rows.append(f'<tr><td class="n">{i}</td><td>{html.escape(t)}</td>'
                        '<td class="c">□</td><td class="c">□</td><td class="c">□</td></tr>')
        rows.append('</table>')
    band = "".join(
        f'<div class="row"><span>{lo}点以上</span><span>{html.escape(msg)}</span></div>'
        for lo, msg, _ in BANDS)
    css = PRINT_CSS.replace("__FONT__", FONT)
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>提案書・営業資料チェック45（印刷用）</title>
<style>{css}</style></head><body>
<h1>提案書・営業資料チェック45</h1>
<p class="sub">出来上がった資料を横に置いて、45項目に印を付けてください。軸ごとに合計すると、どこで落ちているかが分かります。<br>
建設コンサルタントとして15年、公共案件の技術提案書を作成してきた経験から項目を起こしています。</p>
{''.join(rows)}
<div class="tot">
  <div class="row"><b>合計</b><b>　　　／ 90点</b></div>
  <div class="row"><span>構成　　／30</span><span>情報　　／30</span><span>表現　　／30</span></div>
</div>
<div class="tot">{band}</div>
<p class="foot">いちばん点数の低い軸から手を付けてください。3軸を同時に直そうとすると、表現を整えたあとに構成をやり直すことになり、手戻りが増えます。<br>
0点を付けた項目が、そのまま直すところの一覧になります。</p>
</body></html>
"""


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p1 = os.path.join(OUT, "提案書チェック45.html")
    p2 = os.path.join(OUT, "提案書チェック45_印刷用.html")
    open(p1, "w", encoding="utf-8").write(interactive())
    open(p2, "w", encoding="utf-8").write(printable())
    for p in (p1, p2):
        print(p, os.path.getsize(p) // 1024, "KB")

    # 印刷用をPDFにする。ローカルファイルなので通信は起きない。
    p3 = os.path.join(OUT, "提案書チェック45_印刷用.pdf")
    code = f"""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.goto("file://{p2}")
        await pg.pdf(path="{p3}", format="A4", print_background=True)
        await b.close()
asyncio.run(main())
"""
    subprocess.run(["python3", "-c", code], check=True)
    print(p3, os.path.getsize(p3) // 1024, "KB")
