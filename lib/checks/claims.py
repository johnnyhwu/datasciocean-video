"""查核紀錄的程式檢查（規格 §4.2「標記」、§5.5–5.7）。LLM 查核員做判斷，這支只做能用規則判斷的事。

用法：uv run python lib/checks/claims.py <影片 ID>

讀 videos/<id>/factcheck.json（查核員產出）：
{"sentences": {"a1": {"tag": "card_claim", "refs": ["<卡 ID>#c3"], "verdict": "pass", "note": ""}, ...},
 "screen": {"<畫面文字>": {"tag": "...", "refs": [...]}}}
tag ∈ card_claim | prerequisite | illustration | framing | fixed_line

檢查：
1. 每句（含 script 每句的 screen 畫面文字）都有標記，而且一句一個標記。
2. card_claim 一定有 refs；refs 指到的主張存在、而且 status 可用（normal／author_confirmed）。
3. card_claim 句子裡的每個數字都要在引用主張（含限定條件、比較對象）的文字裡找得到；找不到列給 LLM 判斷（可能寫法不同，例如「三成」對「31%」）。
4. framing 句子掃描數字、比較詞、因果詞；掃到就列進關卡 3 的審查包。
5. prerequisite 句子的單位數比例 ≤ 1/3（暫定）。
6. illustration 句子（含畫面文字）有數字時，旁白要交代這是舉例：同一句或同一場較前面的句子要有
   「假設／舉個例子／比方說／例如／舉例」（使用者 2026-11-08：畫面不放「示意」標籤，改在旁白說）。
7. fixed_line 必須和 rules/fixed-lines.md 的模板相符（只能填變數）。
8. 代入計算（使用者 2026-11-07 同意）：card_claim 可以有 "calc": {"expr": "1/(60+3)+1/(60+3)", "result": "0.0317"}。
   程式驗算 expr（只允許數字與 + - * / ( )），結果要和 result 相符（依 result 的小數位數四捨五入）；
   expr 裡的每個數字都要出現在引用主張的文字裡；句子裡的 result 數字不再列為「不在卡上」。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cards  # noqa: E402
from paths import ROOT, load_script, video_dir  # noqa: E402
from textutil import units  # noqa: E402

TAGS = {"card_claim", "prerequisite", "illustration", "framing", "fixed_line"}
NUM = re.compile(r"\d+(?:\.\d+)?%?|[一二三四五六七八九十百千萬億兩]+(?:成|倍|個百分點|分之)")
COMPARE = re.compile(r"更|最|比|超過|不到|勝過|贏|輸|提升|下降|高於|低於|倍|全部|都|從不|總是|一定|幾乎|大幅|完全")
EXAMPLE = re.compile(r"假設|舉個例子|舉例|比方說|比如|例如")
CAUSAL = re.compile(r"因為|所以|導致|造成|使得|讓.*變|因此|由於|結果")


def fixed_templates():
    f = ROOT / "rules/fixed-lines.md"
    pats = []
    for m in re.findall(r"^\s*-\s*`([^`]+)`", f.read_text(), re.M) if f.exists() else []:
        pats.append(re.compile("^" + re.sub(r"\\\{[^}]+\\\}", ".+", re.escape(m)) + "$"))
    return pats


def nums(s):
    return set(NUM.findall(s))


CN = "零一二三四五六七八九"


def cn_num(n: int) -> str:
    """0～9999 的整數轉國字（三、十二、六十、一百零八）。"""
    if n < 10:
        return CN[n]
    out, units_ = "", ["千", "百", "十", ""]
    digits = f"{n:04d}"
    zero = False
    for d, u in zip(digits, units_):
        d = int(d)
        if d == 0:
            zero = bool(out)
            continue
        if zero:
            out += "零"
            zero = False
        out += ("" if (d == 1 and u == "十" and not out) else CN[d]) + u
    return out


def in_text(n: str, text: str) -> bool:
    if n in text:
        return True
    if n.isdigit() and int(n) < 10000:
        return cn_num(int(n)) in text or ("兩" + cn_num(int(n))[1:]) in text
    return False


def check_calc(calc, src_text, extra=None):
    """驗算代入計算。回傳問題清單；extra 收集算式的中間值（例如 60+3 的 63），讓句子可以提到它們。"""
    import ast
    import operator as op
    probs = []
    expr, result = calc.get("expr", ""), str(calc.get("result", ""))
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg}

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            v = ops[type(n.op)](ev(n.left), ev(n.right))
            if extra is not None:
                extra.append(str(int(v)) if float(v).is_integer() else f"{v:.6g}")
            return v
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.operand))
        raise ValueError("算式只能有數字與 + - * / ( )")
    try:
        val = ev(ast.parse(expr, mode="eval"))
    except Exception as e:  # noqa: BLE001
        return [f"算式無法驗算：{expr}（{e}）"]
    dec = len(result.split(".")[1]) if "." in result else 0
    try:
        if round(val, dec) != round(float(result.rstrip("%")), dec):
            probs.append(f"算式 {expr} ＝ {val:.6g}，和寫的結果 {result} 不符")
    except ValueError:
        probs.append(f"結果不是數字：{result}")
    for n in set(re.findall(r"\d+(?:\.\d+)?", expr)):
        if not in_text(n, src_text):
            probs.append(f"算式裡的 {n} 不在引用主張的文字裡")
    return probs


def main():
    vid = sys.argv[1]
    spec = load_script(vid)
    fc = json.loads((video_dir(vid) / "factcheck.json").read_text())
    S, SCR = fc.get("sentences", {}), fc.get("screen", {})
    problems, flagged = [], []
    sents = [s for sc in spec["scenes"] for s in sc["sentences"]]
    total = sum(units(s["display"]) for s in sents)
    prereq = 0
    pats = fixed_templates()
    # 每句之前（含本句），同一場有沒有用口語交代「這是舉例」
    told = {}
    for sc in spec["scenes"]:
        seen = False
        for s in sc["sentences"]:
            seen = seen or bool(EXAMPLE.search(s.get("say") or s["display"]))
            told[s["id"]] = seen
    # 已經用「舉例」交代過的數字：之後再提到（例如 n3 回頭提 sc01 的 0.83）不必再說一次
    shown, ok_before = set(), {}
    for s in sents:
        ok_before[s["id"]] = set(shown)
        if told[s["id"]]:
            texts = [s["display"]] + [t for t in s.get("screen", []) if (SCR.get(t) or {}).get("tag") == "illustration"]
            if (S.get(s["id"]) or {}).get("tag") == "illustration" or len(texts) > 1:
                for t in texts:
                    shown |= nums(t)
    items = [(s["id"], s["display"], S.get(s["id"]), s["id"]) for s in sents]
    items += [(f"畫面：{t}", t, SCR.get(t), s["id"]) for s in sents for t in s.get("screen", [])]
    for key, text, rec, owner in items:
        if not rec:
            problems.append(f"{key} 沒有標記")
            continue
        tag = rec.get("tag")
        if tag not in TAGS:
            problems.append(f"{key} 標記不合法：{tag}（不屬於任何標記就停下來問使用者）")
            continue
        if tag == "card_claim":
            refs = rec.get("refs") or []
            if not refs:
                problems.append(f"{key} 是 card_claim 但沒有來源")
            src_text = ""
            for r in refs:
                try:
                    cid, clid = r.split("#")
                    c = cards.claim(cid, clid)
                except Exception:  # noqa: BLE001
                    problems.append(f"{key} 的來源不存在：{r}")
                    continue
                if c.get("status") not in cards.USABLE:
                    problems.append(f"{key} 引用了不可用的主張 {r}（{c.get('status')}）")
                src_text += c["text"] + str(c.get("comparison_target", "")) + "".join(q["text"] for q in c.get("qualifiers") or [])
            calc = rec.get("calc")
            if calc:
                mids = []
                problems += [f"{key} {p}" for p in check_calc(calc, src_text, mids)]
                src_text += " " + str(calc.get("result", "")) + " " + " ".join(mids)
            miss = [n for n in nums(text) if not in_text(n, src_text)]
            if miss:
                flagged.append(f"{key} 的數字 {miss} 不在引用主張的文字裡（交給查核員判斷是否只是寫法不同）")
        elif tag == "framing":
            hit = sorted(nums(text)) + COMPARE.findall(text) + CAUSAL.findall(text)
            if hit:
                flagged.append(f"{key}（framing）含 {hit}：{text}")
        elif tag == "prerequisite":
            prereq += units(text) if not key.startswith("畫面") else 0
        elif tag == "illustration" and nums(text) and not told.get(owner) and not nums(text) <= ok_before.get(owner, set()):
            problems.append(f"{key}（illustration）有數字，但旁白到這句為止沒有說這是舉例（假設／舉個例子／比方說／例如）：{text}")
        elif tag == "fixed_line" and pats and not any(p.match(text) for p in pats):
            problems.append(f"{key} 是 fixed_line 但和模板不符（只能填變數）：{text}")
        if rec.get("verdict") == "fail":
            problems.append(f"{key} 查核不通過：{rec.get('note', '')}")
    ratio = prereq / max(1, total)
    if ratio > 1 / 3:
        problems.append(f"前置知識佔 {ratio:.0%}，超過 1/3")
    out = {"problems": problems, "flagged_for_gate3": flagged, "prerequisite_ratio": round(ratio, 3)}
    (video_dir(vid) / "factcheck-program.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
