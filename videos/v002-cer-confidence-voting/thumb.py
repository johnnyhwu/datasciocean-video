"""v002 縮圖：三張給 YouTube「測試與比較」（標題固定，只換縮圖），每張押不同的槓桿。
第三版（2026-11-21）：使用者「thumbnail 應該是要讓人一看就知道這個影片在講什麼主題」。
每張的大字都有「AI」加情境，畫面放片中真正的兩個答案 375（錯，多數）與 400（對，少數）。
第二版（只有臉和天平、沒有主題）留在 thumbs/v2/。
只用成片裡出現的元素：有表情的票、天平、token 機率長條、片尾的海。
規則（2026-11-21 從 claude-youtube-editor 的打包規則改寫，見 publish-prep skill）：
一個主角放大到佔半個畫面、一句大字（不重複標題）、比片內更亮更高對比、線條加粗到手機縮圖也看得到。

YTV_VIDEO=v002-cer-confidence-voting PYTHONPATH=lib:videos/v002-cer-confidence-voting uv run python -m manim -qh -s --media_dir out/v002-cer-confidence-voting/thumb videos/v002-cer-confidence-voting/thumb.py ThumbA ThumbB ThumbC
"""
from world import *  # noqa: F401,F403

PURPLE = CONF
HOT = "#FFD45C"          # 縮圖的大字：比片內的金色更亮


def backdrop(scene, cx=0.0, cy=0.0, col="#0F7F88"):
    """比片內亮的底：中間一團青綠光，往外暗到深海色。"""
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


def big_face(p, r, hes=0.0, sure=0.0, look=0.0, k=None):
    """放大的票：線條跟著半徑加粗，填色加深（縮到手機大小也看得出表情）。"""
    f = face(p, r, hes, sure, look)
    k = k or r / .34 * .55
    for m in f:
        if m.get_stroke_width() > 0:
            m.set_stroke(width=m.get_stroke_width() * k)
    f[0].set_fill(interpolate_color(ManimColor("#2A5A60"), ManimColor(PURPLE), sure), .55 + .35 * sure)
    f[0].set_stroke(TXT_STRONG if not sure else "#EBDDFF")
    return f


def drops(p, r, n=2):
    """額外的汗珠（放大版）。"""
    g = VGroup()
    for i, (dx, dy, s) in enumerate([(1.1, .55, .26), (-1.12, .35, .2), (1.25, .05, .16)][:n]):
        d = VMobject().set_points_smoothly([np.array(q) for q in ([0, .2, 0], [.11, -.02, 0], [0, -.14, 0], [-.11, -.02, 0], [0, .2, 0])])
        g.add(d.scale(s * r / .2 * .5).set_fill(PATHC, .95).set_stroke(width=0).move_to(np.array(p) + r * np.array([dx, dy, 0])))
    return g


def shake(p, r, side=1):
    """發抖的線（漫畫線）。"""
    g = VGroup()
    for k in range(3):
        a = (-25 + 25 * k) * DEGREES
        d = np.array([side * np.cos(a), np.sin(a), 0])
        g.add(Line(np.array(p) + d * r * 1.18, np.array(p) + d * r * 1.42).set_stroke(TXT, 7, .85))
    return g


def hook(s, frac, color=HOT):
    """大字：亮金色＋深色描邊＋陰影。"""
    t = B(s, frac, color)
    t.set_stroke("#02161B", 14, background=True)
    sh = t.copy().set_fill("#000000", .55).set_stroke(width=0).shift(np.array([.07, -.09, 0]))
    return VGroup(sh, t)


def tipped_balance(c, th, beam=3.2, hang=1.4, plate=3.0):
    """傾斜的天平（右邊下沉，th 為弧度）。回傳 (群組, 左盤中心, 右盤中心)。"""
    c = np.array(c)
    e = [c + s * beam * np.array([np.cos(th), np.sin(th), 0]) for s in (-1, 1)]
    g = VGroup()
    b = np.array([c[0], -3.25, 0])
    g.add(Line(b, c).set_stroke(TXT, 9))
    g.add(Line(b + LEFT * 1.1, b + RIGHT * 1.1).set_stroke(TXT, 11))
    g.add(Line(e[0], e[1]).set_stroke(TXT_STRONG, 11))
    pcs = []
    for s in range(2):
        pc = e[s] + DOWN * hang
        pcs.append(pc)
        g.add(Line(e[s], pc + LEFT * plate / 2).set_stroke(LINE, 4), Line(e[s], pc + RIGHT * plate / 2).set_stroke(LINE, 4))
        g.add(Line(pc + LEFT * plate / 2, pc + RIGHT * plate / 2).set_stroke(TXT, 9))
    g.add(Dot(c, radius=.2, color=TXT_STRONG))
    return g, pcs[0], pcs[1]


