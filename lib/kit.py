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
- 示意的數字或例子：v4 起不掛 tag("示意")，由旁白交代是舉例（使用者 2026-11-08）。
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
from manim.renderer.cairo_renderer import CairoRenderer  # noqa: E402


def _freeze_round(self, duration):
    """Manim 的靜止等待用 int() 無條件捨去，浮點誤差會少一格（v001 sc06 少 1 格）；改成四捨五入。"""
    self.add_frame(self.get_frame(), num_frames=int(round(duration * self.camera.frame_rate)))


CairoRenderer.freeze_current_frame = _freeze_round

S = json.loads((ROOT / "config/style.json").read_text())
for f in S["font_files"] + S.get("serif_files", []):
    manimpango.register_font(str(ROOT / f))
SERIF = S.get("serif_font", "STIX Two Text")

# YTV_VIDEO＝影片 ID（lib/render.py 會自動設定）。沒設定時是「設計模式」：可以畫靜態圖（吉祥物、草圖、縮圖），但不能用 Timed。
VID = os.environ.get("YTV_VIDEO", "")
VDIR, ODIR = ROOT / "videos" / VID, ROOT / "out" / (VID or "_design")
TL_ = json.loads((VDIR / "timeline.json").read_text()) if VID else {}
_SCRIPT = json.loads((VDIR / "script.json").read_text()) if VID else {}

# ---------------- 配色 ----------------
BG = S["bg"]["deep"]
config.background_color = BG
FW, FH = config.frame_width, config.frame_height
FONT = S["font"]
TXT, TXT_STRONG, MUTED, DIM = S["text"], S["text_strong"], S["muted"], S["dim"]
GOLD = S["brand"]["gold"]
TEAL, TEAL_L, TEAL_M = S["brand"]["teal"], S["brand"]["teal_light"], S["brand"]["teal_mid"]
GOOD, BAD, NEUTRAL = S["role"]["good"], S["role"]["bad"], S["role"]["neutral"]
LINE = S.get("line", "#5E8C8E")   # 細線、刻度、次要連線
SCREEN, PANEL, SEA = S["bg"]["screen"], S["bg"]["panel"], S["bg"]["sea"]
# 每支影片的概念色：script.json 的 "concepts": {"argmax": 0, "期望值": 1}（索引進 concept_pool），在場景裡用 C["argmax"]
C = {k: S["concept_pool"][i] for k, i in _SCRIPT.get("concepts", {}).items()}


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
    t = Text(s, font=FONT, font_size=fs(frac), color=color, weight=weight)
    t._frac, t._h0 = frac, t.height   # 版面檢查用：之後被 scale 縮小，實際字級仍要 ≥ 下限
    return t


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


def pill(s, color, frac=0.04, fill=0.18, pad=0.24, txt=None, bold=False):
    t = (B if bold else T)(s, frac, txt or color)
    r = RoundedRectangle(corner_radius=min(0.3, (t.height + pad) / 2), width=t.width + 2 * pad, height=t.height + pad)
    r.set_stroke(color, 2.5).set_fill(color, fill)
    g = VGroup(r, t.move_to(r))
    g.box, g.txt = r, t
    return g


def tag(s="示意", color=None, frac=0.038):
    """示意標籤：自己補的數字、例子、重畫的估讀圖都要掛（規格 §5.5、§6.8）。
    v2 風格：小字＋細底線，不用膠囊框（2026-11-07 使用者嫌膠囊像小學生做的）。"""
    return note(s, color or MUTED, frac)


def note(s, color=None, frac=0.038):
    """小註記：純文字＋細底線。"""
    t = T(s, frac, color or MUTED)
    u = Line(t.get_corner(DL), t.get_corner(DR)).shift(DOWN * 0.07).set_stroke(color or MUTED, 1.2, 0.6)
    g = VGroup(t, u)
    g.txt = t
    return g


def M(s, frac=0.06, color=TXT, italic=False):
    """數字與公式：襯線字（STIX Two，OFL）。變數用 italic=True。"""
    if frac < S["min_text_frac"] - 1e-9:
        raise ValueError(f"字太小：{frac} < {S['min_text_frac']}（{s}）")
    t = Text(s, font=SERIF, font_size=fs(frac), color=color, slant=ITALIC if italic else NORMAL)
    t._frac, t._h0 = frac, t.height
    return t


def fraction(num, den, frac=0.06, color=TXT, gap=0.1):
    """分數：分子、分數線、分母（各自可以是字串或 Mobject）。g.num / g.bar / g.den。"""
    n = num if isinstance(num, Mobject) else M(num, frac, color)
    d = den if isinstance(den, Mobject) else M(den, frac, color)
    bar = Line(LEFT, RIGHT).set_stroke(color, 2.2).set_width(max(n.width, d.width) + 0.2)
    g = VGroup(n, bar, d).arrange(DOWN, buff=gap)
    g.num, g.bar, g.den = n, bar, d
    return g


def bgplate(name="glow_center"):
    im = ImageMobject(str(bgplates.ensure(name))).set_z_index(-100)
    im.height = FH
    im.move_to(ORIGIN)
    return im


# ---------------- 吉祥物：錘錘（合體版，2026-11-07 使用者定案） ----------------
# 設計（docs/mascot/）：
#   燈籠臉：金色多面錘身挖一扇暗窗，眼睛是兩顆光點，表情只靠光點形狀；想通時整顆從裡面亮起來（「深處的光」）。
#   繩語：垂直掛著＝「！」；繩子一捲＝「？」（錘身就是問號的點）。招牌動作是 curl() → straighten()：從問題到洞見。
#   指標：尖端是天生的指標（point_at）；繩子可以圈住或畫底線（lasso / underline）。
#   撈樣：真實的測深錘尖端塗油脂黏回海底樣本；錘錘收尾時尖端黏著發光的樣本（sample_on），接 takeaway_card 一句話重點。
# 出場原則：開場、收尾、或真的需要「帶觀眾往下挖」的時刻。不是每場都出現；每支影片另有自己的機制角色（反模板）。

