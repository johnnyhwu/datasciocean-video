"""Manim 工具箱：旁白錨定的場景基底（Timed）、版面檢查、品牌配色、通用元件、吉祥物錘錘。

來源：PoC final_xhigh 的 v4/manim/common.py（使用者滿意），2026-11-06 移植並一般化：
- 配色改成品牌「深處的光」：深海背景、米色文字、金色只給最重要的一個元素（config/style.json）。
- 路徑改成每支影片：環境變數 YTV_VIDEO＝影片 ID，讀 videos/<id>/timeline.json，寫 out/<id>/。
- 字型用 manimpango.register_font 在行程內註冊 assets/fonts/ 的 Noto Sans CJK TC，不安裝到系統。
- 主題專用的角色（PoC 的機器人評審、蹺蹺板…）不放這裡，寫在各影片自己的 scenes 檔；
  通用而且證明好用的元件才收進來。

場景寫法（videos/<id>/scenes.py）：
    from kit import *
    class Sc01(Timed):
        SID = "sc01"; BG = "glow_center"
        def construct(self):
            big = B("期望值", 0.11, C["ev"]).move_to(cell(1, 1, 1, 4))
            self.at(self.A("a1", 0.6), pop_in(big), run_time=0.4, sfx="pop")   # a1 念到 60% 時彈出
            self.finish()

規則（規格 §6.2、§6.4）：
- 每個 at() 都要對應某一句旁白（用 A()/E() 錨定），標不出來就刪掉；同一時間只有一個焦點。
- 位置用 cell()/zone 換算，不要自己填座標；字級用畫面高度比例（T/B 的 frac），不低於 style 的 min_text_frac。
- 示意的數字或例子一定掛 tag("示意")。
"""
import json
import os
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import manimpango  # noqa: E402
import numpy as np  # noqa: E402
from manim import *  # noqa: E402,F403

import bgplates  # noqa: E402

S = json.loads((ROOT / "config/style.json").read_text())
for f in S["font_files"]:
    manimpango.register_font(str(ROOT / f))

VID = os.environ.get("YTV_VIDEO")
if not VID:
    raise SystemExit("請設定 YTV_VIDEO=<影片 ID>（lib/render.py 會自動設定）")
VDIR, ODIR = ROOT / "videos" / VID, ROOT / "out" / VID
TL_ = json.loads((VDIR / "timeline.json").read_text())

# ---------------- 配色 ----------------
BG = S["bg"]["deep"]
config.background_color = BG
FW, FH = config.frame_width, config.frame_height
FONT = S["font"]
TXT, TXT_STRONG, MUTED, DIM = S["text"], S["text_strong"], S["muted"], S["dim"]
GOLD = S["brand"]["gold"]
TEAL, TEAL_L, TEAL_M = S["brand"]["teal"], S["brand"]["teal_light"], S["brand"]["teal_mid"]
GOOD, BAD, NEUTRAL = S["role"]["good"], S["role"]["bad"], S["role"]["neutral"]
SCREEN, PANEL, SEA = S["bg"]["screen"], S["bg"]["panel"], S["bg"]["sea"]
# 每支影片的概念色：script.json 的 "concepts": {"argmax": 0, "期望值": 1}（索引進 concept_pool），在場景裡用 C["argmax"]
C = {k: S["concept_pool"][i] for k, i in json.loads((VDIR / "script.json").read_text()).get("concepts", {}).items()}


def zone(name):
    return S["zones"][name]


def _y(frac):
    return (0.5 - frac) * FH


def _x(frac):
    return (frac - 0.5) * FW


TOP, BOTTOM = _y(zone("main")[1]), _y(zone("main")[3])
MIDY = (TOP + BOTTOM) / 2
ANN_Y = _y((zone("annotation")[1] + zone("annotation")[3]) / 2)
XL, XR = _x(zone("main")[0]), _x(zone("main")[2])


def cell(r0, c0, r1=None, c1=None):
    """主畫面格線（預設 6×6，0 起算，含端點）的中心點。動畫程式用它定位，不要自己填座標。"""
    r1 = r0 if r1 is None else r1
    c1 = c0 if c1 is None else c1
    rows, cols = S["grid"]
    assert 0 <= r0 <= r1 < rows and 0 <= c0 <= c1 < cols, "格子超出格線"
    x0, y0, x1, y1 = zone("main")
    cw, rh = (x1 - x0) / cols, (y1 - y0) / rows
    return np.array([_x(x0 + (c0 + c1 + 1) / 2 * cw), _y(y0 + (r0 + r1 + 1) / 2 * rh), 0])


