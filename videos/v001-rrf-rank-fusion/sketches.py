"""v001 規劃草圖（設計模式，低解析度，只看構圖）：
PYTHONPATH=lib uv run python -m manim -ql -s --media_dir out/v001-rrf-rank-fusion/sketch videos/v001-rrf-rank-fusion/sketches.py K1 K2 K3 K4 K5 K6 K7
"""
from kit import *

VEC, FULL, RANK, SCORE, NOISE = S["concept_pool"][1], S["concept_pool"][0], S["concept_pool"][5], S["concept_pool"][2], S["concept_pool"][3]


def label(s):
    return B(s, .045, GOLD).to_corner(UL, buff=.35)


def chart(title, color, rows, x, y=1.3, w=3.2):
    """排行榜：標題＋幾列（名稱、分數）。"""
    head = RoundedRectangle(corner_radius=.12, width=w, height=.6).set_fill(color, .9).set_stroke(width=0)
    ht = B(title, .042, SCREEN).move_to(head)
    g = VGroup(VGroup(head, ht))
    for i, (n, sc) in enumerate(rows):
        r = RoundedRectangle(corner_radius=.08, width=w, height=.5).set_fill(PANEL, 1).set_stroke(color, 2)
        a = B(f"{i + 1}", .04, color).move_to(r.get_left() + RIGHT * .3)
        b = T(n, .04, TXT).move_to(r)
        c = T(sc, .04, color).move_to(r.get_right() + LEFT * .45)
        g.add(VGroup(r, a, b, c))
    return g.arrange(DOWN, buff=.08).move_to([x, y, 0])


def flap_board(w=2.6, h=1.5):
    """機制角色候選：翻牌看板（有臉）。"""
    body = RoundedRectangle(corner_radius=.2, width=w, height=h).set_fill("#20313A", 1).set_stroke(GOLD, 3)
    flaps = VGroup(*[RoundedRectangle(corner_radius=.05, width=.5, height=.7).set_fill("#0E1A20", 1).set_stroke(TXT, 1.5) for _ in range(3)]).arrange(RIGHT, buff=.1).move_to(body).shift(UP * .1)
    digits = VGroup(*[B(s, .05, TXT_STRONG).move_to(f) for s, f in zip("第3名", flaps)])
    eyes = VGroup(*[Dot(radius=.07, color=GOLD) for _ in range(2)]).arrange(RIGHT, buff=.5).next_to(flaps, UP, buff=.1)
    legs = VGroup(*[Line(ORIGIN, DOWN * .5).set_stroke(TXT, 5) for _ in range(2)]).arrange(RIGHT, buff=1.2).next_to(body, DOWN, buff=0)
    return VGroup(legs, body, flaps, digits, eyes)


class K1(Scene):  # 開場：單位不同的東西不能相加
    def construct(self):
        self.add(bgplate("glow_center"), label("1 開場：12.4 公斤 ＋ 0.83 公尺 ＝ ？"))
        left = VGroup(B("向量搜尋", .045, VEC), B("0.83", .1, VEC)).arrange(DOWN).move_to([-3.5, 1.2, 0])
        right = VGroup(B("全文搜尋", .045, FULL), B("12.4", .1, FULL)).arrange(DOWN).move_to([3.5, 1.2, 0])
        eq = B("0.83 ＋ 12.4 ＝ ？", .08, TXT_STRONG).move_to([0, -.6, 0])
        p = Plumb(.35).place([0, 1.4, 0]).set_curled("squint")
        self.add(left, right, eq, p, tag("分數為示意").move_to([5.5, -1.5, 0]))


class K2(Scene):  # 為什麼在乎：一個問題分成好幾路搜尋
    def construct(self):
        self.add(bgplate("glow_left"), label("2 為什麼在乎：一個問題，好幾路搜尋"))
        q = pill("同一個查詢", TXT_STRONG, .045, bold=True).move_to([-4.6, .8, 0])
        routes = VGroup(*[pill(s, c, .042, bold=True) for s, c in (("向量搜尋", VEC), ("全文搜尋", FULL), ("IDF 加權", SCORE))]).arrange(DOWN, buff=.4).move_to([-.6, .8, 0])
        arrows = VGroup(*[Arrow(q.get_right(), r.get_left(), buff=.15, stroke_width=4).set_color(MUTED) for r in routes])
        out = VGroup(T("Cerebras Knowledge", .04, TXT), B("每天 15,000+ 次查詢", .05, GOLD), T("（官方說法）", .038, MUTED)).arrange(DOWN, buff=.12).move_to([4.2, .8, 0])
        self.add(q, routes, arrows, out)


