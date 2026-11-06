"""讀觀念卡（concept-wiki，唯讀）。格式見 rules/card-format.md。

用法：uv run python lib/cards.py <卡 ID> [...]       → 印出可用的主張（含限定條件），pending 的標出來不印內容
      uv run python lib/cards.py --article <文章 slug> → 列出這篇文章的所有卡
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "concept-wiki/wiki"
USABLE = {"normal", "author_confirmed"}


def load(cid: str) -> dict:
    t = (WIKI / "concepts" / f"{cid}.md").read_text()
    fm = yaml.safe_load(t.split("---")[1])
    block = next(b for b in re.findall(r"```yaml\n(.*?)```", t, re.S) if "claims:" in b)
    fm["claims"] = yaml.safe_load(block)["claims"]
    return fm


def claim(cid: str, clid: str) -> dict:
    return next(c for c in load(cid)["claims"] if c["id"] == clid)


def usable_claims(cid: str) -> list[dict]:
    return [c for c in load(cid)["claims"] if c.get("status") in USABLE]


def article_cards(slug: str) -> list[str]:
    out = []
    for f in sorted((WIKI / "concepts").glob("*.md")):
        fm = yaml.safe_load(f.read_text().split("---")[1])
        if fm["sources"][0]["article"] == slug:
            out.append(fm["id"])
    return out


def wiki_commit() -> str:
    return subprocess.run(["git", "-C", str(ROOT / "concept-wiki"), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


if __name__ == "__main__":
    if sys.argv[1] == "--article":
        print("\n".join(article_cards(sys.argv[2])))
        sys.exit()
    for cid in sys.argv[1:]:
        c = load(cid)
        print(f"# {cid}｜{c['title']}\n  context_type={c['context_type']}  blog={c['sources'][0]['url']}")
        for cl in c["claims"]:
            if cl.get("status") not in USABLE:
                print(f"  [{cl['id']}] （{cl.get('status')}，不可用）")
                continue
            extra = f"｜比較對象：{cl['comparison_target']}" if cl.get("comparison_target") else ""
            print(f"  [{cl['id']}] {cl['role']}/{cl['anchor_type']}/imp{cl['importance']}{' (author_confirmed，取保守)' if cl['status'] == 'author_confirmed' else ''}：{cl['text']}{extra}")
            for q in cl.get("qualifiers") or []:
                print(f"       限定：{q['text']}")
            for fg in cl.get("figures") or []:
                print(f"       附圖：concept-wiki/wiki/{fg['file']}")