_GOLD_L, _GOLD_D, _GLOW, _ROPE, _WIN = "#F5CD78", "#AA7628", "#FFE7A8", "#C8964A", "#1A1206"


def _P(x, y):
    return np.array([x, y, 0.0])


def _eyes(mood, centers, k=1.0, angle=0.0):
    g = VGroup()
    for c in centers:
        halo = Circle(.17 * k).set_fill(_GLOW, .28).set_stroke(width=0).move_to(c)
        if mood == "happy":
            e = ArcBetweenPoints(c + _P(-.1, -.03) * k, c + _P(.1, -.03) * k, angle=-PI * .75).set_stroke(_GLOW, 7 * k)
        elif mood == "wow":
            e = Circle(.1 * k).set_stroke(_GLOW, 6 * k).move_to(c)
        elif mood == "flat":
            e = Line(c + _P(-.1, 0) * k, c + _P(.1, 0) * k).set_stroke(_GLOW, 7 * k)
        elif mood == "sad":
            e = ArcBetweenPoints(c + _P(-.1, -.06) * k, c + _P(.1, -.06) * k, angle=PI * .6).set_stroke(_GLOW, 7 * k)
        elif mood == "think":    # 眼珠往右上看
            e = Dot(c + _P(.05, .05) * k, radius=.075 * k, color=_GLOW)
        elif mood == "closed":
            e = ArcBetweenPoints(c + _P(-.1, .0) * k, c + _P(.1, .0) * k, angle=PI * .5).set_stroke(_GLOW, 6 * k)
        elif mood == "squint":   # 懷疑：一邊線一邊點
            e = Line(c + _P(-.1, .02) * k, c + _P(.1, -.02) * k).set_stroke(_GLOW, 7 * k) if c is centers[0] else Dot(c, radius=.085 * k, color=_GLOW)
        else:
            e = Dot(c, radius=.085 * k, color=_GLOW)
        if angle:
            e.rotate(angle, about_point=c)
        g.add(VGroup(halo, e))
    return g