class K3(Scene):  # 暖身：兩份排行榜，分數的尺度不同；正規化會飄
    def construct(self):
        self.add(bgplate("glow_center"), label("3 暖身：兩份排行榜合成一份總榜"))
        a = chart("向量台", VEC, [("A", "0.83"), ("D", "0.71"), ("B", "0.42")], -3.6)
        b = chart("全文台", FULL, [("B", "12.4"), ("C", "9.7"), ("A", "3.1")], .4)
        ruler = VGroup(B("正規化＝橡皮尺", .045, TXT_STRONG), T("同一份文件，換一批結果，值就變了", .04, MUTED)).arrange(DOWN, buff=.15).move_to([4.5, .2, 0])
        self.add(a, b, ruler, tag("示意").move_to([4.5, 2.6, 0]))


class K4(Scene):  # 命名：翻牌看板把分數翻成名次 → 公式
    def construct(self):
        self.add(bgplate("glow_left"), label("4 命名：分數翻成名次 → 1 ÷ (k + 名次)"))
        fb = flap_board().move_to([-4.3, .6, 0])
        f = VGroup(B("RRF 分數 ＝ Σ", .07, TXT_STRONG), VGroup(B("1", .07, TXT_STRONG), Line(LEFT, RIGHT).set_width(2.6).set_stroke(TXT, 4),
                                                              VGroup(B("k ＋", .07, TXT_STRONG), B("名次", .07, RANK)).arrange(RIGHT, buff=.15)).arrange(DOWN, buff=.12)).arrange(RIGHT, buff=.3)
        f.move_to([1.5, 1.4, 0])
        p = Plumb(.3).place([5.7, .4, 0]).set_mood("wow")
        self.add(fb, f, p, T("機制角色候選：翻牌看板（每支影片不同）", .038, MUTED).move_to([-3.6, -1.5, 0]))


class K5(Scene):  # 算給你看：k = 60，A vs B
    def construct(self):
        self.add(bgplate("calm"), label("5 算給你看：k ＝ 60 時，A 和 B 誰贏"))
        rows = VGroup(
            VGroup(B("A", .07, RANK), T("第 3 ＋ 第 3", .045, TXT), B("1/63 ＋ 1/63 ≈ 0.0317", .05, TXT_STRONG)).arrange(RIGHT, buff=.5),
            VGroup(B("B", .07, MUTED), T("第 1 ＋ 第 8", .045, TXT), B("1/61 ＋ 1/68 ≈ 0.0311", .05, TXT)).arrange(RIGHT, buff=.5),
        ).arrange(DOWN, buff=.6, aligned_edge=LEFT).move_to([-.3, .9, 0])
        self.add(rows, tag("依卡上公式計算", RANK).move_to([3.8, -.6, 0]), stamp("A 贏", GOOD, .06, -8).move_to([4.6, 1.6, 0]))


class K6(Scene):  # 反轉：某一路沒撈到，共識變懲罰
    def construct(self):
        self.add(bgplate("currents"), label("6 反轉：某一路完全沒撈到，共識變成懲罰"))
        a = chart("向量台", VEC, [("正解", ""), ("雜訊", ""), ("…", "")], -3.4)
        b = chart("全文台", FULL, [("雜訊", ""), ("…", ""), ("…", "")], .6)
        miss = VGroup(B("正解：沒撈到", .045, MUTED), B("貢獻 ＝ 0", .06, MUTED)).arrange(DOWN).move_to([4.6, 1.0, 0])
        p = Plumb(.28).place([4.6, -.9, 0]).set_mood("flat")
        self.add(a, b, miss, p)


class K7(Scene):  # 補救由淺到深＋這集重點
    def construct(self):
        self.add(bgplate("abyss"), label("7 補救由淺到深 ＋ 這集重點"))
        steps = VGroup(*[pill(s, c, .045, bold=True, txt=TXT_STRONG) for s, c in (("① 拉深召回（top 50～100）", VEC), ("② 修表示層（加原始文字）", FULL), ("③ reranker 重新打分", RANK))])
        steps.arrange(DOWN, buff=.35, aligned_edge=LEFT).move_to([-2.4, .9, 0])
        p = Plumb(.3).place([3.0, .9, 0])
        p.bob.shift(DOWN * .6)
        card = takeaway_card(["名次可以比", "分數不行"], .045).move_to([4.6, -.8, 0])
        self.add(steps, p, card)