def cell_size(nr=1, nc=1):
    rows, cols = S["grid"]
    x0, y0, x1, y1 = zone("main")
    return (x1 - x0) * FW / cols * nc, (y1 - y0) * FH / rows * nr


# ---------------- 文字 ----------------
def fs(frac):
    """字高佔畫面高的比例 → Manim font_size。"""
    return frac * FH / 0.584 * 48


def T(s, frac=0.042, color=TXT, weight=NORMAL):
    if frac < S["min_text_frac"] - 1e-9:
        raise ValueError(f"字太小：{frac} < {S['min_text_frac']}（{s}）")
    return Text(s, font=FONT, font_size=fs(frac), color=color, weight=weight)


def B(s, frac=0.042, color=TXT):
    return T(s, frac, color, BOLD)


def wrap(s, frac, max_w, color=TXT, bold=False, buff=0.12):
    """中文自動換行：依寬度切行（英數不切開），回傳 VGroup。"""
    import re
    toks = re.findall(r"[A-Za-z0-9.%\-]+|.", s)
    lines, cur = [], ""
    mk = B if bold else T
    for t in toks:
        if cur and mk(cur + t, frac, color).width > max_w:
            if t in "，。、；：！？」）":
                cur += t
                t = ""
            lines.append(cur)
            cur = ""
        cur += t
    if cur:
        lines.append(cur)
    return VGroup(*[mk(x, frac, color) for x in lines]).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def pill(s, color, frac=0.034, fill=0.18, pad=0.24, txt=None, bold=False):
    t = (B if bold else T)(s, frac, txt or color)
    r = RoundedRectangle(corner_radius=min(0.3, (t.height + pad) / 2), width=t.width + 2 * pad, height=t.height + pad)
    r.set_stroke(color, 2.5).set_fill(color, fill)
    g = VGroup(r, t.move_to(r))
    g.box, g.txt = r, t
    return g


def tag(s="示意", color=GOLD, frac=0.03):
    """示意標籤：自己補的數字、例子、重畫的估讀圖都要掛（規格 §5.5、§6.8）。"""
    return pill(s, color, frac, fill=0.12, pad=0.16)


def bgplate(name="glow_center"):
    im = ImageMobject(str(bgplates.ensure(name))).set_z_index(-100)
    im.height = FH
    im.move_to(ORIGIN)
    return im


