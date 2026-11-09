"""逐格檢查整支影片（2026-11-10 最後一輪優化時建立）。縮圖表只看得到句尾的畫面，動畫進行中的問題要逐格掃才抓得到。

用法：uv run python lib/checks/frames.py <影片 ID> [-q l|h]
  -q h（預設）：讀 out/<id>/video.mp4（1080p 串接檔）；-q l：直接讀各場的 480p 檔依序接起來（改動中的檢查迴圈用）。幾秒就跑完。

檢查三件事（每格縮成 192×108 灰階，切成 16×9 個區塊）：
1. 跳出／閃爍：某個區塊只在一格之內大變、前後兩格都靜止＝沒有動畫就出現或消失的東西。
   v001 抓到的例子：self.add() 直接加進來的長條；對 Live／always_redraw 物件做 FadeIn／FadeOut／GrowFromEdge
   （複本也帶著 updater，每格被重畫回原樣，動畫沒有效果，結束時才一次跳掉）；點沿路徑走完後 self.remove()。
   ✗＝明顯（區塊差 > 15 或同時 ≥ 3 個區塊）；△＝小（即時讀數換數字也會出現在這裡，看一下是不是）。
2. 空畫面：整格幾乎只有背景超過 0.3 秒（鏡頭移到還沒畫東西的地方）。修法：鏡頭移動的同一個 at() 裡就開始畫。
3. 靜止：沒有任何區塊在變的段落 ≥ 4 秒。比 still.py（整體平均）敏感：寫出一個小數字也算有動。
片尾畫面時段不檢查。結果寫到 out/<id>/frames.json；有 ✗ 或空畫面就回傳 1。
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ffmpeg, load_timeline, out_dir  # noqa: E402

W, H, BS = 192, 108, 12            # 16×9 個 12px 區塊
FPS = 30
POP_HI, POP_QUIET, POP_SEVERE = 6.0, 0.8, 15.0
MOVE = 1.0                          # 任一區塊平均差超過這個值＝這一格有東西在動
EMPTY_FRAC, EMPTY_MIN = 0.002, 0.3  # 和背景不同的像素 < 0.2% 就算空畫面；連續 0.3 秒以上才報
STILL_MIN = 4.0


def where(T, t):
    for sc in T["scenes"]:
        if sc["start"] <= t < sc["start"] + sc["duration"]:
            best = None
            for s in sc["sentences"]:
                if s["abs"] <= t:
                    best = s
            if best is None:
                return f"{sc['id']}/開頭"
            dur = max(best["end"] - best["start"], 1e-6)
            return f"{sc['id']}/{best['id']}@{(t - best['abs']) / dur:.2f}"
    return "片尾"


def source(vid, q):
    """回傳 ffmpeg 的輸入參數：1080p 串接檔，或 480p 各場檔的 concat 清單。"""
    od = out_dir(vid)
    if q == "h":
        return ["-i", str(od / "video.mp4")]
    T = load_timeline(vid)
    clips = []
    for s in T["scenes"]:
        m = sorted((od / "media" / s["id"]).rglob(f"480p30/{s['id']}.mp4"))
        if not m:
            sys.exit(f"還沒有 {s['id']} 的 480p 檔")
        clips.append(m[0])
    lst = od / "concat-l.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    return ["-f", "concat", "-safe", "0", "-i", str(lst)]


def main():
    vid = sys.argv[1]
    q = sys.argv[sys.argv.index("-q") + 1] if "-q" in sys.argv else "h"
    T = load_timeline(vid)
    limit = T["duration"] - T.get("end_screen", 0)
    p = subprocess.Popen([ffmpeg(), "-v", "error", *source(vid, q), "-vf",
                          f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    size = W * H
    prev, bg = None, None
    D, G, E = [], [], []                 # 每格的區塊差、最大區塊差、非背景比例
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.int16)
        if bg is None:
            bg = int(np.median(f))       # 平面底色（v4 預設 flat）
        E.append(float((np.abs(f - bg) > 12).mean()))
        if prev is not None:
            b = np.abs(f - prev).astype(np.float32).reshape(H // BS, BS, W // BS, BS).mean(axis=(1, 3))
            D.append(b)
            G.append(float(b.max()))
        prev = f
    p.wait()
    D = np.stack(D)                      # D[i]：第 i 格 → 第 i+1 格
    n = len(D)
    pops = []
    for i in range(2, n - 2):
        if (i + 1) / FPS >= limit:
            break
        m = D[i]
        quiet = (D[i - 1] < POP_QUIET) & (D[i + 1] < POP_QUIET) & (D[i - 2] < POP_QUIET) & (D[i + 2] < POP_QUIET)
        hit = (m > POP_HI) & quiet
        if hit.any():
            mx, k = float(m[hit].max()), int(hit.sum())
            pops.append({"t": round((i + 1) / FPS, 2), "max": round(mx, 1), "blocks": k,
                         "severe": mx > POP_SEVERE or k >= 3, "at": where(T, (i + 1) / FPS)})
    # 連續好幾格都有「跳出」＝快速移動的光點或框（ShowPassingFlash、Circumscribe），不是跳出：整串拿掉
    keep, run = [], []
    for x in pops + [None]:
        if x is not None and run and x["t"] - run[-1]["t"] <= 2.5 / FPS:
            run.append(x)
            continue
        if run and len(run) < 3:
            keep += run
        run = [x] if x is not None else []
    pops = keep
    # 空畫面
    empties, i = [], 0
    end = int(limit * FPS)                # 片尾畫面時段不算（最後一場淡出後本來就是空的）
    while i < len(E):
        if E[i] < EMPTY_FRAC and i < end:
            j = i
            while j < min(len(E), end) and E[j] < EMPTY_FRAC:
                j += 1
            if (j - i) / FPS >= EMPTY_MIN:
                empties.append({"t": round(i / FPS, 2), "dur": round((j - i) / FPS, 2), "at": where(T, i / FPS)})
            i = j
        else:
            i += 1
    # 靜止
    stills, i, tot = [], 0, 0.0
    moving = np.array(G) > MOVE
    while i < n:
        if not moving[i] and i / FPS < limit:
            j = i
            while j < n and not moving[j] and j / FPS < limit:
                j += 1
            dur = (j - i) / FPS
            if dur >= STILL_MIN:
                stills.append({"t": round(i / FPS, 2), "dur": round(dur, 2), "at": where(T, i / FPS + .5)})
                tot += dur
            i = j
        else:
            i += 1
    for x in pops:
        print(f"{'✗' if x['severe'] else '△'} 跳出 {x['t']:7.2f}s  區塊差 {x['max']:5.1f} × {x['blocks']}  {x['at']}")
    for x in empties:
        print(f"✗ 空畫面 {x['t']:7.2f}s  {x['dur']:.2f}s  {x['at']}")
    for x in stills:
        print(f"  靜止 {x['t']:7.2f}s  {x['dur']:4.1f}s  {x['at']}")
    sev = sum(x["severe"] for x in pops)
    print(f"跳出 {len(pops)}（明顯 {sev}）；空畫面 {len(empties)}；靜止 ≥ {STILL_MIN:.0f}s 共 {len(stills)} 段 {tot:.1f}s"
          f"（正片 {limit:.0f}s 的 {tot / limit:.1%}）")
    json.dump({"pops": pops, "empties": empties, "stills": stills, "still_ratio": tot / limit},
              open(out_dir(vid) / "frames.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(1 if sev or empties else 0)


if __name__ == "__main__":
    main()
