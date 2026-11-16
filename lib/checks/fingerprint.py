"""反模板檢查（規格 §4.4、研究 E/G）：比較這支影片的結構指紋和最近 5 支已完成的影片。

用法：uv run python lib/checks/fingerprint.py <影片 ID>

讀 videos/<id>/fingerprint.json：
{"opening_mode": "反直覺問題", "skeleton": ["hook","why","warmup","notice","name","real","limits","takeaway"],
 "visual_devices": ["蹺蹺板","百格圖","印章"], "music": ["curious_pluck","warm_outro"], "title_pattern": "疑問式",
 "mechanism_character": "機器人評審", "background": "glow_center",
 "fixed_lines": ["intro-2", "takeaway-1", "blog-1"]}

相似度＝各欄位的加權平均（集合欄位用 Jaccard，序列用最長共同子序列比例，單值欄位相等算 1）。
> 0.6（暫定）就交給主流程判斷要不要調整，寫進關卡 3 審查包。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import ROOT, video_dir  # noqa: E402

W = {"opening_mode": 2, "skeleton": 1.5, "visual_devices": 2, "title_pattern": 1, "mechanism_character": 1, "fixed_lines": 0.5}
# 背景（一律 flat）和音樂（一律品牌音樂）是全頻道固定的，2026-11-16 起不列入比對
THRESH = 0.6


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0


def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    return dp[-1][-1] / max(1, max(len(a), len(b)))


def sim(x, y):
    tot = s = 0
    for k, w in W.items():
        if k not in x or k not in y:
            continue
        a, b = x[k], y[k]
        v = lcs(a, b) if k == "skeleton" else jac(a, b) if isinstance(a, list) else float(a == b)
        s += w * v
        tot += w
    return s / tot if tot else 0


vid = sys.argv[1]
me = json.loads((video_dir(vid) / "fingerprint.json").read_text())
others = []
for d in sorted((ROOT / "videos").iterdir()):
    f = d / "fingerprint.json"
    st = d / "state.json"
    if d.name == vid or d.name.startswith("_") or not f.exists():
        continue
    done = json.loads(st.read_text()).get("finished_at", "") if st.exists() else ""
    if done:
        others.append((done, d.name, json.loads(f.read_text())))
recent = sorted(others)[-5:]
rows = [(n, round(sim(me, fp), 2)) for _, n, fp in recent]
for n, v in rows:
    print(f"{n:30} {v:.2f} {'⚠ 太像' if v > THRESH else ''}")
print("沒有可比較的影片" if not rows else f"最高相似度 {max(v for _, v in rows):.2f}（門檻 {THRESH}）")
json.dump({"compared": rows, "threshold": THRESH}, open(video_dir(vid) / "fingerprint-compare.json", "w"), ensure_ascii=False)
