"""デモ5本をスマホ幅で自動操作し、4カット分のスクリーンショットを撮る。"""
import os, sys, json
from playwright.sync_api import sync_playwright

SITE = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) + "/"
OUT = os.path.join(os.path.dirname(__file__), "shots")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

DEMOS = ["isekai", "side-biz", "ai-level", "shachiku", "golf"]

# 可視要素のうち、テキストが一致するものを押す
START_RE = r"(はじめる|始める|スタート|START|診断する|やってみる)"

VIS = """e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
  return r.width>4 && r.height>4 && s.display!=='none' && s.visibility!=='hidden' && +s.opacity>0.05; }"""

FIND_OPTS = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width>4 && r.height>4 && s.display!=='none' && s.visibility!=='hidden' && +s.opacity>0.05; };
  const sels = ['.opts > *', '.options > *', '.chips > *', '.opt', '.choice'];
  const seen = new Set(); const out = [];
  for (const s of sels) document.querySelectorAll(s).forEach(e => {
    if (vis(e) && !seen.has(e)) { seen.add(e); out.push(e); }
  });
  window.__opts = out;
  return out.length;
}"""

RESULT_VISIBLE = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width>4 && r.height>4 && s.display!=='none' && s.visibility!=='hidden' && +s.opacity>0.05; };
  const sels = ['.result', '.res-name', '.res-type', '.level-label', '.rank', '.score', '.verdict-label'];
  return sels.some(s => [...document.querySelectorAll(s)].some(vis));
}"""


CONTENT_BOX = """() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width>4 && r.height>4 && s.display!=='none' && s.visibility!=='hidden' && +s.opacity>0.05
           && r.bottom>0 && r.top < innerHeight; };
  let top=1e9, left=1e9, right=0, bottom=0, found=false;
  document.querySelectorAll('body *').forEach(e => {
    if (!vis(e)) return;
    const r = e.getBoundingClientRect();
    if (r.height > innerHeight * 2) return;      // 全画面ラッパは除外
    found = true;
    top = Math.min(top, r.top); left = Math.min(left, r.left);
    right = Math.max(right, r.right); bottom = Math.max(bottom, r.bottom);
  });
  if (!found) return null;
  const pad = 14;
  top = Math.max(0, top - pad); left = Math.max(0, left - pad);
  right = Math.min(innerWidth, right + pad); bottom = Math.min(innerHeight, bottom + pad);
  return {x: left, y: top, width: right-left, height: bottom-top};
}"""


SHARE_BOX = """() => {
  const sels = ['.share-hint', '.copy-btn', '.again', '.cta', '.promptbox'];
  const els = [];
  sels.forEach(s => document.querySelectorAll(s).forEach(e => {
    const r = e.getBoundingClientRect(); const st = getComputedStyle(e);
    if (r.width>4 && r.height>4 && st.display!=='none' && st.visibility!=='hidden' && +st.opacity>0.05) els.push(e);
  }));
  if (!els.length) return null;
  let top=1e9, left=1e9, right=0, bottom=0;
  els.forEach(e => { const r = e.getBoundingClientRect();
    top=Math.min(top,r.top+scrollY); left=Math.min(left,r.left);
    right=Math.max(right,r.right); bottom=Math.max(bottom,r.bottom+scrollY); });
  const pad = 12;
  const docTop = Math.max(0, top - pad);
  // その領域が画面中央に来るようスクロール位置を決める（縦は400pxで頭打ち）
  const h = Math.min(bottom - top + pad*2, innerHeight);
  const scrollTo = Math.max(0, docTop - (innerHeight - h) / 2);
  return { scrollTo,
           x: Math.max(0, left - pad),
           y: Math.max(0, docTop - scrollY),
           width: Math.min(innerWidth, right - left + pad*2),
           height: h };
}"""


def shoot(pg, name, step):
    path = f"{OUT}/{name}-{step}.png"
    box = pg.evaluate(CONTENT_BOX)
    if box and box["width"] > 100 and box["height"] > 100:
        pg.screenshot(path=path, clip=box)
    else:
        pg.screenshot(path=path)
    return path


def run(pg, name):
    pg.goto(SITE + name + ".html")
    pg.wait_for_timeout(600)
    log = {"name": name, "steps": {}}

    # ① スタート画面
    log["steps"]["1-start"] = shoot(pg, name, "1-start")

    # スタートボタンを押す
    clicked = False
    for sel in ["button", ".start", ".big-btn", ".cta", ".primary", "[onclick]"]:
        for el in pg.query_selector_all(sel):
            try:
                if el.is_visible() and el.inner_text().strip():
                    import re
                    if re.search(START_RE, el.inner_text()):
                        el.click()
                        clicked = True
                        break
            except Exception:
                pass
        if clicked:
            break
    pg.wait_for_timeout(700)

    # ② 設問画面（1問目）
    n = pg.evaluate(FIND_OPTS)
    log["opts_first"] = n
    log["steps"]["2-question"] = shoot(pg, name, "2-question")

    # 最後まで回答する
    for i in range(30):
        if pg.evaluate(RESULT_VISIBLE):
            break
        n = pg.evaluate(FIND_OPTS)
        if not n:
            break
        try:
            pg.evaluate("() => window.__opts[0].click()")
        except Exception:
            break
        pg.wait_for_timeout(450)
    log["answered_rounds"] = i
    log["reached_result"] = pg.evaluate(RESULT_VISIBLE)
    pg.wait_for_timeout(900)

    # ③ 結果画面（上部）
    pg.evaluate("() => window.scrollTo(0,0)")
    pg.wait_for_timeout(300)
    log["steps"]["3-result"] = shoot(pg, name, "3-result")

    # ④ シェア導線のクローズアップ
    box = pg.evaluate(SHARE_BOX)
    path = f"{OUT}/{name}-4-share.png"
    if box:
        pg.evaluate("y => window.scrollTo(0, y)", box["scrollTo"])
        pg.wait_for_timeout(400)
        box2 = pg.evaluate(SHARE_BOX)
        if box2 and box2["width"] > 100 and box2["height"] > 60:
            pg.screenshot(path=path, clip={k: box2[k] for k in ("x", "y", "width", "height")})
            log["steps"]["4-share"] = path
            log["share_found"] = True
            return log
    # 見つからなければ結果下部にフォールバック
    pg.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    pg.wait_for_timeout(500)
    log["steps"]["4-share"] = shoot(pg, name, "4-share")
    log["share_found"] = False
    return log


os.makedirs(OUT, exist_ok=True)
results = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    for name in DEMOS:
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        try:
            results.append(run(pg, name))
        except Exception as e:
            results.append({"name": name, "error": str(e)})
        pg.close()
    b.close()

print(json.dumps(results, ensure_ascii=False, indent=1))
