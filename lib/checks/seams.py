"""場景接縫檢查（v4，2026-11-08）：前一場的最後一格，要和下一場的第一格一樣。

v4 整支片是同一張大圖、鏡頭跟著走，場景之間不能有跳動。肉眼看縮圖抓不到小跳動，所以用程式比對
（cth9191/animate 的 framehash 做法）。

用法：uv run python lib/checks/seams.py <影片 ID> [-q l|h]
比對方式：兩格縮成 64×36 灰階，算 16×9 區塊的平均差。最大區塊差 > 6（0–255）就報錯，
同時寫出並排圖 out/<id>/seams/<前>-<後>.png 方便看哪裡跳。

接縫空檔（2026-11-08 使用者：「轉場的時候會卡住定格幾秒」）：前一場最後一個動作結束，到下一場第一個動作開始，
畫面完全不動的時間＝前一場 tail＋下一場 head（kit 寫在 out/<id>/idle-<場>.json）。
要落在 style.json layout.seam_idle 的範圍（預設 0.8～1.6 秒）：太長像當機，太短上一段來不及看（v2 的回饋）。
修法：前一場最後一個動作晚一點、下一場的鏡頭移動從第 0.1 秒就開始；script.json 的 pad 與最後一句 hold 不要太長。
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, STYLE, ffmpeg, video_dir  # noqa: E402

RES = {"l": "480p30", "h": "1080p30"}
LIMIT = 6.0


def frame(mp4, last, out):
    args = [ffmpeg(), "-v", "error", "-y"]
    args += ["-sseof", "-0.2", "-i", str(mp4), "-update", "1"] if last else ["-i", str(mp4), "-frames:v", "1"]
    subprocess.run(args + [str(out)], check=True)
    return Image.open(out).convert("L")


def main():
    vid = sys.argv[1]
    q = sys.argv[sys.argv.index("-q") + 1] if "-q" in sys.argv else "l"
    tl = json.loads((video_dir(vid) / "timeline.json").read_text())
    od = ROOT / "out" / vid
    sd = od / "seams"
    sd.mkdir(parents=True, exist_ok=True)
    ids = [s["id"] for s in tl["scenes"]]
    bad = []
    for a, b in zip(ids, ids[1:]):
        fa = next((od / "media" / a).rglob(f"{RES[q]}/{a}.mp4"), None)
        fb = next((od / "media" / b).rglob(f"{RES[q]}/{b}.mp4"), None)
        if not fa or not fb:
            print(f"{a}→{b}：找不到渲染檔，略過")
            continue
        ia = frame(fa, True, sd / f"{a}-last.png")
        ib = frame(fb, False, sd / f"{b}-first.png")
        A = np.asarray(ia.resize((64, 36)), float)
        B = np.asarray(ib.resize((64, 36)), float)
        blocks = np.abs(A - B).reshape(9, 4, 16, 4).mean(axis=(1, 3))
        worst = blocks.max()
        ok = worst <= LIMIT
        print(f"{a}→{b}：最大區塊差 {worst:.1f}，平均 {blocks.mean():.2f} {'✓' if ok else '✗ 接縫有跳動'}")
        if not ok:
            bad.append(f"{a}→{b}")
            w, h = ia.size
            pair = Image.new("L", (w * 2 + 10, h))
            pair.paste(ia, (0, 0))
            pair.paste(ib, (w + 10, 0))
            pair.save(sd / f"{a}-{b}.png")
    lo, hi = STYLE.get("layout", {}).get("seam_idle", [0.8, 1.6])
    for a, b in zip(ids, ids[1:]):
        fa, fb = od / f"idle-{a}.json", od / f"idle-{b}.json"
        if not fa.exists() or not fb.exists():
            print(f"{a}→{b}：沒有 idle 紀錄（重新渲染後才有），略過空檔檢查")
            continue
        ta, hb = json.loads(fa.read_text())["tail"], json.loads(fb.read_text())["head"]
        gap = ta + hb
        ok = lo <= gap <= hi
        print(f"{a}→{b}：接縫空檔 {gap:.2f}s（前一場收尾停 {ta:.2f}s＋下一場 {hb:.2f}s 才動） {'✓' if ok else '✗ ' + ('停格太久' if gap > hi else '轉得太快')}")
        if not ok:
            bad.append(f"{a}→{b} 空檔 {gap:.2f}s")
    (od / "seams.txt").write_text("\n".join(bad) or "OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
