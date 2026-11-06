"""吉祥物第二輪概念（2026-11-07）。渲染：
PYTHONPATH=lib uv run python -m manim -qh -s --media_dir out/_mascot docs/mascot/concepts_v2.py Lantern RopeTalk Sampler
"""
from kit import *

GOLD_L, GOLD_D, GLOWC, ROPE = "#F5CD78", "#AA7628", "#FFE7A8", "#C8964A"


def P(*xy):
    return np.array([*xy, 0.0])


def bob(face="lantern", mood="neutral", lit=False):
    """錘身。face: lantern（暗窗＋光點眼）｜porthole（黃銅舷窗＋一隻大眼）｜plain"""
    g = VGroup()
    body = Polygon(P(-.95, .6), P(-.6, 1.0), P(.6, 1.0), P(.95, .6), P(0, -1.7)).set_fill(GLOWC if lit else GOLD, 1).set_stroke(width=0)
    left = Polygon(P(-.95, .6), P(-.6, 1.0), P(-.2, 1.0), P(-.35, .6), P(0, -1.7)).set_fill("#FFF3D0" if lit else GOLD_L, 1).set_stroke(width=0)
    right = Polygon(P(.95, .6), P(.6, 1.0), P(.25, 1.0), P(.4, .6), P(0, -1.7)).set_fill(GOLD if lit else GOLD_D, 1).set_stroke(width=0)
    ridge = Line(P(-.95, .6), P(.95, .6)).set_stroke(GOLD_D, 2, 0.6)
    cap = RoundedRectangle(corner_radius=.08, width=.68, height=.38).set_fill(GOLD_D, 1).set_stroke(width=0).move_to(P(0, 1.31))
    neck = Rectangle(width=.52, height=.2).set_fill(GOLD_D, 1).set_stroke(width=0).move_to(P(0, 1.07))
    g.add(cap, neck, body, left, right, ridge)
    if face == "lantern":
        win = RoundedRectangle(corner_radius=.22, width=1.32, height=.46).set_fill("#1A1206", 1).set_stroke(GOLD_D, 3).move_to(P(0, .38))
        g.add(win)
        g.add(*eyes(mood, [P(-.3, .38), P(.3, .38)]))
    elif face == "porthole":
        ring = Circle(.42).set_fill(SEA, 1).set_stroke("#B07A2A", 10).move_to(P(0, .25))
        rivets = VGroup(*[Dot(ring.get_center() + .42 * np.array([np.cos(a), np.sin(a), 0]), radius=.035, color="#7A5418") for a in np.linspace(0, TAU, 8, endpoint=False)])
        eye = Circle(.24).set_fill("#FFFAF0", 1).set_stroke(width=0).move_to(ring)
        pup = Circle(.12).set_fill(SCREEN, 1).set_stroke(width=0).move_to(ring.get_center() + (P(.07, .03) if mood != "wow" else P(0, 0)))
        shine = Circle(.04).set_fill(WHITE, 1).set_stroke(width=0).move_to(pup.get_center() + P(-.05, .05))
        lid = VGroup()
        if mood == "happy":
            lid = Arc(radius=.24, start_angle=PI * 1.05, angle=PI * 0.9).set_stroke(SEA, 14).move_to(ring.get_center() + P(0, -.12))
        g.add(ring, rivets, eye, pup, shine, lid)
    return g


def eyes(mood, centers):
    out = []
    for c in centers:
        halo = Circle(.17).set_fill(GLOWC, .28).set_stroke(width=0).move_to(c)
        if mood == "happy":
            e = ArcBetweenPoints(c + P(-.1, -.03), c + P(.1, -.03), angle=-PI * .75).set_stroke(GLOWC, 7)
        elif mood == "wow":
            e = Circle(.1).set_stroke(GLOWC, 6).move_to(c)
        elif mood == "flat":
            e = Line(c + P(-.1, 0), c + P(.1, 0)).set_stroke(GLOWC, 7)
        else:
            e = Dot(c, radius=.085, color=GLOWC)
        out += [halo, e]
    return out


