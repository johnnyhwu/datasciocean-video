"""protect_wiki.py 的回歸測試：uv run python .claude/hooks/test_protect_wiki.py"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("protect_wiki.py")
W = "concept" + "-wiki"
CASES = [  # (工具, 輸入, 應該擋)
    ("Write", f"/x/{W}/wiki/a.md", True),
    ("Edit", "/x/lib/kit.py", False),
    ("Bash", f"echo hi > {W}/x", True),
    ("Bash", f"rm -rf {W}/wiki", True),
    ("Bash", f"git -C {W} commit -m x", True),
    ("Bash", f"cd {W} && git reset --hard", True),
    ("Bash", f"sed -i '' s/a/b/ {W}/wiki/x.md", True),
    ("Bash", f"cp /tmp/a.md {W}/wiki/concepts/", True),
    ("Bash", f"git submodule update --remote {W}", False),
    ("Bash", f"cat {W}/wiki/index.md > /tmp/x", False),
    ("Bash", f"cp {W}/wiki/figures/a.png /tmp/", False),
    ("Bash", f'git commit -m "{W} 唯讀，加 git add 說明"', False),
    ("Bash", "uv run python lib/cards.py rrf-rank-fusion", False),
]
bad = 0
for tool, val, block in CASES:
    inp = {"command": val} if tool == "Bash" else {"file_path": val}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_name": tool, "tool_input": inp}), capture_output=True, text=True)
    ok = (r.returncode == 2) == block
    bad += not ok
    print(("✓" if ok else "✗"), "擋" if r.returncode == 2 else "放", val)
sys.exit(1 if bad else 0)
