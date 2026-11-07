"""實驗 x01：30 秒測試片（不發布）。內容：rrf-rank-fusion c1、c3、c5、c6、c9。
sc01 分數尺度不同、不能直接加 → sc02 只看名次（錘錘的「？→！」）→ sc03 公式、k=60、A 與 B 的例子。"""
from kit import *

ORANGE, SKY, MINT = C["BM25"], C["cosine"], C["名次"]


def doc_icon(letter, color, w=.62, h=.8):
    r = RoundedRectangle(corner_radius=.08, width=w, height=h).set_fill(PANEL, 1).set_stroke(color, 3)
    fold = Polygon(r.get_corner(UR) + LEFT * .2, r.get_corner(UR), r.get_corner(UR) + DOWN * .2).set_fill(color, .7).set_stroke(width=0)
    lines = VGroup(*[Line(LEFT * .17, RIGHT * (.17 - .08 * (i % 2))).set_stroke(MUTED, 2.5, .6) for i in range(2)]).arrange(DOWN, buff=.1, aligned_edge=LEFT)
    let = B(letter, .04, TXT_STRONG)
    VGroup(let, lines).arrange(DOWN, buff=.1).move_to(r)
    return VGroup(r, fold, lines, let)


def rank_badge(n, color=MINT, frac=.036):
    return pill(f"第 {n} 名", color, frac, fill=.22, bold=True, txt=TXT_STRONG)


def dot_label(x, y, s, color, dy=.42):
    d = Dot([x, y, 0], radius=.09, color=color)
    lab = B(s, .034, color).move_to([x, y + dy, 0])
    return d, lab


class Sc01(Timed):
    SID = "sc01"
    BG = "glow_center"

    def construct(self):
        y = 1.55
        # --- BM25：範圍不固定的尺 ---
        t_bm = B("BM25", .05, ORANGE).move_to([-3.4, 3.05, 0])
        x0, unit = -5.9, 4.2 / 14
        bm_line = Line([x0, y, 0], [x0 + 14 * unit, y, 0]).set_stroke(ORANGE, 5)
        bm_more = DashedLine([x0 + 14 * unit, y, 0], [x0 + 14 * unit + .6, y, 0], dash_length=.12).set_stroke(ORANGE, 5)
        bm_q = B("？", .045, ORANGE).next_to(bm_more, RIGHT, buff=.08)
        bm_zero = T("0", .032, MUTED).move_to([x0, y - .38, 0])
        bm_tick = Line([x0, y - .12, 0], [x0, y + .12, 0]).set_stroke(ORANGE, 4)
        bm_pts = [dot_label(x0 + v * unit, y, s, ORANGE) for v, s in ((3.1, "3.1"), (9.7, "9.7"), (12.4, "12.4"))]
        bm_note = T("範圍不固定", .034, TXT).move_to([-3.4, y - .9, 0])
        # --- cosine：-1 到 1 ---
        t_cos = B("cosine", .05, SKY).move_to([3.4, 3.05, 0])
        cx, half = 3.4, 2.5
        cos_line = Line([cx - half, y, 0], [cx + half, y, 0]).set_stroke(SKY, 5)
        brackets = VGroup(*[VGroup(Line([cx + s * half, y - .22, 0], [cx + s * half, y + .22, 0]),
                                   Line([cx + s * half, y - .22, 0], [cx + s * (half - .14), y - .22, 0]),
                                   Line([cx + s * half, y + .22, 0], [cx + s * (half - .14), y + .22, 0])).set_stroke(SKY, 5) for s in (-1, 1)])
        cos_ticks = VGroup(*[T(s, .032, MUTED).move_to([cx + v * half, y - .42, 0]) for v, s in ((-1, "-1"), (0, "0"), (1, "1"))])
        cos_pts = [dot_label(cx + v * half, y, s, SKY, dy) for v, s, dy in ((.42, "0.42", .42), (.71, "0.71", .82), (.83, "0.83", .42))]
        cos_note = T("-1 到 1 之間", .034, TXT).move_to([3.4, y - .9, 0])
        hint = tag("分數為示意").move_to([5.55, 3.05, 0])
        # --- 錘錘 ---
        p = Plumb(scale=.27).place([.12, 1.4, 0])

        self.at(self.A("a1", 0.0), FadeIn(t_bm), Create(bm_line), FadeIn(bm_zero), Create(bm_tick), FadeIn(p, shift=DOWN * .4), run_time=.6, sfx="pop", gain=.6)
        self.at(self.A("a1", 0.13), LaggedStart(*[AnimationGroup(GrowFromCenter(d), FadeIn(l, shift=UP * .15)) for d, l in bm_pts], lag_ratio=.25),
                FadeIn(hint), run_time=.7, sfx="tick")
        self.at(self.A("a1", 0.3), Create(bm_more), FadeIn(bm_q, scale=1.4), Write(bm_note), *p.look(LEFT), run_time=.7)
        self.at(self.A("a1", 0.55), FadeIn(t_cos), Create(cos_line), FadeIn(brackets), FadeIn(cos_ticks), *p.look(RIGHT), run_time=.6, sfx="pop", gain=.6)
        self.at(self.A("a1", 0.7), LaggedStart(*[AnimationGroup(GrowFromCenter(d), FadeIn(l, shift=UP * .15)) for d, l in cos_pts], lag_ratio=.25),
                run_time=.7, sfx="tick")
        self.at(self.A("a1", 0.86), Write(cos_note), Indicate(brackets, color=TXT_STRONG, scale_factor=1.15), run_time=.6)

        # --- 直接加起來？ ---
        n1, n2 = B("12.4", .075, ORANGE), B("0.83", .075, SKY)
        eq = VGroup(n1, B("＋", .075, TXT), n2, B("＝", .075, TXT), B("？", .075, BAD)).arrange(RIGHT, buff=.3).move_to([-1.2, -.55, 0])
        self.at(self.A("a2", 0.0), TransformFromCopy(bm_pts[2][1], n1), TransformFromCopy(cos_pts[2][1], n2),
                FadeIn(VGroup(eq[1], eq[3], eq[4])), *p.look(DOWN), run_time=.7, sfx="whoosh", gain=.7)
        self.at(self.A("a2", 0.42), *p.curl(), *p.mood("squint"), Wiggle(eq[4], scale_value=1.3), run_time=.6, sfx="boing", gain=.6)
        st = stamp("沒有意義", BAD, .06).move_to([4.1, -1.2, 0])
        self.at(self.A("a2", 0.8), stamp_in(st), run_time=.32, sfx="thud")
        self.finish()


