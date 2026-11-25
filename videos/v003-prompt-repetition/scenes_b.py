"""v003 Prompt Repetition：sc06～sc10。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scenes_a import *  # noqa: E402,F401,F403

ALT_Y = 10.4
ALT_C, ALT_W = np.array([0, 9.95, 0]), 17.0
COT_P, BERT_P = np.array([-4.6, ALT_Y, 0]), np.array([4.6, ALT_Y, 0])


def clock(c, r=.42, t=0.0):
    c = np.array(c, dtype=float)
    face = Circle(r).set_fill(SEA, 1).set_stroke(TXT_STRONG, 3).move_to(c)
    a = PI / 2 - TAU * t
    hand = Line(c, c + r * .75 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(TXT_STRONG, 3)
    return VGroup(face, hand, Dot(c, radius=.05, color=TXT_STRONG))


class Clock(VGroup):
    def __init__(self, c, r=.42):
        super().__init__()
        self.c, self.r = c, r
        self.t = ValueTracker(0)
        self.add(always_redraw(lambda: clock(self.c, self.r, self.t.get_value())))


def coins(c, n):
    g = VGroup(*[Ellipse(width=.5, height=.18).set_fill(GOLD, .85).set_stroke(GOLD, 1.5) for _ in range(max(n, 1))]).arrange(UP, buff=-.06)
    g.move_to(np.array(c, dtype=float), aligned_edge=DOWN)
    if n == 0:
        g.set_opacity(0)
    return g


def bert_reader(word, p):
    r = reader(word, NEUTRAL, p, w=1.25, h=1.3, frac=.05)
    eye2 = r.eye.copy().move_to(r.patch.get_center())
    pup2 = Dot(eye2.get_center() + RIGHT * .06, radius=.075, color=BG)
    r.remove(r.patch, r[1])
    r.add(eye2, pup2)
    return r


def sc05_cam():
    return LABV_C, LABV_W


def corr_full():
    """長廊的完整樣子（第一遍、接縫、第二遍、筆記、泡泡、兩個標籤）。"""
    D = sc03_end()
    D["sm"] = seam()
    D["rs2"] = corridor(2)
    D["rs2"][1] = reader("bark", P2C, RP(2, 1), joy=1)
    D["ns2"] = [note(RP(2, i), "gold" if i == 1 else "plain") for i in range(5)]
    D["bb2"] = bubble_at(RP(2, 1), meaning(1, 1.25))
    D["l1"], D["l2"] = pass_label(1), pass_label(2)
    return D


# ---------------- sc06：之前的兩種解法 ----------------
class Sc06(Sheet):
    SID = "sc06"

    def construct(self):
        A = self.A
        self.cam_set(*sc05_cam())
        D = sc05_end()
        self.add(*flat(D))
        lab = VGroup(*D["ra"], *D["qa"], *D["ra2"], D["la"], D["nm"], D["nq"])
        # a1 之前就有兩種解法：鏡頭拉到長廊上方
        slots = VGroup(*[RoundedRectangle(corner_radius=.2, width=6.0, height=4.3).set_stroke(LINE, 2, .8).move_to(c + DOWN * .1) for c in (COT_P, BERT_P)])
        self.at(A("a1", 0), self.cam(ALT_C, ALT_W), FadeOut(lab, run_time=.6), Succession(Wait(.8), Create(slots)),
                run_time=1.6, rate_func=SINE)
        # a2 CoT：一台打字機，一步一步想
        tw = typewriter(COT_P + LEFT * 1.6)
        cot = T("Chain-of-Thought（CoT）", .055, DEC).move_to(COT_P + UP * 1.55)
        self.at(A("a2", .05), DrawBorderThenFill(tw[0]), FadeIn(tw[1:]), run_time=.8)
        self.at(A("a2", .3), Write(cot), run_time=.9)
        pp = paper(tw.get_center() + LEFT * 0, 0)
        self.add(pp)
        long_ = paper(COT_P + LEFT * 1.6, 11, q=2)
        long_.nocheck = True
        self.at(A("a2", .6), Transform(pp, paper(COT_P + LEFT * 1.6, 4, q=2)), run_time=1.0, rate_func=linear, sfx="tick", gain=.35)
        # a3 修好理解，但多生成很多字：紙帶拖出畫面、時鐘狂轉、錢幣疊高
        ck = Clock(COT_P + np.array([-1.0, -1.25, 0]))
        cn = coins(COT_P + np.array([.4, -1.6, 0]), 0)
        self.at(A("a2", .85), GrowFromCenter(ck), run_time=.5)
        self.add(cn)
        self.at(A("a3", .3), Transform(pp, long_), ck.t.animate.set_value(3), Transform(cn, coins(COT_P + np.array([.4, -1.6, 0]), 7)), run_time=2.0,
                rate_func=rate_functions.ease_in_quad, sfx="slide", gain=.35)
        # a4 BERT：讓輸入的 token 互相看得見（兩隻眼睛都張開）
        brs = [bert_reader(w, BERT_P + np.array([(k - 1) * 1.55, -.25, 0])) for k, w in enumerate(["The", "bark", "was"])]
        bert = T("BERT", .06, TXT_STRONG).move_to(BERT_P + UP * 1.55)
        arrows = VGroup(*[DoubleArrow(brs[k].get_top() + UP * .15, brs[k + 1].get_top() + UP * .15, buff=.1, stroke_width=3, tip_length=.18).set_color(LIGHT)
                          for k in range(2)])
        self.at(A("a4", .05), Write(bert), LaggedStart(*[GrowFromCenter(r) for r in brs], lag_ratio=.2), run_time=1.2)
        self.at(A("a4", .55), LaggedStart(*[GrowFromCenter(a) for a in arrows], lag_ratio=.3), run_time=.9, sfx="click", gain=.4)
        self.at(A("a4", .85), LaggedStart(*[Wiggle(r, scale_value=1.08, rotation_angle=.03 * TAU) for r in brs], lag_ratio=.2), run_time=1.0)
        # a5 要改模型架構：長廊被拆開
        fix = T("要改架構", .055, TXT_STRONG).move_to(BERT_P + DOWN * 1.45)
        self.at(A("a5", .45), FadeIn(fix, scale=1.3), *[r.animate.rotate(.18 * (k - 1)).shift(DOWN * .1) for k, r in enumerate(brs)], run_time=.8, sfx="thud", gain=.45)
        # a6 只能用 API 呼叫的現成模型做不到：一把鎖
        lock = VGroup(Arc(radius=.28, start_angle=0, angle=PI).set_stroke(TXT_STRONG, 6).shift(UP * .3),
                      RoundedRectangle(corner_radius=.08, width=.8, height=.62).set_fill(TXT_STRONG, 1).set_stroke(width=0)).move_to(BERT_P + RIGHT * 2.35 + UP * 1.45)
        self.at(A("a6", .2), FadeIn(lock, shift=DOWN * .3), run_time=.7, sfx="click", gain=.5)
        self.at(A("a6", .6), shake(lock, n=4, amp=.06), run_time=.7)
        # a7 不改架構、也不增加生成的延遲：兩張方案退到旁邊變暗，鏡頭回到長廊
        alt = VGroup(slots, tw, cot, pp, ck, cn, brs[0], brs[1], brs[2], bert, arrows, fix, lock)
        rest = VGroup(*[m for m in alt if m is not slots and m is not ck])
        self.at(A("a7", .05), FadeOut(ck), slots.animate.set_stroke(opacity=.25), rest.animate.set_opacity(.25), run_time=.8)
        alt.remove(ck)
        self.at(A("a7", .4), self.cam(SEAM_C + UP * .3, SEAM_W), Indicate(D["sm"], color=GOLD, scale_factor=1.04), run_time=1.3, rate_func=SINE)
        self.at(A("a7", .9), FadeOut(alt), run_time=.5)
        self.finish()


# ---------------- sc07：免費的午餐 ----------------
ST_C, ST_W = PANO_C, PANO_W
MID_Y = -1.62                                   # 長廊筆記和工作站之間的空檔（l10～l13 的小圖放這裡）


def pre_machines(n2=False, on=0.0):
    top = machines(10, PRE_C + UP * ROW_DY, P1C, on, k=SK)
    bot = machines(10, PRE_C + DOWN * ROW_DY, P2C, on, k=SK)
    g = VGroup(top, bot)
    if not n2:
        bot.set_opacity(0)
    return g


def sc07_end():
    D = corr_full()
    D["pm"] = pre_machines(True, .6)
    D["pl_"] = station_label("Prefill", PRE_C, ST_DY)
    D["tw"] = typewriter(DEC_C + LEFT * TW_DX, k=SK)
    D["pp"] = paper(DEC_C + LEFT * TW_DX, 5, k=SK)
    D["dl"] = station_label("Decode", DEC_C, ST_DY)
    return D


class Sc07(Sheet):
    SID = "sc07"

    def construct(self):
        A = self.A
        self.cam_set(SEAM_C + UP * .3, SEAM_W)
        D = corr_full()
        self.add(*flat(D))
        # l1 錘錘：輸入變兩倍，不會變慢嗎？
        pl, drop = self.plumb_in(np.array([P2X[4] - .2, CORR_Y + 3.4, 0]), .42)
        self.at(A("l1", 0), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("l1", .25), *pl.mood("squint"), *pl.tilt(.2), run_time=.7)
        # l2 兩個階段：鏡頭往下到工作站
        self.at(A("l2", 0), *self.plumb_out(pl), run_time=.6)
        self.remove(pl)
        self.at(A("l2", .25), self.cam(ST_C, ST_W), run_time=1.6, rate_func=SINE)
        # l3 Prefill：一口氣讀完
        pm = pre_machines(False)
        pl_ = station_label("Prefill", PRE_C, ST_DY)
        self.at(A("l3", .1), LaggedStart(*[DrawBorderThenFill(m) for m in pm[0]], lag_ratio=.05), Write(pl_), run_time=1.1)
        self.at(A("l3", .6), *[m.animate.set_fill(P1C, .75) for m in pm[0]], run_time=.35, sfx="click", gain=.5)
        self.at(A("l3", .8), *[m.animate.set_fill(P1C, .15) for m in pm[0]], run_time=.35)
        # l4 GPU 高度平行
        gpu = T("GPU", .06, MUTED).next_to(pl_, LEFT, buff=.5)
        self.at(A("l4", .2), Write(gpu), run_time=.6)
        # l5 1000 和 500：機器變兩排，還是「啪」一聲同時亮完
        n500 = M("500", .06, TXT).next_to(pm, RIGHT, buff=.45).shift(UP * .3)
        n1000 = M("1000", .06, TXT).next_to(pm, RIGHT, buff=.45).shift(DOWN * .05)
        self.at(A("l5", .1), Write(n500), *[m.animate.set_fill(P1C, .75) for m in pm[0]], run_time=.4, sfx="click", gain=.5)
        self.at(A("l5", .3), *[m.animate.set_fill(P1C, .15) for m in pm[0]], run_time=.3)
        bot = machines(10, PRE_C + DOWN * ROW_DY, P1C, 0, k=SK)
        self.at(A("l5", .45), ReplacementTransform(n500, n1000), LaggedStart(*[GrowFromEdge(m, UP) for m in bot], lag_ratio=.03), run_time=.8)
        self.at(A("l5", .75), *[m.animate.set_fill(P1C, .75) for m in [*pm[0], *bot]], run_time=.4, sfx="click", gain=.5)
        self.at(A("l5", .9), *[m.animate.set_fill(P1C, .15) for m in [*pm[0], *bot]], run_time=.3)
        # l6 Decode：一個 token 一個 token 吐出
        tw = typewriter(DEC_C + LEFT * TW_DX, k=SK)
        dl = station_label("Decode", DEC_C, ST_DY)
        self.at(A("l6", 0), DrawBorderThenFill(tw[0]), FadeIn(tw[1:]), Write(dl), run_time=.9)
        pp = paper(DEC_C + LEFT * TW_DX, 0, k=SK)
        self.add(pp)
        for k in range(1, 6):
            self.at(A("l6", .3 + .12 * k), Transform(pp, paper(DEC_C + LEFT * TW_DX, k, k=SK)), shake(tw[1], n=1, amp=.03), run_time=.25, sfx="tick", gain=.3)
        # l7 只能照順序來：慢
        self.at(A("l7", .3), Indicate(pp, color=DEC, scale_factor=1.1), run_time=.9)
        self.at(A("l7", .7), shake(tw, n=3, amp=.04), run_time=.7)
        # l8 貼兩次，多的字全落在 Prefill：第二排變成第二遍的顏色
        cps = [n.copy().set_z_index(4) for n in D["ns2"]]
        self.at(A("l8", .1), FadeOut(n1000), FadeOut(gpu),
                LaggedStart(*[c.animate.scale(.45).move_to(bot[2 * k].get_center() + RIGHT * .25).set_opacity(0) for k, c in enumerate(cps)], lag_ratio=.12),
                Succession(Wait(.7), AnimationGroup(*[m.animate.set_fill(P2C, .2).set_stroke(P2C) for m in bot])), run_time=1.5, path_arc=.5, sfx="pop", gain=.4)
        self.remove(*cps)
        self.at(A("l8", .6), *[m.animate.set_fill(P2C if m in bot else P1C, .75) for m in [*pm[0], *bot]], run_time=.4, sfx="click", gain=.5)
        self.at(A("l8", .8), *[m.animate.set_fill(P2C if m in bot else P1C, .15) for m in [*pm[0], *bot]], run_time=.3)
        # l9 回答長度沒變：紙帶一樣是五格
        self.at(A("l9", .4), Indicate(pp, color=TXT_STRONG, scale_factor=1.12), run_time=1.0)
        # l10 回答長度高度一致、延遲幾乎沒增加：兩排「回答條＋時間條」，貼兩次只長一點點（不標數值）
        def lane(lbl, col, y, tl):
            t = T(lbl, .06, col).move_to(np.array([-1.75, y, 0]))
            sq = VGroup(*[Square(.24).set_fill(DEC, .5).set_stroke(DEC, 1.2) for _ in range(5)]).arrange(RIGHT, buff=.04).move_to(np.array([-.2, y, 0]))
            tb = Line(np.array([.75, y, 0]), np.array([.75 + tl, y, 0])).set_stroke(TXT_STRONG, 8)
            return t, sq, tb
        t1, s1, tb1 = lane("不貼", P1C, MID_Y + .3, 1.2)
        t2, s2, tb2 = lane("貼兩次", P2C, MID_Y - .4, 1.25)
        ckl = T("時間", .055, MUTED).next_to(VGroup(tb1, tb2), RIGHT, buff=.3)
        lanes = VGroup(t1, s1, tb1, t2, s2, tb2, ckl)
        self.at(A("l10", .05), Write(t1), Write(t2), LaggedStart(*[GrowFromCenter(q) for q in [*s1, *s2]], lag_ratio=.05), run_time=1.0)
        self.at(A("l10", .4), Write(ckl), GrowFromEdge(tb1, LEFT), GrowFromEdge(tb2, LEFT), run_time=1.4, rate_func=linear)
        self.at(A("l10", .78), Wiggle(VGroup(tb1, tb2), scale_value=1.06), run_time=.9)
        # l11 例外：Claude 處理極長文本
        ex = VGroup(T("例外", .058, BAD), T("Claude ＋ 極長文本", .058, TXT_STRONG)).arrange(RIGHT, buff=.35)
        exb = SurroundingRectangle(ex, buff=.22, corner_radius=.12).set_stroke(BAD, 2)
        exc = VGroup(exb, ex).move_to(np.array([0, MID_Y, 0]))
        self.at(A("l11", .05), FadeOut(lanes), run_time=.5)
        self.at(A("l11", .3), Create(exb), Write(ex), run_time=1.0, sfx="thud", gain=.4)
        self.at(A("l11", .72), Wiggle(exc, scale_value=1.06, rotation_angle=.02 * TAU), run_time=.9)
        # l12 論文作者推測：Prefill 或快取
        self.at(A("l12", .4), Indicate(exc, color=TXT_STRONG, scale_factor=1.06), run_time=1.0)
        self.at(A("l12", .78), Wiggle(VGroup(*pm[0], *bot), scale_value=1.05, rotation_angle=.01 * TAU), run_time=.9)
        # l13 免費的午餐
        plate = VGroup(Circle(.7).set_fill(TXT_STRONG, .9).set_stroke(MUTED, 3), Circle(.46).set_stroke(MUTED, 2))
        fork = VGroup(Line(UP * .62, DOWN * .62).set_stroke(TXT_STRONG, 5), *[Line(UP * .62 + RIGHT * d, UP * .3 + RIGHT * d).set_stroke(TXT_STRONG, 4) for d in (-.1, 0, .1)])
        lunch = VGroup(fork.next_to(plate, LEFT, buff=.15), plate)
        fl = T("免費的午餐", .075, TXT_STRONG)
        meal = VGroup(lunch, fl).arrange(RIGHT, buff=.35).move_to(np.array([0, MID_Y, 0]))
        self.at(A("l13", .3), FadeOut(exc), run_time=.4)
        self.at(A("l13", .45), FadeIn(lunch, shift=UP * .3), Write(fl), run_time=1.0, sfx="ding", gain=.4)
        # l14 用 Prefill 多的算力換理解：Prefill 再亮一次，紙帶不變
        self.at(A("l14", .1), *[m.animate.set_fill(P2C if m in bot else P1C, .75) for m in [*pm[0], *bot]], run_time=.4, sfx="click", gain=.45)
        self.at(A("l14", .3), *[m.animate.set_fill(P2C if m in bot else P1C, .6) for m in [*pm[0], *bot]], run_time=.4)
        self.at(A("l14", .6), FadeOut(meal), run_time=.5)
        self.at(A("l14", .85), Indicate(pp, color=DEC, scale_factor=1.12), run_time=.7)
        self.finish()


# ---------------- sc08：證據 ----------------
GRID_C = np.array([-2.2, LAB_Y - .05, 0])
EV_C, EV_W = np.array([-1.15, LAB_Y - .35, 0]), 16.0
MET2 = np.array([3.75, LAB_Y + .25, 0])
CARD8, CARD8_DX = np.array([.6, LAB_Y - .8, 0]), 2.4


def sc07_pm():
    pm = pre_machines(True)
    for m in pm[0]:
        m.set_fill(P1C, .6)
    for m in pm[1]:
        m.set_fill(P2C, .6).set_stroke(P2C).set_opacity(1)
        m.set_fill(P2C, .6)
    return pm


class Sc08(Sheet):
    SID = "sc08"

    def construct(self):
        A = self.A
        self.cam_set(ST_C, ST_W)
        D = corr_full()
        S7 = dict(pm=sc07_pm(), pl_=station_label("Prefill", PRE_C, ST_DY), tw=typewriter(DEC_C + LEFT * TW_DX, k=SK), pp=paper(DEC_C + LEFT * TW_DX, 5, k=SK),
                  dl=station_label("Decode", DEC_C, ST_DY))
        self.add(*flat(D), *S7.values())
        # e1 70 個組合：鏡頭到實驗區，70 個空格
        g = score_grid(70, 14, 47, 0, GRID_C, lit=0)
        n70 = M("70", .075, TXT_STRONG).next_to(g, LEFT, buff=.45)
        self.at(A("e1", 0), self.cam(EV_C, EV_W), Succession(Wait(.6), LaggedStart(*[FadeIn(s) for s in g], lag_ratio=.01)), run_time=1.8, rate_func=SINE)
        self.at(A("e1", .7), Write(n70), run_time=.6, sfx="tick", gain=.4)
        # e2 和不貼比，47 勝 0 敗：格子一格一格亮綠
        lit = score_grid(70, 14, 47, 0, GRID_C)
        win = VGroup(T("47 勝", .075, GOOD), T("0 敗", .075, TXT_STRONG)).arrange(DOWN, buff=.3, aligned_edge=LEFT).next_to(g, RIGHT, buff=.7)
        ctl = T("對照：不貼", .045, MUTED).next_to(g, DOWN, buff=.3).align_to(g, LEFT)
        self.at(A("e2", .05), Write(ctl), run_time=.6)
        self.at(A("e2", .3), LaggedStart(*[Transform(g[k], lit[k]) for k in range(47)], lag_ratio=.04), Succession(Wait(1.2), Write(win[0])), run_time=2.0,
                sfx="pop", gain=.45)
        self.at(A("e2", .85), Write(win[1]), run_time=.5)
        # e3 其餘平手或沒有顯著差異：灰
        tie = T("其餘：平手或不顯著", .045, MUTED).next_to(ctl, RIGHT, buff=.6)
        self.at(A("e3", .1), *[Transform(g[k], lit[k]) for k in range(47, 70)], Succession(Wait(.3), Write(tie, run_time=.8)), run_time=1.1)
        self.at(A("e3", .6), LaggedStart(*[Indicate(g[k], color=TXT_STRONG, scale_factor=1.25) for k in range(47, 70)], lag_ratio=.04), run_time=1.2)
        # e4 一次都沒輸：0 敗跳一下
        self.at(A("e4", .3), Indicate(win[1], color=GOLD, scale_factor=1.3), LaggedStart(*[Indicate(g[k], color=GOOD, scale_factor=1.3) for k in range(0, 47, 2)], lag_ratio=.03),
                run_time=1.4)
        self.at(A("e4", .8), Wiggle(win[1], scale_value=1.25), run_time=.8)
        # e5、e6 選項在前追平問題在前：兩排小讀者站在兩階台階上（只比高低、不標數字）
        FLOOR = LAB_Y - 1.75
        def step(cx, h, col):
            return Rectangle(width=4.7, height=h).set_fill(col, .18).set_stroke(col, 2.5).move_to(np.array([cx, FLOOR + h / 2, 0]))
        def crew(cx, top, names_, cols, **kw):
            rs_ = [reader(n_, c_, np.array([cx + (k - 1.5) * 1.12, top + .56, 0]), w=1.02, h=1.08, frac=.048, **kw) for k, (n_, c_) in enumerate(zip(names_, cols))]
            return VGroup(*rs_)
        LX, RX = -4.4, 1.8
        sa, sb = step(LX, .55, TXT), step(RX, 1.35, QC)
        ca = crew(LX, FLOOR + .55, ["A", "B", "C", "問"], [TXT, TXT, TXT, QC], conf=1)
        cb = crew(RX, FLOOR + 1.35, ["問", "A", "B", "C"], [QC, TXT, TXT, TXT])
        la_ = T("選項在前", .058, TXT).next_to(sa, DOWN, buff=.25)
        lb_ = T("問題在前", .058, QC).next_to(sb, DOWN, buff=.25)
        grid_grp = VGroup(*g, n70, win, ctl, tie)
        self.at(A("e5", 0), FadeOut(grid_grp, run_time=.4), self.cam(np.array([(LX + RX) / 2, FLOOR + .75, 0]), 12.6),
                Succession(Wait(.35), AnimationGroup(GrowFromEdge(sa, DOWN), Write(la_), run_time=.7)), run_time=1.05, rate_func=SINE)
        self.at(A("e5", .35), LaggedStart(*[GrowFromCenter(r) for r in ca], lag_ratio=.15), run_time=.9, sfx="tick", gain=.35)
        self.at(A("e5", .8), GrowFromEdge(sb, DOWN), Write(lb_), LaggedStart(*[GrowFromCenter(r) for r in cb], lag_ratio=.1), run_time=.9)
        # e6 貼兩次後大幅進步：左邊台階升到和右邊一樣高、再高一點點；讀者變開心
        sa2 = step(LX, 1.45, P2C)
        ca2 = crew(LX, FLOOR + 1.45, ["A", "B", "C", "問"], [P2C, P2C, P2C, QC], joy=1)
        x2 = T("貼兩次", .058, P2C).next_to(sa2, UP, buff=1.35)
        self.at(A("e6", .1), Write(x2), run_time=.6)
        self.at(A("e6", .3), Transform(sa, sa2), Transform(ca, ca2), run_time=1.2, rate_func=POP, sfx="pop", gain=.45)
        lvl = DashedLine(np.array([LX - 2.2, FLOOR + 1.35, 0]), np.array([RX + 2.2, FLOOR + 1.35, 0]), dash_length=.12).set_stroke(MUTED, 2, .7)
        lvl.cross_ok = lvl.overlap_ok = True
        self.at(A("e6", .75), Create(lvl), Wiggle(ca, scale_value=1.08, rotation_angle=.02 * TAU), run_time=.9)
        # e7 OpenBookQA、MMLU-Pro
        bm = VGroup(T("OpenBookQA", .058, MUTED), T("MMLU-Pro", .058, MUTED)).arrange(RIGHT, buff=.6).move_to(np.array([(LX + RX) / 2, FLOOR - 1.25, 0]))
        self.at(A("e7", .3), Write(bm), run_time=1.0)
        # e8 NameIndex：清掉計分板，名單回來
        nm = names()
        nl = VGroup(T("NameIndex", .06, TXT_STRONG), T("極端查找題", .05, MUTED)).arrange(RIGHT, buff=.4).next_to(nm, UP, buff=.35).align_to(nm, LEFT)
        old = VGroup(sa, sb, ca, cb, la_, lb_, x2, lvl, bm)
        self.at(A("e8", 0), FadeOut(old), self.cam(EV_C, EV_W), LaggedStart(*[GrowFromCenter(s) for s in nm], lag_ratio=.015), run_time=1.3)
        self.at(A("e8", .45), Write(nl[0]), run_time=.7)
        self.at(A("e8b", .2), Write(nl[1]), run_time=.7)
        # e9 Gemini 2.0 Flash-Lite：21.33% → 97.33%
        mt = Meter(MET2, 0, r=1.25, nd=2)
        ml = T("Gemini 2.0 Flash-Lite", .05, MUTED).move_to(MET2 + DOWN * 1.2)
        mt.live.update()
        self.at(A("e9", 0), Create(mt.arc), FadeIn(mt.ticks), Write(ml), FadeIn(mt.live), run_time=.8)
        self.at(A("e9", .2), mt.v.animate.set_value(21.33), run_time=.9, rate_func=SINE)
        ghost = M("21.33%", .05, MUTED).next_to(mt, LEFT, buff=.35).shift(DOWN * .2)
        nt1 = T("不貼", .05, P1C).next_to(nm, RIGHT, buff=.3)
        self.at(A("e9", .45), FadeIn(ghost, shift=LEFT * .2), Write(nt1), run_time=.5)
        nm2 = names(gold=True).shift(DOWN * .85)
        nt2 = T("貼兩次", .05, P2C).next_to(nm2, RIGHT, buff=.3)
        self.at(A("e9", .6), LaggedStart(*[GrowFromCenter(s) for s in nm2], lag_ratio=.01), mt.v.animate(rate_func=rate_functions.ease_out_cubic).set_value(97.33),
                Succession(Wait(.6), Write(nt2, run_time=.6)), run_time=1.4, sfx="ding", gain=.5)
        # e10 只有一個模型
        one = T("只有一個模型", .05, MUTED).move_to(MET2 + UP * 1.75)
        self.at(A("e10", .2), Write(one), run_time=.8)
        # e10b 第二遍帶著「要找第 25 個」去讀：讀頭走到第 25 格停住，金色亮起
        head = Triangle().scale(.14).rotate(PI).set_fill(QC, 1).set_stroke(width=0).move_to(nm2[0].get_top() + UP * .22)
        head.transient = True
        self.at(A("e10b", .05), FadeIn(head), run_time=.3)
        self.at(A("e10b", .1), head.animate.move_to(nm2[24].get_top() + UP * .22), run_time=1.4, rate_func=rate_functions.ease_out_cubic)
        self.at(A("e10b", .6), Indicate(nm2[24], color=GOLD, scale_factor=2.0), run_time=.9, sfx="pop", gain=.45)
        # e11 會不會只是變長？
        card = prompt_card(CARD8, label="第 25 個是誰？", w=4.2, h=2.6)
        dots = VGroup(*[Dot(radius=.11, color=MUTED) for _ in range(7)]).arrange(RIGHT, buff=.2).next_to(card, LEFT, buff=.45)
        self.at(A("e11", 0), FadeOut(head), FadeOut(VGroup(mt, ml, one, nl, nm, nm2, ghost, nt1, nt2)),
                Succession(Wait(.3), AnimationGroup(DrawBorderThenFill(card.card), FadeIn(card[1:]), run_time=.8)), run_time=1.1)
        self.at(A("e11", .65), card.animate.stretch(1.25, 0), run_time=.6, rate_func=there_and_back)
        # e12 塞一排點號：完全沒用
        self.at(A("e12", .3), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=.15), run_time=.8, sfx="tick", gain=.4)
        x = cross_mark(BAD, .75).move_to(dots)
        for m_ in x.family_members_with_points():
            m_.dots_ok = m_.cross_ok = True
        self.at(A("e12", .78), Create(x), run_time=.5, sfx="thud", gain=.5)
        # e14 提升來自重複有意義的內容：卡片複製成兩張
        card2 = card.copy()
        self.add(card2)
        self.at(A("e14", .1), FadeOut(VGroup(dots, x)), card.animate.shift(LEFT * CARD8_DX), card2.animate.shift(RIGHT * CARD8_DX), run_time=.9, rate_func=POP, sfx="pop", gain=.45)
        self.at(A("e14", .85), Highlight(card2, color=P2C, scale_factor=1.08, inner=False), run_time=.8)
        self.ev_end = VGroup(card, card2)
        self.finish()


def sc08_end():
    c1 = prompt_card(CARD8 + LEFT * CARD8_DX, label="第 25 個是誰？", w=4.2, h=2.6)
    c2 = prompt_card(CARD8 + RIGHT * CARD8_DX, label="第 25 個是誰？", w=4.2, h=2.6)
    return c1, c2


# ---------------- sc09：邊界 ----------------
class Sc09(Sheet):
    SID = "sc09"

    def construct(self):
        A = self.A
        self.cam_set(EV_C, EV_W)
        D = corr_full()
        S7 = [sc07_pm(), station_label("Prefill", PRE_C, ST_DY), typewriter(DEC_C + LEFT * TW_DX, k=SK), paper(DEC_C + LEFT * TW_DX, 5, k=SK), station_label("Decode", DEC_C, ST_DY)]
        c1, c2 = sc08_end()
        self.add(*flat(D), *S7, c1, c2)
        # b1 它也有邊界
        fx = c2.get_right()[0] + .45
        fence = DashedLine(np.array([fx, LAB_Y + 2.6, 0]), np.array([fx, LAB_Y - 3.0, 0]), dash_length=.22).set_stroke(TXT_STRONG, 4, .8)
        self.at(A("b1", .05), Create(fence), run_time=.6)
        self.at(A("b1", .35), VGroup(c1, c2).animate(rate_func=there_and_back).shift(RIGHT * .38), run_time=.7, sfx="thud", gain=.4)
        # b2 開了 CoT：一台打字機
        tw = typewriter(np.array([2.95, LAB_Y + .2, 0]))
        cot = T("CoT", .06, DEC).next_to(tw, UP, buff=.3)
        self.at(A("b2", 0), FadeOut(VGroup(c1, c2, fence)), Succession(Wait(.25), AnimationGroup(DrawBorderThenFill(tw[0]), FadeIn(tw[1:]), Write(cot), run_time=1.0)),
                run_time=1.25)
        # b3 和同樣開 CoT、不貼的比；b3b 5 勝 1 敗 22 平
        g = score_grid(28, 14, 5, 1, GRID_C + DOWN * .2 + LEFT * .6, lit=0)
        ctl = T("對照：同樣開 CoT、不貼", .045, MUTED).next_to(g, DOWN, buff=.35).align_to(g, LEFT)
        self.at(A("b3", .1), LaggedStart(*[FadeIn(s) for s in g], lag_ratio=.02), Write(ctl), run_time=1.3)
        lit = score_grid(28, 14, 5, 1, GRID_C + DOWN * .2 + LEFT * .6)
        res = VGroup(T("5 勝", .065, GOOD), T("1 敗", .065, BAD), T("22 平", .065, TXT)).arrange(RIGHT, buff=.55).next_to(g, UP, buff=.45)
        self.at(A("b3b", 0), LaggedStart(*[Transform(g[k], lit[k]) for k in range(5)], lag_ratio=.15), Write(res[0]), run_time=.6, sfx="pop", gain=.4)
        self.at(A("b3b", .5), Transform(g[5], lit[5]), Write(res[1]), run_time=.5, sfx="thud", gain=.4)
        self.at(A("b3b", .6), *[Transform(g[k], lit[k]) for k in range(6, 28)], Write(res[2]), run_time=.8)
        # b4 開了 CoT，模型自己在回答裡重新想一遍：打字機先把問題打一次（橘色）
        pq = VGroup(*[Square(.34).set_fill(QC, .6).set_stroke(QC, 1.5) for _ in range(4)]).arrange(RIGHT, buff=.05).next_to(tw, RIGHT, buff=.1).shift(UP * .58)
        self.at(A("b4", .2), LaggedStart(*[FadeIn(s, shift=RIGHT * .2) for s in pq], lag_ratio=.25), run_time=1.6, sfx="tick", gain=.35)
        # b4b 理解的問題已經修好
        self.at(A("b4b", .2), Indicate(pq, color=QC, scale_factor=1.1), run_time=.9)
        # b5 再幫它重複一次，好處變小：格子大多是灰的
        self.at(A("b5", .3), LaggedStart(*[Indicate(g[k], color=TXT_STRONG, scale_factor=1.2) for k in range(6, 28, 2)], lag_ratio=.05), run_time=1.2)
        # b6、b7 最適合：資訊提取、閱讀測驗
        star_p = EV_C + np.array([-4.6, -.6, 0])
        star = VGroup(reader("bark", P2C, star_p, joy=1), bubble_at(star_p, meaning(1, 1.0)))
        self.at(A("b6", .05), FadeOut(VGroup(g, ctl, res, tw, cot, pq)), Succession(Wait(.3), GrowFromCenter(star[0], run_time=.6, rate_func=POP)), run_time=.9)
        self.at(A("b6", .45), FadeIn(star[1], scale=.5), run_time=.6, sfx="ding", gain=.35)
        self.at(A("b6", .8), Wiggle(star[0], scale_value=1.08), run_time=.8)
        use = VGroup(T("資訊提取", .07, P2C), T("閱讀測驗", .07, P2C)).arrange(DOWN, buff=.45, aligned_edge=LEFT).next_to(star[0], RIGHT, buff=1.0)
        uls = VGroup(*[underline(u, P2C, 4, .1) for u in use])
        self.at(A("b7", .05), LaggedStart(*[AnimationGroup(Write(u), Create(l_)) for u, l_ in zip(use, uls)], lag_ratio=.35), run_time=1.0, sfx="pop", gain=.4)
        # b8 推理模型自己學會先把問題重說一遍
        rr = small("推理模型", TXT, EV_C + np.array([-2.5, -.5, 0]), w=2.1)
        say_ = bubble(VGroup(*[Square(.3).set_fill(QC, .7).set_stroke(QC, 1.5) for _ in range(3)]).arrange(RIGHT, buff=.05), tail=DL)
        say_.next_to(rr, UR, buff=.05)
        self.at(A("b8", 0), FadeOut(use), FadeOut(uls), FadeOut(star), GrowFromCenter(rr), run_time=.8)
        self.at(A("b8", .55), FadeIn(say_, scale=.6), run_time=.6, sfx="pop", gain=.4)
        self.at(A("b8", .82), Wiggle(rr, scale_value=1.08), run_time=.7)
        # b9 把模型自己摸索出的策略寫了出來：兩張卡片接在它旁邊
        c1, c2 = prompt_card(EV_C + np.array([2.2, -.5, 0]), label="", w=1.8, h=1.2), prompt_card(EV_C + np.array([4.3, -.5, 0]), label="", w=1.8, h=1.2, color=P2C)
        self.at(A("b9", .2), FadeIn(c1, shift=LEFT * .3), FadeIn(c2, shift=LEFT * .3), run_time=.9)
        self.at(A("b9", .8), FadeOut(VGroup(rr, say_, c1, c2)), self.cam(PANO_C, PANO_W), run_time=1.2, rate_func=SINE)
        self.finish()


# ---------------- sc10：三點回顧 ----------------
def pano_parts():
    D = corr_full()
    S7 = dict(pm=sc07_pm(), pl_=station_label("Prefill", PRE_C, ST_DY), tw=typewriter(DEC_C + LEFT * TW_DX, k=SK), pp=paper(DEC_C + LEFT * TW_DX, 5, k=SK),
              dl=station_label("Decode", DEC_C, ST_DY))
    return D, S7


def dim(fr, it, lk, op):
    """回顧：框與線只調線條透明度（set_opacity 會把框填滿）。"""
    op = max(op, .55) if op < 1 else op
    return [fr.animate.set_stroke(opacity=op), it.animate.set_opacity(op), lk.animate.set_stroke(opacity=op)]


class Sc10(Sheet):
    SID = "sc10"
    END_BRAND = True

    def end_clear(self):
        tgt = self.pl_end.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.get_top()[1] + 1.2 - tgt.bodyg.get_bottom()[1]))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(self.pl_end, tgt, rate_func=rate_functions.ease_in_cubic), FadeOut(self.art_end)]

    def construct(self):
        A = self.A
        self.cam_set(PANO_C, PANO_W)
        D, S7 = pano_parts()
        self.add(*flat(D), *S7.values())
        # x1 整條長廊再看一次：光從第二遍一路照回第一遍
        b = Beam(RP(2, 4), P1X[0] - RW / 2, op=.2)
        self.add(b)
        self.at(A("x1", .1), b.reach.animate.set_value(1), FadeOut(D["l1"]), FadeOut(D["l2"]), run_time=1.6, rate_func=SINE)
        self.at(A("x1", .8), b.reach.animate.set_value(0), run_time=.5)
        self.remove(b)
        # ① 第一遍（只能回頭看）
        f1 = recap_frame(VGroup(*D["rs"], *D["ns"]))
        i1 = VGroup(T("①", .062, GOLD), T("只能回頭看", .062, TXT_STRONG)).arrange(RIGHT, buff=.18).next_to(f1, DOWN, buff=.22)
        k1 = recap_link(f1, i1)
        self.at(A("x2", .05), Create(f1), FadeOut(S7["pl_"]), FadeOut(S7["dl"]), run_time=.8, sfx="click", gain=.5)
        self.at(A("x2", .35), Create(k1), Write(i1), run_time=.8)
        self.at(A("x2", .72), Wiggle(D["bb"], scale_value=1.15), run_time=.9)
        # ② 接縫與第二遍
        f2 = recap_frame(VGroup(*D["rs2"], *D["ns2"]))
        i2 = VGroup(T("②", .062, GOLD), T("第二遍看得到全文", .062, TXT_STRONG)).arrange(RIGHT, buff=.18).next_to(f2, DOWN, buff=.22).align_to(f2, LEFT).shift(RIGHT * .5)
        k2 = recap_link(f2, i2)
        self.at(A("x3", .05), *dim(f1, i1, k1, .35), Create(f2), run_time=.8, sfx="click", gain=.5)
        self.at(A("x3", .35), Create(k2), Write(i2), run_time=.8)
        self.at(A("x3", .72), Wiggle(D["bb2"], scale_value=1.18), run_time=.9)
        # ③ Prefill
        f3 = recap_frame(S7["pm"])
        i3t = VGroup(T("多的字", .062, TXT_STRONG), T("在 Prefill", .062, TXT_STRONG)).arrange(DOWN, buff=.14, aligned_edge=LEFT)
        i3 = VGroup(T("③", .062, GOLD), i3t).arrange(RIGHT, buff=.18, aligned_edge=UP).next_to(f3, RIGHT, buff=.6)
        k3 = Line(f3.get_right(), np.array([i3.get_left()[0] - .06, f3.get_right()[1], 0])).set_stroke(TXT_STRONG, 2)
        self.at(A("x4", .05), *dim(f2, i2, k2, .35), Create(f3), run_time=.8, sfx="click", gain=.5)
        self.at(A("x4", .35), Create(k3), Write(i3), run_time=.8)
        self.at(A("x4", .72), Wiggle(S7["pm"], scale_value=1.05, rotation_angle=.01 * TAU), run_time=.9)
        # x5 開了 CoT 好處就不明顯：打字機閃一下
        self.at(A("x5", .2), Highlight(S7["tw"], color=DEC, scale_factor=1.08, inner=False), run_time=.9)
        self.at(A("x5", .7), *dim(f1, i1, k1, 1), *dim(f2, i2, k2, 1), run_time=.6)
        # x6 錘錘：完整的文章在說明欄
        pl, drop = self.plumb_in(np.array([P2X[3] + STEP / 2, ST_Y + .2, 0]), .45)
        art = VGroup(T("完整文章", .058, TXT), T("在說明欄", .058, TXT)).arrange(DOWN, buff=.12).next_to(np.array([P2X[3] + STEP / 2, ST_Y + .2, 0]), LEFT, buff=.8)
        self.at(A("x6", 0), FadeOut(VGroup(S7["tw"], S7["pp"])), *drop, run_time=.7)
        self.lipsync(pl)
        self.at(A("x6", .3), FadeIn(art, shift=DOWN * .15), *pl.look(DOWN), run_time=.7)
        self.at(A("x6", .55), *pl.hop(-.22), run_time=.45)
        self.at(A("x6", .8), *pl.hop(-.22), run_time=.45)
        self.pl_end, self.art_end = pl, art
        self.finish()