# ---------------- 吉祥物：錘錘（logo 的測深錘） ----------------
class Plumb(VGroup):
    """頻道吉祥物。造型來自 logo：繩子＋圓柱帽＋多面錐形金色錘身。
    gear: None｜"goggles"（潛水鏡）｜"lamp"（頭燈）——造型定案前保留三種（docs/mascot/）。
    動作：look(v) 看向、blink()、mood("happy"/"o"/"flat"/"wow")、glow_on()/glow_off()（找到洞見時發光）、
    swing(角度)（以繩頂為軸擺動）、dive(距離)（沿繩下潛）；lipsync 由 Timed.lipsync(plumb, speaker="mascot") 驅動。
    出場原則：開場與收尾、或真的需要「帶觀眾往下挖」的時刻；不是每個場景都出現（避免模板感）。"""

    def __init__(self, scale=1.0, gear=None, rope=3.0):
        super().__init__()
        gold, gold_l, gold_d = GOLD, "#F5CD78", "#AA7628"
        k = 0.01
        body = Polygon(*[np.array([x, y, 0]) * k for x, y in [(-95, 60), (-60, 100), (60, 100), (95, 60), (0, -170)]])
        body.set_fill(gold, 1).set_stroke(width=0)
        lit = Polygon(*[np.array([x, y, 0]) * k for x, y in [(-95, 60), (-60, 100), (-20, 100), (-35, 60), (0, -170)]])
        lit.set_fill(gold_l, 1).set_stroke(width=0)
        shade = Polygon(*[np.array([x, y, 0]) * k for x, y in [(95, 60), (60, 100), (25, 100), (40, 60), (0, -170)]])
        shade.set_fill(gold_d, 1).set_stroke(width=0)
        cap = RoundedRectangle(corner_radius=0.08, width=0.68, height=0.38).set_fill(gold_d, 1).set_stroke(width=0)
        cap.move_to(np.array([0, 1.31, 0]))
        neck = Rectangle(width=0.52, height=0.2).set_fill(gold_d, 1).set_stroke(width=0).move_to(np.array([0, 1.07, 0]))
        top = cap.get_top()
        self.rope = Line(top, top + UP * rope).set_stroke("#C8964A", 4)
        eyes = VGroup(*[Ellipse(width=0.34, height=0.44).set_fill("#FFFAF0", 1).set_stroke(width=0).move_to([x, 0.6, 0]) for x in (-0.3, 0.3)])
        pupils = VGroup(*[Circle(0.085).set_fill(SCREEN, 1).set_stroke(width=0).move_to(e.get_center() + DOWN * 0.02) for e in eyes])
        shines = VGroup(*[Circle(0.028).set_fill(WHITE, 1).set_stroke(width=0).move_to(p.get_center() + UL * 0.035) for p in pupils])
        mouth = ArcBetweenPoints(np.array([-0.17, 0.3, 0]), np.array([0.17, 0.3, 0]), angle=PI / 2.2).set_stroke(SCREEN, 5)
        talk = Ellipse(width=0.26, height=0.16).set_fill(SCREEN, 1).set_stroke(width=0).move_to(mouth).set_opacity(0)
        self.halo = VGroup(*[Circle(r).set_fill(GOLD, 0.07).set_stroke(width=0) for r in (0.9, 1.3, 1.8)]).move_to([0, 0.2, 0])
        self.halo.set_opacity(0)
        self.add(self.rope, self.halo, cap, neck, body, lit, shade, eyes, pupils, shines, mouth, talk)
        self.body, self.eyes, self.pupils, self.shines, self.mouth, self.talk, self.cap = body, eyes, pupils, shines, mouth, talk, cap
        self.gear = None
        if gear == "goggles":
            g = RoundedRectangle(corner_radius=0.26, width=1.24, height=0.64).set_stroke("#7EC8F2", 6).set_fill(opacity=0).move_to([0, 0.6, 0])
            strap = Line([-0.62, 0.6, 0], [-0.95, 0.5, 0]).set_stroke("#7EC8F2", 5)
            self.gear = VGroup(g, strap)
        elif gear == "lamp":
            self.gear = Circle(0.15).set_fill("#FFF0C8", 1).set_stroke(width=0).move_to(cap)
        if self.gear is not None:
            self.add(self.gear)
        self.nocheck_parts = [self.rope]  # 繩子刻意伸出畫面上緣，不算越界
        self.scale(scale)

    def look(self, v):
        v = np.array(v, dtype=float)
        k = 0.07 * self.eyes[0].height / 0.44
        return [Transform(self.pupils, VGroup(*[p.copy().move_to(e.get_center() + DOWN * 0.02 * self.eyes[0].height / 0.44 + v * k)
                                                 for p, e in zip(self.pupils, self.eyes)])),
                Transform(self.shines, VGroup(*[s.copy().shift(v * k - (s.get_center() - p.get_center() - UL * 0.035 * self.eyes[0].height / 0.44))
                                                 for s, p in zip(self.shines, self.pupils)]))]

    def blink(self):
        return VGroup(self.eyes, self.pupils, self.shines).animate(rate_func=there_and_back, run_time=0.25).stretch(0.08, 1)

    def mood(self, m):
        c, w = self.mouth.get_center(), 0.34 * self.eyes[0].height / 0.44
        sw = 5 * self.eyes[0].height / 0.44
        if m in ("o", "wow"):
            new = Circle(w * 0.3).set_stroke(SCREEN, sw).move_to(c)
        else:
            ang = {"happy": PI / 2.2, "flat": 0.001, "sad": -PI / 2.2}[m]
            new = ArcBetweenPoints(c + LEFT * w / 2, c + RIGHT * w / 2, angle=ang).set_stroke(SCREEN, sw)
        return Transform(self.mouth, new)

    def glow_on(self):
        return self.halo.animate.set_opacity(1)

    def glow_off(self):
        return self.halo.animate.set_opacity(0)

    def swing(self, angle=0.18, run=1.2):
        piv = self.rope.get_end()
        return Rotate(self, angle, about_point=piv, rate_func=there_and_back, run_time=run)

    def dive(self, dist=1.5):
        """沿繩下潛：錘身往下、繩子跟著變長（繩頂不動）。"""
        top = self.rope.get_end().copy()
        others = VGroup(*[m for m in self if m is not self.rope])
        return [others.animate.shift(DOWN * dist), self.rope.animate.put_start_and_end_on(self.rope.get_start() + DOWN * dist, top)]


