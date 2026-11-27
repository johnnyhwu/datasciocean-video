"""v005 LLM-as-a-Verifier：sc01～sc05。大圖元件在 world.py，分鏡在 board.py，設計在 design.md。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa: E402,F401,F403

EASE = rate_functions.ease_in_out_sine
_Indicate = Indicate


class Indicate(_Indicate):
    """不給 color 時只放大、不改色（manim 預設會閃成黃色；用 get_color() 碰到群組會把填色整片塗白）。"""

    def __init__(self, mobject, scale_factor=1.2, color=None, **kw):
        self._keep = color is None
        super().__init__(mobject, scale_factor=scale_factor, color=color or YELLOW, **kw)

    def create_target(self):
        if not self._keep:
            return super().create_target()
        return self.mobject.copy().scale(self.scale_factor)
H7_SHOT = (PANEL_P["judge"] + RIGHT * 1.4, 9.5)
ROW_C = S1 + np.array([1.3, .85, 0])
JUDGE2 = S1 + np.array([-4.6, -.8, 0])
_PAPER_DIR = Path(__file__).resolve().parents[2] / "out" / "v005-llm-verifier" / "paper"
TITLE_KEY = (126, 388, 171, 202)         # 「LLM-as-a-Verifier:」的像素範圍（程式量測）
FIG_TB = (125, 400, 431, 612)            # Figure 1 的 Terminal-Bench 那一格


# ---------------- 共用 ----------------
class Sheet5(Timed):
    BG = "flat"

    def plumb_in(self, p, scale=.42):
        top = self.camera.frame.get_top()[1] + .6
        pl = Plumb(scale, top_y=top).place(p + UP * 4)
        pl.set_mood("neutral")
        tgt = pl.copy().place(p)
        return pl, [Transform(pl, tgt, rate_func=rate_functions.ease_out_back)]

    def tail(self, *anims, run=.6, gap=1.0):
        """場景收尾的小動作：結束在下一場開始前 gap 秒（接縫空檔 0.8～1.6 秒）。"""
        end = self.sc["frames"] / config.frame_rate
        self.at(max(self.t, end - gap - run), *anims, run_time=run)

    def plumb_out(self, pl):
        tgt = pl.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.get_top()[1] + 1.0 - tgt.bodyg.get_bottom()[1]))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(pl, tgt, rate_func=rate_functions.ease_in_cubic)]


PAGE_CUTS = {"top": ("page1_top.png", (95, 105, 1130, 640)), "cut": ("page1_cut.png", (95, 105, 1130, 1150))}
BAR865 = (160, 216, 432, 606)            # Figure 1 裡 Terminal-Bench 86.5% 那根紅柱（含數字）


def paper_page(c, h=5.2, which="top"):
    """論文第 1 頁（arXiv 2607.05391v2，CC BY 4.0）。top＝標題到 Figure 1；cut＝標題到摘要。.px 換座標；.mark 螢光筆。"""
    c = np.array(c, dtype=float)
    fn, crop = PAGE_CUTS[which]
    img = ImageMobject(str(_PAPER_DIR / fn))
    img.height = h
    img.move_to(c)
    w = img.width
    sh = Rectangle(width=w, height=h).set_fill("#000000", .45).set_stroke(width=0).move_to(c + np.array([.12, -.14, 0]))
    sh.nocheck = True
    g = Group(sh, img)
    x0, y0, x1, y1 = crop

    def px(x, y):
        return c + np.array([((x - x0) / (x1 - x0) - .5) * w, (.5 - (y - y0) / (y1 - y0)) * h, 0])

    def mark(box, color, pad=6):
        a, b = px(box[0] - pad, box[2] - pad), px(box[1] + pad, box[3] + pad)
        r = Rectangle(width=b[0] - a[0], height=a[1] - b[1]).set_fill(color, .38).set_stroke(width=0).move_to((a + b) / 2)
        r.nocheck = True
        return r
    g.img, g.px, g.mark = img, px, mark
    g.nocheck = True
    return g


def task_card():
    c = VGroup(T("題目：把沒優化過的 SQL 查詢改快", .04, INK), T("輸出要完全相同", .04, GOOD)).arrange(DOWN, buff=.14)
    box = SurroundingRectangle(c, buff=.2, corner_radius=.12).set_fill(PANEL, 1).set_stroke(MUTED, 2)
    return VGroup(box, c).move_to(TASK_C)


def db_icon(p, label, color=MUTED):
    p = np.array(p, dtype=float)
    body = Rectangle(width=.8, height=.55).set_fill(PANEL, 1).set_stroke(color, 2.5).move_to(p)
    top = Ellipse(width=.8, height=.24).set_fill(PANEL, 1).set_stroke(color, 2.5).move_to(body.get_top())
    lab = T(label, .038, TXT).next_to(body, RIGHT, buff=.2)
    g = VGroup(body, top, lab)
    g.overlap_ok = True
    return g


def paper_row(scores, dim_idx=()):
    g = VGroup()
    for i, s in enumerate(scores):
        pap = RoundedRectangle(corner_radius=.08, width=1.15, height=1.45).set_fill(PANEL, 1).set_stroke(MUTED, 2)
        it = VGroup(pap, B(str(s), .072, INK).move_to(pap))
        it.score = s
        if i in dim_idx:
            it.set_opacity(.3)
        g.add(it)
    g.arrange(RIGHT, buff=.45).move_to(ROW_C)
    return g


def medal(p):
    rib = VGroup(Polygon(LEFT * .2 + UP * .2, LEFT * .02 + UP * .2, LEFT * .12 + DOWN * .15).set_fill(BAD, 1).set_stroke(width=0),
                 Polygon(RIGHT * .2 + UP * .2, RIGHT * .02 + UP * .2, RIGHT * .12 + DOWN * .15).set_fill(DIST, 1).set_stroke(width=0))
    med = VGroup(rib, Circle(.26).set_fill(ARG, 1).set_stroke(GOLD, 3)).arrange(DOWN, buff=-.08)
    m = VGroup(med, T("獎勵", .04, TXT)).arrange(RIGHT, buff=.15)
    return m.move_to(p)


def tb_box():
    box = RoundedRectangle(corner_radius=.15, width=3.5, height=1.3).set_fill(PANEL, 1).set_stroke(DIST, 3).move_to(S1 + np.array([-.1, -1.95, 0]))
    lab = B("Terminal-Bench", .045, DIST).move_to(box.get_top() + DOWN * .38)
    cards = VGroup(*[RoundedRectangle(corner_radius=.05, width=.5, height=.34).set_fill(SCREEN, 1).set_stroke(MUTED, 1.5) for _ in range(4)]).arrange(RIGHT, buff=.12)
    cards.move_to(box.get_center() + DOWN * .32)
    g = VGroup(box, lab, cards)
    g.box, g.lab, g.cards = box, lab, cards
    return g


def token_row():
    toks = ["…", "這條", "軌跡", "我", "給"]
    g = VGroup(*[token_box(t, TEAL_L) for t in toks], token_box("<score_A>", DIST)).arrange(RIGHT, buff=.12)
    g.move_to(np.array([S2[0] - 1.6, TOK_Y, 0]))
    return g


def empty_cells(w):
    """百格板的格子先畫成空的（之後一格一格上色）。回傳上色後的目標顏色。"""
    cols = [c.get_fill_color() for c in w.cells]
    for c in w.cells:
        c.set_fill(opacity=0)
    return cols


def judge_blank(p, s=.9, mood="unsure"):
    """胸口塞了一塊沒有數字的灰牌（被壓扁後的分數）。"""
    j = judge(p, s, mood, "", TIE)
    j.win.set_fill(TIE, .9)
    return j


def pressed(J):
    return press(J.head.get_top() + UP * .95, w=2.0, label="只取最高")


# ---------------- builders：每場最後一格 ----------------
def sc01_end():
    A, Bs = scroll("甲", SCR_A), scroll("乙", SCR_B)
    ck = check_mark(GOOD, .3).next_to(A.title, RIGHT, buff=.25)
    xb = cross_mark(BAD, .3).next_to(Bs.title, RIGHT, buff=.25)
    ck.set_z_index(2)
    xb.set_z_index(2)
    J = judge_blank(JUDGE1)
    pr = pressed(J)
    P1 = board_panel("judge", PANEL_P["judge"], show_bad=False, legend=True, title="1～5 分評審")
    return dict(A=A, Bs=Bs, ck=ck, xb=xb, J=J, pr=pr, P1=P1)


def sc02_end():
    d = sc01_end()
    J = judge(JUDGE2, .85, "unsure", "?")
    row = VGroup(*paper_row([5, 5, 4, 3, 2, 1])[:4])
    md = medal(row[0].get_top() + UP * .62)
    stuck = VGroup(SurroundingRectangle(VGroup(row[0], row[1]), color=TIE, buff=.12), B("卡住", .05, TIE))
    stuck[1].next_to(stuck[0], DOWN, buff=.25)
    return dict(P1=d["P1"], J=J, row=row, md=md, stuck=stuck)


def s2_final():
    """sc03 結束時腦袋站的樣子。"""
    sk = skull()
    base_a = Line(A_POS + LEFT * 2.2, A_POS + RIGHT * 2.2).set_stroke(LINE, 3)
    base_b = Line(B_POS + LEFT * 2.2, B_POS + RIGHT * 2.2).set_stroke(LINE, 3)
    c5a, c5b = cube5(A_POS + UP * .45), cube5(B_POS + UP * .45)
    eqs = B("＝", .09, TIE).move_to((c5a.get_center() + c5b.get_center()) / 2)
    bin_ = discard_bin(True)
    bin_.chips.set_opacity(.25)
    tA, tB = score_tag("A"), score_tag("B")
    nX = T("軌跡 X", .042, INK).move_to(A_POS + DOWN * .82)
    nY = T("軌跡 Y", .042, INK).move_to(B_POS + DOWN * .82)
    return dict(sk=sk, base_a=base_a, base_b=base_b, c5a=c5a, c5b=c5b, eqs=eqs, bin=bin_, tA=tA, tB=tB, nX=nX, nY=nY)


def s1_final():
    return station1()


def sc03_end():
    """sc03 最後一格：考場收好、計分板（開場那塊）、腦袋站兩個灰 5＋「＝」，壓模停在 Y 上。"""
    d = dict(P1=sc01_end()["P1"], st1=s1_final())
    d.update(s2_final())
    d["prs"] = press(d["c5b"].get_top() + UP * .45)
    return d


def s4_final():
    rul = ruler_v(np.array([S4[0] - 5.3, BASE4, 0]))
    ta, tb = tower_x(), tower_y()
    v1 = T("2.25", .04, BG).move_to(ta.blocks[4])
    v2 = T("1.4", .04, BG).move_to(ta.blocks[3])
    la = T("軌跡 X", .04, INK).next_to(np.array([TX_X, BASE4, 0]), DOWN, buff=.25)
    lb = T("軌跡 Y", .04, INK).next_to(np.array([TY_X, BASE4, 0]), DOWN, buff=.25)
    pa = pointer(np.array([TX_X + .8, ta.top_y, 0]), "4.16")
    pb = pointer(np.array([TY_X + .8, tb.top_y, 0]), "約 4.3")
    return dict(rul=rul, ta=ta, tb=tb, v1=v1, v2=v2, la=la, lb=lb, pa=pa, pb=pb)


def sc04_end():
    d = sc03_end()
    d["prs"] = press(d["c5a"].get_top() + UP * .45)
    d.update(s4_final())
    return d


def sc05_end():
    d = sc04_end()
    d.pop("P1")
    d.update(s3_final())
    return d


def mini_cards():
    """k1 回到計分板時帶回開場的甲、乙：圖例左右各一張小卡（甲在左、乙在右，和開場一樣）。"""
    y = S3[1] + 2.45

    def mc(name, mk, x):
        box = RoundedRectangle(corner_radius=.1, width=1.75, height=.62).set_fill(PANEL, 1).set_stroke(MUTED, 2)
        row_ = VGroup(B(name, .04, INK), mk).arrange(RIGHT, buff=.16).move_to(box)
        return VGroup(box, row_).move_to(np.array([x, y, 0]))
    return VGroup(mc("軌跡甲", check_mark(GOOD, .2), S3[0] - 4.65), mc("軌跡乙", cross_mark(BAD, .2), S3[0] + 4.65))


def s3_final():
    P1 = board_panel("judge", PANEL_P["judge"])
    P2 = board_panel("v5", PANEL_P["v5"])
    P3 = board_panel("v20", PANEL_P["v20"])
    lg = board_legend(True)
    a1 = arrow_lab(P1.waf.get_right(), P2.waf.get_left(), "argmax", "→ 期望值", ARG, EV)
    a2 = arrow_lab(P2.waf.get_right(), P3.waf.get_left(), "5 格", "→ 20 格", GK)
    return dict(P1=P1, P2=P2, P3=P3, lg=lg, a1=a1, a2=a2, mc=mini_cards())


def arrow_lab(a, b, l1, l2, col, col2=None):
    ar = Arrow(a, b, buff=.15, color=col, stroke_width=5, max_tip_length_to_length_ratio=.3)
    lab = VGroup(T(l1, .038, col), T(l2, .038, col2 or col)).arrange(DOWN, buff=.1).next_to(ar, DOWN, buff=.18)
    g = VGroup(ar, lab)
    g.ar, g.lab = ar, lab
    return g


def add_all(scene, *ds):
    for d in ds:
        for v in (d.values() if isinstance(d, dict) else [d]):
            scene.add(v)


# ================= sc01 一百次裡 88 次平手 =================
class Sc01(Sheet5):
    SID = "sc01"

    def construct(self):
        A_ = self.A
        self.add(road())
        self.cam_set(S1, 14)
        A, Bs = scroll("甲", SCR_A), scroll("乙", SCR_B)
        A.lines.set_opacity(0).shift(LEFT * .35)
        Bs.lines.set_opacity(0).shift(LEFT * .35)
        ck = check_mark(GOOD, .3).next_to(A.title, RIGHT, buff=.25)
        xb = cross_mark(BAD, .3).next_to(Bs.title, RIGHT, buff=.25)
        ck.set_z_index(2)
        xb.set_z_index(2)
        # h1 兩卷軌跡滑進來；一個做對、一個偷吃步
        self.at(0, FadeIn(A, shift=RIGHT * 2.5), FadeIn(Bs, shift=LEFT * 2.5), run_time=1.0, sfx="slide", gain=.35)
        self.at(A_("h1", .3), Indicate(A.title, scale_factor=1.12), Indicate(Bs.title, scale_factor=1.12), run_time=.6)
        self.at(A_("h1", .42), LaggedStart(*[l.animate.set_opacity(.28).shift(RIGHT * .35) for l in list(A.lines) + list(Bs.lines)], lag_ratio=.35), run_time=3.4)
        self.at(A_("h1a", .15), Create(ck), run_time=.4)
        self.at(A_("h1a", .6), Create(xb), run_time=.4)
        # h5 評審走進來
        J = judge(JUDGE1, .9, "calm", "?")
        self.at(A_("h5", .02), FadeIn(J, shift=UP * 1.2), run_time=.7)
        self.at(A_("h5", .3), Indicate(J, scale_factor=1.06), run_time=.6)
        self.at(A_("h5", .55), Indicate(J.score, color=INK, scale_factor=1.4), run_time=.7)
        self.at(A_("h5", .85), Wiggle(J, scale_value=1.04, rotation_angle=.015 * TAU), run_time=.7)
        # h6 兩塊一樣的灰牌、＝、同分；這一對縮成一格飛向計分板
        chips = VGroup(*[RoundedRectangle(corner_radius=.08, width=.6, height=.6).set_fill(TIE, .95).set_stroke(width=0)
                         .move_to(np.array([q[0], S1[1] + 2.1, 0])) for q in (SCR_A, SCR_B)])
        eqc = B("＝", .07, TIE).move_to(np.array([S1[0], S1[1] + 2.1, 0]))
        tie_l = T("同分", .04, TIE).next_to(eqc, DOWN, buff=.28)
        self.at(A_("h6", .0), LaggedStart(*[FadeIn(c, scale=1.8) for c in chips], lag_ratio=.35), run_time=.5)
        self.at(A_("h6", .15), Write(eqc), FadeIn(tie_l, shift=UP * .1), run_time=.45)
        P1 = board_panel("judge", PANEL_P["judge"], show_bad=False, legend=True, title="1～5 分評審")
        tgt = empty_cells(P1.waf)
        lg = P1.count
        P1.remove(lg)
        cell = RoundedRectangle(corner_radius=.03, width=.22, height=.22).set_fill(TIE, 1).set_stroke(width=0).move_to(eqc)
        cell.set_z_index(3)
        cell.transient = True
        dst = P1.waf.cells[12]
        self.at(A_("h6", .63), ReplacementTransform(chips, cell), FadeOut(eqc), FadeOut(tie_l), run_time=.35)
        self.at(A_("h6", .7), self.cam(*H7_SHOT), cell.animate(rate_func=EASE).move_to(dst),
                Succession(Wait(.7), AnimationGroup(FadeIn(P1.waf.frame), Write(P1.title))), run_time=1.8, rate_func=EASE)
        # h7 88 格灰、12 格綠，圖例跟著數字出現
        greys = [c for c, col in zip(P1.waf.cells, tgt) if ManimColor(col).to_hex().lower() == ManimColor(TIE).to_hex().lower()]
        greens = [c for c, col in zip(P1.waf.cells, tgt) if ManimColor(col).to_hex().lower() == ManimColor(GOOD).to_hex().lower()]
        self.remove(cell)
        dst.set_fill(TIE, 1)
        self.at(A_("h7", .02), LaggedStart(*[c.animate.set_fill(TIE, 1) for c in greys if c is not dst], lag_ratio=.02), FadeIn(lg[1], shift=LEFT * .2), run_time=1.6)
        self.at(A_("h7", .6), LaggedStart(*[c.animate.set_fill(GOOD, 1) for c in greens], lag_ratio=.06), FadeIn(lg[0], shift=LEFT * .2), run_time=1.0, sfx="pop", gain=.4)
        P1.add(lg)
        # h1b 回考場：題目卡、甲的兩行
        tc = task_card()
        self.at(A_("h1b", .0), Succession(self.cam(S2 + LEFT * 2, 40).build().set_run_time(1.1).set_rate_func(EASE),
                                           self.cam(S1, 14).build().set_run_time(1.1).set_rate_func(EASE)),
                Succession(Wait(1.5), FadeIn(tc, shift=DOWN * .2, run_time=.7)), run_time=2.2)
        self.at(A_("h1b", .7), *[l.animate.set_opacity(1) for l in A.lines], run_time=.6)
        # h3 乙偷吃步：一行一行寫出；資料庫複製出 /tmp 分身
        d1 = db_icon(SCR_B + np.array([-1.3, -2.45, 0]), "db")
        d2 = db_icon(SCR_B + np.array([.6, -2.45, 0]), "/tmp", BAD)
        nv = T("↑ 沒真正驗證", .038, BAD).move_to(Bs.lines[3]).align_to(Bs.lines[3], LEFT)
        self.at(A_("h3", .02), Bs.lines[0].animate.set_opacity(1), FadeIn(d1, shift=UP * .2), run_time=.6)
        self.at(A_("h3", .25), TransformFromCopy(d1, d2), run_time=.7, sfx="pop", gain=.35)
        self.at(A_("h3", .45), Bs.lines[1].animate.set_opacity(1), run_time=.5)
        self.at(A_("h3", .65), Bs.lines[2].animate.set_opacity(1), run_time=.5)
        self.at(A_("h3", .85), FadeIn(nv, shift=UP * .15), Bs.lines[3].animate.set_opacity(0), run_time=.5, sfx="scratch", gain=.4)
        # h4 最後卻回報：內部 diff 檢查通過
        hl4 = SurroundingRectangle(Bs.lines[3], color=ARG, buff=.07)
        hl4.set_z_index(2)
        self.at(A_("h4", .2), FadeOut(nv, shift=UP * .15), Bs.lines[3].animate.set_opacity(1), run_time=.5)
        self.at(A_("h4", .45), Create(hl4), run_time=.5, sfx="pop", gain=.4)
        # h8 評審真的看不出來嗎？放大、冒汗；兩卷變暗
        J2 = judge(JUDGE1, 1.1, "unsure", "?")
        self.at(A_("h8", .02), FadeOut(d1), FadeOut(d2), ReplacementTransform(J, J2), A.animate.set_opacity(.35), Bs.animate.set_opacity(.35), ck.animate.set_opacity(.35), xb.animate.set_opacity(.35), FadeOut(hl4), run_time=.8)
        # h9 其實看出來了：小泡泡
        bub = bubble(VGroup(T("好像…", .042, BG), T("改了資料庫？", .042, BG)).arrange(DOWN, buff=.1), tail=DOWN).next_to(J2.head, UP, buff=.3)
        self.at(A_("h9", .02), FadeOut(tc, shift=UP * .2), run_time=.5)
        self.at(A_("h9", .3), FadeIn(bub, scale=.6, shift=DOWN * .2), run_time=.6, sfx="pop", gain=.4)
        self.at(A_("h9", .78), Wiggle(bub, scale_value=1.04, rotation_angle=.01 * TAU), run_time=.8)
        pl, drop = self.plumb_in(S1 + np.array([-4.2, 2.2, 0]), .36)
        self.at(A_("h9", .92), *drop, run_time=.5)
        # h10 「只取最高」鐵板落下，把泡泡壓成一塊沒有數字的灰牌
        J3 = judge(JUDGE1, .9, "unsure", "?")
        bub.transient = True
        self.at(A_("h10", .02), ReplacementTransform(J2, J3), bub.animate.next_to(J3.head, UP, buff=.35), *pl.curl(), *pl.look(RIGHT), run_time=.7)
        J4 = judge_blank(JUDGE1)
        pr = pressed(J4)
        pr.shift(UP * 4)
        self.add(pr)
        self.at(A_("h10", .35), pr.animate(rate_func=rate_functions.ease_in_quad).shift(DOWN * 4),
                FadeOut(bub, scale=.05, target_position=J3.win.get_center(), rate_func=rate_functions.ease_in_quad), run_time=.55, sfx="thud", gain=.55)
        self.at(A_("h10", .55), ReplacementTransform(J3, J4), A.animate.set_opacity(1), Bs.animate.set_opacity(1), ck.animate.set_opacity(1), xb.animate.set_opacity(1), run_time=.5)
        pl.nocheck = True
        self.at(A_("h10", .72), Indicate(J4.win, color=TIE, scale_factor=1.25), *self.plumb_out(pl), run_time=.5)
        self.remove(pl)
        self.finish()


# ================= sc02 平手就挑不出來 =================
class Sc02(Sheet5):
    SID = "sc02"

    def construct(self):
        A_ = self.A
        self.add(road())
        self.cam_set(S1, 14)
        d = sc01_end()
        add_all(self, d)
        A, Bs, J = d["A"], d["Bs"], d["J"]
        # i1 片頭音樂期間：兩卷收起，評審退到左邊，浮出片名
        J2 = judge(JUDGE2, .85, "calm", "?")
        ttl = B("LLM-as-a-Verifier", .075, INK).move_to(TASK_C + DOWN * .2)
        self.at(0, FadeOut(VGroup(A, d["ck"]), shift=LEFT * 1.5), FadeOut(VGroup(Bs, d["xb"]), shift=RIGHT * 1.5), FadeOut(d["pr"], shift=UP * 1.5),
                ReplacementTransform(J, J2), run_time=1.6, rate_func=EASE)
        self.at(A_("i1", .3), Write(ttl), run_time=1.0, sfx="ding", gain=.4)
        # w1 一疊卷子飛來，各蓋上整數分數，排成一列
        row = paper_row([5, 3, 4, 2, 5, 1])
        self.at(A_("w1", .02), FadeOut(ttl, shift=UP * .3), LaggedStart(*[FadeIn(r[0], shift=LEFT * 2) for r in row], lag_ratio=.12), run_time=1.2)
        self.at(A_("w1", .5), LaggedStart(*[Write(r[1]) for r in row], lag_ratio=.15), run_time=1.2)
        # w2 依分數排隊，低分淘汰，第一名拿獎牌
        order = [0, 4, 2, 1, 3, 5]
        tgt = paper_row([5, 5, 4, 3, 2, 1])
        for r in row:
            r.pass_ok = True
        self.at(A_("w2", .02), *[row[i].animate(path_arc=PI / 2).move_to(tgt[k]) for k, i in enumerate(order)], run_time=1.0, rate_func=EASE, sfx="slide", gain=.35)
        row = VGroup(*[row[i] for i in order])
        self.at(A_("w2", .55), *[FadeOut(row[i], shift=DOWN * 3 + RIGHT * (i - 4) * .6, rate_func=rate_functions.ease_in_quad) for i in (4, 5)], run_time=.7, sfx="thud", gain=.4)
        row = VGroup(*row[:4])
        md = medal(row[0].get_top() + UP * .62)
        self.at(A_("w2", .7), FadeIn(md, shift=DOWN * .5), run_time=.6, sfx="ding", gain=.35)
        # w4 一道題比一百次 vs 一整套測驗：Terminal-Bench 箱子
        tb = tb_box()
        self.at(A_("w4", .3), FadeIn(tb.box), Write(tb.lab), run_time=.8)
        self.at(A_("w4", .6), LaggedStart(*[FadeIn(c, shift=DOWN * .6) for c in tb.cards], lag_ratio=.2), run_time=1.0)
        # w4b 27% 平手
        w27 = waffle([0, 27, 0], [GOOD, TIE, BAD], cell_=.22, gap=.04).move_to(S1 + np.array([4.4, -1.0, 0]))
        l27 = B("27% 平手", .05, TIE).next_to(w27, UP, buff=.22)
        self.at(A_("w4b", .05), FadeIn(w27.frame), run_time=.5)
        self.at(A_("w4b", .35), LaggedStart(*[FadeIn(c, scale=.5) for c in w27.cells], lag_ratio=.03), Write(l27), run_time=1.3)
        # w5 平手就挑不出來：最前面兩張卡住
        J3 = judge(JUDGE2, .85, "unsure", "?")
        stuck = VGroup(SurroundingRectangle(VGroup(row[0], row[1]), color=TIE, buff=.12), B("卡住", .05, TIE))
        stuck[1].next_to(stuck[0], DOWN, buff=.25)
        self.at(A_("w5", .02), FadeOut(VGroup(tb, w27, l27)), run_time=.5)
        self.at(A_("w5", .2), Create(stuck[0]), FadeIn(stuck[1], shift=UP * .1), ReplacementTransform(J2, J3), run_time=.6, sfx="thud", gain=.45)
        self.at(A_("w5", .55), Wiggle(VGroup(row[0], row[1]), scale_value=1.05, rotation_angle=.02 * TAU), run_time=.8)
        self.tail(Indicate(stuck[1], scale_factor=1.15))
        self.finish()


# ================= sc03 評審的腦袋 =================
class Sc03(Sheet5):
    SID = "sc03"

    def construct(self):
        A_ = self.A
        self.add(road())
        self.cam_set(S1, 14)
        d = sc02_end()
        add_all(self, d)
        # b1 鏡頭推到下一站；評審的頭殼放大成外框
        sk = skull()
        eyes = VGroup(*[Dot(S2 + np.array([dx, .3, 0]), radius=.45, color=INK).set_opacity(.25) for dx in (-2.2, 2.2)])
        eyes.nocheck = True
        self.at(0, self.cam(S2, 14), Succession(Wait(.7), AnimationGroup(DrawBorderThenFill(sk), FadeIn(eyes))), run_time=1.9, rate_func=EASE)
        # 考場收成最後的樣子（鏡頭已離開）
        self.remove(d["J"], d["row"], d["md"], d["stuck"])
        self.add(s1_final())
        # b2 一個 token 接一個 token
        trow = token_row()
        self.at(A_("b2", .0), FadeOut(eyes), run_time=.3)
        for k, f in enumerate((.12, .26, .4, .54, .66, .8)):
            self.at(A_("b2", f), FadeIn(trow[k], shift=RIGHT * .2), run_time=.22, gain=.3)
        # b3 分數那一格：一整組機率
        bars_a = dist_bars(PA, A_POS)
        bars_a.pass_ok = True
        for b in bars_a.bars:
            b.pass_ok = True
        self.at(A_("b2", .88), Create(bars_a.base), FadeIn(bars_a.labs), run_time=.5)
        self.at(A_("b3", .25), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_a.bars], lag_ratio=.15), run_time=1.3)
        self.at(A_("b3", .7), LaggedStart(*[Indicate(b, color=DIST, scale_factor=1.12) for b in bars_a.bars], lag_ratio=.15), run_time=1.2)
        # b4a 另外舉個例子
        note = pill("例子", "#E8E2D0", .06, fill=.95, txt=BG).move_to(S2 + np.array([-4.9, -2.25, 0]))
        self.at(A_("b4a", .4), FadeIn(note, scale=1.6), run_time=.5, sfx="pop", gain=.35)
        # b4 軌跡 X：0.45、0.35
        nX = T("軌跡 X", .042, INK).move_to(A_POS + DOWN * .82)
        self.at(A_("b4", .02), Write(nX), run_time=.5)
        self.at(A_("b4", .35), LaggedStart(*[FadeIn(n, shift=UP * .1) for n in bars_a.nums], lag_ratio=.1), run_time=1.0)
        self.at(A_("b4", .7), Indicate(bars_a.nums[4]), Indicate(bars_a.nums[3]), run_time=.8)
        # b5 argmax：壓模降下
        tA = score_tag("A")
        prs = press(np.array([bars_a.bars[4].get_x(), bars_a.bars[4].get_top()[1] + .95, 0]))
        self.at(A_("b5", .02), ReplacementTransform(trow, tA), FadeOut(note, scale=.8), run_time=.7)
        self.at(A_("b5", .45), FadeIn(prs, shift=DOWN * 1.2), run_time=.7, sfx="slide", gain=.35)
        # b6 壓下：1～4 分碎掉掉進丟掉槽，原地剩灰色 5
        c5a = cube5(A_POS + UP * .45)
        base_a = Line(A_POS + LEFT * 2.2, A_POS + RIGHT * 2.2).set_stroke(LINE, 3)
        prs2 = press(c5a.get_top() + UP * .45)
        bin_ = discard_bin(True)
        bin_.pass_ok = True
        self.at(A_("b6", .0), FadeIn(bin_[0]), FadeIn(bin_[1]), FadeOut(bars_a.nums), run_time=.4)
        self.at(A_("b6", .15), Transform(prs, prs2), ReplacementTransform(bars_a.bars[4], c5a),
                *[FadeOut(bars_a.bars[i], shift=DOWN * .5, scale=.3) for i in range(4)],
                ReplacementTransform(bars_a.base, base_a), FadeOut(bars_a.labs), run_time=.8, sfx="thud", gain=.5)
        self.at(A_("b6", .5), LaggedStart(*[FadeIn(c, shift=DOWN * .3) for c in bin_.chips], lag_ratio=.15), run_time=.7)
        # b7 0.35 也丟了
        hl = SurroundingRectangle(bin_.chips[3], color=DIST, buff=.07)
        self.at(A_("b7", .1), Create(hl), bin_.chips[3].animate.set_opacity(1), run_time=.6)
        self.at(A_("b7", .6), Indicate(bin_.chips[3], scale_factor=1.3), run_time=.7)
        # b8 軌跡 Y
        bars_b = dist_bars([None, None, None, .30, .52], B_POS, unknown=.18)
        tB = score_tag("B")
        nY = T("軌跡 Y", .042, INK).move_to(B_POS + DOWN * .82)
        self.at(A_("b8", .02), FadeOut(hl), bin_.chips[3].animate.set_opacity(.5), FadeIn(tB), Write(nY), run_time=.6)
        self.at(A_("b8", .3), Create(bars_b.base), FadeIn(bars_b.labs), GrowFromEdge(bars_b.bars[4], DOWN), GrowFromEdge(bars_b.bars[3], DOWN),
                FadeIn(bars_b.nums[3]), FadeIn(bars_b.nums[4]), run_time=.9)
        self.at(A_("b8", .75), FadeIn(bars_b.other), run_time=.5)
        # b9 壓模滑過去，Y 也是 5
        c5b = cube5(B_POS + UP * .45)
        base_b = Line(B_POS + LEFT * 2.2, B_POS + RIGHT * 2.2).set_stroke(LINE, 3)
        prs3 = press(c5b.get_top() + UP * .45)
        hov = press(np.array([bars_b.bars[4].get_x(), bars_b.bars[4].get_top()[1] + .5, 0]))
        self.at(A_("b9", .0), FadeOut(bars_b.nums), FadeOut(bars_b.other), FadeOut(bars_b.labs), FadeOut(bars_b.bars[:4]), Transform(prs, hov, path_arc=PI / 3), run_time=.6, rate_func=EASE, sfx="slide", gain=.3)
        self.at(A_("b9", .45), Transform(prs, prs3), ReplacementTransform(bars_b.bars[4], c5b),
                ReplacementTransform(bars_b.base, base_b), run_time=.7, sfx="thud", gain=.45)
        # b10 兩個 5：平手
        eqs = B("＝", .09, TIE).move_to((c5a.get_center() + c5b.get_center()) / 2)
        self.at(A_("b10", .3), Write(eqs), run_time=.5, sfx="ding", gain=.35)
        # b11 舉例聲明：數字變暗
        self.at(A_("b11", .2), bin_.chips.animate.set_opacity(.25), Indicate(VGroup(nX, nY), scale_factor=1.12), run_time=.9)
        self.tail(Indicate(eqs, scale_factor=1.25))
        self.finish()


# ================= sc04 改算期望值 =================
class Sc04(Sheet5):
    SID = "sc04"

    def construct(self):
        A_ = self.A
        self.add(road())
        self.cam_set(S2, 14)
        d = sc03_end()
        add_all(self, d)
        prs = d["prs"]
        # e1 論文首頁：腦袋壓暗，截圖滑進來
        dim2 = Rectangle(width=STW + .4, height=STH + .4).set_fill(BG, .92).set_stroke(width=0).move_to(S2)
        dim2.nocheck = True
        pp = paper_page(S2 + UP * .2, 4.4)
        pp.set_z_index(5)
        pp.shift(DOWN * 7)
        self.at(A_("e1", .02), FadeIn(dim2), pp.animate(rate_func=EASE).shift(UP * 7), run_time=1.1, sfx="slide", gain=.35)
        mk = pp.mark(TITLE_KEY, GOLD)
        mk.set_z_index(6)
        self.at(A_("e1", .62), GrowFromEdge(mk, LEFT), run_time=.7)
        # e1b verifier
        self.at(A_("e1b", .05), Group(pp, mk).animate(rate_func=EASE).scale(1.07), run_time=2.4)
        # e2 不取最高，改算期望值：X 的長條滑到期望值塔
        prsA = press(d["c5a"].get_top() + UP * .45)
        rul = ruler_v(np.array([S4[0] - 5.3, BASE4, 0]))
        head4 = T("分數 × 機率", .045, EV).move_to(FORM_C + UP * 1.95)
        br = bars_row()
        gp = pointer(np.array([TX_X + .8, BASE4, 0]))
        gp.set_z_index(3)
        self.at(A_("e2", .02), FadeOut(pp, shift=UP * .5), FadeOut(mk), FadeOut(dim2), Transform(prs, prsA), run_time=.6)
        ghost = d["c5a"].copy()
        ghost.set_z_index(3)
        ghost.pass_ok = True
        self.add(ghost)
        self.at(A_("e2", .15), self.cam(S4, 14), ReplacementTransform(ghost, br),
                Succession(Wait(.9), FadeIn(head4)), run_time=2.2, rate_func=EASE)
        self.at(A_("e2", .78), Indicate(head4, color=EV, scale_factor=1.15), run_time=.8)
        # e3 每一項乘出來就是一塊積木；算式一行一行出現
        ta = tower_x()
        fm = formula(eq=False)
        v1 = T("2.25", .04, BG).move_to(ta.blocks[4])
        v2 = T("1.4", .04, BG).move_to(ta.blocks[3])
        la = T("軌跡 X", .04, INK).next_to(np.array([TX_X, BASE4, 0]), DOWN, buff=.25)
        self.at(A_("e3", .02), FadeOut(br.labs), FadeOut(br.nums), FadeOut(br[-1]), FadeOut(br.base), run_time=.4)
        order = [0, 1, 2, 3, 4]
        fr = [.12, .25, .38, .52, .7]
        for i, f in zip(order, fr):
            self.at(A_("e3", f), ReplacementTransform(br.bars[i], ta.blocks[i]), Write(fm.fx[4 - i]), run_time=.5)
        self.at(A_("e3", .85), FadeIn(v1), FadeIn(v2), FadeIn(fm.calc), Write(la), FadeIn(rul), run_time=.5)
        # e4 塔頂 4.16
        pa = pointer(np.array([TX_X + .8, ta.top_y, 0]), "4.16")
        pa.set_z_index(3)
        self.at(A_("e4", .0), FadeIn(gp, scale=.5), run_time=.3)
        self.at(A_("e4", .12), gp.animate(rate_func=EASE).move_to(pa[0]), run_time=.9)
        self.remove(gp)
        self.add(pa[0])
        self.at(A_("e4", .6), Write(pa[1]), Write(fm.eq), run_time=.6, sfx="ding", gain=.4)
        self.add(pa)
        # e5 軌跡 Y：3.8 加其餘，約 4.3
        tb = tower_y()
        lb = T("軌跡 Y", .04, INK).next_to(np.array([TY_X, BASE4, 0]), DOWN, buff=.25)
        b38 = Brace(tb.blocks, RIGHT, color=EV, buff=.12)
        l38 = VGroup(b38, B("3.8", .045, EV).next_to(b38, RIGHT, buff=.24))
        l38.add(T("代入公式計算", .038, MUTED).next_to(l38[1], DOWN, buff=.18, aligned_edge=LEFT))
        pb = pointer(np.array([TY_X + .8, tb.top_y, 0]), "約 4.3")
        pb.set_z_index(3)
        self.at(A_("e5", .02), FadeOut(fm), FadeOut(fm.eq), Write(lb), LaggedStart(*[GrowFromEdge(b, DOWN) for b in tb.blocks], lag_ratio=.4), run_time=1.0)
        self.at(A_("e5", .35), GrowFromCenter(b38), Write(l38[1]), FadeIn(l38[2]), run_time=.6)
        self.at(A_("e5", .62), GrowFromEdge(tb.oth, DOWN), FadeIn(tb[2]), run_time=.5)
        self.at(A_("e5", .8), FadeIn(pb, shift=LEFT * .3), run_time=.5, sfx="pop", gain=.4)
        # e6 放大 4.0～4.4：兩個指針分開
        zi = zoom_inset()
        hi = VGroup(*[Line(rul[0].get_start() + UP * (i / 10) * UNIT, rul[0].get_start() + UP * (i / 10) * UNIT + RIGHT * .2).set_stroke(GOLD, 2.5) for i in range(40, 45)])
        self.at(A_("e6", .02), FadeOut(l38), FadeOut(head4), Create(hi), run_time=.6)
        self.at(A_("e6", .25), FadeIn(zi[0]), FadeIn(zi[7]), Create(zi[1]), FadeIn(zi[2]), FadeIn(zi[3]), run_time=.7)
        self.at(A_("e6", .5), TransformFromCopy(pa[0], zi[5][0]), TransformFromCopy(pb[0], zi[6][0]), FadeIn(zi[5][1]), FadeIn(zi[6][1]), run_time=.8)
        self.at(A_("e6", .75), Create(zi[4]), run_time=.5, sfx="pop", gain=.45)
        # e7 同樣寫下 5 分，背後的機率不一樣
        g5 = VGroup(T("argmax", .045, ARG).move_to(np.array([(TX_X + TY_X) / 2, ta.top_y + 1.35, 0])),
                    cube5(np.array([TX_X, ta.top_y + .55, 0])).scale(.7), cube5(np.array([TY_X, tb.top_y + .55, 0])).scale(.7))
        self.at(A_("e7", .02), FadeOut(zi), FadeOut(hi), run_time=.5)
        self.at(A_("e7", .25), FadeIn(g5[1], shift=DOWN * .3), FadeIn(g5[2], shift=DOWN * .3), Write(g5[0]), run_time=.7)
        pl, drop = self.plumb_in(S4 + np.array([4.6, .5, 0]), .42)
        self.at(A_("e7", .55), *drop, run_time=.55)
        self.at(A_("e7", .72), Wiggle(g5[1]), Wiggle(g5[2]), *pl.curl(), *pl.look(LEFT), run_time=.8)
        # e7b 期望值把差別留下：細刻度亮起、灰 5 裂開
        self.at(A_("e7b", .1), Create(hi), run_time=.6)
        self.at(A_("e7b", .5), g5[1].animate.move_to(pa[0]).scale(.3).set_opacity(0), g5[2].animate.move_to(pb[0]).scale(.3).set_opacity(0),
                FadeOut(g5[0], shift=UP * .2), Indicate(pa[1]), Indicate(pb[1]), run_time=.9, sfx="pop", gain=.4)
        self.remove(g5[1], g5[2])
        self.at(A_("e7b", .75), *pl.straighten(), run_time=.5)
        self.at(A_("e7b", .88), *pl.light_on(), *pl.hop(.25), run_time=.5, sfx="ding", gain=.35)
        # e8 論文指出：判斷本來就是連續的
        pl.nocheck = True
        self.at(A_("e8", .05), FadeOut(hi), *self.plumb_out(pl), run_time=.5)
        self.remove(pl)
        self.at(A_("e8", .22), ShowPassingFlash(rul[0].copy().set_stroke(GOLD, 6), time_width=.5), run_time=1.0)
        # 「是 argmax 把它壓扁了」：兩根指針被壓回同一個灰色的 5，再彈回來
        sq = VGroup(cube5(np.array([TX_X, ta.top_y + .55, 0])).scale(.7), cube5(np.array([TY_X, tb.top_y + .55, 0])).scale(.7))
        sql = T("argmax", .045, ARG).move_to(np.array([(TX_X + TY_X) / 2, ta.top_y + 1.35, 0]))
        sq.transient = sql.transient = True
        self.at(A_("e8", .6), TransformFromCopy(pa[0], sq[0]), TransformFromCopy(pb[0], sq[1]), FadeIn(sql, shift=DOWN * .2), run_time=.55, sfx="thud", gain=.4)
        self.at(A_("e8", .86), FadeOut(sq, scale=.4), FadeOut(sql), run_time=.4)
        self.tail(Indicate(pa[0], color=GOLD, scale_factor=1.3), Indicate(pb[0], color=GOLD, scale_factor=1.3))
        self.finish()


# ================= sc05 回到那一百次 =================
class Sc05(Sheet5):
    SID = "sc05"

    def construct(self):
        A_ = self.A
        self.add(road())
        self.cam_set(S4, 14)
        d = sc04_end()
        add_all(self, d)
        P1o = d["P1"]
        f = s3_final()
        P1 = board_panel("judge", PANEL_P["judge"], show_bad=False)
        lg2 = board_legend(False)
        P2e = board_panel("v5", PANEL_P["v5"], filled=False)
        P3e = board_panel("v20", PANEL_P["v20"], filled=False)
        # k1 回到開頭那一百次：鏡頭往上
        self.at(0, self.cam(S3, 14), Succession(Wait(.8), AnimationGroup(ReplacementTransform(P1o, P1), FadeIn(lg2, shift=DOWN * .2), FadeIn(P2e), FadeIn(P3e), FadeIn(f["mc"][0], shift=RIGHT * .4), FadeIn(f["mc"][1], shift=LEFT * .4), run_time=1.0)),
                run_time=1.8, rate_func=EASE)
        # k2 只把 argmax 換成期望值
        a1 = f["a1"]
        self.at(A_("k2", .2), GrowArrow(a1.ar), run_time=.6, sfx="click", gain=.35)
        self.at(A_("k2", .45), FadeIn(a1.lab, shift=UP * .1), run_time=.5)
        # k2b 88 次平手消失，69 次甲排前面；圖例多一行「乙排前面」
        P2 = f["P2"]
        tgt2 = empty_cells(P2.waf)
        self.remove(P2e)
        self.add(P2.waf.frame, P2.title)
        self.add(P2.waf.cells)
        self.at(A_("k2b", .02), ReplacementTransform(lg2, f["lg"]), run_time=.4)
        self.at(A_("k2b", .12), LaggedStart(*[c.animate.set_fill(col, .3 if ManimColor(col).to_hex().lower() == ManimColor(BAD).to_hex().lower() else 1) for c, col in zip(P2.waf.cells, tgt2)], lag_ratio=.012), run_time=1.6, sfx="pop", gain=.4)
        P1f = f["P1"]
        self.at(A_("k2b", .6), FadeIn(P2.count), ReplacementTransform(P1, P1f), run_time=.6)
        # k3 5 格換 20 格：77 次
        a2, P3 = f["a2"], f["P3"]
        tgt3 = empty_cells(P3.waf)
        self.at(A_("k3", .1), GrowArrow(a2.ar), FadeIn(a2.lab, shift=UP * .1), run_time=.7, sfx="click", gain=.35)
        self.remove(P3e)
        self.add(P3.waf.frame, P3.title, P3.waf.cells)
        self.at(A_("k3", .45), LaggedStart(*[c.animate.set_fill(col, .3 if ManimColor(col).to_hex().lower() == ManimColor(BAD).to_hex().lower() else 1) for c, col in zip(P3.waf.cells, tgt3)], lag_ratio=.012), run_time=1.4, sfx="pop", gain=.4)
        self.at(A_("k3", .85), FadeIn(P3.count), run_time=.4)
        # k4 每一步只動一個地方
        self.at(A_("k4", .1), Indicate(a1, color=ARG, scale_factor=1.15), run_time=.8)
        self.at(A_("k4", .5), Indicate(a2, color=GK, scale_factor=1.15), run_time=.8)
        # k5 紅格出現：第二面 31 次反而把乙排前面
        reds = [c for P in (P2,) for c in P.waf.cells if ManimColor(c.get_fill_color()).to_hex().lower() == ManimColor(BAD).to_hex().lower()]
        others = [c for P in (P1f, P2, P3) for c in P.waf.cells if c not in reds]
        self.at(A_("k5", .15), *[c.animate.set_fill(opacity=.3) for c in others], *[c.animate.set_fill(opacity=1) for c in reds], run_time=.6)
        self.at(A_("k5", .35), Indicate(P2.count[-1], color=BAD, scale_factor=1.4), run_time=.8)
        self.at(A_("k5", .75), *[c.animate.set_fill(opacity=1) for c in others], run_time=.6)
        self.tail(Indicate(P2.count[-1], scale_factor=1.3))
        self.finish()
