"""分鏡拼圖（v004 之後加）：把 kit.Board 存的每一拍（out/<id>/board/NN-名稱.png）3×3 拼成一張，
每格標「編號 名稱」和這一拍的說明，字幕區（下方 18%）畫洋紅線，有版面問題的格子加紅框。

用法：uv run python lib/checks/board.py <影片 ID>
輸出：out/<id>/board/sheet-NN.png；給 Claude 自己看，也給 ux-reviewer 的分鏡審（見 make-video 第 4 節）。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, out_dir  # noqa: E402

vid = sys.argv[1]
d = out_dir(vid) / "board"
beats = json.loads((d / "beats.json").read_text())
for old in d.glob("sheet-*.png"):
    old.unlink()
font_f = next(iter(sorted((ROOT / "assets/fonts").glob("*.[ot]tf"))))
F = ImageFont.truetype(str(font_f), 18)
W, H, LAB = 640, 360, 30
pages = [beats[i:i + 9] for i in range(0, len(beats), 9)]
for p, page in enumerate(pages, 1):
    rows = (len(page) + 2) // 3
    sheet = Image.new("RGB", (3 * W + 8, rows * (H + LAB + 4)), (20, 20, 20))
    for j, b in enumerate(page):
        im = Image.open(d / f"{b['n']:02d}-{b['name']}.png").convert("RGB").resize((W, H))
        dr = ImageDraw.Draw(im)
        y = int(H * 0.82)
        dr.line([(0, y), (W, y)], fill=(255, 0, 255), width=1)
        if b["problems"]:
            dr.rectangle([0, 0, W - 1, H - 1], outline=(255, 60, 60), width=4)
        x0, y0 = (j % 3) * (W + 4), (j // 3) * (H + LAB + 4)
        sheet.paste(im, (x0, y0 + LAB))
        ImageDraw.Draw(sheet).text((x0 + 4, y0 + 5), f"{b['n']:02d} {b['name']}  {b['note']}"[:46], font=F, fill=(235, 235, 235))
    sheet.save(d / f"sheet-{p:02d}.png")
bad = [b for b in beats if b["problems"]]
print(f"{len(beats)} 拍 → {len(pages)} 張：{d}")
print("版面問題：" + ("無" if not bad else "、".join(f"{b['n']:02d} {b['name']}（{len(b['problems'])}）" for b in bad)))
