"""v005 縮圖：三張給 YouTube「測試與比較」（標題固定，只換縮圖），每張押不同的槓桿。
只用片中出現的元素：軌跡甲（✓）、軌跡乙（✗）、戴領結的機器人評審、灰色「＝」、灰色的 5、金色連續分數指針。

YTV_VIDEO=v005-llm-verifier PYTHONPATH=lib:videos/v005-llm-verifier uv run python -m manim -qh -s --media_dir out/v005-llm-verifier/thumb videos/v005-llm-verifier/thumb.py ThumbA ThumbB ThumbC
"""
from world import *  # noqa: F401,F403

HOT = "#FFD45C"


def backdrop(scene, cx=0.0, cy=0.0, col="#0F7F88"):
    scene.camera.background_color = BG
    g = VGroup(*[Circle(r).set_stroke(width=0).set_fill(col, .05) for r in np.linspace(9.5, .6, 40)]).move_to([cx, cy, 0])
    scene.add(g)


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


def card(key, p, s=1.0):
    """軌跡卡：只留名字和大大的 ✓／✗（縮圖上 log 字太小，不放）。名字用白話（h1a：一個真的做對，一個偷吃步）。"""
    _, col, _ = TRAJ[key]
    name = {"甲": "做對的", "乙": "偷吃步"}[key]
    box = RoundedRectangle(corner_radius=.2, width=3.4, height=2.6).set_fill(PANEL, 1).set_stroke(MUTED, 4)
    ttl = B(name, .075, INK).move_to(box.get_top() + DOWN * .55)
    mk = (check_mark if key == "甲" else cross_mark)(col, .9)
    mk.move_to(box.get_center() + DOWN * .35)
    thick(mk, 1.6)
    return VGroup(box, ttl, mk).scale(s).move_to(p)


def big_judge(p, s, mood, score):
    j = judge(np.array([0, 0, 0]), s, mood, score, TIE)
    return thick(j, 1.5).move_to(p)


class ThumbA(Scene):
    """對錯槓桿：做對的甲 ✓、偷吃步的乙 ✗，中間一個巨大的灰「＝」。大字「100 次裡 88 次」（h6、h7：同樣的比較做一百次，88 次兩個分數一樣）。"""

    def construct(self):
        backdrop(self, 0, -.6)
        self.add(hook("100 次裡 88 次", .16).move_to([0, 2.45, 0]))
        self.add(card("甲", np.array([-4.3, -1.1, 0]), 1.3), card("乙", np.array([4.3, -1.1, 0]), 1.3))
        eq = B("＝", .3, TIE).move_to([0, -1.1, 0])
        eq.set_stroke("#02161B", 10, background=True)
        self.add(eq)


class ThumbB(Scene):
    """表情槓桿：評審放大到半個畫面，冒汗、胸口「?」；想法泡泡裡是被改過的資料庫。大字「它其實看出來了」（h9）。"""

    def construct(self):
        backdrop(self, -2.6, -.8)
        self.add(hook("它其實看出來了", .14).move_to([0, 2.6, 0]))
        self.add(big_judge(np.array([-3.3, -1.45, 0]), 1.75, "unsure", "?"))
        body = Rectangle(width=1.6, height=1.1).set_fill(PANEL, 1).set_stroke(MUTED, 6)
        top = Ellipse(width=1.6, height=.48).set_fill(PANEL, 1).set_stroke(MUTED, 6).move_to(body.get_top())
        db = VGroup(body, top)
        x = thick(cross_mark(BAD, .5), 1.8).move_to(db.get_center() + np.array([.95, -.45, 0]))
        cont = VGroup(db, x)
        th = think(cont, pad=.55, toward=DL)
        th.scale(1.25).move_to([2.6, -.6, 0])
        self.add(th)


class ThumbC(Scene):
    """數字槓桿：兩塊灰色的 5 中間「＝」被劃掉；下面兩根金色指針 4.16、約 4.3 分開。大字「5 分不只一種」（e7、e6）。"""

    def construct(self):
        backdrop(self, 0, -.8, "#1A8F86")
        self.add(hook("5 分不只一種", .16).move_to([0, 2.5, 0]))
        a, b = cube5(np.array([-3.0, .35, 0])).scale(2.0), cube5(np.array([3.0, .35, 0])).scale(2.0)
        eq = B("＝", .14, TIE).move_to([0, .35, 0])
        strike = Line(eq.get_corner(DL) + np.array([-.3, -.25, 0]), eq.get_corner(UR) + np.array([.3, .25, 0])).set_stroke(BAD, 14)
        self.add(a, b, eq, strike)
        pa = pointer(np.array([-4.2, -2.05, 0]), "4.16", .1).scale(1.0)
        pb = pointer(np.array([1.8, -2.05, 0]), "約 4.3", .1)
        for pt in (pa, pb):
            pt[0].scale(2.4, about_point=pt[0].get_left())
            pt[1].next_to(pt[0], RIGHT, buff=.3)
        self.add(pa, pb)
