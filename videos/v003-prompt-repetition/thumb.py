"""v003 縮圖：三張給 YouTube「測試與比較」（標題固定，只換縮圖），每張押不同的槓桿。
規則（publish-prep、使用者 2026-11-21）：站在滑手機的「笨笨的人類」角度，一眼看出主題；
一個主角放大到佔半個畫面、一句大字（不重複標題）、比片內更亮更高對比、線條加粗。
只用片中出現的元素：提示卡「第 25 個是誰？」、Ctrl+V、準確率 21%→97%（h2、e9：NameIndex，Gemini 2.0 Flash-Lite）、
戴半邊眼罩的讀者與泡泡（sc02、sc05）、錘錘、片尾的海。

YTV_VIDEO=v003-prompt-repetition PYTHONPATH=lib:videos/v003-prompt-repetition uv run python -m manim -qh -s --media_dir out/v003-prompt-repetition/thumb videos/v003-prompt-repetition/thumb.py ThumbA ThumbB ThumbC
"""
from world import *  # noqa: F401,F403

HOT = "#FFD45C"
RED = "#FF6B5E"


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


def glow(mob, color, n=10, spread=.5):
    return VGroup(*[mob.copy().set_fill(color, .05).set_stroke(color, 30 * (1 + spread * k), .035) for k in range(n)])


def card(c, scale=1.0, color=P1C):
    k = prompt_card(np.array(c), label="第 25 個是誰？", w=3.2, h=2.0, color=color).scale(scale)
    for m in k.family_members_with_points():
        if m.get_stroke_width() > 0:
            m.set_stroke(width=m.get_stroke_width() * 2.0)
    return k


def keycap(s, p, color, frac=.07):
    t = B(s, frac, color)
    box = RoundedRectangle(corner_radius=.2, width=t.width + .6, height=t.height + .45).set_fill("#06262C", .95).set_stroke(color, 7)
    return VGroup(box.move_to(p), t.move_to(p))


class ThumbA(Scene):
    """數字槓桿：21% 灰、打叉感的箭頭 → 97% 發光。大字「AI 準確率」。出處：h2（21%→97%）、e9。"""

    def construct(self):
        backdrop(self, 2.8, -.3)
        self.add(sea(-3.6))
        self.add(hook("AI 準確率", .15).move_to([0, 2.95, 0]))
        n1 = M("21%", .22, "#9FB3B3").move_to([-3.6, -.1, 0])
        n2 = M("97%", .3, HOT).move_to([2.9, -.1, 0])
        ar = Arrow([-1.55, -.1, 0], [.15, -.1, 0], buff=0, stroke_width=22, max_tip_length_to_length_ratio=.45).set_color(TXT_STRONG)
        self.add(n1, ar, glow(n2, HOT), n2)
        self.add(keycap("Ctrl+V ×2", [-3.6, -2.05, 0], P2C, .07))


class ThumbB(Scene):
    """動作槓桿：同一張提示卡貼兩次（兩張大卡），中間「×2」，右下角小儀表 97%。大字「只要貼兩次？」。
    出處：h1（Ctrl+C、Ctrl+V、第 25 個是誰？）、h2、h3（錘錘：只是貼兩次？）。"""

    def construct(self):
        backdrop(self, 0, -.5)
        self.add(sea(-3.6))
        self.add(hook("只要貼兩次？", .15).move_to([0, 2.95, 0]))
        c1, c2 = card([-3.5, -.15, 0], 1.45, P1C), card([3.5, -.15, 0], 1.45, P2C)
        self.add(c1, c2, hook("×2", .16, TXT_STRONG).move_to([0, -.15, 0]))
        self.add(keycap("Ctrl+C", [-3.5, -2.35, 0], P1C, .06), keycap("Ctrl+V", [3.5, -2.35, 0], P2C, .06))


class ThumbC(Scene):
    """角色槓桿：一個超大的戴半邊眼罩讀者（bark），泡泡裡狗和樹糊在一起，汗珠；右邊第二遍的 bark 拿到金色樹皮。
    大字「AI 只能回頭看」。出處：r6（只能回頭看）、w6（狗叫聲？樹皮？）、p6（第二遍：金色的樹皮）。"""

    def construct(self):
        backdrop(self, 2.5, -.5)
        self.add(sea(-3.75))
        self.add(hook("AI 只能回頭看", .14).move_to([0, 3.0, 0]))
        p1, p2 = np.array([-3.4, -1.55, 0]), np.array([3.4, -1.55, 0])
        r1 = reader("bark", P1C, p1, conf=1).scale(1.55, about_point=p1)
        r2 = reader("bark", P2C, p2, joy=1).scale(1.55, about_point=p2)
        for r in (r1, r2):
            for m in r.family_members_with_points():
                if m.get_stroke_width() > 0:
                    m.set_stroke(width=m.get_stroke_width() * 1.8)
        b1 = bubble_at(p1, meaning(0, 1.25)).scale(1.35, about_point=p1).shift(RIGHT * 1.3 + DOWN * .25)
        b2 = bubble_at(p2, meaning(1, 1.25)).scale(1.35, about_point=p2).shift(LEFT * 1.3 + DOWN * .25)
        self.add(r1, b1, r2, glow(b2, HOT, 6), b2)
        self.add(hook("第一遍", .07, P1C).next_to(r1, DOWN, buff=.2), hook("第二遍", .07, P2C).next_to(r2, DOWN, buff=.2))
