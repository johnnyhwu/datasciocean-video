"""字型檢查（規格 §6.6）：腳本、字幕與場景程式裡的中文字都要被內嵌字型收錄；繁中文字裡不能混入簡體字。

用法：uv run python lib/checks/fonts.py <影片 ID>
- 掃描 script.json 的 display、out/<id>/subs.zh-TW.srt、videos/<id>/scenes*.py 裡的字串常數。
- 簡體字偵測：單字經 OpenCC s2tw 轉換後會變的，就疑似簡體。少數繁簡同形的誤報請人工確認。
"""
import ast
import json
import sys
from pathlib import Path

import opencc
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, STYLE, load_script, out_dir, video_dir  # noqa: E402

vid = sys.argv[1]
cmaps = [TTFont(ROOT / f).getBestCmap() for f in STYLE["font_files"]]
spec = load_script(vid)
text = "".join(s["display"] for sc in spec["scenes"] for s in sc["sentences"])
srt = out_dir(vid) / "subs.zh-TW.srt"
if srt.exists():
    text += srt.read_text()
for f in video_dir(vid).glob("scenes*.py"):
    for node in ast.walk(ast.parse(f.read_text())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text += node.value
chars = {c for c in text if c.strip() and ord(c) > 127}
missing = sorted(c for c in chars if not all(ord(c) in cm for cm in cmaps))
s2t = opencc.OpenCC("s2tw")
leak = sorted(c for c in chars if s2t.convert(c) != c)
print("缺字：", missing or "無")
print("疑似簡體字：", leak or "無")
sys.exit(1 if missing or leak else 0)
