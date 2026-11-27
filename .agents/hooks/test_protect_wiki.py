"""protect_wiki.py 的回歸測試：uv run python .agents/hooks/test_protect_wiki.py"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("protect_wiki.py")
W = "concept" + "-wiki"
CASES = [  # (工具, 輸入, 應該擋)
    ("write_file", f"/x/{W}/wiki/a.md", True),
    ("edit_file", f"{W}/wiki/a.md", True),
    ("edit_file", "/x/lib/kit.py", False),
    ("run_command", f"echo hi > {W}/x", True),
    ("run_command", f"rm -rf {W}/wiki", True),
    ("run_command", f"git -C {W} commit -m x", True),
    ("run_command", f"cd {W} && git reset --hard", True),
    ("run_command", f"sed -i '' s/a/b/ {W}/wiki/x.md", True),
    ("run_command", f"cp /tmp/a.md {W}/wiki/concepts/", True),
    ("run_command", f"git submodule update --remote {W}", False),
    ("run_command", f"cat {W}/wiki/index.md > /tmp/x", False),
    ("run_command", f"cp {W}/wiki/figures/a.png /tmp/", False),
    ("run_command", f'git commit -m "{W} 唯讀，加 git add 說明"', False),
    ("run_command", "uv run python lib/cards.py rrf-rank-fusion", False),
]
bad = 0
for tool, val, block in CASES:
    args = {"CommandLine": val} if tool == "run_command" else {"Path": val}
    payload = {"toolCall": {"id": "test", "name": tool, "args": args}}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = {}
    denied = r.returncode == 0 and out.get("decision") == "deny"
    allowed = r.returncode == 0 and out.get("decision") == "allow"
    ok = denied if block else allowed
    bad += not ok
    print(("✓" if ok else "✗"), "擋" if denied else ("放" if allowed else f"錯({r.returncode})"), val)
sys.exit(1 if bad else 0)