# ---------------- 通用動作與元件（PoC 證明好用的） ----------------
def stamp(s, color=BAD, frac=0.075, angle=-12):
    t = B(s, frac, color)
    r = RoundedRectangle(corner_radius=0.15, width=t.width + 0.6, height=t.height + 0.4).set_stroke(color, 8).set_fill(BG, 0.7)
    return VGroup(r, t.move_to(r)).rotate(angle * DEGREES)


def stamp_in(m, scale=2.6, run=0.32):
    m.save_state()
    m.scale(scale).set_opacity(0)
    return Restore(m, rate_func=rush_into, run_time=run)


def pop_in(m, run=0.4):
    return GrowFromCenter(m, rate_func=rate_functions.ease_out_back, run_time=run)


def shake(m, n=4, run=0.35, amp=0.04):
    return Wiggle(m, scale_value=1 + amp, rotation_angle=0.03 * TAU, n_wiggles=n, run_time=run)


def jolt(m, d=0.12):
    return m.animate(rate_func=there_and_back).shift(UP * d)


def bubble(content, pad=0.28, tail=DL, fill="#F2E0C0"):
    box = RoundedRectangle(corner_radius=0.28, width=content.width + 2 * pad, height=content.height + 2 * pad).set_fill(fill, 1).set_stroke(width=0)
    box.move_to(content)
    c = box.get_corner(tail)
    sx = 1 if tail[0] > 0 else -1
    sy = 1 if tail[1] > 0 else -1
    tri = Polygon(c + np.array([-sx * 0.55, -sy * 0.1, 0]), c + np.array([-sx * 0.15, -sy * 0.1, 0]),
                  c + np.array([sx * 0.15, sy * 0.35, 0])).set_fill(fill, 1).set_stroke(width=0)
    return VGroup(tri, box, content)


def think(content, pad=0.3, fill="#F2E0C0", toward=DL):
    box = RoundedRectangle(corner_radius=0.45, width=content.width + 2 * pad, height=content.height + 2 * pad).set_fill(fill, 1).set_stroke(width=0).move_to(content)
    c = box.get_corner(toward)
    dots = VGroup(*[Circle(r).set_fill(fill, 1).set_stroke(width=0).move_to(c + toward * (0.25 + 0.3 * i)) for i, r in enumerate([0.14, 0.09, 0.06])])
    return VGroup(dots, box, content)


