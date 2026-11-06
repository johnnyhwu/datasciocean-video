"""PreToolUse hook：擋住任何寫入 concept-wiki submodule 的動作（規格 §2：唯一資料來源，唯讀）。

只看「寫入目標」是不是 concept-wiki：檔案編輯的路徑、重新導向／tee／rm／mv／cp／sed -i 的目標、
以及 `git -C …concept-wiki` 或 `cd concept-wiki` 之後的寫入型 git 指令。單純提到這個字（例如 commit 訊息）不擋。
`git submodule update` 允許（那是更新指標，不改卡）。
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

d = json.load(sys.stdin)
tool, inp = d.get("tool_name", ""), d.get("tool_input", {})
bad = False
if tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
    bad = "/concept-wiki/" in (inp.get("file_path") or inp.get("notebook_path") or "")
elif tool == "Bash":
    c = inp.get("command", "")
    if "concept-wiki" in c:
        bad = any(re.search(p, c) for p in PATTERNS)
if bad:
    print("concept-wiki 是唯讀的唯一資料來源，不可寫入（規格 §2）。要更新卡請到 datasciocean-concept-wiki repo 處理。", file=sys.stderr)
    sys.exit(2)
