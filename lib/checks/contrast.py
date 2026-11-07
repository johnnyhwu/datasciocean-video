"""配色對比度（WCAG 2.x）。規格 §6.5：文字對比度至少 4.5:1（暫定）。

用法：uv run python lib/checks/contrast.py      → 檢查 config/style.json 的文字色、角色色、概念色對兩種背景（深海、海）的對比度
函式：contrast(hex1, hex2) → 比值
"""
import json
import sys
from pathlib import Path


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


if __name__ == "__main__":
    S = json.loads((Path(__file__).resolve().parents[2] / "config/style.json").read_text())
    bgs = {"深海 deep": S["bg"]["deep"], "海 sea": S["bg"]["sea"], "面板 panel": S["bg"]["panel"]}
    colors = {"text": S["text"], "text_strong": S["text_strong"], "muted": S["muted"], "dim": S["dim"], "gold": S["brand"]["gold"],
              **{f"role.{k}": v for k, v in S["role"].items()}, **{f"concept[{i}]": c for i, c in enumerate(S["concept_pool"])}}
    need = S.get("contrast_min", 4.5)
    bad = []
    print(f"{'顏色':16}" + "".join(f"{k:>14}" for k in bgs))
    for name, c in colors.items():
        row = [contrast(c, b) for b in bgs.values()]
        print(f"{name:12}{c:>9}" + "".join(f"{v:>13.1f}{'✗' if v < need else ' '}" for v in row))
        if name != "dim" and min(row[:2]) < need:
            bad.append(name)
    print("低於門檻（dim 是刻意的低對比裝飾色，不用在文字）：", bad or "無")
    sys.exit(1 if bad else 0)
