"""風格樣張 v2（設計模式，靜態）：圖為主、字為輔；細線、少粗體、不用膠囊；數字與公式用 STIX Two（OFL）襯線字。
PYTHONPATH=lib uv run python -m manim -qh -s --media_dir out/v001-rrf-rank-fusion/style videos/v001-rrf-rank-fusion/style_v2.py SA SB SC
"""
from kit import *

manimpango.register_font(str(ROOT / "assets/fonts/STIX2Text-Regular.otf"))
manimpango.register_font(str(ROOT / "assets/fonts/STIX2Text-Italic.otf"))
SERIF = "STIX Two Text"
VEC, FULL, RANK, SCORE = S["concept_pool"][1], S["concept_pool"][0], S["concept_pool"][5], S["concept_pool"][2]
LINE = "#5E8C8E"   # 細線、刻度


def M(s, frac=.06, color=TXT, italic=False):
    """數字與公式：襯線字（變數用斜體）。"""
    t = Text(s, font=SERIF, font_size=fs(frac), color=color, slant=ITALIC if italic else NORMAL)
    t._frac, t._h0 = frac, t.height
    return t


def note(s, color=MUTED, frac=.038):
    """小註記（示意、依卡上公式計算）：純文字＋細底線，不用膠囊。"""
    t = T(s, frac, color)
    u = Line(t.get_corner(DL), t.get_corner(DR)).shift(DOWN * .06).set_stroke(color, 1.2, .6)
    return VGroup(t, u)


def frac_(num, den, frac=.065, color=TXT):
    n = num if isinstance(num, Mobject) else M(num, frac, color)
    d = den if isinstance(den, Mobject) else M(den, frac, color)
    bar = Line(LEFT, RIGHT).set_stroke(color, 2.2).set_width(max(n.width, d.width) + .2)
    return VGroup(n, bar, d).arrange(DOWN, buff=.1)


class SA(Scene):  # sc03：正規化＝橡皮尺，換一批結果，同一份文件的值就變了
    def construct(self):
        self.add(bgplate("glow_center"))
        cap = T("正規化：用這一批結果的最高與最低，把分數縮到 0～1", .04, TXT).move_to([XL, 3.15, 0], aligned_edge=LEFT)
        self.add(cap)
        x0, x1, y = -5.4, 5.4, .55
        pos = lambda v: x0 + (x1 - x0) * v
        band = Rectangle(width=x1 - x0, height=.16).set_fill(SCORE, .35).set_stroke(SCORE, 1.5).move_to([0, y, 0])
        ticks = VGroup(*[Line([pos(v), y - .2, 0], [pos(v), y + .2, 0]).set_stroke(LINE, 2) for v in np.linspace(0, 1, 11)])
        labs = VGroup(M("0", .05, MUTED).next_to(band, LEFT, buff=.25), M("1", .05, MUTED).next_to(band, RIGHT, buff=.25))
        self.add(band, ticks, labs)
        # 第一批：最高 12.4；第二批出現 30
        old = {"A": 0, "C": .71, "B": 1.0}
        new = {"A": 0, "C": (9.7 - 3.1) / (30 - 3.1), "B": (12.4 - 3.1) / (30 - 3.1)}
        for n in "ACB":
            col = TXT_STRONG if n == "B" else TXT
            if old[n] != new[n]:
                g = Dot([pos(old[n]), y, 0], radius=.11, color=col).set_opacity(.25)
                arc = ArcBetweenPoints([pos(old[n]), y + .3, 0], [pos(new[n]), y + .3, 0], angle=.9).set_stroke(GOLD if n == "B" else LINE, 2.5 if n == "B" else 1.5)
                arc.add_tip(tip_length=.16, tip_width=.14)
                self.add(g, arc)
            d = Dot([pos(new[n]), y, 0], radius=.12, color=col)
            self.add(d, M(n, .06, col, italic=True).next_to(d, DOWN, buff=.55 if n != "A" else .55).shift(RIGHT * (.0)))
        hi = VGroup(T("這一批的最高", .038, MUTED), M("12.4  →  30", .055, FULL)).arrange(DOWN, buff=.12).move_to([pos(1), 2.15, 0])
        self.add(hi)
        bval = VGroup(T("同一份文件", .04, TXT), M("B", .055, TXT_STRONG, italic=True), M(":  1.00  →  0.35", .055, GOLD)).arrange(RIGHT, buff=.15)
        bval.move_to([0, -1.25, 0])
        self.add(bval, note("示意").move_to([XR - .4, -1.65, 0]))


