"""v004 縮圖：三張給 YouTube「測試與比較」（標題固定，只換縮圖），每張押不同的槓桿。
只用片中出現的元素：玻璃球「模型」、跑道、金色工具呼叫單、FAILED／PASSED 紙條、開場的流程圖（規劃器、執行器、檢查器）、片尾的海。

YTV_VIDEO=v004-claude-code-loop PYTHONPATH=lib:videos/v004-claude-code-loop uv run python -m manim -qh -s --media_dir out/v004-claude-code-loop/thumb videos/v004-claude-code-loop/thumb.py ThumbA ThumbB ThumbC
"""
from world import *  # noqa: F401,F403

HOT = "#FFD45C"


def backdrop(scene, cx=0.0, cy=0.0, col="#0F7F88"):
    scene.camera.background_color = BG
    g = VGroup(*[Circle(r).set_stroke(width=0).set_fill(col, .045) for r in np.linspace(9.5, .6, 40)]).move_to([cx, cy, 0])
    scene.add(g)


def sea(surf, step=.38):
    cols = ["#36A3A1", "#1E8890", "#10707C", "#0A5A66", "#074652", "#05343E"]
    xs = np.linspace(-FW / 2 - .2, FW / 2 + .2, 120)
    rng = np.random.default_rng(11)
    g = VGroup()
    for i, c in enumerate(cols):
        ph, ph2 = rng.uniform(0, TAU, 2)
        y = surf - i * step + .1 * np.sin(.62 * xs + ph) + .05 * np.sin(1.45 * xs + ph2)
        pts = [np.array([x, yy, 0]) for x, yy in zip(xs, y)] + [np.array([xs[-1], -FH, 0]), np.array([xs[0], -FH, 0])]
        g.add(VMobject().set_points_as_corners(pts + [pts[0]]).set_fill(c, 1).set_stroke(width=0))
    return g


def hook(s, frac, color=HOT):
    t = B(s, frac, color)
    t.set_stroke("#02161B", 14, background=True)
    sh = t.copy().set_fill("#000000", .55).set_stroke(width=0).shift(np.array([.07, -.09, 0]))
    return VGroup(sh, t)


def thick(g, k=2.0):
    for m in g.family_members_with_points():
        if m.get_stroke_width() > 0:
            m.set_stroke(width=m.get_stroke_width() * k)
    return g


def loop(c, s):
    """跑道＋玻璃球，放大 s 倍，中心 c。"""
    t = track()
    b = glass_model(LOOP_C, BALL_R)
    g = VGroup(t, b).scale(s, about_point=LOOP_C).move_to(c)
    glow = VGroup(*[Circle(R * s).move_to(c).set_stroke(TEAL_L, 18 + 10 * k, .06) for k in range(6)])
    return VGroup(glow, thick(g, 1.6))


def badge(p=(0, 3.35)):
    t1, t2 = B(">_", .075, TEAL_L), B("Claude Code", .075, TXT_STRONG)
    row_ = VGroup(t1, t2).arrange(RIGHT, buff=.3)
    box = RoundedRectangle(corner_radius=.15, width=row_.width + .7, height=row_.height + .4).set_fill("#06181C", 1).set_stroke(TEAL_L, 5)
    return VGroup(box, row_.move_to(box)).move_to([p[0], p[1], 0])


def big_chip(text, kind, p, frac=.075):
    ink, fill = ROW_STYLE[kind]
    t = B(text, frac, ink)
    box = RoundedRectangle(corner_radius=.12, width=t.width + .5, height=t.height + .36).set_fill(fill, 1).set_stroke("#02161B", 4)
    return VGroup(box, t.move_to(box)).move_to(p)


class ThumbA(Scene):
    """主角槓桿：一顆超大的玻璃球在發光跑道中央，金色小單在跑，FAILED、PASSED 紙條貼在跑道上。大字「沒有規劃器？」（h1～h4、L#c5）。"""

    def construct(self):
        backdrop(self, 0, -.3)
        self.add(sea(-3.75), badge())
        self.add(hook("沒有規劃器？", .15).move_to([0, 2.15, 0]))
        c = np.array([0, -1.05, 0])
        self.add(loop(c, .88))
        sl = slip("Bash", "pytest", mood="happy").scale(1.35).move_to(c + np.array([3.6, .6, 0]))
        self.add(sl)
        self.add(big_chip("FAILED", "err", c + np.array([-4.3, .7, 0])), big_chip("PASSED", "ok", c + np.array([-4.3, -.7, 0])))


class ThumbB(Scene):
    """對比槓桿：左邊開場那張流程圖灰掉、打叉；右邊只剩一個發光的圈。大字「拆掉流程圖」（sc01 流程圖塌成一個圈）。"""

    def construct(self):
        backdrop(self, 3.2, -.4)
        self.add(sea(-3.75), badge())
        self.add(hook("拆掉流程圖", .15).move_to([0, 2.15, 0]))
        names = ["規劃器", "執行器", "檢查器"]
        bx = VGroup(*[flow_box(n, np.array([-4.3, .45 - 1.4 * k, 0]), "#9FB3B3", .09) for k, n in enumerate(names)])
        ar = VGroup(*[Arrow(bx[k].get_bottom(), bx[k + 1].get_top(), buff=.08, stroke_width=8).set_color("#9FB3B3") for k in range(2)])
        fc = thick(VGroup(bx, ar), 1.6)
        x = cross_mark(BAD, 2.4).move_to(fc)
        thick(x, 2.2)
        self.add(fc, x)
        self.add(Arrow([-2.2, -.95, 0], [-.6, -.95, 0], buff=0, stroke_width=20, max_tip_length_to_length_ratio=.45).set_color(TXT_STRONG))
        self.add(loop(np.array([3.1, -1.0, 0]), .85))


class ThumbC(Scene):
    """失敗槓桿：紅色 FAILED 紙條被一個大箭頭繞回玻璃球。大字「錯了就再跑一圈」（w9、L#c9：失敗只是另一種觀察）。"""

    def construct(self):
        backdrop(self, 1.5, -.4)
        self.add(sea(-3.75), badge())
        self.add(hook("錯了就再跑一圈", .14).move_to([0, 2.15, 0]))
        c = np.array([2.6, -1.0, 0])
        self.add(loop(c, .85))
        fail = big_chip("FAILED 沒過", "err", np.array([-3.9, -1.3, 0]), .08)
        self.add(fail)
        arc = CurvedArrow(fail.get_top() + UP * .1, c + np.array([-1.3, 1.3, 0]), angle=-PI / 2.4, stroke_width=16, tip_length=.45).set_color(HOT)
        self.add(arc)