def rays(center, r0=1.3, r1=2.0, n=10):
    return VGroup(*[Line(center + r0 * np.array([np.cos(a), np.sin(a), 0]), center + r1 * np.array([np.cos(a), np.sin(a), 0]))
                    .set_stroke(GOLD, 5, .8) for a in np.linspace(0, TAU, n, endpoint=False)])


def rope(points, marks=True):
    r = VMobject().set_points_smoothly([P(*p) for p in points]).set_stroke(ROPE, 7)
    g = VGroup(r)
    if marks:  # 測深繩上的刻度（真實的測深繩每隔幾噚有一個標記）
        for a in (0.25, 0.5, 0.75):
            p = r.point_from_proportion(a)
            g.add(Dot(p, radius=.06, color="#C9A7FF" if a == .5 else TEAL_L))
    return g


def caption(s, sub, x):
    return VGroup(B(s, .042, TXT_STRONG), T(sub, .03, MUTED)).arrange(DOWN, buff=.12).move_to(P(x, -3.25))


def title(s, sub):
    t = VGroup(B(s, .055, GOLD), T(sub, .032, TXT)).arrange(DOWN, buff=.12, aligned_edge=LEFT).to_corner(UL, buff=.4)
    bg = RoundedRectangle(corner_radius=.12, width=t.width + .4, height=t.height + .3).set_fill(SCREEN, .92).set_stroke(width=0).move_to(t)
    return VGroup(bg, t).set_z_index(10)


XS = [-5.1, -1.7, 1.7, 5.1]


class Lantern(Scene):
    """A：燈籠錘——暗窗裡兩顆光點當眼睛，表情只靠光點形狀；頓悟時從裡面亮起來。"""

    def construct(self):
        self.add(bgplate("abyss"), title("A｜燈籠錘", "錘身挖一扇暗窗，眼睛是兩顆光點；想通的時候，整顆從裡面亮起來"))
        poses = [("neutral", False, "平常", "光點眨眼、左右看"), ("flat", False, "懷疑", "光點壓成一條線"),
                 ("happy", False, "開心", "光點彎成 ^ ^"), ("wow", True, "頓悟", "從內部發光＋光芒")]
        for x, (m, lit, a, b) in zip(XS, poses):
            g = bob("lantern", m, lit).scale(.7).move_to(P(x, .2))
            if lit:
                self.add(Circle(1.6).set_fill(GOLD, .12).set_stroke(width=0).move_to(g), rays(g.get_center() + P(0, .1), 1.25, 1.75).scale(1))
            self.add(Line(g.get_top(), P(x, 4.2)).set_stroke(ROPE, 5), g, caption(a, b, x))


class RopeTalk(Scene):
    """B：繩語——垂著時就是「！」，繩子捲起來就是「？」；尖端當指標，繩子能畫底線、套圈。"""

    def construct(self):
        self.add(bgplate("glow_left"), title("B｜繩語", "垂直掛著＝「！」；繩子一捲＝「？」。尖端是天生的指標，繩子是它的手"))
        # 1. ！
        g1 = bob("lantern", "neutral").scale(.55).move_to(P(XS[0], -.6))
        self.add(Line(g1.get_top(), P(XS[0], 3.2)).set_stroke(ROPE, 9), g1, caption("！", "垂著的時候", XS[0]))
        # 2. ？（錘身就是問號的那個點）
        g2 = bob("lantern", "flat").scale(.55).move_to(P(XS[1], -1.0))
        top = g2.get_top()
        hook = rope([(top[0] - .75, 1.95), (top[0] - .7, 2.55), (top[0] - .25, 2.95), (top[0] + .3, 2.95), (top[0] + .72, 2.55),
                     (top[0] + .65, 1.95), (top[0] + .2, 1.55), (top[0], 1.15), (top[0], top[1])])
        self.add(hook, g2, caption("？", "好奇的時候", XS[1]))
        # 3. 指標：尖端指向重點
        target = pill("argmax", "#FF9F5A", .04, bold=True).move_to(P(XS[2] + .55, -.9))
        g3 = bob("lantern", "wow").scale(.45).rotate(PI / 3).move_to(P(XS[2] - .75, .45))
        cap3 = g3[0].get_center()
        self.add(rope([(XS[2] - .2, 3.2), (XS[2] - .9, 2.4), (XS[2] - 1.5, 1.6), cap3[:2]], marks=False), g3, target,
                 caption("指", "尖端就是指標", XS[2]))
        # 4. 套圈＋底線
        word = B("名次", .06, TXT_STRONG).move_to(P(XS[3], .9))
        lasso = Ellipse(width=1.9, height=1.0).set_stroke(ROPE, 7).move_to(word)
        under = Line(P(XS[3] - .9, -.15), P(XS[3] + .7, -.15)).set_stroke(ROPE, 7)
        g4 = bob("lantern", "happy").scale(.4).rotate(PI / 2).next_to(under, RIGHT, buff=-.05)
        self.add(word, lasso, under, g4, caption("圈、畫線", "繩子圈住關鍵字", XS[3]))