class Plumb(VGroup):
    """頻道吉祥物「錘錘」。用 place(點) 擺位置（點＝錘身中心；繩子自動往上接到畫面外）。
    動作（都回傳動畫 list，丟進 Timed.at(...) 用 * 展開）：
      mood("neutral|happy|flat|wow|squint")、look(方向)、blink()、
      curl()（繩子捲成「？」）、straighten()（拉直成「！」）、point_at(點)、upright()、
      light_on()/light_off()（從內部發光）、sample_on()（尖端黏著發光樣本）、swing()、dive(距離)。
    說話：script 的 speaker 寫 mascot，場景呼叫 self.lipsync(plumb)；說話時眼睛的光暈隨音量變亮。"""

    def __init__(self, scale=0.6, top_y=None):
        super().__init__()
        self.k, self.angle = scale, 0.0
        self.top_y = FH / 2 + .6 if top_y is None else top_y   # 繩子往上接到哪（鏡頭移動的場景要設成畫面上緣之外）
        cap = RoundedRectangle(corner_radius=.08, width=.68, height=.38).set_fill(_GOLD_D, 1).set_stroke(width=0).move_to(_P(0, 1.31))
        neck = Rectangle(width=.52, height=.2).set_fill(_GOLD_D, 1).set_stroke(width=0).move_to(_P(0, 1.07))
        body = Polygon(_P(-.95, .6), _P(-.6, 1.0), _P(.6, 1.0), _P(.95, .6), _P(0, -1.7)).set_fill(GOLD, 1).set_stroke(width=0)
        left = Polygon(_P(-.95, .6), _P(-.6, 1.0), _P(-.2, 1.0), _P(-.35, .6), _P(0, -1.7)).set_fill(_GOLD_L, 1).set_stroke(width=0)
        right = Polygon(_P(.95, .6), _P(.6, 1.0), _P(.25, 1.0), _P(.4, .6), _P(0, -1.7)).set_fill(_GOLD_D, 1).set_stroke(width=0)
        ridge = Line(_P(-.95, .6), _P(.95, .6)).set_stroke(_GOLD_D, 2, .6)
        win = RoundedRectangle(corner_radius=.22, width=1.32, height=.46).set_fill(_WIN, 1).set_stroke(_GOLD_D, 3).move_to(_P(0, .38))
        self.eyes = _eyes("neutral", [_P(-.3, .38), _P(.3, .38)])
        self.hook = Dot(_P(0, 1.5), radius=.001).set_opacity(0)          # 繩子的接點
        self.tip = Dot(_P(0, -1.7), radius=.001).set_opacity(0)          # 尖端（指標、樣本的位置）
        self.sample = VGroup(Circle(.5).set_fill(GOLD, .25).set_stroke(width=0), Dot(radius=.2, color=_GLOW)).move_to(_P(0, -1.7)).set_opacity(0)
        self.facets = VGroup(body, left, right)
        self.bob = VGroup(cap, neck, body, left, right, ridge, win, self.eyes, self.hook, self.tip, self.sample)
        self.halo = Circle(1.6).set_fill(GOLD, .14).set_stroke(width=0).move_to(_P(0, .1)).set_opacity(0)
        self.rays = VGroup(*[Line(_P(np.cos(a), np.sin(a)) * 1.3 + _P(0, .1), _P(np.cos(a), np.sin(a)) * 1.85 + _P(0, .1)).set_stroke(GOLD, 5, .8)
                             for a in np.linspace(0, TAU, 10, endpoint=False)]).set_opacity(0)
        VGroup(self.bob, self.halo, self.rays).scale(scale, about_point=ORIGIN)
        self.rope = self._straight_rope()
        self.rope.nocheck = True     # 繩子刻意伸出畫面上緣（越界不算）
        self.rope.rope_check = True  # 但繩子穿過文字仍要抓
        self.nocheck_parts = [self.rope]
        self.bodyg = VGroup(self.halo, self.rays, self.bob)   # 常駐的子群組：旋轉、彈跳都對它做（臨時 VGroup 會被 Manim 拆出 Plumb）
        self.add(self.rope, self.bodyg)

    # --- 位置與繩子 ---
    def center(self):
        return self.facets.get_center()

    def place(self, point):
        d = np.array(point) - self.center()
        self.bodyg.shift(d) if hasattr(self, "bodyg") else VGroup(self.bob, self.halo, self.rays).shift(d)
        self.rope.become(self._straight_rope())
        return self

    def _rope(self, pts):
        return VMobject().set_points_smoothly([np.array(p) for p in pts]).set_stroke(_ROPE, max(3, 9 * self.k))

    def _straight_rope(self):
        h = self.hook.get_center()
        top = self.top_y
        return self._rope([h + _P(0, (top - h[1]) * i / 8) for i in range(9)])

    def _question_rope(self):
        h, k = self.hook.get_center(), self.k / .6
        offs = [(0, 0), (0, .3), (.15, .62), (.55, .9), (.62, 1.38), (.28, 1.72), (-.22, 1.72), (-.6, 1.4), (-.64, 1.0)]
        return self._rope([h + _P(x * k, y * k) for x, y in offs])

    def curl(self):
        return [Transform(self.rope, self._question_rope(), rate_func=rate_functions.ease_in_out_back)]

    def set_curled(self, mood=None):
        """不播動畫，直接設成「？」狀態（場景接續上一場時用）；mood 一起設定表情。"""
        self.rope.become(self._question_rope())
        if mood:
            self.eyes.become(_eyes(mood, self._eye_centers(), self.k, self.angle))
        return self

    def set_mood(self, mood):
        """不播動畫，直接設定表情。"""
        self.eyes.become(_eyes(mood, self._eye_centers(), self.k, self.angle))
        return self

    def straighten(self):
        return [Transform(self.rope, self._straight_rope(), rate_func=rate_functions.ease_in_out_back)]

    # --- 表情 ---
    def _eye_centers(self):
        return [g[0].get_center() for g in self.eyes]

    def mood(self, m):
        return [Transform(self.eyes, _eyes(m, self._eye_centers(), self.k, self.angle))]

    def look(self, v):
        v = np.array(v, dtype=float) * .06 * self.k
        return [g[1].animate.move_to(g[0].get_center() + v) for g in self.eyes]

    def blink(self):
        return [self.eyes.animate(rate_func=there_and_back, run_time=.25).stretch(.1, 1)]

    def speak(self, amp):
        for g in self.eyes:
            g[0].set_fill(_GLOW, .28 + .6 * amp)

    # --- 發光、樣本 ---
    def light_on(self):
        return [self.halo.animate.set_opacity(1).set_fill(GOLD, .14), self.rays.animate.set_opacity(1).set_stroke(GOLD, 5, .8),
                self.facets[0].animate.set_fill(_GLOW, 1), self.facets[1].animate.set_fill("#FFF3D0", 1), self.facets[2].animate.set_fill(GOLD, 1)]

    def light_off(self):
        return [self.halo.animate.set_opacity(0), self.rays.animate.set_opacity(0),
                self.facets[0].animate.set_fill(GOLD, 1), self.facets[1].animate.set_fill(_GOLD_L, 1), self.facets[2].animate.set_fill(_GOLD_D, 1)]

    def sample_on(self):
        return [self.sample[0].animate.set_fill(GOLD, .25), self.sample[1].animate.set_opacity(1)]

    # --- 指、擺、潛 ---
    def point_at(self, target):
        c = self.center()
        v = np.array(target) - c
        want = np.arctan2(v[1], v[0]) + PI / 2       # 尖端原本朝下（-90°）
        delta = (want - self.angle + PI) % TAU - PI
        self.angle += delta
        h = self.hook.get_center() - c
        h2 = c + np.array([h[0] * np.cos(delta) - h[1] * np.sin(delta), h[0] * np.sin(delta) + h[1] * np.cos(delta), 0])
        top = _P(self.rope.get_end()[0], self.top_y)
        mid = (top + h2) / 2 + _P(-.6 * np.sign(delta), 0)
        new_rope = self._rope([top, (top + mid) / 2, mid, (mid + h2) / 2, h2])
        return [Rotate(self.bob, delta, about_point=c), Rotate(self.halo, delta, about_point=c), Transform(self.rope, new_rope)]

    def upright(self):
        c = self.center()
        d = -self.angle
        self.angle = 0.0
        tmp = self.bob.copy().rotate(d, about_point=c)
        h = tmp[8].get_center()
        top = self.top_y
        return [Rotate(self.bob, d, about_point=c), Rotate(self.halo, d, about_point=c),
                Transform(self.rope, self._rope([h + _P(0, (top - h[1]) * i / 8) for i in range(9)]))]

    # --- 生動一點的動作（2026-11-07 使用者：表情和動作可以再生動） ---
    def _body(self):
        return self.bodyg

    def hop(self, h=.3):
        """彈跳＋擠壓伸展：先壓扁、彈起拉長、落地再壓扁回正。"""
        body = self._body()
        base = body.copy()
        rope0 = self.rope.copy()

        def upd(m, a):
            y = h * np.sin(PI * a)
            sq = 1 - .18 * np.sin(2 * PI * a) if a < .5 else 1 + .12 * np.sin(2 * PI * (a - .5))
            body.become(base.copy().stretch(sq, 1, about_edge=DOWN).shift(UP * y))
            self.rope.become(rope0.copy().shift(UP * y))
        return [UpdateFromAlphaFunc(self, upd, rate_func=linear)]

    def nod(self, n=2, angle=.18):
        """點頭（同意、恍然大悟）。"""
        c = self.hook.get_center()
        return [Rotate(self._body(), angle, about_point=c, rate_func=lambda t: np.sin(n * PI * t) * (1 - t))]

    def shake_head(self, n=3, angle=.12):
        """搖頭（不對、不是這樣）。"""
        c = self.hook.get_center()
        return [Rotate(self._body(), angle, about_point=c, rate_func=lambda t: np.sin(2 * n * PI * t) * (1 - t))]

    def tilt(self, angle=.25):
        """歪頭（疑惑）；再呼叫 tilt(-angle) 回正。"""
        return [Rotate(self._body(), angle, about_point=self.hook.get_center())]

    def emote(self, sym="？", color=None, side=RIGHT):
        """頭上冒出一個符號（？！…），回傳 (物件, 出現動畫)；之後自己 FadeOut。"""
        t = Text(sym, font=FONT, font_size=fs(.07 * self.k / .3), color=color or GOLD, weight=BOLD)
        t._frac, t._h0 = .07 * self.k / .3, t.height
        t.move_to(self.facets.get_corner(UP + side) + (side * .25 + UP * .35) * self.k / .3)
        t.overlap_ok = True
        return t, [GrowFromPoint(t, self.facets.get_top(), rate_func=rate_functions.ease_out_back)]

    def swing(self, angle=.15, run=1.2):
        return [Rotate(self, angle, about_point=self.rope.get_end() if self.rope.get_end()[1] > self.rope.get_start()[1] else self.rope.get_start(),
                       rate_func=there_and_back, run_time=run)]

    def dive(self, dist=1.5):
        g = self.bodyg
        top = FH / 2 + .6
        h = self.hook.get_center() + DOWN * dist
        top = self.top_y
        return [g.animate.shift(DOWN * dist), Transform(self.rope, self._rope([h + _P(0, (top - h[1]) * i / 8) for i in range(9)]))]


