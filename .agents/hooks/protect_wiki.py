"""PreToolUse hook：擋住任何寫入 concept-wiki submodule 的動作（規格 §2：唯一資料來源，唯讀）。

只看「寫入目標」是不是 concept-wiki：檔案編輯的路徑、重新導向／tee／rm／mv／cp／sed -i 的目標、
以及 `git -C …concept-wiki` 或 `cd concept-wiki` 之後的寫入型 git 指令。單純提到這個字（例如 commit 訊息）不擋。
`git submodule update` 允許（那是更新指標，不改卡）。

Antigravity PreToolUse 介面：
- stdin JSON：{"toolCall": {"name": "...", "args": {...}}, ...}
- stdout JSON：{"decision": "allow"} 或 {"decision": "deny", "reason": "..."}
"""
import json
import re
import sys

W = r"[^\s'\";|&]*concept-wiki"  # 指向 concept-wiki 的路徑片段
PATTERNS = [
    rf">>?\s*{W}",                                   # echo x > concept-wiki/...
    rf"\btee\s+(-a\s+)?{W}",
    rf"\b(rm|mv|touch|mkdir|chmod|truncate)\b[^|;&]*\s{W}",
    rf"\bcp\b[^|;&]*\s{W}\S*\s*($|[|;&])",           # cp 的最後一個參數（目標）在 concept-wiki
    rf"\bsed\s+-i\b[^|;&]*{W}",
    rf"\bgit\s+-C\s+{W}\S*\s+(commit|add|rm|mv|checkout|reset|push|stash|clean|restore|apply|merge|rebase|pull)\b",
    rf"\bcd\s+{W}\S*\s*&&[^|;]*\bgit\s+(commit|add|rm|mv|checkout|reset|push|stash|clean|restore|apply|merge|rebase|pull)\b",
]

REASON = "concept-wiki 是唯讀的唯一資料來源，不可寫入（規格 §2）。要更新卡請到 datasciocean-concept-wiki repo 處理。"

d = json.load(sys.stdin)
tool_call = d.get("toolCall", {})
tool = tool_call.get("name", "")
args = tool_call.get("args", {}) or {}

bad = False
if tool in ("edit_file", "write_file"):
    path = args.get("Path") or args.get("path") or ""
    bad = "/concept-wiki/" in path or path.startswith("concept-wiki/")
elif tool == "run_command":
    c = args.get("CommandLine") or args.get("command") or ""
    if "concept-wiki" in c:
        bad = any(re.search(p, c) for p in PATTERNS)

if bad:
    print(json.dumps({"decision": "deny", "reason": REASON}, ensure_ascii=False))
else:
    print(json.dumps({"decision": "allow"}))
