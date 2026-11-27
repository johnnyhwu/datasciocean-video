"""產生 upload.json（標題、三語說明欄）。簡體用 OpenCC＋config/zh-cn-terms.yaml（與字幕同一套）。英文只翻譯。"""
import json, sys
from pathlib import Path
sys.path.insert(0, "lib")
ID = "v005-llm-verifier"
V = Path("videos") / ID
TITLE = "AI 評審：做對和偷吃步，為什麼同分？｜LLM-as-a-Verifier"
THUMB = sys.argv[1] if len(sys.argv) > 1 else "A"
chap = (V / "chapters.txt").read_text().strip()
PAPER = 'LLM-as-a-Verifier: A General-Purpose Verification Framework'

zh = f"""兩條 AI agent 的軌跡，一條真的做對、一條偷吃步；同樣的比較請 AI 評審做 100 次，88 次給了一樣的分數。
問題出在只取機率最高的那個分數（argmax），其他分數的機率全被丟掉；改算期望值，平手就拆開了。
代價是：它每次都得表態，100 次裡有 31 次反而把偷吃步的那條排在前面。

延伸閱讀
完整文章：https://datasciocean.com/paper-intro/llm-as-a-verifier/
原始論文（arXiv）：{PAPER}
https://arxiv.org/abs/2607.05391

章節
{chap}

論文首頁截圖出處：Kwok et al., "{PAPER}", arXiv:2607.05391, CC BY 4.0."""

EN_CHAP = {"88 次平手": "88 ties", "評審為什麼會平手": "Why the judge ties", "評審的腦袋裡": "Inside the judge's head",
           "改算期望值": "Use the expected value instead", "回到那一百次": "Back to those 100 comparisons", "三個旋鈕": "Three knobs",
           "證據有多乾淨": "How clean is the evidence", "代價：每次都要表態": "The cost: it must always pick a side", "三點回顧": "Three-point recap"}
en_chap = "\n".join(l.split(" ", 1)[0] + " " + EN_CHAP[l.split(" ", 1)[1]] for l in chap.splitlines())
en = f"""Two AI agent trajectories: one really solves the task, the other takes a shortcut. We ask an AI judge to make the same comparison 100 times, and 88 times it gives them the same score.
The problem is that only the score with the highest probability is kept (argmax), and the probabilities of all the other scores are thrown away; compute the expected value instead, and the ties break apart.
The cost: it has to pick a side every time, and in 31 out of 100 it actually ranks the shortcut trajectory first.

Further reading
Full article (in Chinese): https://datasciocean.com/paper-intro/llm-as-a-verifier/
Paper (arXiv): {PAPER}
https://arxiv.org/abs/2607.05391

Chapters
{en_chap}

Paper first-page screenshot: Kwok et al., "{PAPER}", arXiv:2607.05391, CC BY 4.0."""
EN_TITLE = "AI Judges: Why Do the Right Answer and the Shortcut Get the Same Score? | LLM-as-a-Verifier"

import opencc, yaml
cc = opencc.OpenCC("tw2sp")
terms = yaml.safe_load(open("config/zh-cn-terms.yaml")) or {}
def to_cn(s):
    s = cc.convert(s)
    for a, b in (terms.items() if isinstance(terms, dict) else []):
        if isinstance(b, str):
            s = s.replace(a, b)
    return s
out = {"title": TITLE, "description": zh, "language": "zh-TW", "category_id": 28,
       "tags": ["LLM-as-a-Verifier", "LLM-as-a-Judge", "AI 評審", "AI Agent", "argmax", "期望值", "Expected Value", "Verifier", "LLM", "Terminal-Bench", "論文解讀"],
       "contains_synthetic_media": False,
       "localizations": {"en": {"title": EN_TITLE, "description": en}, "zh-CN": {"title": to_cn(TITLE), "description": to_cn(zh)}},
       "video": f"out/{ID}/deliver/{ID}-nomusic.mp4",   # 2026-11-27：品牌音樂被 Content ID 維持認領，使用者選無音樂版
       "thumbnail": f"videos/{ID}/thumbs/{THUMB}.png",
       "captions": [{"language": "zh-TW", "name": "", "file": f"out/{ID}/deliver/subs.zh-TW.srt"},
                    {"language": "zh-CN", "name": "", "file": f"out/{ID}/deliver/subs.zh-CN.srt"}]}
(V / "upload.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(out["localizations"]["zh-CN"]["title"]); print(len(TITLE), len(EN_TITLE))
