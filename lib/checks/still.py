"""找畫面幾乎不動的段落（≥ 4 秒）。PoC 經驗：超過 4 秒不動就補小動作；細線或小字在動時可能誤報，要看清楚。

用法：uv run python lib/checks/still.py <影片 ID>（讀 out/<id>/video.mp4；片尾畫面時段不算）
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ffmpeg, load_timeline, out_dir  # noqa: E402

vid = sys.argv[1]
T = load_timeline(vid)
W, H, FPS, MIN = 160, 90, 4, 4.0
raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(out_dir(vid) / "video.mp4"), "-vf", f"fps={FPS},scale={W}:{H},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
still = d < 0.35
limit = T["duration"] - T.get("end_screen", 0)


def where(t):
    for sc in T["scenes"]:
        if sc["start"] <= t < sc["start"] + sc["duration"]:
            for s in sc["sentences"]:
                if s["abs"] <= t < s["abs"] + (s["end"] - s["start"]) + 1.0:
                    return f"{sc['id']}/{s['id']}"
            return sc["id"]


runs, i, tot = [], 0, 0.0
while i < len(still):
    if still[i]:
        j = i
        while j < len(still) and still[j]:
            j += 1
        dur = (j - i) / FPS
        if dur >= MIN and i / FPS < limit:
            runs.append((i / FPS, dur))
            tot += dur
        i = j
    else:
        i += 1
for t, dur in runs:
    print(f"{t:7.1f}s  {dur:4.1f}s  {where(t + 0.5)}")
print(f"{len(runs)} 段靜止 ≥ {MIN}s，共 {tot:.1f}s（正片 {limit:.0f}s 的 {tot / limit:.1%}）")
json.dump({"runs": runs, "total_s": tot, "ratio": tot / limit}, open(out_dir(vid) / "still.json", "w"))
