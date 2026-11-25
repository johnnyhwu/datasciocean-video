"""產生 upload.json（標題、三語說明欄）。簡體用 OpenCC＋config/zh-cn-terms.yaml（與字幕同一套）。"""
import json, sys
from pathlib import Path
sys.path.insert(0, "lib")
ID = "v004-claude-code-loop"
V = Path("videos") / ID
TITLE = sys.argv[1] if len(sys.argv) > 1 else "Claude Code 拆開來看：裡面只有一個迴圈"
THUMB = sys.argv[2] if len(sys.argv) > 2 else "A"
chap = (V / "chapters.txt").read_text().strip()

zh = f"""一個會自己讀程式、改程式、跑測試的 AI，裡面一定有規劃器、執行器、檢查器吧？Claude Code 沒有另外掛規劃模組。在我們看來，它的核心只有一個迴圈：模型開一張工具呼叫單，Harness 去執行，結果接回對話紀錄，模型再決定下一步，直到它自己判斷做完了。
每次動手都要開單，Harness 才能在動作發生前檢查權限、記 log、觸發 Hook；失敗只是另一種觀察，會變成下一輪的輸入。權限是漸進式的，加上受限的執行環境，讓犯錯便宜、可以挽回。紙卷滿了就摘要，大範圍的搜尋交給 Subagent；Skills、Hooks、MCP 則是三個擴充點。

延伸閱讀
完整文章：https://datasciocean.com/ai-concept/claude-code/
Claude Code 官方文件：https://code.claude.com/docs/zh-TW/overview

章節
{chap}"""

EN_CHAP = {"只有一個迴圈？": "Just one loop?", "模型沒有手": "The model has no hands", "舉例：修一個沒過的測試": "Example: fixing a failing test",
           "做、看、再做": "Act, observe, repeat", "每次動手都要開單": "Every action needs a tool call", "讓犯錯便宜又可逆": "Make mistakes cheap and reversible",
           "紙卷滿了怎麼辦": "When the transcript fills up", "Skills、Hooks、MCP": "Skills, Hooks, MCP", "三點回顧": "Three-point recap"}
en_chap = "\n".join(l.split(" ", 1)[0] + " " + EN_CHAP[l.split(" ", 1)[1]] for l in chap.splitlines())
en = f"""An AI that reads code, edits code, and runs tests on its own must have a planner, an executor, and a checker inside, right? Claude Code doesn't bolt on a separate planning module. As we see it, its core is just one loop: the model writes out a tool call, the Harness executes it, the result is appended to the transcript, and the model decides the next step, until it judges on its own that the work is done.
Every action needs an explicit tool call, so the Harness can check permissions, write a log, and trigger Hooks before the action happens; a failure is just another observation that becomes the input for the next round. Permissions are graduated, and together with a restricted execution environment they make mistakes cheap and reversible. When the transcript fills up, it gets summarized, and wide searches are handed to a Subagent; Skills, Hooks, and MCP are three extension points.

Further reading
Full article (in Chinese): https://datasciocean.com/ai-concept/claude-code/
Claude Code official docs: https://code.claude.com/docs/en/overview

Chapters
{en_chap}"""
EN_TITLE = {"Claude Code 拆開來看：裡面只有一個迴圈": "Claude Code, Taken Apart: There's Just One Loop Inside",
            "Claude Code 拆解：一個迴圈、一張單、一卷紙": "Claude Code Taken Apart: One Loop, One Tool Call, One Transcript",
            "Claude Code 沒有規劃器？它怎麼自己修 bug": "Claude Code Has No Planner? How It Fixes Bugs on Its Own",
            "Claude Code 怎麼自己修 bug？做、看、再做": "How Does Claude Code Fix Bugs on Its Own? Act, Observe, Repeat"}
import opencc, yaml
cc = opencc.OpenCC("tw2sp")
terms = yaml.safe_load(open("config/zh-cn-terms.yaml")) or {}
def to_cn(s):
    s = cc.convert(s)
    for a, b in (terms.items() if isinstance(terms, dict) else []):
        if isinstance(b, str):
            s = s.replace(a, b)
    return s.replace("/zh-TW/", "/zh-CN/")
out = {"title": TITLE, "description": zh, "language": "zh-TW", "category_id": 28,
       "tags": ["Claude Code", "AI Agent", "Agentic Loop", "Anthropic", "LLM", "工具呼叫", "Tool Use", "Harness", "MCP", "Subagent", "Hooks", "Skills", "context window"],
       "contains_synthetic_media": False,
       "localizations": {"en": {"title": EN_TITLE[TITLE], "description": en}, "zh-CN": {"title": to_cn(TITLE), "description": to_cn(zh)}},
       "thumbnail": f"videos/{ID}/thumbs/{THUMB}.png",
       "captions": [{"language": "zh-TW", "name": "", "file": f"out/{ID}/deliver/subs.zh-TW.srt"},
                    {"language": "zh-CN", "name": "", "file": f"out/{ID}/deliver/subs.zh-CN.srt"}]}
(V / "upload.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(out["localizations"]["zh-CN"]["title"]); print(len(TITLE))
