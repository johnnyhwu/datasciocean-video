"""v001 縮圖（專用構圖，只用成片裡出現的元素：公式、錘錘、片尾的海）。
YTV_VIDEO=v001-rrf-rank-fusion PYTHONPATH=lib uv run python -m manim -qh -s --media_dir out/v001-rrf-rank-fusion/thumb videos/v001-rrf-rank-fusion/thumb.py Thumb
"""
from kit import *

RANK, KC = C["名次"], C["k"]


def sea(surf, step=.55):
    cols = ["#2F8E8F", "#17757F", "#0D606C", "#084E59", "#063E48", "#042F38"]
    xs = np.linspace(-FW / 2 - .2, FW / 2 + .2, 120)
    rng = np.random.default_rng(7)
    g = VGroup()
    for i, c in enumerate(cols):
        ph, ph2 = rng.uniform(0, TAU, 2)
        y = surf - i * step + .1 * np.sin(.62 * xs + ph) + .05 * np.sin(1.45 * xs + ph2)
        pts = [np.array([x, yy, 0]) for x, yy in zip(xs, y)] + [np.array([xs[-1], -FH, 0]), np.array([xs[0], -FH, 0])]
        g.add(VMobject().set_points_as_corners(pts + [pts[0]]).set_fill(c, 1).set_stroke(width=0))
    return g


class Thumb(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(sea(-2.7, .45))
        # 錘錘：右邊，垂進海裡，亮著
        p = Plumb(1.15).place([4.75, -.75, 0])
        p.set_mood("happy")
        p.facets[0].set_fill("#FFE7A8", 1); p.facets[1].set_fill("#FFF3D0", 1); p.facets[2].set_fill(GOLD, 1)
        glow = VGroup(*[Circle(r).set_stroke(width=0).set_fill(GOLD, .013) for r in np.linspace(3.8, .4, 50)]).move_to(p.center())
        self.add(glow, p)
        # 大字
        big = B("不看分數", .2, TXT_STRONG)
        big.move_to([-2.2, 2.45, 0])
        # 公式
        fr = .15
        den = VGroup(M("k", fr, KC, italic=True), M("+", fr, TXT_STRONG), T("名次", fr * .8, RANK, BOLD)).arrange(RIGHT, buff=.22)
        f = fraction(M("1", fr, TXT_STRONG), den, fr, TXT_STRONG, gap=.2)
        f.bar.set_stroke(TXT_STRONG, 6)
        sig = M("Σ", .24, TXT_STRONG)
        form = VGroup(sig, f).arrange(RIGHT, buff=.45)
        form.move_to([-2.2, -.75, 0])
        self.add(big, form)
