"""ココナラのキーワードごとに、供給（出品数）と需要（評価件数の積み上げ）を数える。

需要の代理指標として、検索上位に並ぶ出品の「評価件数」の合計を使う。
評価は購入後にしか付かないので、そこに金が動いた回数がそのまま出る。
"""
import re, html, subprocess, urllib.parse, time, json, sys

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")


def fetch(url):
    r = subprocess.run(["curl", "-sS", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def lines(s):
    b = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\\1>", " ", s)
    t = html.unescape(re.sub(r"(?s)<[^>]+>", "\n", b))
    out = []
    for x in (y.strip() for y in t.split("\n")):
        if x and (not out or out[-1] != x):
            out.append(x)
    return out


def total(L):
    """総件数は「1,234」「件中」「1 - 60」「件表示」の並びで出る。"""
    for i, x in enumerate(L):
        if x == "件中" and i and re.fullmatch(r"[\d,]+", L[i - 1]):
            return int(L[i - 1].replace(",", ""))
    return None


def cards(L):
    """出品カードを (価格, 評価件数) で拾う。"""
    i0 = max([k for k, x in enumerate(L) if x == "お気に入り数順"] + [0])
    cur = L[i0 + 1:i0 + 400]
    out, i = [], 0
    while i < len(cur) - 6:
        if cur[i].endswith("ます") and 8 < len(cur[i]) < 45:
            seg = cur[i:i + 13]
            price = next((seg[j] for j in range(len(seg) - 1) if seg[j + 1] == "円"), None)
            rat = next((seg[j + 1] for j in range(len(seg) - 1)
                        if re.fullmatch(r"[45]\.\d", seg[j]) and seg[j + 1].startswith("(")), None)
            n = int(re.sub(r"[^\d]", "", rat)) if rat else 0
            p = int(price.replace(",", "")) if price and price.replace(",", "").isdigit() else None
            out.append((cur[i], p, n))
            i += 5
        else:
            i += 1
    return out


KEYWORDS = json.load(open(sys.argv[1]))
res = []
for kw in KEYWORDS:
    q = urllib.parse.quote(kw)
    L = lines(fetch(f"https://coconala.com/search?keyword={q}"))
    tot = total(L)
    cs = cards(L)
    req = None   # 公開依頼の件数はOR検索らしく桁が合わないため使わない
    rats = [n for _, _, n in cs]
    prices = [p for _, p, _ in cs if p]
    res.append(dict(kw=kw, supply=tot, req=req, cards=len(cs),
                    rat_sum=sum(rats), rat_max=max(rats) if rats else 0,
                    rat_med=sorted(rats)[len(rats)//2] if rats else 0,
                    price_med=sorted(prices)[len(prices)//2] if prices else None))
    print(f"{kw:<24} 出品{str(tot):>7}  評価中央{res[-1]['rat_med']:>4}  "
          f"最大{res[-1]['rat_max']:>5}  価格中央{res[-1]['price_med']}")
    time.sleep(1.2)
json.dump(res, open("kw_result.json", "w"), ensure_ascii=False, indent=1)
