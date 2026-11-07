"""實驗 x01 的校準對照圖（設計模式，輸出兩張靜態圖）：
PYTHONPATH=lib uv run python -m manim -qh -s --media_dir out/_x01-calib experiments/x01-test-clip/calibration.py Sizes Colors
"""
import sys
from pathlib import Path

from kit import *

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib" / "checks"))
from contrast import contrast  # noqa: E402

FRACS = [0.024, 0.027, 0.030, 0.034, 0.038, 0.042, 0.050, 0.060]
CODES = "ABCDEFGH"


def raw(s, frac, color=TXT, weight=NORMAL):
    """校準用：可以低於 min_text_frac 的文字。"""
    return Text(s, font=FONT, font_size=fs(frac), color=color, weight=weight)


class Sizes(Scene):
    def construct(self):
        self.add(bgplate("glow_center"))
        self.add(raw("字級對照：每一列最左邊是代號與字高（佔畫面高度的比例）", .036, TXT_STRONG, BOLD).move_to([0, 3.45, 0]))
        self.add(raw("左：一般（Regular）　右：粗體（Bold）　請用手機橫向全螢幕看，回答「哪一列以下太小」", .028, MUTED).move_to([0, 2.95, 0]))
        y = 2.35
        for code, f in zip(CODES, FRACS):
            h = f * FH
            lab = raw(f"{code}  {f:.3f}", .03, GOLD, BOLD).move_to([-6.2, y - h / 2, 0], aligned_edge=LEFT)
            reg = raw("名次不是分數 k=60", f, TXT).move_to([-4.3, y - h / 2, 0], aligned_edge=LEFT)
            bold = raw("名次不是分數 k=60", f, TXT, BOLD).move_to([1.2, y - h / 2, 0], aligned_edge=LEFT)
            self.add(lab, reg, bold)
            y -= h + .2
        box = Rectangle(width=FW * .9, height=FH * .15).set_stroke("#FF00FF", 3).move_to([0, (0.5 - .875) * FH, 0])
        self.add(box, raw("↓ 字幕區（實際字幕大小以預覽影片為準）", .026, "#FF66FF").next_to(box, UP, buff=.06).align_to(box, LEFT))


class Colors(Scene):
    def construct(self):
        self.add(bgplate("glow_center"))
        self.add(raw("配色對照：概念色（每支影片挑 4～5 個）與角色色", .036, TXT_STRONG, BOLD).move_to([0, 3.45, 0]))
        self.add(raw("數字是和背景的對比度（WCAG，≥ 4.5 才算文字夠清楚）；請看「哪一個顏色在手機上不好讀或和別的分不清」", .028, MUTED).move_to([0, 2.95, 0]))
        pool = S["concept_pool"]
        roles = [("強調（金）", GOLD), ("正確", GOOD), ("錯誤", BAD), ("中性", NEUTRAL), ("主文字", TXT), ("次要文字", MUTED)]
        y0 = 2.3
        for i, c in enumerate(pool):
            y = y0 - i * .56
            sw = RoundedRectangle(corner_radius=.06, width=1.1, height=.38).set_fill(c, 1).set_stroke(width=0).move_to([-5.6, y, 0])
            t1 = raw(f"{i + 1}", .034, GOLD, BOLD).move_to([-6.35, y, 0])
            t2 = raw("名次 RRF 0.83", .04, c, BOLD).move_to([-4.85, y, 0], aligned_edge=LEFT)
            t3 = raw("名次 RRF 0.83", .034, c).move_to([-1.85, y, 0], aligned_edge=LEFT)
            cr = contrast(c, S["bg"]["sea"])
            t4 = raw(f"{cr:.1f}", .03, MUTED).move_to([.4, y, 0])
            self.add(sw, t1, t2, t3, t4)
        for i, (n, c) in enumerate(roles):
            y = y0 - i * .56
            sw = RoundedRectangle(corner_radius=.06, width=.9, height=.38).set_fill(c, 1).set_stroke(width=0).move_to([1.9, y, 0])
            t2 = raw(n, .036, c, BOLD).move_to([2.6, y, 0], aligned_edge=LEFT)
            cr = contrast(c, S["bg"]["sea"])
            t4 = raw(f"{cr:.1f}", .03, MUTED).move_to([5.9, y, 0])
            self.add(sw, t2, t4)
        # 同時出現 5 個概念色時，分不分得清
        demo = VGroup(*[RoundedRectangle(corner_radius=.08, width=1.5, height=.5).set_fill(c, .9).set_stroke(width=0) for c in pool[:5]]).arrange(RIGHT, buff=.2)
        demo.move_to([0, -2.2, 0])
        self.add(demo, raw("同時用 5 個概念色時，分得清嗎？", .03, MUTED).next_to(demo, UP, buff=.12))
