"""觀眾體驗自審的素材包（2026-11-23 建立）：給 ux-reviewer 子代理用，它只看這個資料夾，不看 Claude 的想法。

用法：uv run python lib/checks/uxpack.py <影片 ID> [--thumbs A,B,C]
      uv run python lib/checks/uxpack.py <影片 ID> --board      # 分鏡審（旁白合成之前；時間軸用 timeline.py --estimate）
輸出：out/<id>/uxreview/
  board/          （--board）分鏡 sheet-*.png 與 beats.md，取代 filmstrip；沒有縮圖也可以
  watch.md        逐句時間表（時間、場景、說話者、字幕），對照 filmstrip 每格左上的秒數看
  filmstrip/      整片逐秒縮圖（沿用 out/<id>/filmstrip/，沒有就先跑 filmstrip.py -q h）
  thumb-*.png     縮圖原尺寸與手機尺寸（320×180）
  feed.png        假的推薦列：這支的縮圖＋標題，和頻道其他影片並排（判斷「會不會停下來點」）
  packaging.md    標題、說明欄前三行、縮圖候選
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, load_timeline, out_dir, video_dir  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("vid")
ap.add_argument("--thumbs", default="", help="縮圖候選檔名（thumbs/ 底下，不含 .png），預設用 upload.json 的縮圖")
ap.add_argument("--board", action="store_true", help="分鏡審：放分鏡（out/<id>/board/）而不是逐秒縮圖")
a = ap.parse_args()

V, O = video_dir(a.vid), out_dir(a.vid)
dst = O / "uxreview"
if dst.exists():
    shutil.rmtree(dst)
dst.mkdir()

# 1. 逐句時間表
T = load_timeline(a.vid)
mm = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
lines = [f"# {a.vid} 逐句時間表（總長 {mm(T['duration'])}，最後 {T.get('end_screen', 20)} 秒是固定的頻道片尾動畫）", "",
         "| 時間 | 場景 | 句 | 說話者 | 字幕 |", "|---|---|---|---|---|"]
for sc in T["scenes"]:
    for s in sc["sentences"]:
        who = "錘錘" if s.get("speaker") == "mascot" else "旁白"
        lines.append(f"| {mm(s['abs'])} | {sc['id']} {sc['name']} | {s['id']} | {who} | {s['display']} |")
(dst / "watch.md").write_text("\n".join(lines) + "\n")

# 2. 逐秒縮圖（成片審）或分鏡（分鏡審）
if a.board:
    bd = O / "board"
    if not list(bd.glob("sheet-*.png")):
        sys.exit("沒有分鏡：先渲染 videos/<id>/board.py，再跑 lib/checks/board.py <id>")
    (dst / "board").mkdir()
    for f in sorted(bd.glob("sheet-*.png")):
        shutil.copy(f, dst / "board" / f.name)
    beats = json.loads((bd / "beats.json").read_text())
    (dst / "board" / "beats.md").write_text("# 分鏡（每一拍的靜態畫面；動作要靠說明想像）\n\n| # | 名稱（句 id-描述） | 這一拍畫面在演什麼 |\n|---|---|---|\n"
                                           + "".join(f"| {b['n']:02d} | {b['name']} | {b['note']} |\n" for b in beats))
else:
    fs = O / "filmstrip"
    if not list(fs.glob("s*.png")):
        subprocess.run([sys.executable, str(ROOT / "lib/checks/filmstrip.py"), a.vid, "-q", "h"], check=True)
    shutil.copytree(fs, dst / "filmstrip")

# 3. 縮圖與推薦列
up = json.loads((V / "upload.json").read_text()) if (V / "upload.json").exists() else {}
names = [n for n in a.thumbs.split(",") if n]
paths = [V / "thumbs" / f"{n}.png" for n in names] or ([ROOT / up["thumbnail"]] if up.get("thumbnail") else [])
if not paths and not a.board:
    sys.exit("沒有縮圖：先照 publish-prep 做縮圖，或用 --thumbs 指定")
title = up.get("title", T.get("title", a.vid))
font_f = next(iter(sorted((ROOT / "assets/fonts").glob("*.[ot]tf"))))
F = lambda n: ImageFont.truetype(str(font_f), n)
for p in paths:
    im = Image.open(p).convert("RGB")
    im.resize((1280, 720)).save(dst / f"thumb-{p.stem}.png")
    im.resize((320, 180), Image.LANCZOS).save(dst / f"thumb-{p.stem}-phone.png")

others = []
for d in sorted((ROOT / "videos").glob("v*")):
    if d.name == a.vid or not (d / "upload.json").exists():
        continue
    u = json.loads((d / "upload.json").read_text())
    if u.get("thumbnail") and (ROOT / u["thumbnail"]).exists():
        others.append((ROOT / u["thumbnail"], u["title"]))


def wrap(t, f, w, dr):
    out, cur = [], ""
    for ch in t:
        if dr.textlength(cur + ch, font=f) > w:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    return out + [cur] if cur else out


TW, TH, PAD = 360, 203, 24
for p in paths:
    tiles = [(p, title)] + others[-3:]
    canvas = Image.new("RGB", (PAD + len(tiles) * (TW + PAD), TH + 150), (15, 15, 15))
    dr = ImageDraw.Draw(canvas)
    for i, (tp, tt) in enumerate(tiles):
        x = PAD + i * (TW + PAD)
        canvas.paste(Image.open(tp).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, PAD))
        for j, ln in enumerate(wrap(tt, F(20), TW, dr)[:2]):
            dr.text((x, PAD + TH + 12 + j * 28), ln, font=F(20), fill=(241, 241, 241))
        dr.text((x, PAD + TH + 72), "DataSci Ocean", font=F(16), fill=(170, 170, 170))
    canvas.save(dst / f"feed-{p.stem}.png")

desc = up.get("description", "").split("\n")
(dst / "packaging.md").write_text(
    f"# 包裝\n\n- 標題：{title}\n- 縮圖候選：{', '.join(p.stem for p in paths)}（thumb-*.png；手機尺寸 *-phone.png；推薦列 feed-*.png，第一格是這支）\n"
    f"- 說明欄前三行：\n\n> " + "\n> ".join(desc[:3]) + "\n")
n_img = len(list((dst / ("board" if a.board else "filmstrip")).glob("*.png")))
print(f"→ {dst}（{'分鏡' if a.board else 'filmstrip'} {n_img} 張、縮圖 {len(paths)} 張）")
