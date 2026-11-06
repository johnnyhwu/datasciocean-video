"""渲染：每個場景各自渲染（平行、各用自己的 media 資料夾，避免文字快取互搶），再無損串接成 out/<id>/video.mp4。

用法：uv run python lib/render.py <影片 ID> [-q l|h] [--scenes sc03,sc05] [-j 4]

- 場景類別寫在 videos/<id>/scenes*.py，類別名＝場景 ID 首字大寫（sc01 → Sc01）。
- -q l：480p30，檢查用；-q h：1080p30，成片用。只重渲改過的場景：--scenes。
- 渲完印出每場的版面檢查（out/<id>/layout-<場>.txt）。同一場渲染失敗 3 次就停下回報（規格 §4.3）。
- 串接只在所有場景都有 1080p 檔時做（-q h）。格數必須等於 timeline 的 frames。
"""
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import ROOT, ffmpeg, load_timeline, out_dir, video_dir  # noqa: E402

RES = {"l": "480p30", "h": "1080p30"}


def find_file(vid, cls):
    for f in sorted(video_dir(vid).glob("scenes*.py")):
        if re.search(rf"^class {cls}\(", f.read_text(), re.M):
            return f
    raise SystemExit(f"找不到場景類別 {cls}（videos/{vid}/scenes*.py）")


def render_one(vid, sid, q):
    cls = sid[0].upper() + sid[1:]
    f = find_file(vid, cls)
    od = out_dir(vid)
    media = od / "media" / sid
    env = {**os.environ, "YTV_VIDEO": vid, "PYTHONPATH": str(ROOT / "lib")}
    log = od / f"log-{sid}-{q}.txt"
    for k in range(3):
        r = subprocess.run([sys.executable, "-m", "manim", f"-q{q}", "--fps", "30", "--disable_caching",
                            "--media_dir", str(media), "-o", sid, str(f), cls],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        log.write_text(r.stdout + "\n" + r.stderr)
        if r.returncode == 0:
            mp4 = next(media.rglob(f"{RES[q]}/{sid}.mp4"))
            return sid, mp4, None
    tail = "\n".join(r.stderr.strip().splitlines()[-12:])
    return sid, None, f"渲染失敗 3 次：{log}\n{tail}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid")
    ap.add_argument("-q", default="l", choices=["l", "h"])
    ap.add_argument("--scenes", default="")
    ap.add_argument("-j", type=int, default=4)
    a = ap.parse_args()
    T = load_timeline(a.vid)
    sids = [s for s in a.scenes.split(",") if s] or [s["id"] for s in T["scenes"]]
    with ThreadPoolExecutor(a.j) as ex:
        res = list(ex.map(lambda s: render_one(a.vid, s, a.q), sids))
    od = out_dir(a.vid)
    fails = [(s, e) for s, m, e in res if e]
    for s in sids:
        p = od / f"layout-{s}.txt"
        print(f"{s}: {p.read_text().strip() if p.exists() else '(沒有版面紀錄)'}")
    if fails:
        for s, e in fails:
            print(f"\n✗ {s}: {e}")
        sys.exit(1)
    if a.q == "h":
        clips = []
        for s in [x["id"] for x in T["scenes"]]:
            m = list((od / "media" / s).rglob(f"1080p30/{s}.mp4"))
            if not m:
                print(f"還沒有 {s} 的 1080p 檔，先不串接")
                return
            clips.append(m[0])
        lst = od / "concat.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        r = subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(od / "video.mp4")])
        if r.returncode:
            sys.exit("串接失敗")
        r = subprocess.run([ffmpeg(), "-i", str(od / "video.mp4"), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"], capture_output=True, text=True)
        frames = int(re.findall(r"frame=\s*(\d+)", r.stderr)[-1])
        print(f"video.mp4：{frames} 格（timeline {T['frames']}）{'✓' if frames == T['frames'] else '✗ 不一致'}")


if __name__ == "__main__":
    main()