class SB(Scene):  # sc05：公式＋代入計算
    def construct(self):
        self.add(bgplate("calm"))
        rank = T("名次", .055, RANK)
        f = VGroup(M("RRF(", .065), M("d", .065, italic=True), M(")  =  Σ", .065),
                   frac_(M("1", .065), VGroup(M("k + ", .065, italic=False), rank).arrange(RIGHT, buff=.08))).arrange(RIGHT, buff=.1)
        f.move_to([0, 2.55, 0])
        under = T("每一路", .038, MUTED).next_to(f[2].get_corner(DR) + LEFT * .2, DOWN, buff=.25)
        self.add(f, under)
        rows = []
        for i, (L_, a, b, v, w) in enumerate((("A", "3", "3", "0.0317", 1.0), ("B", "1", "8", "0.0311", .981))):
            y = .75 - i * 1.35
            lab = M(L_, .07, TXT_STRONG, italic=True).move_to([-5.6, y, 0])
            t1 = frac_(M("1", .055), VGroup(M("60 + ", .055), M(a, .055, VEC)).arrange(RIGHT, buff=.05), .055)
            t2 = frac_(M("1", .055), VGroup(M("60 + ", .055), M(b, .055, FULL)).arrange(RIGHT, buff=.05), .055)
            expr = VGroup(t1, M("+", .055), t2, M("≈", .055), M(v, .06, GOLD if i == 0 else TXT)).arrange(RIGHT, buff=.25)
            expr.next_to(lab, RIGHT, buff=.6)
            bar = Rectangle(width=3.0 * w, height=.2).set_fill(GOLD if i == 0 else LINE, .9).set_stroke(width=0).move_to([2.9, y, 0], aligned_edge=LEFT)
            self.add(lab, expr, bar)
            rows.append(bar)
        axis = Line([2.9, 1.25, 0], [2.9, -.85, 0]).set_stroke(LINE, 1.5)
        self.add(axis, M("0", .045, MUTED).next_to(axis, DOWN, buff=.1))
        leg = VGroup(T("向量台名次", .038, VEC), T("全文台名次", .038, FULL)).arrange(RIGHT, buff=.5).move_to([-2.6, -1.55, 0])
        self.add(leg, note("k ＝ 60，依卡上公式計算").move_to([4.0, -1.65, 0]))


class SC(Scene):  # sc07：三欄名次連線（向量 → 全文 → 總榜），正解在全文缺席，被雜訊超車
    def construct(self):
        self.add(bgplate("currents"))
        xs = {"v": -4.4, "f": -.6, "t": 3.6}
        ys = [2.55, 1.8, 1.05, .3, -.45]
        heads = VGroup(T("向量搜尋", .042, VEC).move_to([xs["v"], 3.25, 0]), T("全文搜尋", .042, FULL).move_to([xs["f"], 3.25, 0]),
                       T("RRF 總榜", .042, TXT_STRONG).move_to([xs["t"], 3.25, 0]))
        self.add(heads)
        for x in xs.values():
            for i, y in enumerate(ys):
                self.add(M(str(i + 1), .042, LINE).move_to([x - .55, y, 0]))
        vec = {"正解": 0, "a": 1, "b": 2, "雜訊": 3, "c": 4}
        ful = {"d": 0, "e": 1, "f": 2, "雜訊": 3, "g": 4}
        tot = {"雜訊": 0, "正解": 1, "d": 2, "a": 3, "e": 4}
        col = lambda n: GOOD if n == "正解" else (TXT_STRONG if n == "雜訊" else LINE)
        # 連線（同一份文件跨欄）
        for n in set(vec) | set(ful):
            pts = []
            if n in vec: pts.append([xs["v"], ys[vec[n]], 0])
            if n in ful: pts.append([xs["f"], ys[ful[n]], 0])
            if n in tot: pts.append([xs["t"], ys[tot[n]], 0])
            if n == "正解":
                miss = [xs["f"], -1.25, 0]
                self.add(DashedLine(pts[0], miss, dash_length=.1).set_stroke(GOOD, 2, .7), DashedLine(miss, pts[1], dash_length=.1).set_stroke(GOOD, 2, .7))
                self.add(Circle(.17).set_stroke(GOOD, 2).set_fill(opacity=0).move_to(miss), T("沒撈到 → 0", .038, GOOD).next_to(miss, RIGHT, buff=.25))
                continue
            if len(pts) > 1:
                strong = n == "雜訊"
                self.add(VMobject().set_points_smoothly(pts if len(pts) == 2 else pts).set_stroke(TXT_STRONG if strong else LINE, 3 if strong else 1.3, 1 if strong else .5))
        for colname, dct in (("v", vec), ("f", ful), ("t", tot)):
            for n, r in dct.items():
                c = col(n)
                self.add(Dot([xs[colname], ys[r], 0], radius=.15 if n in ("正解", "雜訊") else .1, color=c))
        self.add(T("雜訊", .042, TXT_STRONG).next_to(Dot([xs["t"], ys[0], 0]), RIGHT, buff=.3),
                 T("正解", .042, GOOD).next_to(Dot([xs["t"], ys[1], 0]), RIGHT, buff=.3))
        self.add(T("兩路都排第 4", .038, MUTED).move_to([(xs["v"] + xs["f"]) / 2, ys[3] + .42, 0]))
        self.add(note("排名為示意").move_to([XR - .7, -1.55, 0]))