class Sampler(Scene):
    """C：撈樣員——黃銅舷窗一隻大眼；尖端塗了油脂，潛下去會黏回一顆發光的「樣本」＝這支影片帶走的那句話。"""

    def construct(self):
        self.add(bgplate("calm"), title("C｜撈樣員", "真實的測深錘尖端塗油脂，用來黏回海底的樣本；錘錘黏回來的是「今天的洞見」"))
        for x, (m, a, b) in zip(XS[:3], [("neutral", "下潛前", "舷窗裡一隻大眼"), ("happy", "碰到底", "笑彎了眼"), ("wow", "撈到了", "尖端黏著發光的樣本")]):
            g = bob("porthole", m).scale(.62).move_to(P(x, .1))
            self.add(Line(g.get_top(), P(x, 4.2)).set_stroke(ROPE, 5), g, caption(a, b, x))
            if a == "撈到了":
                tip = g.get_bottom()
                self.add(Circle(.55).set_fill(GOLD, .25).set_stroke(width=0).move_to(tip), Dot(tip, radius=.2, color=GLOWC), rays(tip, .35, .7, 8).set_stroke(width=3))
        card = VGroup(RoundedRectangle(corner_radius=.15, width=3.1, height=1.6).set_fill(SEA, 1).set_stroke(GOLD, 3),
                      VGroup(T("今天撈上來的：", .03, MUTED), B("名次比分數", .045, GOLD), B("更好比較", .045, GOLD)).arrange(DOWN, buff=.1))
        card[1].move_to(card[0])
        self.add(card.move_to(P(XS[3], .4)), caption("收尾儀式", "把樣本變成一句話重點", XS[3]))


class QToBang(Scene):
    """招牌動作：「？」的繩子拉直成「！」，同時從裡面亮起來（約 4 秒）。"""

    def construct(self):
        self.add(bgplate("abyss"))
        g = bob("lantern", "flat").scale(.6).move_to(P(0, -1.2))
        top = g.get_top()
        q = rope([(-.75, 1.75), (-.7, 2.35), (-.25, 2.75), (.3, 2.75), (.72, 2.35), (.65, 1.75), (.2, 1.35), (0, .95), (0, top[1])], marks=False)
        bang_pts = [(0, 4.3 - k * (4.3 - top[1]) / 8) for k in range(9)]
        bang = rope(bang_pts, marks=False)
        lit = bob("lantern", "wow", lit=True).scale(.6).move_to(g)
        halo = Circle(1.5).set_fill(GOLD, .14).set_stroke(width=0).move_to(g)
        r = rays(g.get_center() + P(0, .1), 1.15, 1.6)
        cap = VGroup(B("？", .07, TXT_STRONG)).move_to(P(3.2, .5))
        self.add(q, g, cap)
        self.wait(0.6)
        self.play(Wiggle(g, scale_value=1.04, rotation_angle=.04 * TAU, n_wiggles=3), run_time=0.8)
        self.play(Transform(q[0], bang[0]), Transform(cap[0], B("！", .07, GOLD).move_to(cap)), run_time=0.7, rate_func=rate_functions.ease_in_out_back)
        self.play(FadeIn(halo), Transform(g, lit), LaggedStart(*[Create(x) for x in r], lag_ratio=.05), run_time=0.6)
        self.wait(1.2)
