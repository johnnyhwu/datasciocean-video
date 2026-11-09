"""整片逐秒縮圖（2026-11-10 最後一輪優化時建立）：每秒取一格，跳過和上一張幾乎一樣的，3×3 拼成一張，
每格標「秒數 場景/句子@比例」。給 Claude 做整片回顧用（sheet.py 只看句尾，看不到動畫進行中的樣子）。

用法：uv run python lib/checks/filmstrip.py <影片 ID> [-q l|h] [--from 秒] [--to 秒] [--step 1]
輸出：out/<id>/filmstrip/sNN.png（每次執行先清空）。字幕區（下方 20%）畫一條洋紅線；標籤放在字幕區，不擋畫面。
順序建議：先跑 frames.py（程式抓得到的先修），再用這個逐張看（版面、讀起來會不會誤會、鏡頭落點）。
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, ffmpeg, load_timeline, out_dir  # noqa: E402
from checks.frames import source, where  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("vid")
ap.add_argument("-q", default="h", choices=["l", "h"])
ap.add_argument("--from", dest="t0", type=float, default=0.0)
ap.add_argument("--to", dest="t1", type=float, default=None)
ap.add_argument("--step", type=float, default=1.0)
a = ap.parse_args()
T = load_timeline(a.vid)
t1 = a.t1 if a.t1 is not None else T["duration"]
W, H = 640, 360
out = out_dir(a.vid) / "filmstrip"
out.mkdir(exist_ok=True)
for p in out.glob("*.png"):
    p.unlink()
font_p = ROOT / "assets/fonts"
font = next((ImageFont.truetype(str(f), 18) for f in sorted(font_p.glob("*.otf")) + sorted(font_p.glob("*.ttf"))), ImageFont.load_default())
FPS = 30
n0, n1, sn = round((a.t0 + a.step / 2) * FPS), round(t1 * FPS), max(1, round(a.step * FPS))
with tempfile.TemporaryDirectory() as d:
    # 用格號取樣（select），標的秒數才準；fps 濾鏡加 -ss 會挑到前後的格子
    subprocess.run([ffmpeg(), "-v", "error", *source(a.vid, a.q), "-vf",
                    f"select='gte(n\\,{n0})*lte(n\\,{n1})*not(mod(n-{n0}\\,{sn}))',scale={W}:{H}:flags=area",
                    "-fps_mode", "vfr", f"{d}/f%05d.png"], check=True)
    files = sorted(Path(d).glob("f*.png"))
    kept, last = [], None
    for k, f in enumerate(files):
        t = (n0 + k * sn) / FPS
        im = Image.open(f).convert("RGB")
        small = np.asarray(im.convert("L").resize((160, 90)), float)
        if last is not None and np.abs(small - last).mean() < 0.25:
            continue
        kept.append((t, im))
        last = small
n = 0
for i in range(0, len(kept), 9):
    sheet = Image.new("RGB", (3 * W + 8, 3 * H + 8), (90, 90, 90))
    for j, (t, im) in enumerate(kept[i:i + 9]):
        dr = ImageDraw.Draw(im)
        dr.line([(0, int(.80 * H)), (W, int(.80 * H))], fill=(120, 40, 120), width=1)
        dr.rectangle([0, H - 26, 330, H], fill=(0, 0, 0))
        dr.text((4, H - 24), f"{t:6.1f}s {where(T, t)}", fill=(255, 120, 255), font=font)
        sheet.paste(im, ((j % 3) * (W + 4), (j // 3) * (H + 4)))
    n += 1
    sheet.save(out / f"s{n:02d}.png")
print(f"{len(kept)} 格（去掉重複）→ {n} 張：{out}")
