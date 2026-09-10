# -*- coding: utf-8 -*-
"""ココナラ コンテンツマーケットを、カテゴリ／キーワードごとに測る。

一覧はJavaScriptで描画されるうえ、この環境からはブラウザで開けない。
ページが叩いているGraphQL（apiprxy.coconala.com）を直接呼ぶ。

コンテンツ出品には販売件数が出ないので、需要の代理指標は**お気に入り数**。
無料で押せる分だけ販売より軽い指標だが、「見て、欲しいと思った人の数」は拾える。
供給は totalCount（その条件の出品総数）。
"""
import json
import re
import subprocess
import sys
import time

API = "https://apiprxy.coconala.com/graphql"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

Q_SEARCH = ("query S($filter: ContentsMarketSearchPublicContentsFilter!)"
            "{r: contentsMarketSearchPublicContents(filter:$filter)"
            "{contents{title price favoriteCount kind category{name parent{name}}}"
            " paginationInfo{totalCount}}}")

Q_CATS = ("query C($filter: ContentsMarketCategoriesSearchFilter!)"
          "{contentsMarketCategories(filter:$filter)"
          "{databaseId name parentId children{databaseId name}}}")


def gql(query, variables):
    body = json.dumps({"query": query, "variables": variables})
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "45", "-X", "POST", API,
         "-H", "Content-Type: application/json",
         "-H", "Origin: https://coconala.com",
         "-H", "Referer: https://coconala.com/contents_market/",
         "-A", UA, "--data-binary", "@-"],
        input=body.encode(), capture_output=True)
    try:
        d = json.loads(r.stdout.decode("utf-8", "replace"))
    except Exception:
        return None
    if "errors" in d:
        print("  GQL ERR", d["errors"][0]["message"][:120])
        return None
    return d.get("data")


def med(xs):
    return sorted(xs)[len(xs) // 2] if xs else None


def probe(**flt):
    """1条件を測る。上位40件の価格とお気に入り数を返す。"""
    flt.setdefault("limit", 40)
    flt.setdefault("page", 1)
    d = gql(Q_SEARCH, {"filter": flt})
    if not d:
        return None
    r = d["r"]
    cs = r["contents"]
    fav = [c["favoriteCount"] for c in cs]
    pr = [c["price"] for c in cs if c["price"]]
    return dict(total=r["paginationInfo"]["totalCount"], n=len(cs),
                fav_sum=sum(fav), fav_max=max(fav) if fav else 0, fav_med=med(fav),
                price_med=med(pr), price_max=max(pr) if pr else None,
                top=[(c["title"][:38], c["price"], c["favoriteCount"]) for c in cs[:5]])


def line(label, r):
    if not r:
        return f"{label:<26} —"
    return (f"{label:<26} 出品{r['total']:>6}  価格中央{str(r['price_med']):>7}  "
            f"★合計{r['fav_sum']:>6} 最大{r['fav_max']:>5} 中央{str(r['fav_med']):>4}")


if __name__ == "__main__":
    mode = sys.argv[1]
    out = []
    if mode == "cats":
        d = gql(Q_CATS, {"filter": {}})
        tree = [p for p in d["contentsMarketCategories"] if p["parentId"] is None]
        for p in tree:
            for c in p["children"]:
                r = probe(categoryIds=[c["databaseId"]])
                print(line(f"{p['name']} > {c['name']}", r))
                out.append(dict(parent=p["name"], name=c["name"],
                                id=c["databaseId"], **(r or {})))
                time.sleep(0.3)
    else:
        for kw in json.load(open(sys.argv[2])):
            r = probe(keyword=kw)
            print(line(kw, r))
            out.append(dict(kw=kw, **(r or {})))
            time.sleep(0.3)
    json.dump(out, open(sys.argv[-1], "w"), ensure_ascii=False, indent=1)
