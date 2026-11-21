"""第二版的角色草圖（靜態）：每條路徑一顆有表情的票。
YTV_VIDEO=<id> PYTHONPATH=lib:videos/<id> uv run python -m manim -qm -s --media_dir out/<id>/sketch2 videos/<id>/sketch2.py A
"""
from world import *  # noqa: F401,F403


def voter(r=.3, conf=1.0, look=0.0):
    """一顆票。conf 高：眼神穩、微笑；conf 低：眉毛下垂、嘴巴歪、冒汗。look：眼睛往左右看（−1～1）。"""
    hes = conf < .5
    body = Circle(r).set_stroke(TXT_STRONG, 2.6).set_fill(CONF if not hes else TXT, .34 if not hes else .14)
    g = VGroup(body)
    ex, ey, er = .36 * r, .12 * r, .11 * r
    for s in (-1, 1):
        c = np.array([s * ex + look * .08 * r, ey, 0])
        g.add(Dot(c, radius=er * (1.0 if not hes else 1.25), color=TXT_STRONG))
        if hes:   # 擔心的眉毛：外側往下
            g.add(Line(c + np.array([-s * .16 * r, .30 * r, 0]), c + np.array([s * .20 * r, .17 * r, 0])).set_stroke(TXT_STRONG, 2.2))
    if hes:
        xs = np.linspace(-.3 * r, .3 * r, 14)
        m = VMobject().set_points_smoothly([np.array([x, -.38 * r + .06 * r * np.sin(x / r * 18), 0]) for x in xs]).set_stroke(TXT_STRONG, 2.2)
        drop = VMobject().set_points_smoothly([np.array(q) * r for q in ([0, .2, 0], [.11, -.02, 0], [0, -.14, 0], [-.11, -.02, 0], [0, .2, 0])])
        drop.set_fill(PATHC, .9).set_stroke(width=0).move_to(np.array([.98 * r, .78 * r, 0]))
        g.add(m, drop)
    else:
        g.add(ArcBetweenPoints(np.array([-.26 * r, -.3 * r, 0]), np.array([.26 * r, -.3 * r, 0]), angle=1.3).set_stroke(TXT_STRONG, 2.4))
    return g


def shake(m, n=3, d=.07):
    """抖動線（靜態草圖用）。"""
    g = VGroup()
    for s in (-1, 1):
        for k in range(n):
            x = m.get_edge_center(RIGHT if s > 0 else LEFT)[0] + s * (d + k * d)
            g.add(Line([x, m.get_y() - .12 + .04 * k, 0], [x, m.get_y() + .12 - .04 * k, 0]).set_stroke(MUTED, 1.8, .8 - .2 * k))
    return g


def dress(bal, confs, scale_by=None):
    """把天平上的球換成有表情的票。"""
    g = VGroup()
    for i in range(5):
        p, r = bal.slot(i)
        v = voter(r, confs[i], look=.6 if i in LEFT_I else -.6).move_to(p)
        g.add(v)
    bal.balls.set_opacity(0)
    return g


class A(MovingCameraScene):
    """開場：三顆在冒汗的票，壓過兩顆很篤定的票。"""
    def construct(self):
        self.camera.background_color = BG
        self.camera.frame.set(width=HOOK_W).move_to(Timed.view(HOOK_C, HOOK_W))
        bal = Balance()
        bal.dyn.clear_updaters()
        vs = dress(bal, [.2, .9, .3, .3, .95])
        pl = Plumb(.5).place(PIV + LEFT * 4.6 + DOWN * 1.6)
        pl.set_mood("puzzled") if hasattr(pl, "set_mood") else None
        self.add(bal, vs, *[shake(vs[i]) for i in LEFT_I[:1]], bal.readout(0), bal.readout(1), pl)


class B(MovingCameraScene):
    """票沿著自己的路徑一步一步走：有把握的大步走，猶豫的在第二步發抖。"""
    def construct(self):
        self.camera.background_color = BG
        self.camera.frame.set(width=ROW_W + 3.2).move_to(Timed.view(ROW_C + DOWN * 1.2, ROW_W + 3.2))
        W = sheet(bars=False, scores=False)
        self.add(*flat(W))
        v0 = voter(.3, .2).move_to(P(0, 1) + UP * .62)
        v1 = voter(.3, .9).move_to(P(1, 2) + UP * .62 + LEFT * 1.2)
        v2 = voter(.3, .3).move_to(P(2, 0) + UP * .62 + RIGHT * .5)
        trail = VGroup(*[Dot(P(1, 2) + UP * .62 + LEFT * (1.5 + .22 * k), radius=.03, color=CONF).set_opacity(.7 - .15 * k) for k in range(4)])
        self.add(v0, shake(v0), v1, trail, v2)


class D(MovingCameraScene):
    """CER 的投票：票的大小＝信心。兩顆大的壓過三顆小的。"""
    def construct(self):
        self.camera.background_color = BG
        self.camera.frame.set(width=HOOK_W).move_to(Timed.view(HOOK_C, HOOK_W))
        bal = Balance(w=SCORES, mode=1)
        bal.dyn.clear_updaters()
        vs = dress(bal, [.2, .9, .3, .3, .95])
        pl = Plumb(.5).place(PIV + LEFT * 4.6 + DOWN * 1.2)
        pl.set_mood("happy")
        self.add(bal, vs, bal.readout(0), bal.readout(1), title(), sub_label("信心加總", CONF), pl)