def waffle(counts, colors, cell_=0.21, gap=0.045):
    """10×10 百格圖：把百分比變成可數的格子。"""
    cells = VGroup()
    order = []
    for k, c in enumerate(counts):
        order += [colors[k]] * c
    for idx, colr in enumerate(order):
        r, cidx = idx % 10, idx // 10
        cells.add(RoundedRectangle(corner_radius=0.03, width=cell_, height=cell_).set_fill(colr, 1).set_stroke(width=0)
                  .move_to([cidx * (cell_ + gap), -r * (cell_ + gap), 0]))
    frame = VGroup(*[RoundedRectangle(corner_radius=0.03, width=cell_, height=cell_).set_fill(WHITE, 0.07).set_stroke(width=0)
                     .move_to([i // 10 * (cell_ + gap), -(i % 10) * (cell_ + gap), 0]) for i in range(100)])
    g = VGroup(frame, cells)
    g.cells, g.frame = cells, frame
    return g


def num(val, nd=0, frac=0.05, color=TXT, suffix="", at=ORIGIN, prefix=""):
    """會滾動的數字：m.tr.animate.set_value(v)。"""
    tr = ValueTracker(val)

    def draw():
        p = at() if callable(at) else at
        return B(f"{prefix}{tr.get_value():.{nd}f}{suffix}", frac, color).move_to(p)
    m = always_redraw(draw)
    m.tr = tr
    return m


class Bars(VGroup):
    """橫條圖（軸從 0 起，條長與數值成正比；規格 §6.7）。items: [(標籤, 值, 顏色)]。"""

    def __init__(self, items, vmax, w=6.0, rowh=0.7, frac=0.036, fmt="{:.1f}%", label_w=2.4):
        super().__init__()
        self.bars, self.vals, self.labels = VGroup(), VGroup(), VGroup()
        for i, (lab, v, col) in enumerate(items):
            y = -i * rowh
            lt = T(lab, frac, TXT).move_to([-label_w / 2 - 0.2, y, 0], aligned_edge=RIGHT).align_to([0 - 0.2, 0, 0], RIGHT)
            bar = Rectangle(width=max(0.02, v / vmax * w), height=rowh * 0.6).set_fill(col, 0.95).set_stroke(width=0)
            bar.move_to([0, y, 0], aligned_edge=LEFT)
            val = B(fmt.format(v), frac, TXT).next_to(bar, RIGHT, buff=0.15)
            self.labels.add(lt)
            self.bars.add(bar)
            self.vals.add(val)
        axis = Line([0, rowh * 0.5, 0], [0, -(len(items) - 0.5) * rowh, 0]).set_stroke(MUTED, 2)
        self.add(axis, self.labels, self.bars, self.vals)

    def grow(self, i, run=0.8):
        b = self.bars[i]
        return [GrowFromEdge(b, LEFT, run_time=run), FadeIn(self.vals[i], shift=RIGHT * 0.2, run_time=run)]


def check_mark(color=GOOD, s=0.35):
    return VMobject().set_points_as_corners([[-0.5, 0, 0], [-0.15, -0.35, 0], [0.5, 0.4, 0]]).scale(s).set_stroke(color, 8)


def cross_mark(color=BAD, s=0.3):
    return VGroup(Line([-0.5, -0.5, 0], [0.5, 0.5, 0]), Line([-0.5, 0.5, 0], [0.5, -0.5, 0])).scale(s).set_stroke(color, 8)


def coin(color=GOLD, r=0.16, label=None, frac=0.03):
    c = VGroup(Circle(r).set_fill(color, 1).set_stroke("#AA7628", 2), Circle(r * 0.7).set_stroke("#AA7628", 1.5, 0.7))
    if label:
        c.add(B(label, frac, SCREEN).move_to(c))
    return c


def token_box(s, color=TEAL_L, frac=0.04, pad=0.18):
    """一個 token／詞的方塊。"""
    t = B(s, frac, TXT)
    r = RoundedRectangle(corner_radius=0.1, width=t.width + 2 * pad, height=t.height + 2 * pad).set_fill(PANEL, 1).set_stroke(color, 3)
    return VGroup(r, t.move_to(r))


def shatter(m, n=5, dist=4.0, seed=1):
    rng = np.random.default_rng(seed)
    x0, x1, y0, y1 = m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1]
    col = m.get_fill_color()
    rows = max(1, int(n * (y1 - y0) / max(0.3, x1 - x0)))
    pcs = VGroup()
    for i in range(n):
        for j in range(rows):
            w, h = (x1 - x0) / n, (y1 - y0) / rows
            pcs.add(Square(1).stretch_to_fit_width(w * 0.9).stretch_to_fit_height(h * 0.9).set_fill(col, 0.9).set_stroke(width=0)
                    .move_to([x0 + (i + .5) * w, y0 + (j + .5) * h, 0]))
    anims = [p.animate(rate_func=rate_functions.ease_in_quad).shift(DOWN * (dist + rng.uniform(0, 1.5)) + RIGHT * rng.uniform(-1.2, 1.2))
             .rotate(rng.uniform(-3, 3)).set_opacity(0) for p in pcs]
    return pcs, LaggedStart(*anims, lag_ratio=0.01)


def confetti(center, n=40, seed=3, colors=None):
    colors = colors or [GOLD, TEAL_L, "#FF8FB1", "#7EC8F2", GOOD]
    rng = np.random.default_rng(seed)
    bits = VGroup(*[Rectangle(width=0.12, height=0.06).set_fill(colors[i % len(colors)], 1).set_stroke(width=0).move_to(center) for i in range(n)])
    anims = []
    for b in bits:
        a = rng.uniform(0.3, PI - 0.3)
        r = rng.uniform(1.5, 3.5)
        anims.append(b.animate(rate_func=rate_functions.ease_out_cubic).shift([r * np.cos(a), r * np.sin(a) - 0.8, 0]).rotate(rng.uniform(-6, 6)).set_opacity(0))
    return bits, anims


# ---------------- 章節卡、進度條 ----------------
def chapter_card(n, title, subtitle=None):
    """斜切的章節卡：深海色塊＋金色圓章大號數字＋章名。"""
    w = FW + 3.0
    panel = Polygon([-w / 2 - 1.2, -FH / 2 - 0.3, 0], [w / 2 - 1.2, -FH / 2 - 0.3, 0], [w / 2 + 1.2, FH / 2 + 0.3, 0], [-w / 2 + 1.2, FH / 2 + 0.3, 0])
    panel.set_fill(SEA, 1).set_stroke(GOLD, 0)
    edge = Line([w / 2 - 1.2, -FH / 2 - 0.3, 0], [w / 2 + 1.2, FH / 2 + 0.3, 0]).set_stroke(GOLD, 10)
    shadow = panel.copy().set_fill(SCREEN, 1).shift(RIGHT * 0.5)
    circ = Circle(0.85).set_fill(GOLD, 1).set_stroke(width=0)
    nn = B(str(n), 0.12, SCREEN).move_to(circ)
    ttl = B(title, 0.085, TXT_STRONG)
    sub = T(subtitle or TL_.get("title", ""), 0.036, MUTED)
    head = VGroup(VGroup(circ, nn), ttl).arrange(RIGHT, buff=0.5)
    content = VGroup(head, sub).arrange(DOWN, buff=0.35).move_to(UP * 0.35)
    g = VGroup(shadow, panel, edge, content)
    g.nocheck = True
    g.content = content
    g.set_z_index(500)
    return g


def bbox_in(m, frame):
    c, fw, fh = frame.get_center(), frame.width, frame.height
    return [(m.get_left()[0] - c[0]) / fw + 0.5, 0.5 - (m.get_top()[1] - c[1]) / fh,
            (m.get_right()[0] - c[0]) / fw + 0.5, 0.5 - (m.get_bottom()[1] - c[1]) / fh]


class Timed(MovingCameraScene):
    """旁白錨定的場景基底。時間全部來自 timeline.json（旁白先行），不寫絕對秒數。"""
    SID = None
    BG = "glow_center"

    def setup(self):
        super().setup()
        self.problems, self.cues = [], []
        self.sc = next(s for s in TL_["scenes"] if s["id"] == self.SID)
        self.idx = [s["id"] for s in TL_["scenes"]].index(self.SID)
        self.t, self.f = 0.0, 0
        self.zone_check = True
        self.add(bgplate(self.sc.get("bg", self.BG)))
        self.hud = self.make_hud()
        self.add(self.hud)
        self.chap_now = self.sc.get("chapter")
        nxt = TL_["scenes"][self.idx + 1] if self.idx + 1 < len(TL_["scenes"]) else None
        self.next_chapter = nxt.get("chapter") if nxt else None
        self.card = None
        if self.chap_now:
            self.card = chapter_card(*self.chap_now)
            self.add(self.card)

    def make_hud(self):
        """頂端的細進度條（全片時間），章節處有刻度。片尾畫面時段淡出。"""
        total = TL_["duration"] - TL_.get("end_screen", 0)
        starts = [s["start"] for s in TL_["scenes"] if s.get("chapter")]
        y = FH / 2 - 0.16
        x0, x1 = -FW / 2 + 0.3, FW / 2 - 0.3
        track = Line([x0, y, 0], [x1, y, 0]).set_stroke(TXT, 3, 0.12)
        ticks = VGroup(*[Line([x0 + (x1 - x0) * st / total, y - 0.05, 0], [x0 + (x1 - x0) * st / total, y + 0.05, 0]).set_stroke(TXT, 2, 0.35) for st in starts])
        t0 = self.sc["start"]
        fill = Line([x0, y, 0], [x0 + 0.001, y, 0]).set_stroke(GOLD, 3, 0.9)

        def upd(m):
            g = (t0 + self.renderer.time) / total
            m.put_start_and_end_on([x0, y, 0], [x0 + max(0.002, (x1 - x0) * min(1, g)), y, 0])
        fill.add_updater(upd)
        g = VGroup(track, ticks, fill)
        g.nocheck = True
        g.set_z_index(400)
        return g

    # --- 時間錨點 ---
    def A(self, sid, frac=0.0, off=0.0):
        """第 sid 句念到 frac 比例的時間（場景內秒數）。"""
        s = next(x for x in self.sc["sentences"] if x["id"] == sid)
        return s["start"] + frac * (s["end"] - s["start"]) + off

    def E(self, sid, off=0.0):
        return self.A(sid, 1.0, off)

    def sfx(self, kind, t=None, gain=1.0):
        self.cues.append({"t": round(self.f / config.frame_rate if t is None else t, 3), "kind": kind, "gain": gain})

    def at(self, t, *anims, run_time=0.8, sfx=None, gain=1.0, **kw):
        """等到第 t 秒（精確到影格）播放動畫；同時發生的放在同一個 at()。晚於 t 就記一筆 starts late。"""
        fps = config.frame_rate
        target = round(t * fps)
        if target > self.f:
            self.wait((target - self.f) / fps)
            self.f = target
        elif target < self.f - 1:
            self.problems.append(f"{self.SID}: animation at {t:.2f}s starts late (now {self.f / fps:.2f}s)")
        if sfx:
            for k in (sfx if isinstance(sfx, (list, tuple)) else [sfx]):
                self.sfx(k, gain=gain)
        if anims:
            n = max(1, round(run_time * fps))
            self.play(*anims, run_time=n / fps, **kw)
            self.f += n
        self.t = self.f / fps
        self.check()

    # --- 轉場 ---
    def card_out(self, t=0.75):
        if self.card is None:
            return
        self.at(t, self.card.animate(rate_func=rate_functions.ease_in_cubic).shift(LEFT * (FW + 4)), run_time=0.55, sfx="whoosh", gain=0.8)
        self.remove(self.card)

    def whip_in(self, *mobs, t=0.0, run=0.5):
        g = Group(*mobs)
        g.shift(RIGHT * FW)
        self.add(*mobs)
        self.at(t, g.animate(rate_func=rate_functions.ease_out_cubic).shift(LEFT * FW), run_time=run)

    def content(self):
        return [m for m in self.mobjects if m is not self.hud and not isinstance(m, ImageMobject) and m is not self.card]

    def finish(self, mode=None):
        """場景收尾：card＝下一場有章節時蓋上章節卡；whip＝往左甩出；fade＝淡出；none；
        endscreen＝最後一場：內容淡出，留下 end_screen 秒乾淨畫面給 YouTube 片尾元素。預設依 timeline 判斷。"""
        fps = config.frame_rate
        end = self.sc["frames"]
        last = self.idx + 1 == len(TL_["scenes"])
        if mode is None:
            mode = "endscreen" if last else ("card" if self.next_chapter else "whip")
        if self.f > end:
            self.problems.append(f"{self.SID}: animations overrun the scene by {(self.f - end) / fps:.2f}s")
        if mode == "card":
            n_in = round(0.5 * fps)
            start = end - round(1.15 * fps)
            card = chapter_card(*self.next_chapter)
            card.shift(RIGHT * (FW + 4))
            self.at(start / fps, card.animate(rate_func=rate_functions.ease_out_cubic).shift(LEFT * (FW + 4)), run_time=n_in / fps, sfx="swoosh", gain=0.9)
            self.wait((end - self.f) / fps)
            self.f = end
        elif mode == "whip":
            n = round(0.45 * fps)
            if self.f < end - n:
                self.wait((end - n - self.f) / fps)
                self.f = end - n
            mobs = self.content()
            if mobs:
                self.sfx("whoosh", gain=0.7)
                self.play(Group(*mobs).animate(rate_func=rate_functions.ease_in_cubic).shift(LEFT * FW), run_time=(end - self.f) / fps)
                self.f = end
        elif mode == "endscreen":
            es = round(TL_.get("end_screen", 20) * fps)
            clean = end - es
            n = round(0.8 * fps)
            if self.f > clean - n:
                self.problems.append(f"{self.SID}: 內容侵入片尾畫面時段（{(self.f - clean + n) / fps:.2f}s）")
            else:
                self.wait((clean - n - self.f) / fps)
                self.f = clean - n
            self.play(*[FadeOut(m) for m in self.mobjects if not isinstance(m, ImageMobject)], run_time=n / fps)
            self.f += n
            self.wait(max(0, end - self.f) / fps)
            self.f = end
        elif mode == "fade":
            n = round(0.8 * fps)
            if self.f < end - n:
                self.wait((end - n - self.f) / fps)
                self.f = end - n
            self.play(*[FadeOut(m) for m in self.mobjects if m is not self.hud], FadeOut(self.hud), run_time=(end - self.f) / fps)
            self.f = end
        else:
            if self.f < end:
                self.wait((end - self.f) / fps)
                self.f = end

    def chapter_tag(self, num_, text):
        circ = Circle(0.21).set_fill(GOLD, 1).set_stroke(width=0)
        n = B(str(num_), 0.03, SCREEN).move_to(circ)
        g = VGroup(VGroup(circ, n), T(text, 0.03, MUTED)).arrange(RIGHT, buff=0.15)
        g.move_to([XL, TOP - 0.05, 0], aligned_edge=UL)
        return g

    # --- 嘴型同步（依該說話者的音檔音量） ---
    def lipsync(self, who, speaker="mascot"):
        sents = [s for s in self.sc["sentences"] if s.get("speaker") == speaker]
        envs = []
        for s in sents:
            p = ODIR / f"audio/{s['id']}.wav"
            if not p.exists():
                continue
            with wave.open(str(p)) as w:
                sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.0
            hop = sr // 30
            e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
            e = np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1)
            envs.append((s["start"], e))

        def upd(m):
            t = self.renderer.time
            amp = 0.0
            for st, e in envs:
                k = int((t - st) * 30)
                if 0 <= k < len(e):
                    amp = float(e[k])
            on = amp > 0.08
            w = who.mouth.get_width() * 0.9
            m.stretch_to_fit_width(max(0.05, w)).stretch_to_fit_height(max(0.03, 0.04 + 0.22 * amp * who.eyes[0].height / 0.44))
            m.move_to(who.mouth.get_center())
            m.set_opacity(1 if on else 0)
            who.mouth.set_stroke(opacity=0 if on else 1)
        who.talk.add_updater(upd)

    # --- 版面檢查（每個 at() 之後） ---
    def check(self):
        if not self.zone_check:
            return
        frame = self.camera.frame
        mx, my = S["zones"]["safe_margin_x"], S["zones"]["safe_margin_y"]
        sub_y0 = zone("subtitle")[1]
        for top in self.mobjects:
            if getattr(top, "nocheck", False) or isinstance(top, ImageMobject):
                continue
            skip = {id(x) for p in getattr(top, "nocheck_parts", []) for x in p.get_family()}
            leaves = [x for x in top.family_members_with_points() if isinstance(x, VMobject) and id(x) not in skip
                      and (x.get_fill_opacity() > 0.05 or (x.get_stroke_width() > 0 and x.get_stroke_opacity() > 0.05))]
            if not leaves:
                continue
            b = bbox_in(VGroup(*leaves), frame)
            if b[2] < 0 or b[0] > 1:
                continue
            if b[3] > sub_y0 + 3e-3 or b[0] < mx - 3e-3 or b[2] > 1 - mx + 3e-3 or b[1] < my - 3e-3:
                self.problems.append(f"{self.SID} t={self.t:.2f}s {top.__class__.__name__} outside zones {[round(x, 3) for x in b]}")

    def tear_down(self):
        super().tear_down()
        ODIR.mkdir(parents=True, exist_ok=True)
        (ODIR / f"layout-{self.SID}.txt").write_text("\n".join(dict.fromkeys(self.problems)) or "OK")
        (ODIR / f"sfx-{self.SID}.json").write_text(json.dumps(self.cues))
