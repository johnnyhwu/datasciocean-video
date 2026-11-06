"""中文計數、字幕斷行、時間格式。單位定義見 rules/speech-rate.md。"""
import re
import sys

UNIT_RE = re.compile(r"[一-鿿]|[A-Za-z0-9]+(?:[.\-][A-Za-z0-9]+)*")
NO_BREAK = re.compile(r"[A-Za-z0-9<>/%.\-]+")
PUNCT_BREAK = "，、；：！？"


def units(s: str) -> int:
    """唸出來的單位數：中文字 1、英文字或數字串 1。"""
    return len(UNIT_RE.findall(s))


def width(s: str) -> float:
    """顯示寬度（全形字 1、半形 0.5）。"""
    return sum(0.5 if ord(c) < 128 else 1 for c in s)


def split_lines(text: str, max_w: float = 18, max_lines: int = 2) -> list[str]:
    """字幕斷行：先在標點斷，再在詞界斷；不切開英數、數字與單位。超過 max_lines 就報錯（要回頭拆句）。"""
    t = text.strip().rstrip("。")
    if width(t) <= max_w:
        return [t]
    protected = set()
    for m in NO_BREAK.finditer(t):
        protected.update(range(m.start() + 1, m.end()))
    import jieba
    jieba.setLogLevel(60)
    bounds, pos = set(), 0
    for w in jieba.cut(t):
        pos += len(w)
        bounds.add(pos)
    best = None
    for i in range(1, len(t)):
        if i not in bounds or i in protected:
            continue
        a, b = t[:i].rstrip("，、；： "), t[i:].lstrip(" ")
        if width(a) <= max_w and width(b) <= max_w:
            score = abs(width(a) - width(b)) + (0 if t[i - 1] in PUNCT_BREAK else 20)
            if best is None or score < best[0]:
                best = (score, [a, b])
    if best is None:
        raise ValueError(f"字幕放不進 {max_lines} 行 × {max_w} 字，請拆句：{text}")
    return best[1]


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def yt_time(t: float) -> str:
    t = int(t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


if __name__ == "__main__":
    print(split_lines(sys.argv[1]))
