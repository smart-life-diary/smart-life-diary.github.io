"""Instagram リール用の縦型動画（1080×1920 / mp4）を書き出す。

デモをヘッドレスChromiumで操作しながら録画し、ffmpeg でテロップを焼き込む。
ページ全体に zoom をかけて等倍で録るため、拡大による劣化がない。
"""
import os, shutil, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(HERE, "reelwork")
OUT = os.path.join(HERE, "..", "..", "reels")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"

W, H = 1080, 1920
VW, VH = 1080, 1420   # 録画サイズ。上下に帯を足して 1080×1920 に仕上げる
PAD_TOP = 300         # 上の帯。ここにテロップを置くので本文と絶対に重ならない
ZOOM = 2.2            # 1080 / 2.2 ≒ 491 CSS px
BAR = "0x0E1424"      # 帯の色

# リールの定義。テロップは (開始秒, 終了秒, 位置, テキスト)
REELS = [
    {
        "slug": "isekai",
        "name": "reel1-isekai",
        "telops": [
            (0.2, 3.2, "top",    "7問に答えるだけで\n異世界の職業が決まる診断"),
            (4.0, 8.5, "top",    "選ぶだけ。30秒で終わります"),
            (12.0, 16.0, "top",  "全12タイプ\nレーダーチャートまで出ます"),
            (17.0, 21.0, "mid",  "プロフィールのリンクから\n遊べます"),
        ],
    },
    {
        "slug": "shachiku",
        "name": "reel2-shachiku",
        "telops": [
            (0.2, 3.2, "top",    "休日でも通知でビクッとする人\n見てください"),
            (4.0, 8.5, "top",    "隠れ社畜度を7問で測ります"),
            (12.0, 16.0, "top",  "パーセントで出ます\nあなたは何点でしょうか"),
            (17.0, 21.5, "mid",  "プロフィールのリンクから\n測れます"),
        ],
    },
    {
        "slug": "side-biz",
        "name": "reel3-sidebiz",
        "telops": [
            (0.2, 3.2, "top",    "集客の入口に\n診断を置くと変わります"),
            (4.0, 8.5, "top",    "売り込まずに\n相手が自分で気づく"),
            (12.0, 16.0, "top",  "結果画面から\n予約やLINE登録へ導線"),
            (17.0, 21.5, "mid",  "こういう診断を制作しています\n詳細はプロフィールへ"),
        ],
    },
]

POS = {   # (x, y) の式。top は上の帯の中。本文に重ならない
    "top": ("(w-text_w)/2", "(300-text_h)/2 + 20"),
    "mid": ("(w-text_w)/2", "(h-text_h)/2"),
}


def record(slug, name):
    """デモを操作しながら webm で録画する。"""
    from playwright.sync_api import sync_playwright
    d = os.path.join(WORK, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx = b.new_context(
            viewport={"width": VW, "height": VH},
            record_video_dir=d,
            record_video_size={"width": VW, "height": VH},
        )
        pg = ctx.new_page()
        pg.goto(f"file://{SITE}/{slug}.html")
        # zoom を掛けると 100dvh が実寸より大きく計算され、中央寄せのページで
        # カードが画面外へ押し出される。min-height を無効化して上寄せに固定する。
        pg.add_style_tag(content=(
            f"html{{zoom:{ZOOM}}}"
            "html,body{min-height:0!important}"
            "body{align-items:flex-start!important;padding-top:24px!important}"
        ))
        pg.wait_for_timeout(3400)                       # スタート画面を見せる

        # 開始ボタン
        for sel in ["button.start", "button.big-btn", "button"]:
            el = pg.query_selector(sel)
            if el and el.is_visible():
                el.click()
                break
        pg.wait_for_timeout(900)

        # 1問ずつ、読める速さで回答する
        for i in range(30):
            if pg.query_selector(".result:not([style*='display: none'])") and \
               pg.is_visible("#result"):
                break
            opts = [o for o in pg.query_selector_all(".opt, .opts > *") if o.is_visible()]
            if not opts:
                break
            opts[i % len(opts)].click()
            pg.wait_for_timeout(1050)
        pg.wait_for_timeout(1800)                       # 結果の演出を見せる

        # 結果をゆっくりスクロールして全体を見せる
        pg.evaluate("""async () => {
          const end = document.body.scrollHeight - innerHeight;
          const steps = 90;
          for (let i = 0; i <= steps; i++) {
            window.scrollTo(0, end * i / steps);
            await new Promise(r => setTimeout(r, 42));
          }
        }""")
        pg.wait_for_timeout(900)
        pg.evaluate("() => window.scrollTo({top:0, behavior:'smooth'})")
        pg.wait_for_timeout(2600)

        path = pg.video.path()
        ctx.close()
        b.close()
    return path


def find_lead(src):
    """Playwright の録画はページ描画前から始まる。空白が続く先頭の秒数を返す。"""
    w, h, fps = 96, 126, 4
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", src,
         "-vf", f"fps={fps},scale={w}:{h}", "-pix_fmt", "rgb24",
         "-f", "rawvideo", "-"],
        capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    frames = np.frombuffer(raw[:n * w * h * 3], dtype=np.uint8).reshape(n, h, w, 3)
    for i, f in enumerate(frames):
        body = f[int(h * 0.2):int(h * 0.9)]
        if (body > 245).all(axis=2).mean() < 0.98:      # 真っ白でなくなった時点
            return max(0.0, i / fps - 0.3)
    return 0.0


def burn(src, name, telops):
    """テロップを焼き込んで mp4 にする。"""
    os.makedirs(OUT, exist_ok=True)
    txtdir = os.path.join(WORK, name + "-txt")
    os.makedirs(txtdir, exist_ok=True)

    # 上下に帯を足して 9:16 にする。テロップは上の帯に置く
    filters = [f"pad={W}:{H}:0:{PAD_TOP}:color={BAR}"]
    for i, (t0, t1, pos, text) in enumerate(telops):
        tf = os.path.join(txtdir, f"{i}.txt")
        with open(tf, "w") as f:
            f.write(text)
        x, y = POS[pos]
        filters.append(
            f"drawtext=fontfile={FONT}:textfile={tf}"
            f":fontsize=56:fontcolor=white:line_spacing=16"
            + (":box=1:boxcolor=black@0.66:boxborderw=28" if pos == "mid" else "")
            + (
            f":x={x}:y={y}:enable='between(t\\,{t0}\\,{t1})'")
        )
    vf = ",".join(filters) if filters else "null"

    lead = find_lead(src)
    dur = max(t1 for t0, t1, *_ in telops) + 0.6
    dst = os.path.join(OUT, name + ".mp4")
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{lead:.2f}", "-t", f"{dur:.2f}",
        "-i", src,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "96k", "-shortest",
        "-movflags", "+faststart",
        dst,
    ]
    subprocess.run(cmd, check=True)
    return dst, lead


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    for r in REELS:
        src = record(r["slug"], r["name"])
        dst, lead = burn(src, r["name"], r["telops"])
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", dst],
            capture_output=True, text=True).stdout.strip()
        print(f"{dst}  {float(dur):.1f}s  {os.path.getsize(dst)//1024}KB  "
              f"（先頭{lead:.1f}sの空白を除去）")