def takeaway_card(lines, frac=.055, w=None):
    """收尾（v3 細線風格）：小字「這集重點」＋左側一條金色細線＋重點句（米白）。不用框、不用粗體。內容要過查核。"""
    body = VGroup(*[T(s, frac, TXT_STRONG) for s in ([lines] if isinstance(lines, str) else lines)]).arrange(DOWN, buff=.28, aligned_edge=LEFT)
    head = T("這集重點", .04, GOLD)
    inner = VGroup(head, body).arrange(DOWN, buff=.35, aligned_edge=LEFT)
    rule = Line(UP, DOWN).set_stroke(GOLD, 2, .9).set_height(inner.height + .2).next_to(inner, LEFT, buff=.35)
    g = VGroup(rule, inner)
    g.rule, g.head, g.body = rule, head, body
    return g


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


class Highlight(Indicate):
    """強調但不把底色填滿（v001 逐格檢查，2026-11-10）。Indicate 用 set_color 把整組換色：
    有不透明底色的卡片會變成一整塊強調色，字母或星星看不見。這裡「有外框又有不透明底色」的形狀只換外框色並加粗，
    其他部分（文字、線、沒有外框的圖示）照常換色；一樣放大再回來。卡片、方框一律用它，不要用 Indicate。"""

    def __init__(self, mobject, color=GOLD, scale_factor=1.12, inner=True, **kw):
        self.inner = inner        # False：裡面的字母／圖示保留原色（例如綠星一直是綠的），只有外框變色
        super().__init__(mobject, scale_factor=scale_factor, color=color, **kw)

    def create_target(self):
        t = self.mobject.copy().scale(self.scale_factor)
        for x in t.family_members_with_points():
            if not isinstance(x, VMobject):
                continue
            if x.get_stroke_width() > 0 and x.get_fill_opacity() > 0.5:
                x.set_stroke(self.color, width=x.get_stroke_width() * 1.7, family=False)
            elif self.inner:
                x.set_color(self.color, family=False)
        return t


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

    def __init__(self, items, vmax, w=6.0, rowh=0.7, frac=0.04, fmt="{:.1f}%", label_w=2.4):
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


def coin(color=GOLD, r=0.2, label=None, frac=0.038):
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


# ---------------- 章節標題、進度條 ----------------
def chapter_card(n, title, subtitle=None):
    """章節標題（v3，2026-11-08）：主畫面正中，細金線上方是襯線數字、下方是章名。不用整面色塊掃過。
    上一場收尾時寫出來；下一場開頭由 open_chapter() 把它變形成左上角的章節標籤（同一個物件縮過去，不是換一個）。"""
    nn = M(str(n), .085, GOLD)
    rule = Line(LEFT * .9, RIGHT * .9).set_stroke(GOLD, 1.5, .8)
    ttl = T(title, .062, TXT_STRONG)
    g = VGroup(nn, rule, ttl).arrange(DOWN, buff=.28).move_to([0, MIDY, 0])
    g.num, g.rule, g.ttl = nn, rule, ttl
    g.chrome = True
    return g


def chapter_tag_mob(n, text):
    nn = M(str(n), .045, GOLD)
    rule = Line(UP * .14, DOWN * .14).set_stroke(GOLD, 1.5, .8)
    t = T(text, .038, MUTED)
    g = VGroup(nn, rule, t).arrange(RIGHT, buff=.18)
    g.move_to([XL, TOP + .02, 0], aligned_edge=UL)
    g.num, g.rule, g.ttl = nn, rule, t
    g.chrome = True
    return g


def bbox_in(m, frame):
    c, fw, fh = frame.get_center(), frame.width, frame.height
    return [(m.get_left()[0] - c[0]) / fw + 0.5, 0.5 - (m.get_top()[1] - c[1]) / fh,
            (m.get_right()[0] - c[0]) / fw + 0.5, 0.5 - (m.get_bottom()[1] - c[1]) / fh]


