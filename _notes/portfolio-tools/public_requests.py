# -*- coding: utf-8 -*-
"""ココナラの公開依頼を、カテゴリごとに取ってきて一覧にする。

/requests 配下はサーバー側で描画されているので curl で取れる。
カード1件は c-searchItemWrapper で囲まれていて、その中に
依頼ID・カテゴリ・タイトル・予算・応募者数・募集期限が入っている。

応募者数が拾えるのが大きい。**応募が少ない依頼ほど、読まれる確率が高い。**
"""
import html
import re
import subprocess
import sys

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def fetch(url):
    r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "45", "-L", url],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def txt(frag):
    frag = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", frag)
    t = html.unescape(re.sub(r"(?s)<[^>]+>", "\n", frag))
    out = []
    for x in (y.strip() for y in t.split("\n")):
        if x and (not out or out[-1] != x):
            out.append(x)
    return out


def cards(page):
    """c-searchItemWrapper ごとに切り出して、必要な項目を拾う。"""
    parts = page.split('class="c-searchItemWrapper')
    for p in parts[1:]:
        m = re.search(r'href="/requests/(\d+)"', p)
        if not m:
            continue
        rid = m.group(1)
        cat = re.search(r'href="/requests/categories/\d+"[^>]*>\s*([^<]{1,40}?)\s*<', p)
        L = txt(p[:14000])
        # タイトルはカテゴリ名の次に来る
        title = ""
        if cat:
            cname = html.unescape(cat.group(1)).strip()
            for i, x in enumerate(L):
                if x == cname and i + 1 < len(L):
                    title = L[i + 1]
                    break
        else:
            cname = ""
        def after(word, n=1):
            for i, x in enumerate(L):
                if x == word and i + n < len(L):
                    return L[i + n]
            return ""
        # 予算は「見積り希望」か「5千円未満」のように分かれて出る
        bud = ""
        for i, x in enumerate(L):
            if x == "予算":
                bud = " ".join(L[i + 1:i + 4]).replace(" 応募者数", "")
                break
        prop = after("応募者数")
        days = after("あと")
        yield dict(id=rid, cat=cname, title=title,
                   budget=re.sub(r"\s+", "", bud)[:18],
                   proposals=prop if prop.isdigit() else "?",
                   days=days if days.isdigit() else "?")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        url = (f"https://coconala.com/requests/categories/{arg}"
               if arg.isdigit() else arg)
        page = fetch(url)
        tot = re.search(r'c-searchHeader_resultHits[^>]*>([\d,]+)<', page)
        rows = list(cards(page))
        print(f"\n===== {url}   総件数 {tot.group(1) if tot else '?'}   取得 {len(rows)}件")
        for r in rows:
            print(f"  応募{r['proposals']:>3}  残{r['days']:>2}日  {r['budget']:<14} "
                  f"[{r['cat']}] {r['title'][:52]}")
            print(f"        https://coconala.com/requests/{r['id']}")
