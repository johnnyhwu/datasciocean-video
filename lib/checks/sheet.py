"""縮圖表：每句旁白結束後 0.25 秒的畫面拼成一張（4 欄），洋紅框是字幕區。給視覺檢查員或使用者看。

用法：uv run python lib/checks/sheet.py <影片 ID> <場景 ID> [-q l|h]   → out/<id>/sheets/<場景>.png
規則：每場只送這一張低解析度圖給視覺檢查員（規格 §6.4、§10）。程式的版面檢查先過了才送。
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import STYLE, ffmpeg, load_timeline, out_dir  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("vid")
ap.add_argument("sid")
ap.add_argument("-q", default="l")
a = ap.parse_args()
T = load_timeline(a.vid)
sc = next(s for s in T["scenes"] if s["id"] == a.sid)
od = out_dir(a.vid)
clip = next((od / "media" / a.sid).rglob(f"{'480p30' if a.q == 'l' else '1080p30'}/{a.sid}.mp4"))
# 取樣時間：句尾後 0.25 秒；但不能落在場景結尾的轉場（章節卡 1.15 秒、甩鏡 0.45 秒）或片尾畫面裡
idx = [x["id"] for x in T["scenes"]].index(a.sid)
nxt = T["scenes"][idx + 1] if idx + 1 < len(T["scenes"]) else None
tail = (1.25 if nxt and nxt.get("chapter") else 0.5) if nxt else T.get("end_screen", 0) + 0.9
ts = [min(s["end"] + 0.25, sc["duration"] - tail) for s in sc["sentences"]]
cols = 4
rows = (len(ts) + cols - 1) // cols
W, H = 480, 270
sheet = Image.new("RGB", (cols * W, rows * H), "gray")
z = STYLE["zones"]["subtitle"]
with tempfile.TemporaryDirectory() as d:
    for k, t in enumerate(ts):
        f = Path(d) / "f.png"
        subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{max(0, t - 0.05):.2f}", "-i", str(clip), "-frames:v", "1", "-y", str(f)], check=True)
        im = Image.open(f).convert("RGB").resize((W, H))
        dr = ImageDraw.Draw(im)
        dr.rectangle([int(z[0] * W), int(z[1] * H), int(z[2] * W), int(z[3] * H)], outline=(255, 0, 255))
        dr.text((4, 4), f"{sc['sentences'][k]['id']} {t:.1f}s", fill=(255, 0, 255))
        sheet.paste(im, ((k % cols) * W, (k // cols) * H))
(od / "sheets").mkdir(exist_ok=True)
outp = od / "sheets" / f"{a.sid}.png"
sheet.save(outp)
print(outp)