class Sc02(Timed):
    SID = "sc02"
    BG = "glow_left"

    def construct(self):
        ys = [1.7, .6, -.5]
        t_bm = B("BM25", .045, ORANGE).move_to([-4.65, 2.65, 0])
        t_cos = B("cosine", .045, SKY).move_to([1.45, 2.65, 0])
        hint = tag("分數為示意").move_to([-1.6, 2.65, 0])
        left_docs = VGroup(*[doc_icon(L_, ORANGE).move_to([-5.4, y, 0]) for L_, y in zip("DAC", ys)])
        right_docs = VGroup(*[doc_icon(L_, SKY).move_to([2.2, y, 0]) for L_, y in zip("ABD", ys)])
        left_chips = VGroup(*[pill(s, ORANGE, .036, fill=.2, bold=True).move_to([-3.9, y, 0]) for s, y in zip(("12.4", "9.7", "3.1"), ys)])
        right_chips = VGroup(*[pill(s, SKY, .036, fill=.2, bold=True).move_to([.7, y, 0]) for s, y in zip(("0.83", "0.71", "0.42"), ys)])
        left_ranks = VGroup(*[rank_badge(i + 1).move_to([-3.9, y, 0]) for i, y in enumerate(ys)])
        right_ranks = VGroup(*[rank_badge(i + 1).move_to([.7, y, 0]) for i, y in enumerate(ys)])
        p = Plumb(scale=.42).place([4.9, .8, 0])
        p.set_curled("squint")
        self.add(self.chapter_tag(1, "名次，不是分數"), t_bm, t_cos, hint, left_docs, right_docs, left_chips, right_chips, p)
        self.card_out()

        # 「不看分數」：分數碎掉
        pieces = VGroup()
        anims = []
        for chip in [*left_chips, *right_chips]:
            pcs, an = shatter(chip.box, n=4, dist=2.5, seed=len(pieces))
            pieces.add(pcs)
            anims += [an, FadeOut(chip.txt, scale=.5)]
        self.at(self.A("b1", 0.3), run_time=.1)
        self.remove(*[c.box for c in [*left_chips, *right_chips]])
        self.add(pieces)
        self.at(self.A("b1", 0.32), *anims, FadeOut(hint), run_time=.7, sfx="crunch", gain=.7)
        self.remove(pieces)
        # 「只看名次」：名次出現，錘錘的繩子拉直成「！」——招牌時刻
        self.at(self.A("b1", 0.66), LaggedStart(*[pop_in(m) for m in [*left_ranks, *right_ranks]], lag_ratio=.08),
                *p.straighten(), *p.mood("wow"), run_time=.7, sfx="chime")
        self.at(self.E("b1", 0.05), *p.light_on(), run_time=.5, sfx="rise", gain=.5)

        # 「名次每一路都有，也能直接互相比較」
        links = VGroup(*[DoubleArrow(l.get_right() + RIGHT * .12, r.get_left() + LEFT * .12, buff=0, stroke_width=4,
                                     tip_length=.18).set_color(MINT) for l, r in zip(left_ranks, right_ranks)])
        eqs = VGroup(*[B("＝", .04, MINT).next_to(a, UP, buff=.06) for a in links])
        self.at(self.A("b2", 0.15), Indicate(left_ranks, color=MINT, scale_factor=1.08), Indicate(right_ranks, color=MINT, scale_factor=1.08), run_time=.7)
        self.at(self.A("b2", 0.55), LaggedStart(*[GrowFromCenter(a) for a in links], lag_ratio=.2), LaggedStart(*[FadeIn(e) for e in eqs], lag_ratio=.2),
                *p.light_off(), *p.mood("happy"), run_time=.8, sfx="ding", gain=.6)
        self.finish()