class Timed(MovingCameraScene):
    """旁白錨定的場景基底。時間全部來自 timeline.json（旁白先行），不寫絕對秒數。"""
    SID = None
    BG = "glow_center"
    LAY = S.get("layout", {})
    HUD = False      # v4：不放頂端進度條（框架元素讓畫面像投影片）
    CARDS = False    # v4：不放章節卡與角落章節標籤；章節只寫進 YouTube 說明欄（chapters.txt）

    def setup(self):
        super().setup()
        self.problems, self.cues = [], []
        self.sc = next(s for s in TL_["scenes"] if s["id"] == self.SID)
        self.idx = [s["id"] for s in TL_["scenes"]].index(self.SID)
        self.t, self.f = 0.0, 0
        self.zone_check = True
        self.last_anim_end = 0.0
        self.seen = {}          # id(頂層物件) → [出現時間, 物件]（停留時間檢查）
        self.balance_log = []   # (時間, 內容中心偏移, 內容高度比例)
        self.first_anim = None  # 第一個動作開始的時間（接縫空檔檢查，lib/checks/seams.py）
        self.faded = set()      # 被 FadeOut／Uncreate 這類動畫拿掉的物件（停留檢查只看這些；鏡頭移開、變形成別的不算）
        bg = self.sc.get("bg", self.BG)
        if bg != "flat":                 # flat＝平面底色（v4 預設；鏡頭移動時背景也不會露邊）
            self.add(bgplate(bg))
        self.hud = self.make_hud() if self.HUD else VGroup()
        if self.HUD:
            self.add(self.hud)
        self.chap_now = self.sc.get("chapter") if self.CARDS else None
        nxt = TL_["scenes"][self.idx + 1] if self.idx + 1 < len(TL_["scenes"]) else None
        self.next_chapter = nxt.get("chapter") if (nxt and self.CARDS) else None
        self.card = None
        if self.chap_now:
            self.card = chapter_card(*self.chap_now)
            self.add(self.card)

    def make_hud(self):
        """頂端的細進度條（全片時間），章節處有刻度。"""
        total = TL_["duration"] - TL_.get("end_screen", 0)
        starts = [s["start"] for s in TL_["scenes"] if s.get("chapter")]
        y = FH / 2 - 0.16
        x0, x1 = -FW / 2 + 0.3, FW / 2 - 0.3
        track = Line([x0, y, 0], [x1, y, 0]).set_stroke(TXT, 2, 0.1)
        ticks = VGroup(*[Line([x0 + (x1 - x0) * st / total, y - 0.05, 0], [x0 + (x1 - x0) * st / total, y + 0.05, 0]).set_stroke(TXT, 1.5, 0.3) for st in starts])
        t0 = self.sc["start"]
        fill = Line([x0, y, 0], [x0 + 0.001, y, 0]).set_stroke(GOLD, 2, 0.8)

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
        self.anim_start = self.f / fps

        def _flat(xs):
            for x in xs:
                yield x
                yield from _flat(getattr(x, "animations", []) or [])
        self.faded |= {id(a.mobject) for a in _flat(anims) if getattr(a, "remover", False)}
        if anims:
            if self.first_anim is None:
                self.first_anim = self.anim_start
            n = max(1, round(run_time * fps))
            paused = self._pause_live(list(_flat(anims)))
            self.play(*anims, run_time=n / fps, **kw)
            for x, ups in paused:
                for u in ups:
                    x.add_updater(u)
            self.f += n
            self.last_anim_end = self.f / fps
        self.t = self.f / fps
        self.check()

    def _pause_live(self, anims):
        """Transform 類動畫（FadeIn／FadeOut／Indicate／Highlight／GrowFromEdge／.animate…）播放期間，
        暫停被動畫物件（和包住它的群組）的 updater，播完由 at() 恢復。
        原因（v001 逐格檢查，2026-11-10）：Transform 會複製物件，複本也帶著 updater，每格被重畫回原樣。
        結果是 Live 讀數、always_redraw 圖形做 FadeOut 不會淡（結束時一次消失）、FadeIn／GrowFromEdge 直接跳出來、
        Indicate 沒反應。Write／Create 不受影響，不暫停。"""
        paused, seen = [], set()

        def hold(x):
            if x.updaters and id(x) not in seen:
                seen.add(id(x))
                x.update(0)                      # 先更新到現在的值，再凍結
                paused.append((x, list(x.updaters)))
                x.clear_updaters(recursive=False)
        for a in anims:
            if not isinstance(a, Transform) or a.mobject is None:
                continue
            for m in (a.mobject, getattr(a, "target_mobject", None)):
                if m is not None:
                    for x in m.get_family():
                        hold(x)
            # 被動畫的是某個 always_redraw 群組裡的子物件：包住它的群組自己的 updater 也要停
            for top in self.mobjects:
                fam = top.get_family()
                if top is a.mobject or not any(x is a.mobject for x in fam):
                    continue
                for x in fam:
                    if x is not a.mobject and any(y is a.mobject for y in x.get_family()):
                        hold(x)
        return paused

    # --- 鏡頭（v4：一張大圖，鏡頭跟著走） ---
    @staticmethod
    def view(p, width=None):
        """讓世界座標 p 落在主畫面中心時，鏡頭中心該在哪（主畫面中心比畫面中心高 MIDY）。"""
        w = width or FW
        return np.array(p, dtype=float) - UP * MIDY * w / FW

    def cam_set(self, p, width=None):
        """不播動畫，直接設定鏡頭（場景開頭接上一場最後一格用）。"""
        self.camera.frame.set(width=width or FW).move_to(self.view(p, width))

    def cam(self, p, width=None):
        """鏡頭移到 p（世界座標，會落在主畫面中心），寬度 width。回傳動畫，放進 at()。"""
        return self.camera.frame.animate.set(width=width or FW).move_to(self.view(p, width))

    def screen_pt(self, fx, fy):
        """畫面比例座標（0–1，左上原點）→ 目前鏡頭下的世界座標。"""
        f = self.camera.frame
        return f.get_center() + np.array([(fx - .5) * f.width, (.5 - fy) * f.height, 0])

    # --- 轉場（v3：不甩、不掃；內容淡出、章名在正中寫出，下一場把章名縮成左上角標籤） ---
    def open_chapter(self, t=0.35, run=0.7):
        """場景開頭：上一場留下的章節標題變形成左上角標籤。回傳標籤。"""
        if self.card is None:
            return None
        tag_ = chapter_tag_mob(*self.chap_now)
        self.at(t, ReplacementTransform(self.card, tag_), run_time=run)
        self.tag_mob = tag_
        return tag_

    def card_out(self, t=0.35):   # 舊名，相容
        return self.open_chapter(t)

    def content(self):
        return [m for m in self.mobjects if m is not self.hud and m is not self.camera.frame and not isinstance(m, ImageMobject)]

    def _hold_check(self, exit_start):
        fps = config.frame_rate
        hold = exit_start / fps - self.last_anim_end
        need = self.LAY.get("min_end_hold", 2.0)
        if hold < need - 1e-3:
            self.problems.append(f"{self.SID}: 收尾停留只有 {hold:.2f}s（至少 {need}s）：最後一個動作結束後要讓觀眾看清楚再轉場")

    def finish(self, mode=None):
        """場景收尾：card＝內容淡出、正中寫出下一章的章名；fade＝內容淡出；none；
        endscreen＝最後一場：內容淡出，留下 end_screen 秒乾淨畫面。預設依 timeline 判斷。
        轉場開始前，最後一個動作至少要停 min_end_hold 秒（程式檢查）。"""
        fps = config.frame_rate
        end = self.sc["frames"]
        last = self.idx + 1 == len(TL_["scenes"])
        if mode is None:
            mode = "endscreen" if last else ("card" if self.next_chapter else ("none" if not self.CARDS else "fade"))
        if self.f > end:
            self.problems.append(f"{self.SID}: animations overrun the scene by {(self.f - end) / fps:.2f}s")
        nf = round(0.6 * fps)
        if mode == "card":
            nw = round(0.8 * fps)
            start = end - nf - nw - round(0.35 * fps)
            self._hold_check(start)
            if self.f < start:
                self.wait((start - self.f) / fps)
                self.f = start
            mobs = [m for m in self.content()]
            self.sfx("swoosh", gain=0.5)
            self.play(*[FadeOut(m) for m in mobs], run_time=nf / fps)
            self.f += nf
            card = chapter_card(*self.next_chapter)
            self.play(LaggedStart(FadeIn(card.num, shift=UP * .1), Create(card.rule), Write(card.ttl), lag_ratio=.25), run_time=nw / fps)
            self.f += nw
            self.wait(max(0, end - self.f) / fps)
            self.f = end
        elif mode == "endscreen":
            es = round(TL_.get("end_screen", 20) * fps)
            clean = end - es
            n = round(0.8 * fps)
            self._hold_check(clean - n)
            if self.f > clean - n:
                self.problems.append(f"{self.SID}: 內容侵入片尾畫面時段（{(self.f - clean + n) / fps:.2f}s）")
            else:
                self.wait((clean - n - self.f) / fps)
                self.f = clean - n
            self.play(*[FadeOut(m) for m in self.content()], run_time=n / fps)
            self.f += n
            self.wait(max(0, end - self.f) / fps)
            self.f = end
        elif mode == "fade":
            self._hold_check(end - nf)
            if self.f < end - nf:
                self.wait((end - nf - self.f) / fps)
                self.f = end - nf
            self.play(*[FadeOut(m) for m in self.content()], run_time=(end - self.f) / fps)
            self.f = end
        else:
            if self.f < end:
                self.wait((end - self.f) / fps)
                self.f = end

    def chapter_tag(self, num_, text):
        return chapter_tag_mob(num_, text)

    # --- 嘴型同步（依該說話者的音檔音量） ---
    def lipsync(self, who, speaker="mascot"):
        """依該說話者的音檔音量驅動角色：有 speak(amp) 的角色（錘錘）用它；否則開合 who.talk（PoC 機器人式的嘴）。"""
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

        def amp_now():
            t = self.renderer.time
            for st, e in envs:
                k = int((t - st) * 30)
                if 0 <= k < len(e):
                    return float(e[k])
            return 0.0

        if hasattr(who, "speak"):
            who.eyes.add_updater(lambda m: who.speak(amp_now()))
            return

        def upd(m):
            amp = amp_now()
            on = amp > 0.08
            w = who.mouth.get_width() * 0.9
            m.stretch_to_fit_width(max(0.05, w)).stretch_to_fit_height(max(0.03, 0.04 + 0.22 * amp * who.eyes[0].height / 0.44))
            m.move_to(who.mouth.get_center())
            m.set_opacity(1 if on else 0)
            who.mouth.set_stroke(opacity=0 if on else 1)
        who.talk.add_updater(upd)

    # --- 版面檢查（每個 at() 之後） ---
    # (1) 越界：超出安全邊界或壓到字幕區；(2) 元素重疊：兩個頂層元素部分重疊；(3) 實際字級：被 scale 縮到低於下限；
    # (4) 字壓字：任兩段文字的框重疊（不看 overlap_ok，只看 cross_ok）；(5) 線穿字、線穿點：細線經過別人的文字或圓點；
    # (6) 版面平衡：內容的中心偏離主畫面中心、或內容太扁（擠在上半部）；(7) 停留：元素出現不到 min_dwell 秒就被拿掉。
    # 刻意的重疊（印章蓋在東西上）在物件設 overlap_ok = True；刻意讓線穿過文字（刪除線）設 cross_ok = True；
    # 刻意一閃而過的設 transient = True。章節標籤等「框架」元素設 chrome = True（不算進版面平衡）。
    OVERLAP_MIN, OVERLAP_MAX = 0.04, 0.85

    def _visible_bbox(self, top, frame):
        skip = {id(x) for p in getattr(top, "nocheck_parts", []) for x in p.get_family()}
        skip |= {id(x) for x in top.get_family() if getattr(x, "nocheck", False)}
        leaves = [x for x in top.family_members_with_points() if isinstance(x, VMobject) and id(x) not in skip
                  and (x.get_fill_opacity() > 0.05 or (x.get_stroke_width() > 0 and x.get_stroke_opacity() > 0.05))]
        return bbox_in(VGroup(*leaves), frame) if leaves else None

    @staticmethod
    def _label(m):
        if isinstance(m, Text):
            return f"「{m.text[:12]}」"
        t = next((x for x in m.get_family() if isinstance(x, Text)), None)
        return f"{m.__class__.__name__}「{t.text[:12]}」" if t is not None else m.__class__.__name__

    @staticmethod
    def _flag(m, top, name):
        return getattr(m, name, False) or getattr(top, name, False)

    def _solids(self, top):
        """頂層物件裡看得見的實心部件（文字、填色形狀），回傳 (物件, 左下, 右上)。"""
        out, stack = [], [top]
        while stack:
            m = stack.pop()
            if getattr(m, "nocheck", False) or getattr(m, "overlap_ok", False) and m is not top:
                continue
            if isinstance(m, Text):
                if m.get_fill_opacity() > 0.3 and m.text.strip():
                    out.append((m, m.get_corner(DL)[:2], m.get_corner(UR)[:2]))
                continue
            if isinstance(m, VMobject) and m.has_points() and m.get_fill_opacity() > 0.3 and m.width > 0.02:
                out.append((m, m.get_corner(DL)[:2], m.get_corner(UR)[:2]))
            stack.extend(m.submobjects)
        return out

    def _parts(self, top):
        """頂層物件裡看得見的文字、細線、圓點。"""
        texts, lines, dots = [], [], []
        stack = [(top, False, False)]
        while stack:
            m, cross, nchk = stack.pop()
            cross = cross or getattr(m, "cross_ok", False)
            if getattr(m, "rope_check", False):
                lines.append((m, cross))
                continue
            nchk = nchk or getattr(m, "nocheck", False)
            if nchk:
                continue
            if isinstance(m, Text):
                if m.get_fill_opacity() > 0.3 and len(m.text.strip()) > 0:
                    texts.append((m, cross))
                continue
            if isinstance(m, Dot) or (isinstance(m, Circle) and m.get_fill_opacity() > 0.5):
                if m.get_fill_opacity() > 0.3:
                    dots.append((m, cross))
                continue
            if isinstance(m, VMobject) and m.has_points() and m.get_fill_opacity() < 0.05 and m.get_stroke_width() > 0 \
                    and m.get_stroke_opacity() > 0.3 and max(m.width, m.height) > 0.5:
                if getattr(top, "dots_ok", False):
                    m.dots_ok = True
                lines.append((m, cross))
            stack.extend((c, cross, nchk) for c in m.submobjects)
        return texts, lines, dots

    def check(self):
        if not self.zone_check:
            return
        L = self.LAY
        frame = self.camera.frame
        mx, my = S["zones"]["safe_margin_x"], S["zones"]["safe_margin_y"]
        sub_y0 = zone("subtitle")[1]
        boxes, visible = [], set()
        for top in self.mobjects:
            if getattr(top, "nocheck", False) or isinstance(top, ImageMobject) or top is self.hud or top is self.camera.frame:
                continue
            b = self._visible_bbox(top, frame)
            if b is None:
                continue
            if b[2] < 0 or b[0] > 1 or b[3] < 0 or b[1] > 1:
                continue
            visible.add(id(top))
            # 鏡頭移動時，長線條本來就會延伸到畫面外（只有線、沒有字和填色），不算越界
            off_cam = b[0] < 0 or b[2] > 1 or b[1] < 0 or b[3] > 1
            line_only = not any(isinstance(x, Text) or (x.has_points() and x.get_fill_opacity() > .05)
                                for x in top.family_members_with_points() if isinstance(x, VMobject))
            if off_cam and line_only:
                boxes.append((top, b))
                continue
            if b[3] > sub_y0 + 3e-3 or b[0] < mx - 3e-3 or b[2] > 1 - mx + 3e-3 or b[1] < my - 3e-3:
                self.problems.append(f"{self.SID} t={self.t:.2f}s {self._label(top)} outside zones {[round(float(x), 3) for x in b]}")
            boxes.append((top, b))
            for x in top.get_family():
                if getattr(x, "_frac", None) and x._h0 > 0 and x.get_fill_opacity() > 0.05:
                    eff = x._frac * x.height / x._h0 * FW / frame.width   # 鏡頭拉遠，字也跟著變小
                    if eff < S["min_text_frac"] - 1e-3:
                        self.problems.append(f"{self.SID} t={self.t:.2f}s 字被縮小到 {eff:.3f}（下限 {S['min_text_frac']}）：{x.text[:12]}")
        sol = [(top, self._solids(top)) for top, _ in boxes]
        for i in range(len(sol)):
            for j in range(i + 1, len(sol)):
                (ma, A_), (mb, B_) = sol[i], sol[j]
                if getattr(ma, "overlap_ok", False) or getattr(mb, "overlap_ok", False):
                    continue
                hit = None
                for xa, a0, a1 in A_:
                    for xb, b0, b1 in B_:
                        w = min(a1[0], b1[0]) - max(a0[0], b0[0])
                        h = min(a1[1], b1[1]) - max(a0[1], b0[1])
                        if w <= 0 or h <= 0:
                            continue
                        small = min((a1 - a0).prod(), (b1 - b0).prod())
                        r = w * h / max(small, 1e-9)
                        if self.OVERLAP_MIN < r < self.OVERLAP_MAX:
                            hit = (r, xa, xb)
                            break
                    if hit:
                        break
                if hit:
                    self.problems.append(f"{self.SID} t={self.t:.2f}s 重疊 {hit[0]:.0%}：{self._label(ma)}／{self._label(hit[1])} × {self._label(mb)}／{self._label(hit[2])}")
        self._fine_check([t for t, _ in boxes])
        self._balance([(t, b) for t, b in boxes if not getattr(t, "chrome", False)])
        # 停留時間
        now = self.t
        for top, _ in boxes:
            if id(top) not in self.seen:
                self.seen[id(top)] = [now, top]
        for k in list(self.seen):
            if k not in visible:
                t0, m = self.seen.pop(k)
                dwell = getattr(self, "anim_start", now) - t0
                if k in self.faded and dwell < L.get("min_dwell", 1.5) - 1e-3 and not getattr(m, "transient", False) \
                        and not getattr(m, "chrome", False):
                    self.problems.append(f"{self.SID} t={t0:.2f}s {self._label(m)} 只停留 {dwell:.2f}s 就被拿掉（至少 {L.get('min_dwell', 1.5)}s）")

    def _fine_check(self, tops):
        pad = self.LAY.get("line_text_pad", 0.06)
        T_, Ln, Dt = [], [], []
        for k, top in enumerate(tops):
            a, b, c = self._parts(top)
            T_ += [(m, cr, k) for m, cr in a]
            Ln += [(m, cr, k) for m, cr in b]
            Dt += [(m, cr, k) for m, cr in c]
        boxes = [(m, cr, k, m.get_corner(DL)[:2], m.get_corner(UR)[:2]) for m, cr, k in T_]
        # 字壓字
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ma, ca, _, a0, a1 = boxes[i]
                mb, cb, _, b0, b1 = boxes[j]
                if ca or cb:
                    continue
                w = min(a1[0], b1[0]) - max(a0[0], b0[0])
                h = min(a1[1], b1[1]) - max(a0[1], b0[1])
                if w > 0.02 and h > 0.02:
                    small = min((a1 - a0).prod(), (b1 - b0).prod())
                    if w * h > 0.08 * small:
                        self.problems.append(f"{self.SID} t={self.t:.2f}s 字壓字：{self._label(ma)} × {self._label(mb)}")
        # 線穿字、線穿點
        for ln, cr, k in Ln:
            if cr:
                continue
            pts = np.array([ln.point_from_proportion(u) for u in np.linspace(0.02, 0.98, 80)])[:, :2]
            ends = np.array([ln.get_start()[:2], ln.get_end()[:2]])
            for m, tcr, tk, lo, hi in boxes:
                if tcr:
                    continue
                inside = np.all((pts > lo - pad) & (pts < hi + pad), axis=1)
                if inside.sum() >= 2:
                    self.problems.append(f"{self.SID} t={self.t:.2f}s 線穿過文字：{self._label(ln)} × {self._label(m)}")
            for d, dcr, dk in Dt:
                if dcr or getattr(ln, "dots_ok", False):
                    continue
                c, r = d.get_center()[:2], d.width / 2
                if np.min(np.linalg.norm(ends - c, axis=1)) < r + 0.08:   # 線的端點接在這個點上：正常
                    continue
                if np.min(np.linalg.norm(pts - c, axis=1)) < r * 0.9:
                    self.problems.append(f"{self.SID} t={self.t:.2f}s 線穿過圓點：{self._label(ln)} 經過 {self._label(d)}")

    def _balance(self, boxes):
        if not boxes or self.t < 0.5:
            return
        x0 = min(b[0] for _, b in boxes); y0 = min(b[1] for _, b in boxes)
        x1 = max(b[2] for _, b in boxes); y1 = max(b[3] for _, b in boxes)
        mz = zone("main")
        mh = mz[3] - mz[1]
        off = ((y0 + y1) / 2 - (mz[1] + mz[3]) / 2) / mh   # 正＝偏下，負＝偏上
        fill = (y1 - y0) / mh
        self.balance_log.append((self.t, off, fill))

    def _balance_report(self):
        L = self.LAY
        tol, mf = L.get("balance_tol", 0.14), L.get("min_fill_h", 0.45)
        log = self.balance_log
        bad = []
        for (t, off, fill), nxt in zip(log, log[1:] + [(self.f / config.frame_rate, 0, 0)]):
            dur = nxt[0] - t
            if dur <= 0:
                continue
            # 偏上／偏下；或內容夠多（> mf 的一半高）卻把主畫面下方 30% 空著
            if abs(off) > tol:
                bad.append((t, dur, off, fill))
        total = sum(x[1] for x in bad)
        for t, dur, off, fill in bad:
            if dur >= 1.0:
                why = f"內容中心偏{'上（下方空著）' if off < 0 else '下'} {abs(off):.0%}"
                self.problems.append(f"{self.SID} t={t:.2f}s 版面不平衡（{dur:.1f}s）：{why.strip()}")
        return total

    def tear_down(self):
        super().tear_down()
        self._balance_report()
        ODIR.mkdir(parents=True, exist_ok=True)
        (ODIR / f"layout-{self.SID}.txt").write_text("\n".join(dict.fromkeys(self.problems)) or "OK")
        (ODIR / f"sfx-{self.SID}.json").write_text(json.dumps(self.cues))
        # 接縫空檔：開頭多久才第一個動作、最後一個動作結束後還停多久（seams.py 把前一場的 tail 加下一場的 head）
        (ODIR / f"idle-{self.SID}.json").write_text(json.dumps(
            {"head": round(self.first_anim or 0.0, 3), "tail": round(self.sc["frames"] / config.frame_rate - self.last_anim_end, 3)}))
