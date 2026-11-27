"""v005 LLM-as-a-Verifier：sc06～sc11（旋鈕台、成績單、代價、回顧）。共用元件在 scenes_a.py 與 world.py。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scenes_a import *  # noqa: E402,F401,F403


def sc_bg(scene, d):
    scene.add(road())
    add_all(scene, d)


def knob_turn(K_old, K_new):
    """旋鈕換狀態：外框、指針、字一起變；回傳動畫。"""
    return ReplacementTransform(K_old, K_new)


# ---------------- builders ----------------
def base5():
    """旋鈕台以外的整張圖（sc06 之後都在）：前四站的最後樣子。"""
    return sc05_end()


def sc06_end():
    return dict(pn=panel5(), K=knobs((True, False, False), ("G=20", None, None)), G=stage_g(True, True, False))


def sc07_end():
    kt = k_table()
    br_ = kt.arrows
    brl = T("2.7～2.9 個百分點", .042, MUTED).next_to(kt.arrows[1], RIGHT, buff=.4)
    x16 = T("16 倍", .048, INK).next_to(kt.link, LEFT, buff=.3).set_y(kt.yg - .45)
    return dict(pn=panel5(), K=knobs((False, True, False), (None, "K=16", None)), kt=kt, br=br_, brl=brl, x16=x16)


def sc08_end():
    C = stage_c(3)
    for l_ in C.ls:
        l_.remove(l_[2])
    return dict(pn=panel5(), K=knobs((False, False, True), (None, None, "C=3")), C=C)


def sota_r(step=7):
    """論文首頁（真的截圖）＋最佳成績；step 8 加兩台終端機。"""
    pp = paper_page(np.array([LX - 1.45, S6[1] + .45, 0]), 3.0, "cut")
    t = T("論文的最佳成績 86.5%", .042, INK).move_to(np.array([LX, S6[1] + 2.45, 0]))
    a_, b_ = pp.px(BAR865[0] - 6, BAR865[2] - 6), pp.px(BAR865[1] + 6, BAR865[3] + 6)
    mk = Rectangle(width=b_[0] - a_[0], height=a_[1] - b_[1]).set_stroke(GOLD, 7).set_fill(opacity=0).move_to((a_ + b_) / 2)
    mk.nocheck = True
    g = dict(t=t, pp=pp, mk=mk)
    if step >= 8:
        a = term_icon(np.array([LX + 1.3, S6[1] + .9, 0]), .85)
        b = term_icon(np.array([LX + 1.3, S6[1] - 1.1, 0]), .85, alt=True)
        g.update(a=a, b=b, ne=B("≠", .08, INK).move_to(np.array([LX + 1.3, S6[1] - .1, 0])),
                 la=T("最佳成績", .038, TXT).next_to(a, RIGHT, buff=.25), lb=T("對照的成績", .038, TXT).next_to(b, RIGHT, buff=.25),
                 hp=T("另一套 harness", .038, MUTED))
        g["hp"].next_to(g["lb"], DOWN, buff=.24, aligned_edge=LEFT)
    return g


def sc09_end():
    return dict(ev=evidence(6))


# ================= sc06 旋鈕 G =================
class Sc06(Sheet5):
    SID = "sc06"

    def construct(self):
        A_ = self.A
        self.cam_set(S3, 14)
        sc_bg(self, base5())
        pn = panel5()
        K = knobs()
        # g1 鏡頭往下到旋鈕台，三個旋鈕依序亮燈
        self.at(0, self.cam(S5, 14), Succession(Wait(1.2), FadeIn(pn)), run_time=2.4, rate_func=EASE)
        for i, f in enumerate((.45, .62, .79)):
            self.at(A_("g1", f), DrawBorderThenFill(K[i]), run_time=.5, sfx="click", gain=.3)
        # g2 G 亮，其他兩個變暗；5 格粗尺，兩個點掉進同一格
        st = stage_g(True, True, False)
        coarse, fine, lc, lf, d1, d2, same, fa, fb, acc, rd = st
        K1 = knobs((True, False, False))
        self.at(A_("g2", .02), knob_turn(K, K1), run_time=.5)
        self.at(A_("g2", .3), Create(coarse[0]), FadeIn(coarse[1]), FadeIn(lc), run_time=.7)
        d1s, d2s = d1.copy().shift(UP * 1.2).set_opacity(0), d2.copy().shift(UP * 1.2).set_opacity(0)
        self.at(A_("g2", .7), Indicate(coarse[0], scale_factor=1.06), run_time=.7)
        # g3 兩個相近的判斷擠進粗尺同一格；下面換上 20 格細尺，兩個點落在相鄰兩格
        self.at(A_("g3", .12), ReplacementTransform(d1s, d1), Succession(Wait(.15), ReplacementTransform(d2s, d2)), run_time=.6, rate_func=rate_functions.ease_out_bounce)
        self.at(A_("g3", .32), FadeIn(same, shift=LEFT * .15), run_time=.4)
        self.at(A_("g3", .45), Create(fine[0]), FadeIn(lf), run_time=.7)
        self.at(A_("g3", .68), TransformFromCopy(d1, fa), TransformFromCopy(d2, fb), run_time=.7, sfx="pop", gain=.4)
        self.at(A_("g3", .9), Indicate(fa, scale_factor=1.6), Indicate(fb, scale_factor=1.6), run_time=.5)
        # g5 G 轉到 20；計分板 5 格 → 20 格，69 → 77
        K2 = knobs((True, False, False), ("G=20", None, None))
        self.at(A_("g5", .05), knob_turn(K1, K2), run_time=.8, sfx="knob", gain=.45)
        self.at(A_("g5", .3), Write(acc), run_time=.8)
        self.at(A_("g5", .55), Create(rd[0]), GrowFromEdge(rd[1], DOWN), FadeIn(rd[2]), FadeIn(rd[3]), run_time=.5)
        self.at(A_("g5", .8), GrowFromEdge(rd[4], DOWN), Write(rd[5]), FadeIn(rd[6]), run_time=.6, sfx="pop", gain=.4)
        # g6 沒有新資訊，只是更細的格子：細尺的格子一格一格亮起來
        self.at(A_("g6", .12), LaggedStart(*[c.animate(rate_func=there_and_back).set_fill(GK, .7) for c in fine.cells], lag_ratio=.06), run_time=2.0)
        self.tail(Indicate(rd[5], scale_factor=1.2))
        self.finish()


# ================= sc07 旋鈕 K =================
class Sc07(Sheet5):
    SID = "sc07"

    def construct(self):
        A_ = self.A
        self.cam_set(S5, 14)
        sc_bg(self, base5())
        d = sc06_end()
        add_all(self, d)
        # q1 K 亮；一排小評審各丟一個分數點，金色平均線落在中間
        K1 = knobs((False, True, False), (None, "K", None))
        k1 = stage_k(1)
        js, sl, lavg, lk = k1
        ln, ds, am = sl
        self.at(A_("q1", .0), FadeOut(d["G"], shift=DOWN * .3), knob_turn(d["K"], K1), run_time=.6, sfx="knob", gain=.4)
        self.at(A_("q1", .18), LaggedStart(*[FadeIn(j, shift=UP * .3) for j in js], lag_ratio=.12), Create(ln), run_time=.9)
        self.at(A_("q1", .45), LaggedStart(*[TransformFromCopy(j.head, dt) for j, dt in zip(js, ds)], lag_ratio=.12), run_time=1.0)
        self.at(A_("q1", .72), Create(am), FadeIn(lavg), Write(lk), run_time=.7)
        # q3 晃動 vs 偏誤
        k2 = stage_k(2)
        wob, bias, note_ = k2
        self.at(A_("q3", .0), FadeOut(k1), run_time=.4)
        self.at(A_("q3", .08), Create(wob[0]), FadeIn(wob[4]), LaggedStart(*[FadeIn(x, scale=.5) for x in wob[1]], lag_ratio=.1), Create(wob[3]), FadeIn(note_), run_time=.9)
        self.at(A_("q3", .32), Create(wob[2]), run_time=.5)
        self.at(A_("q3", .55), Create(bias[0]), FadeIn(bias[4]), LaggedStart(*[FadeIn(x, scale=.5) for x in bias[1]], lag_ratio=.1), Create(bias[3]), run_time=.9, sfx="thud", gain=.35)
        self.at(A_("q3", .8), Create(bias[2]), run_time=.5)
        # q4 永遠多 2 公斤的秤
        sca = stage_k(3)[3]
        plat, dial, ticks, true_t, needle, wt, rdg = sca
        self.at(A_("q4", .02), FadeIn(VGroup(plat, dial, ticks, true_t)), k2.animate.set_opacity(.3), run_time=.5)
        self.at(A_("q4", .25), FadeIn(wt, shift=DOWN * .6), Create(needle), run_time=.5, sfx="thud", gain=.4)
        self.at(A_("q4", .5), Write(rdg), run_time=.5)
        self.at(A_("q4", .75), Wiggle(needle, scale_value=1, rotation_angle=.04 * TAU, n_wiggles=3), wt.animate(rate_func=there_and_back).shift(UP * .25), run_time=.8)
        # q6b 換一種量法：配對準確率
        pi = pair_icon(STAGE_C + UP * .35).scale(1.7)
        pl_ = T("配對準確率", .05, TXT).next_to(pi, DOWN, buff=.35)
        self.at(A_("q6b", .0), FadeOut(k2), FadeOut(sca), run_time=.5)
        self.at(A_("q6b", .25), FadeIn(pi[0], shift=RIGHT * .4), FadeIn(pi[1], shift=LEFT * .4), FadeIn(pi[2]), run_time=.7)
        self.at(A_("q6b", .55), Create(pi[3]), Write(pl_), run_time=.6)
        # q7 對照表：verifier 問 1 次
        kt = k_table()
        head, rows, cells, link, axis = kt
        K2 = knobs((False, True, False), (None, "K=16", None))
        self.at(A_("q7", .0), FadeOut(VGroup(pi, pl_)), knob_turn(K1, K2), run_time=.5)
        self.at(A_("q7", .15), Create(axis[0]), FadeIn(axis[1]), FadeIn(axis[2]), FadeIn(rows), FadeIn(head), run_time=.6)
        self.at(A_("q7", .55), GrowFromCenter(cells[2][0]), Write(cells[2][1]), run_time=.5, sfx="pop", gain=.35)
        # q7b 追上一般評審問 16 次，都是 74.7%：金色虛線連起兩點
        self.at(A_("q7b", .2), GrowFromCenter(cells[1][0]), Write(cells[1][1]), run_time=.5)
        self.at(A_("q7b", .6), Create(link), Indicate(cells[1][1]), Indicate(cells[2][1]), run_time=.8, sfx="ding", gain=.4)
        # q8 每個 K 的差距差不多：兩條平行的斜箭頭一樣長
        e = sc07_end()
        self.at(A_("q8", .05), GrowFromCenter(cells[0][0]), Write(cells[0][1]), GrowFromCenter(cells[3][0]), Write(cells[3][1]), run_time=.6)
        self.at(A_("q8", .38), Create(e["br"][0]), Create(e["br"][1]), run_time=.7)
        self.at(A_("q8", .72), FadeIn(e["brl"], shift=LEFT * .2), run_time=.5)
        # q8b 16 倍只在追平的那一點成立
        x16 = e["x16"]
        self.at(A_("q8b", .1), ShowPassingFlash(link.copy().set_stroke(GOLD, 8), time_width=.6), FadeIn(x16, shift=RIGHT * .1), run_time=.8)
        self.tail(Indicate(x16, scale_factor=1.2))
        self.finish()


# ================= sc08 旋鈕 C =================
class Sc08(Sheet5):
    SID = "sc08"

    def construct(self):
        A_ = self.A
        self.cam_set(S5, 14)
        sc_bg(self, base5())
        d = sc07_end()
        add_all(self, d)
        C3 = stage_c(3)
        sc, ls = C3.sc, C3.ls
        # c1 C 亮；軌跡乙上的大問號裂成三個小問號
        K1 = knobs((False, False, True), (None, None, "C=3"))
        self.at(A_("c1", .0), FadeOut(VGroup(d["kt"], d["br"], d["brl"], d["x16"])), knob_turn(d["K"], K1), run_time=.6, sfx="knob", gain=.4)
        self.at(A_("c1", .2), FadeIn(sc, shift=UP * .3), run_time=.7)
        bigq = B("?", .1, CK).move_to(sc.paper.get_right() + RIGHT * 1.0)
        smq = VGroup(*[B("?", .05, CK).move_to(l_[0]) for l_ in ls])
        for q_ in smq:
            q_.overlap_ok = True
        self.at(A_("c1", .45), FadeIn(bigq, scale=1.6), run_time=.5)
        self.at(A_("c1", .75), ReplacementTransform(VGroup(bigq, bigq.copy(), bigq.copy()), smq), run_time=.7, sfx="pop", gain=.4)
        # c2 三面放大鏡升起
        self.at(A_("c2", .2), *[ReplacementTransform(q, VGroup(l_[0], l_[1])) for q, l_ in zip(smq, ls)], run_time=.8)
        self.at(A_("c2", .55), LaggedStart(*[Write(l_[2]) for l_ in ls], lag_ratio=.3), run_time=1.0)
        # c2b 各看一行
        rowhl = VGroup(*[Rectangle(width=sc.paper.width - .2, height=sc.lines[i].height + .16).set_fill(CK, .16).set_stroke(width=0).move_to(np.array([sc.paper.get_x(), sc.lines[i].get_y(), 0])) for i in LENS_ROWS])
        rowhl.overlap_ok = True
        for k, (i, f) in enumerate(zip(LENS_ROWS, (.08, .4, .7))):
            self.at(A_("c2b", f), Highlight(ls[k][0], color=CK, scale_factor=1.25), FadeIn(rowhl[k]), sc.lines[i].animate.set_color(CK), run_time=.7)
        # c3 單獨一面 75.2～76.4，三面一起 78.3
        bars2 = stage_c(2).bars
        base = bars2[0]
        self.at(A_("c3", .02), *[sc.lines[i].animate.set_color(TXT) for i in LENS_ROWS], FadeOut(rowhl), *[FadeOut(l_[2]) for l_ in ls], Create(base), run_time=.5)
        for l_ in ls:
            l_.remove(l_[2])
        for k, f in enumerate((.12, .26, .4)):
            r, v, lb = bars2[1 + 3 * k: 4 + 3 * k]
            self.at(A_("c3", f), GrowFromEdge(r, DOWN), FadeIn(v), FadeIn(lb), run_time=.6)
        r, v, lb = bars2[10:13]
        self.at(A_("c3", .7), GrowFromEdge(r, DOWN), FadeIn(v), FadeIn(lb), run_time=.7, sfx="pop", gain=.4)
        self.at(A_("c3", .9), Indicate(v, scale_factor=1.25), run_time=.6)
        self.at(A_("c4", .12), Indicate(K1[2], color=CK, scale_factor=1.15), run_time=.7)
        self.at(A_("c4", .28), LaggedStart(*[Indicate(bars2[2 + 3 * k], scale_factor=1.2) for k in range(4)], lag_ratio=.2), run_time=.9)
        # c4 證據最薄：4 個？5 個？沒試過
        q, nt = C3[-2], C3[-1]
        self.at(A_("c4", .5), LaggedStart(*[Create(x[0]) for x in q], lag_ratio=.3), LaggedStart(*[FadeIn(x[1]) for x in q], lag_ratio=.3), run_time=.9)
        self.at(A_("c4", .8), FadeIn(nt), run_time=.4)
        # c4b 誤差範圍重疊
        bars3 = C3.bars
        self.remove(*bars2)
        for k in range(4):
            r, v, lb = bars3[1 + 4 * k: 4 + 4 * k]
            self.add(r, lb)
        self.add(bars3[0])
        bands = [bars3[4 + 4 * k] for k in range(4)]
        vals = [bars3[2 + 4 * k] for k in range(4)]
        old_vals = [bars2[2 + 3 * k] for k in range(4)]
        self.add(*old_vals)
        self.at(A_("c4b", .05), *[ReplacementTransform(o, n) for o, n in zip(old_vals, vals)], LaggedStart(*[FadeIn(b, scale=.6) for b in bands], lag_ratio=.15), run_time=1.0, sfx="pop", gain=.35)
        self.remove(*bars3)
        self.add(bars3)
        # c4c 沒說範圍代表什麼，也沒檢定
        strip = Rectangle(width=bars3.get_width() + .1, height=.6).set_fill(INK, .14).set_stroke(width=0)
        strip.move_to(np.array([bars3.get_x(), np.mean([b.get_y() for b in bands]), 0]))
        strip.overlap_ok = True
        self.at(A_("c4c", .1), FadeIn(strip, rate_func=there_and_back_with_pause), run_time=1.6)
        self.remove(strip)
        self.at(A_("c4c", .6), Wiggle(VGroup(*bands), scale_value=1.05, rotation_angle=.01 * TAU), run_time=.9)
        self.tail(Indicate(nt, scale_factor=1.2))
        self.finish()


# ================= sc09 換個領域 =================
class Sc09(Sheet5):
    SID = "sc09"

    def construct(self):
        A_ = self.A
        self.cam_set(S5, 14)
        sc_bg(self, base5())
        d = sc08_end()
        add_all(self, d)
        E = evidence(6)
        t1, robot, vb, p166, t2, term, vb2, p34 = E
        # v1 鏡頭往左到成績單；三個旋鈕都亮回來
        self.at(0, self.cam(S6, 14), knob_turn(d["K"], knobs()), Succession(Wait(.7), AnimationGroup(FadeIn(t1, shift=DOWN * .2), Create(vb[0]), FadeIn(robot, shift=UP * .3), lag_ratio=.25)), run_time=1.8, rate_func=EASE)
        # v2 機械手臂
        self.at(A_("v2", .2), Wiggle(robot, scale_value=1.05, rotation_angle=.03 * TAU), run_time=.9)
        self.at(A_("v2", .6), Indicate(t1[1], color=ARG), run_time=.7)
        self.at(A_("v2", .85), Wiggle(robot, scale_value=1.03, rotation_angle=.02 * TAU), run_time=.8)
        # v3 70.8 → 87.4，+16.6
        self.at(A_("v3", .25), GrowFromEdge(vb[1], DOWN), FadeIn(vb[2]), FadeIn(vb[3]), run_time=.6)
        self.at(A_("v3", .5), GrowFromEdge(vb[4], DOWN), FadeIn(vb[5]), FadeIn(vb[6]), run_time=.7)
        self.at(A_("v3", .8), Write(p166), run_time=.5, sfx="pop", gain=.45)
        # v4 寫程式：同一批候選，只換挑法
        self.at(A_("v4", .05), FadeIn(t2, shift=DOWN * .2), run_time=.6)
        self.at(A_("v4", .45), DrawBorderThenFill(term), run_time=.7)
        self.at(A_("v4", .8), Indicate(t2[1], color=EV), run_time=.7)
        # v4b 只交一次 83.1；v4c verifier 挑 86.5
        self.at(A_("v4b", .2), Create(vb2[0]), GrowFromEdge(vb2[1], DOWN), FadeIn(vb2[2]), FadeIn(vb2[3]), run_time=.8)
        self.at(A_("v4b", .72), Indicate(vb2[2], scale_factor=1.25), run_time=.6)
        self.at(A_("v4c", .25), GrowFromEdge(vb2[4], DOWN), FadeIn(vb2[5]), FadeIn(vb2[6]), run_time=.8)
        # v5 左欄換成論文首頁：最佳成績 86.5%
        sr = sota_r(8)
        left = VGroup(t1, robot, vb, p166)
        sr["pp"].shift(DOWN * 6)
        self.at(A_("v5", .0), FadeOut(left, shift=LEFT * .5), run_time=.5)
        self.at(A_("v5", .15), sr["pp"].animate(rate_func=EASE).shift(UP * 6), FadeIn(sr["t"]), run_time=.8, sfx="slide", gain=.3)
        sr["mk"].set_z_index(6)
        self.at(A_("v5", .55), Create(sr["mk"]), Indicate(vb2[5], color=GOLD), run_time=.6)
        self.at(A_("v5", .8), ShowPassingFlash(sr["mk"].copy().set_stroke(GOLD, 12), time_width=.5), run_time=.7)
        # v5b 兩台終端機，對照的成績換了 harness
        self.at(A_("v5b", .02), FadeIn(sr["a"]), FadeIn(sr["la"]), run_time=.5)
        self.at(A_("v5b", .35), FadeIn(sr["b"]), FadeIn(sr["lb"]), run_time=.5)
        self.at(A_("v5b", .7), FadeIn(sr["hp"], shift=UP * .15), run_time=.4)
        # v5c harness 是什麼：兩台外框不同
        self.at(A_("v5c", .2), Indicate(sr["a"][0], color=TEAL_L, scale_factor=1.08), Indicate(sr["b"], scale_factor=1.08), run_time=.9)
        # v5d 變因不只一個
        self.at(A_("v5d", .05), Write(sr["ne"]), run_time=.5, sfx="thud", gain=.45)
        # v6 真正算在 verifier 頭上的是 3.4
        srg = Group(*sr.values())
        self.at(A_("v6", .0), FadeOut(srg, shift=LEFT * .4), run_time=.5)
        self.at(A_("v6", .15), FadeIn(left, shift=RIGHT * .4), run_time=.6)
        dimL = Rectangle(width=6.6, height=6.2).set_fill(BG, .6).set_stroke(width=0).move_to(np.array([LX, S6[1] - .1, 0]))
        dimL.nocheck = True
        self.at(A_("v6", .45), Write(p34), FadeIn(dimL), run_time=.6, sfx="ding", gain=.4)
        self.tail(Indicate(p34, scale_factor=1.2), FadeOut(dimL))
        self.finish()


# ================= sc10 每次都要表態 =================
class Sc10(Sheet5):
    SID = "sc10"

    def construct(self):
        A_ = self.A
        self.cam_set(S6, 14)
        sc_bg(self, base5())
        add_all(self, sc08_end())
        d = sc09_end()
        add_all(self, d)
        # x1 紅色的格子
        rb = red_board(31)
        reds = rb.waf.cells[100 - 31:]
        dims = rb.waf.cells[:100 - 31]
        self.at(A_("x1", .0), FadeOut(d["ev"]), FadeIn(rb.waf.frame), FadeIn(dims), run_time=.6)
        self.at(A_("x1", .45), LaggedStart(*[FadeIn(c, scale=.4) for c in reds], lag_ratio=.03), Write(rb[1]), run_time=1.0, sfx="pop", gain=.4)
        # x2 只取最高：一百次排錯 0 次，只是不表態
        c2 = cost(2)
        J, tc, mw, ml, ring = c2[1:6]
        dimR = Rectangle(width=5.4, height=4.6).set_fill(BG, .7).set_stroke(width=0).move_to((RED_C + RED2_C) / 2 + UP * .2)
        dimR.nocheck = True
        self.at(A_("x2", .02), FadeIn(J, shift=UP * .4), FadeIn(dimR), run_time=.6)
        self.at(A_("x2", .2), FadeIn(tc, shift=DOWN * .2, lag_ratio=.15), run_time=.8)
        self.at(A_("x2", .45), FadeIn(mw, scale=.8), FadeIn(ml[0]), run_time=.6)
        self.at(A_("x2", .65), Write(ml[1]), run_time=.4)
        self.at(A_("x2", .8), Create(ring), run_time=.5, sfx="click", gain=.4)
        # x3 期望值逼它每次表態：31 次表錯；20 格還有 23 次
        c3 = cost(3)
        J3 = c3[1]
        rb2, hdr = c3[-2], c3[-1]
        lab31 = c3[0][1]
        self.at(A_("x3", .02), ReplacementTransform(J, J3), FadeOut(dimR), run_time=.6, sfx="thud", gain=.35)
        self.at(A_("x3", .3), ReplacementTransform(rb[1], lab31), FadeIn(hdr, shift=DOWN * .15), run_time=.6)
        self.at(A_("x3", .58), FadeIn(rb2.waf.frame), FadeIn(rb2.waf.cells[:77]), run_time=.4)
        self.at(A_("x3", .68), LaggedStart(*[FadeIn(c, scale=.4) for c in rb2.waf.cells[77:]], lag_ratio=.03), Write(rb2[1]), run_time=.9, sfx="pop", gain=.4)
        # x4 平手就交給人審：只取最高反而比較安全
        c4 = cost(4)
        tr, small = c4[-2], c4[-1]
        small.set_z_index(2)
        J4 = c4[1]
        self.at(A_("x4", .02), FadeOut(VGroup(mw, ml, ring)), FadeIn(tr, shift=DOWN * .2), ReplacementTransform(J3, J4), FadeIn(dimR), run_time=.6)
        tc.pass_ok = True
        tc.set_z_index(2)
        self.at(A_("x4", .3), ReplacementTransform(tc, small, path_arc=-PI / 4), run_time=1.0, sfx="slide", gain=.4)
        self.at(A_("x4", .75), Indicate(tr[1]), run_time=.6)
        # x5 論文沒有談這一層
        qb = cost(5)[-1]
        self.at(A_("x5", .1), Create(qb[0]), FadeIn(qb[1]), run_time=.6)
        # x6 平手算半分：77 比 56
        hc = half_credit()
        base, g12, g44, g77, va, vb, la, lb, f = hc
        self.at(A_("x6", .0), FadeOut(VGroup(tr, small, qb)), run_time=.5)
        self.at(A_("x6", .12), Write(f), Create(base), run_time=.8)
        self.at(A_("x6", .32), GrowFromEdge(g12, DOWN), FadeIn(la), run_time=.5)
        self.at(A_("x6", .45), GrowFromEdge(g44, DOWN), Write(va), run_time=.5)
        self.at(A_("x6", .62), GrowFromEdge(g77, DOWN), FadeIn(lb), run_time=.6)
        self.at(A_("x6", .8), Write(vb), run_time=.4, sfx="ding", gain=.4)
        self.tail(Indicate(vb, scale_factor=1.2), FadeOut(dimR))
        self.finish()


# ================= sc11 三點回顧 =================
def sc10_end():
    c = cost(6)
    return dict(c=c)


class Sc11(Sheet5):
    SID = "sc11"
    END_BRAND = True

    def end_clear(self):
        tgt = self.pl.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.get_top()[1] + 2.5 - tgt.bodyg.get_bottom()[1]))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(self.pl, tgt, rate_func=rate_functions.ease_in_cubic), FadeOut(self.art)]

    def construct(self):
        A_ = self.A
        self.cam_set(S6, 14)
        self.add(road())
        b5 = base5()
        add_all(self, b5)
        e8 = sc08_end()
        add_all(self, e8)
        e10 = sc10_end()
        add_all(self, e10)
        # z1 拉到全景：先收掉小字，一道金光沿整條路流一次
        small = [x for top in self.mobjects for x in top.get_family() if isinstance(x, Text)]
        path = VMobject().set_points_as_corners([S1, S2, S3, S4, S5, S6]).set_stroke(GOLD, 14)
        path.transient = True
        self.at(A_("z1", .0), self.cam(PANO_C, PANO_W), *[x.animate.set_opacity(0) for x in small],
                Succession(Wait(1.0), ShowPassingFlash(path, time_width=.35)), run_time=2.2, rate_func=EASE)
        # 三點回顧：框 → 短線 → 下方寫字
        tgt = [VGroup(b5["c5a"], b5["prs"], b5["base_a"]), VGroup(b5["ta"], b5["tb"]), e10["c"][0]]
        labs = [("①", "只取最高 → 平手"), ("②", "期望值 → 拆開"), ("③", "每次都要表態")]
        ys = [S2[1] - 4.2, S4[1] - 3.9, S6[1] - 3.9]
        frames, links, items = [], [], []
        for k in range(3):
            fr = SurroundingRectangle(tgt[k], buff=.35, corner_radius=.3).set_stroke(TXT_STRONG, 4).set_fill(opacity=0)
            fr.overlap_ok = fr.dots_ok = True
            it = VGroup(B(labs[k][0], .17, GOLD), B(labs[k][1], .17, TXT_STRONG)).arrange(RIGHT, buff=.5)
            it.move_to(np.array([fr.get_x(), ys[k], 0]))
            ln = Line(fr.get_bottom(), it.get_top() + UP * .3).set_stroke(TXT_STRONG, 3)
            frames.append(fr), links.append(ln), items.append(it)
        sids = ["z2", "z3", "z4"]
        for k in range(3):
            prev = []
            if k:
                prev = [frames[k - 1].animate.set_stroke(opacity=.35), links[k - 1].animate.set_stroke(opacity=.35), items[k - 1].animate.set_opacity(.4)]
            self.at(A_(sids[k], .03), *prev, Create(frames[k]), run_time=.6, sfx="ding", gain=.4)
            self.at(A_(sids[k], .22), Create(links[k]), FadeIn(items[k], shift=UP * .3), run_time=.6)
            fl = frames[k].copy().set_stroke(GOLD, 8)
            fl.transient = True
            self.at(A_(sids[k], .52), ShowPassingFlash(fl, time_width=.4), run_time=.6)
            if k < 2:
                self.at(A_(sids[k], .7), Indicate(items[k], scale_factor=1.08), run_time=.4)
        self.at(A_("z4", .75), *[m.animate.set_stroke(opacity=1) for m in frames[:2] + links[:2]], *[it.animate.set_opacity(1) for it in items[:2]], run_time=.6)
        # z5 錘錘：完整文章在說明欄
        pc = np.array([9.3, .9, 0])
        top = self.camera.frame.get_top()[1] + 1.5
        pl = Plumb(1.4, top_y=top).place(pc + UP * 12)
        pl.set_mood("neutral")
        drop = [Transform(pl, pl.copy().place(pc), rate_func=rate_functions.ease_out_back)]
        art = VGroup(T("完整文章", .145, TXT_STRONG), T("在說明欄", .145, TXT_STRONG)).arrange(DOWN, buff=.3).move_to(np.array([14.2, .1, 0]))
        self.at(A_("z5", .0), *drop, run_time=.7)
        self.lipsync(pl)
        self.at(A_("z5", .3), FadeIn(art, shift=DOWN * .3), *pl.look(DOWN), run_time=.6)
        self.at(A_("z5", .55), *pl.hop(-.6), run_time=.45)
        self.at(A_("z5", .8), *pl.hop(-.6), run_time=.45)
        self.pl, self.art = pl, art
        self.finish()