class Sc03(Timed):
    SID = "sc03"
    BG = "calm"

    def construct(self):
        # --- 公式（以 Text 排，不用 LaTeX）---
        lhs = VGroup(B("RRF 分數", .055, TXT_STRONG), B("＝", .055, TXT)).arrange(RIGHT, buff=.25)
        sigma = B("Σ", .1, TXT_STRONG)
        under = T("每一路", .03, MUTED).next_to(sigma, DOWN, buff=.12)
        num_ = B("1", .055, TXT_STRONG)
        k_ = B("k", .055, TXT_STRONG)
        den = VGroup(k_, B("＋", .055, TXT), B("名次", .055, MINT)).arrange(RIGHT, buff=.15)
        bar = Line(LEFT, RIGHT).set_stroke(TXT, 4).set_width(den.width + .3)
        frac_ = VGroup(num_, bar, den).arrange(DOWN, buff=.14)
        formula = VGroup(lhs, VGroup(sigma, under), frac_).arrange(RIGHT, buff=.35).move_to([-1.0, 2.35, 0])
        under.next_to(sigma, DOWN, buff=.12)
        note1 = T("每一路的 weight 預設 1.0（這裡省略）", .03, MUTED).move_to([0, ANN_Y, 0])
        kpill = pill("k ＝ 60", GOLD, .05, fill=.2, bold=True, txt=TXT_STRONG).move_to([3.9, 2.35, 0])
        note2 = T("60 來自 Cormack 等人 2009 年論文的建議值", .03, MUTED).move_to([0, ANN_Y, 0])
        p = Plumb(scale=.36).place([5.45, 1.0, 0])
        p.set_mood("happy")
        self.add(p)

        self.at(self.A("c1", 0.0), Write(lhs), FadeIn(VGroup(sigma, under)), run_time=.6)
        self.at(self.A("c1", 0.18), Write(frac_), run_time=.8, sfx="tick")
        self.at(self.A("c1", 0.45), Indicate(den[2], color=MINT, scale_factor=1.2), Indicate(k_, color=TXT_STRONG), run_time=.6)
        self.at(self.A("c1", 0.75), Indicate(sigma, color=GOLD, scale_factor=1.25), FadeIn(note1, shift=UP * .1), run_time=.6)
        self.at(self.A("c2", 0.3), TransformFromCopy(k_, kpill), FadeOut(note1), FadeIn(note2, shift=UP * .1), *p.look(LEFT), run_time=.7, sfx="pop")

        # --- 舉例：A 兩路都第 3，B 一路第 1、一路第 8 ---
        ex = tag("舉例", MINT).move_to([-5.55, .95, 0])
        heads = VGroup(T("第一路", .03, MUTED).move_to([-4.0, .95, 0]), T("第二路", .03, MUTED).move_to([-2.6, .95, 0]),
                       T("RRF 分數", .03, MUTED).move_to([.2, .95, 0]))
        rows = []
        for i, (L_, r1, r2, w) in enumerate((("A", 3, 3, 4.0), ("B", 1, 8, 3.7))):
            y = .15 - i * 1.15
            d = doc_icon(L_, MINT).move_to([-5.55, y, 0])
            b1_ = pill(f"第 {r1}", MINT, .034, fill=.2, bold=True, txt=TXT_STRONG).move_to([-4.0, y, 0])
            b2_ = pill(f"第 {r2}", MINT, .034, fill=.2, bold=True, txt=TXT_STRONG).move_to([-2.6, y, 0])
            bar_ = Rectangle(width=w, height=.42).set_fill(MINT if i == 0 else NEUTRAL, .9).set_stroke(width=0).move_to([-1.6, y, 0], aligned_edge=LEFT)
            rows.append((d, b1_, b2_, bar_))
        sk = tag("長度為示意").move_to([2.9, .95, 0])
        self.at(self.A("c3", 0.04), FadeIn(ex), FadeIn(heads), FadeOut(note2), *p.look(DOWN + LEFT), run_time=.5)
        self.at(self.A("c3", 0.2), FadeIn(rows[0][0], shift=RIGHT * .2), pop_in(rows[0][1]), pop_in(rows[0][2]), run_time=.6, sfx="tick")
        self.at(self.A("c3", 0.48), FadeIn(rows[1][0], shift=RIGHT * .2), pop_in(rows[1][1]), pop_in(rows[1][2]), run_time=.6, sfx="tick")
        self.at(self.A("c3", 0.72), GrowFromEdge(rows[0][3], LEFT), GrowFromEdge(rows[1][3], LEFT), FadeIn(sk), run_time=.7, sfx="rise", gain=.5)
        self.at(self.A("c3", 0.9), *p.point_at(rows[0][3].get_right() + RIGHT * .15), Indicate(rows[0][3], color=MINT, scale_factor=1.05),
                run_time=.7, sfx="ding", gain=.6)
        self.finish()