RED = "#FF6B5E"


def tag(s, p, color, frac=.085):
    """答案牌：深底圓角框＋大數字。"""
    t = M(s, frac, color)
    box = RoundedRectangle(corner_radius=.18, width=t.width + .5, height=t.height + .36).set_fill("#06262C", .95).set_stroke(color, 6)
    return VGroup(box.move_to(p), t.move_to(p))


def cross(p, r, color=RED, w=22):
    p = np.array(p)
    return VGroup(Line(p + r * np.array([-1, 1, 0]), p + r * np.array([1, -1, 0])), Line(p + r * np.array([-1, -1, 0]), p + r * np.array([1, 1, 0]))).set_stroke(color, w)


def check(p, r, color=HOT, w=22):
    p = np.array(p)
    return VMobject().set_points_as_corners([p + r * np.array([-1, 0, 0]), p + r * np.array([-.35, -.65, 0]), p + r * np.array([1, .8, 0])]).set_stroke(color, w)


def two_line(a, b, frac_a, frac_b, ca=HOT, cb=TXT_STRONG):
    la, lb = hook(a, frac_a, ca), hook(b, frac_b, cb)
    return VGroup(la, lb).arrange(DOWN, buff=.18, aligned_edge=LEFT)


class ThumbA(Scene):
    """對錯槓桿：AI 算 5 次，三顆冒汗的票都說 375（多數決選它，錯），兩顆紫色笑臉說 400（對）。
    大字「AI 多數決 選錯了」。出處：h1–h3（算五次、三次 375、兩次 400、多數決選 375），e6（多數決「又被騙過去了」），
    400＝100×5×0.8（s5 的例子），v7（票比較少的那邊反而贏了）。"""

    def construct(self):
        backdrop(self, 0, -1.0)
        self.add(sea(-3.55))
        self.add(hook("AI 多數決", .15).move_to([-2.3, 2.95, 0]), hook("選錯了", .15, RED).move_to([3.9, 2.95, 0]))
        r = .92
        lx = [-5.3, -3.35, -1.4]
        for x in lx:
            p = np.array([x, .05, 0])
            self.add(big_face(p, r, hes=1, look=.4, k=2.4), drops(p, r, 1))
        self.add(tag("375", [-3.75, -2.05, 0], TXT_STRONG, .12))
        self.add(cross([-1.95, -2.0, 0], .36, w=20))
        self.add(T("3 票", .06, TXT).move_to([-3.35, 1.45, 0]))
        rr = 1.12
        for x in (2.55, 5.0):
            self.add(big_face(np.array([x, .05, 0]), rr, sure=1, look=-.4, k=2.2))
        self.add(tag("400", [3.78, -2.05, 0], HOT, .12))
        self.add(check([5.55, -2.0, 0], .42))
        self.add(T("2 票", .06, TXT).move_to([3.78, 1.6, 0]))
        self.add(Line([.55, 1.5, 0], [.55, -2.9, 0]).set_stroke(LINE, 5, .7))


class ThumbB(Scene):
    """情緒槓桿：一顆巨大、冒汗發抖、手上是 375 的票。大字「AI 很猶豫／也算一票？」。
    出處：h4（那三票算的時候好像不太確定），b3（過程充滿猶豫…也算一票），h5（多數決只數票數）。"""

    def construct(self):
        backdrop(self, -3.0, -.4)
        self.add(sea(-3.55))
        p, r = np.array([-3.4, -.35, 0]), 2.3
        self.add(shake(p, r, -1), big_face(p, r, hes=1, look=.6, k=3.4), drops(p, r, 3))
        self.add(tag("375", p + np.array([1.9, -2.0, 0]), TXT_STRONG, .11))
        g = two_line("AI 很猶豫", "也算一票？", .17, .15)
        self.add(g.move_to([3.2, .45, 0]))


class ThumbC(Scene):
    """數字槓桿：天平。左盤 3 顆猶豫的 375、加起來 1.70；右盤 2 顆有把握的 400、加起來 1.88，天平倒向右邊。
    大字「AI 投票 看信心」。出處：v3–v7（信心加起來 1.70 vs 1.88，票少的反而贏），c1–c2。"""

    def construct(self):
        backdrop(self, 2.5, -1.2)
        self.add(sea(-3.55))
        th = -12 * DEGREES
        bal, lc, rc = tipped_balance([0.0, 1.35, 0], th, beam=4.3, hang=1.9, plate=4.4)
        self.add(bal)
        rl = .62
        for dx in (-1.35, 0, 1.35):
            p = lc + RIGHT * dx + UP * (rl + .06)
            self.add(big_face(p, rl, hes=1, look=.5), drops(p, rl, 1))
        rr = 1.0
        for dx in (-1.08, 1.08):
            self.add(big_face(rc + RIGHT * dx + UP * (rr + .06), rr, sure=1, look=-.5, k=2.0))
        self.add(tag("375：1.70", lc + DOWN * .8, TXT_STRONG, .085))
        self.add(tag("400：1.88", rc + DOWN * .8, HOT, .095))
        self.add(hook("AI 投票 看信心", .15).move_to([0, 3.05, 0]))


def glow(mob, color, n=10, spread=.5):
    """數字背後的光暈。"""
    return VGroup(*[mob.copy().set_fill(color, .05).set_stroke(color, 30 * (1 + spread * k), .035) for k in range(n)])


class ThumbD(Scene):
    """第四版（2026-11-21）。使用者：「站在一個笨笨的人類的角度…人類常常滑過去，除非真的 catch his eyes」。
    只留兩個超大的數字：375（三票、錯）打叉，400（兩票、對）發光打勾。大字「AI 多數決 竟然錯了」（使用者要補上「AI 多數決」）。
    出處：h2（三次 375、兩次 400），400＝100×5×0.8（s5），e6（多數決又被騙過去了），b4（模型有時會反覆給出同一個錯誤答案）。
    數字是片中假設的例子。標題「同一題問 AI 五次，答案不一樣，該信哪個？」負責交代 AI，縮圖負責反轉。"""

    def construct(self):
        backdrop(self, 3.3, -.2)
        self.add(sea(-3.6))
        h1, h2 = hook("AI 多數決", .155), hook("竟然錯了", .155, RED)
        self.add(VGroup(h1, h2).arrange(RIGHT, buff=.45).move_to([0, 2.9, 0]))
        # 左：375，灰白、被打叉，底下三顆冒汗的小票
        n1 = M("375", .3, "#C9D6D6").move_to([-3.55, .1, 0])
        self.add(n1, cross([-3.55, .1, 0], 1.25, w=30))
        for k, x in enumerate((-4.85, -3.55, -2.25)):
            p = np.array([x, -2.45, 0])
            self.add(big_face(p, .55, hes=1, look=.3, k=1.6), drops(p, .55, 1))
        # 右：400，亮金色發光、打勾，底下兩顆有把握的紫色笑臉
        n2 = M("400", .3, HOT).move_to([3.35, .1, 0])
        n2.set_stroke("#02161B", 10, background=True)
        halo = VGroup(*[Circle(r).set_stroke(width=0).set_fill(HOT, .028) for r in np.linspace(3.0, .4, 26)]).move_to(n2)
        self.add(halo, n2, check([5.95, 1.2, 0], .5, w=26))
        for x in (2.85, 4.25):
            self.add(big_face(np.array([x, -2.45, 0]), .62, sure=1, look=-.3, k=1.7))
        self.add(T("3 票", .06, TXT).next_to([-2.25, -2.45, 0], RIGHT, buff=.75))
        self.add(T("2 票", .06, HOT).next_to([4.25, -2.45, 0], RIGHT, buff=.8))
