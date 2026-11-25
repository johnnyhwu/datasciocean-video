"""v004 Claude Code：sc06～sc10。大圖元件在 world.py，共用的 stage() 在 scenes_a.py。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa: E402,F401,F403
from scenes_a import ROWS, CARDS_C, CARDS_W, Sheet4, add_stage, person, stage  # noqa: E402

GATE_VC, GATE_VW = np.array([3.7, .5, 0]), 15.6
ALL_C, ALL_W = np.array([.97, .45, 0]), 19.4
WIDE_C, WIDE_W = np.array([.97, .25, 0]), 19.4
SCR_C, SCR_W = np.array([-5.2, -.25, 0]), 17.5
PANO_C, PANO_W = np.array([.95, .42, 0]), 19.6

FENCE_C, FENCE_WH = np.array([2.6, .55, 0]), (11.2, 6.8)
GAUGE_C = np.array([9.0, .25, 0])
PIPE_Y = 3.8
LIMIT_ROWS = 9


# ---------------- 小元件 ----------------
def check_tag(s, x, y=3.4, color=GOOD):
    t = T(s, .05, TXT)
    ck = T("✓", .05, color)
    g = VGroup(t, ck).arrange(RIGHT, buff=.12)
    box = RoundedRectangle(corner_radius=.1, width=g.width + .3, height=g.height + .22).set_fill(PANEL, .95).set_stroke(LINE, 2)
    g.move_to(box)
    out = VGroup(box, g).move_to(np.array([x, y, 0]))
    out.ck = ck
    return out


def pipeline(op=1.0):
    """開場那張流程圖，攤成一條多階段管線。"""
    names = ["規劃器", "執行器", "檢查器", "除錯器"]
    xs = [-4.2, -1.4, 1.4, 4.2]
    bx = VGroup(*[flow_box(n, np.array([x, PIPE_Y, 0]), TXT, .058, op) for n, x in zip(names, xs)])
    ar = VGroup(*[Arrow(bx[i].get_right(), bx[i + 1].get_left(), buff=.12, stroke_width=3.5, tip_length=.16).set_color(LINE) for i in range(3)])
    g = VGroup(ar, bx)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = True
    g.bx, g.ar = bx, ar
    return g


def gauge(c=GAUGE_C, v=0.0, op=1.0, s=1.3):
    """權限模式的旋鈕：半圓刻度（四段，不是只有開和關），指針位置 v 0→1。"""
    arc = Arc(radius=.62 * s, start_angle=PI, angle=-PI, arc_center=c).set_stroke(TXT, 3, op)
    ticks = VGroup()
    for k in range(4):
        a = PI - PI * (k + .5) / 4
        ticks.add(Line(c + .5 * s * np.array([np.cos(a), np.sin(a), 0]), c + .72 * s * np.array([np.cos(a), np.sin(a), 0])).set_stroke([GOOD, TEAL_L, "#E8C46A", "#E8A06A"][k], 5, op))
    a = PI - PI * (.125 + .75 * v)
    needle = Line(c, c + .55 * s * np.array([np.cos(a), np.sin(a), 0])).set_stroke(INK, 5, op)
    hub = Dot(c, radius=.07, color=INK).set_opacity(op)
    g = VGroup(arc, ticks, needle, hub)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    g.needle = needle
    return g


def fence(op=1.0):
    r = RoundedRectangle(corner_radius=.5, width=FENCE_WH[0], height=FENCE_WH[1]).move_to(FENCE_C)
    f = DashedVMobject(r, num_dashes=90, dashed_ratio=.6).set_stroke(GOOD, 4, op)
    lab = T("工作目錄", .054, GOOD).set_opacity(op).move_to(r.get_corner(UL) + np.array([1.15, -.42, 0]))
    g = VGroup(f, lab)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    for m in f.family_members_with_points():
        m.nocheck = True
    f.nocheck = True
    g.line, g.lab = f, lab
    return g


def folder(c, color=MUTED):
    body = RoundedRectangle(corner_radius=.06, width=.8, height=.56).set_fill(color, .25).set_stroke(color, 2.5).move_to(c)
    tab = RoundedRectangle(corner_radius=.04, width=.32, height=.14).set_fill(color, .5).set_stroke(color, 2).move_to(body.get_corner(UL) + np.array([.2, .05, 0]))
    return VGroup(tab, body)


def hook_icon(c, color=TEAL_L, s=1.0):
    stem = Line(c + UP * .3 * s, c + DOWN * .05 * s).set_stroke(color, 5)
    cup = Arc(radius=.16 * s, start_angle=PI, angle=PI, arc_center=c + DOWN * .05 * s).set_stroke(color, 5)
    barb = Line(c + np.array([-.16, -.05, 0]) * s, c + np.array([-.16, .08, 0]) * s).set_stroke(color, 5)
    return VGroup(stem, cup, barb)


def puff(c, r=.22):
    p_ = Circle(r).set_fill(MUTED, .55).set_stroke(width=0).move_to(c)
    p_.overlap_ok = True
    return p_


def sc05_end():
    d = stage(rows=7)
    return d


# ---------------- sc06：收費站 ----------------
class Sc06(Sheet4):
    SID = "sc06"

    def construct(self):
        A = self.A
        from scenes_a import TOOL_C, TOOL_W
        self.cam_set(TOOL_C, TOOL_W)
        d = sc05_end()
        add_stage(self, d)
        for m in [d["ball"], d["gate"], *d["ball"].family_members_with_points(), *d["gate"].family_members_with_points()]:
            m.nocheck = True
        G, ball = d["gate"], d["ball"]
        self.G, self.ball, self.tb, self.rows = G, ball, d["tb"], d["rows"]
        # g1 為什麼一定要開單
        scr = VGroup(d["stop"], d["rows"])
        self.at(A("g1", 0), self.cam(GATE_VC, GATE_VW), FadeOut(scr), run_time=1.2, rate_func=SINE)
        # g2 用說的：「我現在要去改檔案了」→ 飄過收費站，什麼都沒發生
        sp = speech("我要去改檔案了", np.array([-1.3, 2.85, 0]))
        self.at(A("g2", .1), FadeIn(sp, shift=UP * .2, scale=.7), run_time=.45)
        self.at(A("g2", .5), sp.animate.move_to(np.array([6.3, 2.85, 0])).set_opacity(.45), run_time=1.3, rate_func=rate_functions.ease_in_sine)
        # g3 一張明確的工具呼叫單＝乾淨的攔截點
        sl = slip("Edit", "calc.py").scale(.35).move_to(UP * .3)
        self.at(A("g3", .05), sl.animate.scale(1 / .35).move_to(P(90)), FadeOut(sp), run_time=.5, sfx="pop", gain=.3)
        self.at(A("g3", .25), run_slip(sl, 90, GATE_A + 42, run=1), run_time=.8)
        self.at(A("g3", .55), jolt(sl, .1), G.lamp.animate.set_fill("#E8C46A"), Highlight(G.booth, color=TXT_STRONG, scale_factor=1.08, inner=False), run_time=.6, sfx="click", gain=.4)
        # g4 檢查權限、記 log、觸發 Hook
        tags = [check_tag(s, x) for s, x in (("權限", 4.7), ("log", 6.4), ("Hook", 8.1))]
        for tg, f in zip(tags, (.3, .52, .74)):
            self.at(A("g4", f), FadeIn(tg, shift=DOWN * .2, scale=.8), run_time=.4, sfx="tick", gain=.35)
        # g5 每一輪都看得到、查得到 → 放行
        self.at(A("g5", .1), Transform(G.arm, gate(arm_up=1).arm), G.lamp.animate.set_fill(GOOD), Indicate(tags[1], color=TXT_STRONG, scale_factor=1.1), run_time=.5)
        self.at(A("g5", .45), run_slip(sl, GATE_A + 42, 0, run=1), Succession(Wait(1.2), AnimationGroup(Transform(G.arm, gate().arm), G.lamp.animate.set_fill(MUTED), run_time=1)), run_time=1.0)
        # g6 失敗只是另一種觀察
        self.at(A("g6", 0), FadeOut(sl, scale=.5), FadeOut(VGroup(*tags)), FadeIn(scr), self.cam(WORK_C, WORK_W), run_time=1.1, rate_func=SINE)
        # g7 測試失敗、語法錯誤、權限被拒絕 → 都不會讓迴圈停下來
        errs = [chip(s, "err") for s in ("測試失敗", "語法錯誤", "權限被拒絕")]
        for e, x in zip(errs, (3.0, 0, -3.0)):
            e.move_to(np.array([x, -2.9, 0]))
        for e, f in zip(errs, (.1, .38, .66)):
            self.at(A("g7", f), FadeIn(e, scale=.6), run_time=.35, sfx="thud", gain=.35)
        # g8 只會變成下一輪的輸入，讓模型重新規劃
        self.at(A("g8", .05), *[e.animate.move_to(LOOP_C + LEFT * .2).scale(.2).set_opacity(0) for e in errs],
                ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.4), run_time=1.0, sfx="swoosh", gain=.3)
        self.at(A("g8", .6), ShowPassingFlash(track_glow(GOLD, 8), time_width=.35), run_time=1.3, rate_func=SINE)
        # g9 開場那張流程圖：一條多階段管線
        pp = pipeline()
        self.at(A("g9", 0), self.cam(CARDS_C, CARDS_W), Succession(Wait(.5), LaggedStart(*[FadeIn(b, shift=DOWN * .2) for b in pp.bx], lag_ratio=.2)), run_time=1.6, rate_func=SINE)
        self.at(A("g9", .55), LaggedStart(*[GrowArrow(a) for a in pp.ar], lag_ratio=.3), run_time=.8)
        # g10 遇到意外就顯得脆弱：卡住、冒煙
        bang = chip("意外", "err").next_to(pp.bx[1], UP, buff=.25)
        self.at(A("g10", .05), FadeIn(bang, shift=DOWN * .3), run_time=.35, sfx="thud", gain=.5)
        smoke = VGroup(*[puff(pp.bx[1].get_top() + np.array([dx, .2, 0]), r) for dx, r in ((-.3, .18), (.1, .24), (.4, .16))])
        self.at(A("g10", .3), Wiggle(pp.bx[1], scale_value=1.06, n_wiggles=6), *[a.animate.set_color(MUTED).set_opacity(.35) for a in pp.ar[1:]],
                *[b.animate.set_opacity(.35) for b in pp.bx[2:]], run_time=.7)
        self.at(A("g10", .7), LaggedStart(*[FadeIn(p, shift=UP * .35, scale=.5) for p in smoke], lag_ratio=.3), run_time=.8)
        # g11 能從錯誤中恢復的單一迴圈，比較穩健
        hero = slip("Bash", "pytest").move_to(P(90))
        self.at(A("g11", .1), FadeIn(hero, scale=.6), run_time=.35)
        self.at(A("g11", .3), MoveAlongPath(hero, Arc(radius=R, start_angle=PI / 2, angle=-TAU, arc_center=LOOP_C)), ShowPassingFlash(track_glow(GOLD, 9), time_width=.35), run_time=2.0, rate_func=SINE, sfx="swoosh", gain=.35)
        self.at(A("g11", .9), FadeOut(hero, scale=.5), run_time=.4)
        self.finish()


def sc06_end():
    d = stage(rows=7)
    pp = pipeline()
    pp.ar[1:].set_color(MUTED).set_opacity(.35)
    pp.bx[2:].set_opacity(.35)
    bang = chip("意外", "err").next_to(pp.bx[1], UP, buff=.25)
    smoke = VGroup(*[puff(pp.bx[1].get_top() + np.array([dx, .2, 0]), r) for dx, r in ((-.3, .18), (.1, .24), (.4, .16))])
    d["pipe"] = VGroup(pp, bang, smoke)
    return d


# ---------------- sc07：犯錯要便宜 ----------------
class Sc07(Sheet4):
    SID = "sc07"

    def construct(self):
        A = self.A
        self.cam_set(CARDS_C, CARDS_W)
        d = sc06_end()
        add_stage(self, d)
        self.add(d["pipe"])
        G, ball = d["gate"], d["ball"]
        self.G, self.ball, self.tb, self.rows = G, ball, d["tb"], d["rows"]
        for m in [ball, *ball.family_members_with_points()]:
            m.nocheck = True
        # s1 沒人看著、能執行任意指令的 Agent
        self.at(A("s1", 0), FadeOut(d["pipe"], shift=UP * .3), self.cam(WORK_C, WORK_W), run_time=1.2, rate_func=SINE)
        hero = slip("Bash").move_to(P(90))
        self.at(A("s1", .45), FadeIn(hero, scale=.6), run_time=.35)
        self.at(A("s1", .6), MoveAlongPath(hero, Arc(radius=R, start_angle=PI / 2, angle=-TAU, arc_center=LOOP_C)), run_time=1.4, rate_func=SINE)
        # s2 安全不能只靠模型每次都猜對
        qs = VGroup(*[T("？", .06, TXT_STRONG).move_to(LOOP_C + np.array([x, 1.35, 0])) for x in (-.5, 0, .5)])
        self.at(A("s2", .2), FadeOut(hero), LaggedStart(*[FadeIn(q, shift=UP * .2) for q in qs], lag_ratio=.3), ball.animate(rate_func=there_and_back).rotate(.12), run_time=.9)
        self.at(A("s2", .65), Wiggle(qs, scale_value=1.15), run_time=.9)
        # s3 讓犯錯便宜、可以挽回
        undo = VGroup(Arc(radius=.55, start_angle=PI * .15, angle=PI * 1.4, arc_center=LOOP_C + UP * 1.55).set_stroke(GOOD, 7))
        undo.add(Triangle().scale(.17).set_fill(GOOD, 1).set_stroke(width=0).rotate(-PI / 2 + PI * .15).move_to(undo[0].get_end()))
        self.at(A("s3", .12), FadeOut(qs), Create(undo), run_time=.8, sfx="swoosh", gain=.3)
        self.at(A("s3", .6), Rotate(undo, angle=PI / 3, rate_func=there_and_back), run_time=.8)
        # s5 權限是漸進式的
        gg = gauge(v=0.0, s=1.0)
        scr = VGroup(d["stop"], d["rows"])
        self.at(A("s5", .05), FadeOut(undo), FadeOut(scr), self.cam(GATE_VC, GATE_VW), run_time=1.0, rate_func=SINE)
        self.at(A("s5", .35), Create(gg[0]), LaggedStart(*[Create(t) for t in gg[1]], lag_ratio=.25), FadeIn(gg[2:]), run_time=1.0)
        self.at(A("s5", .75), Rotate(gg.needle, angle=-PI * .75, about_point=GAUGE_C, rate_func=there_and_back), run_time=1.2)
        # s6 由使用者選，不是模型
        mode = VGroup(T("權限", .054, TXT_STRONG), T("模式", .054, TXT_STRONG)).arrange(DOWN, buff=.06).next_to(gg, UP, buff=.15)
        user = person(np.array([9.0, 2.6, 0]), USER)
        ulab = T("使用者", .054, USER).next_to(user, UP, buff=.1)
        self.at(A("s6", .05), Write(mode), run_time=.5)
        self.at(A("s6", .4), FadeIn(VGroup(user, ulab), shift=LEFT * .3), run_time=.45)
        self.at(A("s6", .62), Rotate(gg.needle, angle=-PI * .375, about_point=GAUGE_C), run_time=.6, sfx="knob", gain=.45)
        self.at(A("s6", .85), ball.animate(rate_func=there_and_back).shift(UP * .12), run_time=.4)
        # s7 要不要問你，看能不能挽回
        self.at(A("s7", .2), LaggedStart(*[Indicate(t_, color=TXT_STRONG, scale_factor=1.3) for t_ in gg[1]], lag_ratio=.2), run_time=1.0)
        self.at(A("s7", .6), Rotate(gg.needle, angle=PI * .3, about_point=GAUGE_C, rate_func=there_and_back), run_time=1.0)
        # s8 讀檔、跑測試自動放行
        self.at(A("s8", .05), FadeIn(scr), self.cam(ALL_C, ALL_W), run_time=.9, rate_func=SINE)
        for f, tool, arg in ((.3, "Read", "calc.py"), (.62, "Bash", "pytest")):
            sl = slip(tool, arg).move_to(P(90))
            self.at(A("s8", f), FadeIn(sl, scale=.6), G.lamp.animate.set_fill(GOOD), Transform(G.arm, gate(arm_up=1).arm), run_time=.3)
            self.at(A("s8", f) + .32, run_slip(sl, 90, -40, run=1), run_time=.9)
            sl.transient = True
            self.at(A("s8", f) + 1.25, FadeOut(sl, scale=.5), run_time=.25)
        self.at(A("s8", .98), Transform(G.arm, gate().arm), G.lamp.animate.set_fill(MUTED), run_time=.3)
        # s10 需要確認的動作先問你；不核准 → 拒絕也接回紙卷
        rm = slip("Bash", "刪除檔案").move_to(P(90))
        self.at(A("s10", .02), FadeIn(rm, scale=.6), run_time=.3)
        self.at(A("s10", .1), run_slip(rm, 90, GATE_A + 42, run=1), G.lamp.animate.set_fill("#E8C46A"), run_time=.6)
        ask = speech("可以嗎？", np.array([6.9, 3.2, 0]), .054)
        self.at(A("s10", .25), FadeIn(ask, scale=.7), run_time=.35, sfx="pop", gain=.35)
        no = cross_mark(MUTED, .26).move_to(ask)
        no.cross_ok = no.overlap_ok = True
        self.at(A("s10", .42), Create(no), Wiggle(user), run_time=.5, sfx="scratch", gain=.4)
        rej = chip("拒絕：不刪", "obs")
        rej.move_to(rm)
        for m in rej.family_members_with_points():
            m.overlap_ok = True
        self.at(A("s10", .58), FadeOut(VGroup(ask, no)), ReplacementTransform(rm, rej), G.lamp.animate.set_fill(MUTED), run_time=.4)
        r7 = row("拒絕：不刪", "obs", 7)
        for m in [*rm.get_family(), *r7.get_family(), *rej.get_family()]:
            m.overlap_ok = True
        for m in rej.get_family():
            m.cross_ok = True
        rej.transient = True
        self.at(A("s10", .7), ReplacementTransform(rej, r7), run_time=.8, sfx="slide", gain=.3)
        # s11 另一道防線：受限的環境
        fc = fence()
        self.at(A("s11", .05), self.cam(WIDE_C, WIDE_W), run_time=1.1, rate_func=SINE)
        self.at(A("s11", .45), Create(fc.line), run_time=1.2)
        self.at(A("s11", .8), Write(fc.lab), run_time=.5)
        # s12 錯的指令也碰不到工作目錄以外
        outs = VGroup(folder(np.array([8.65, -1.5, 0])), folder(np.array([9.35, -1.5, 0])), folder(np.array([9.0, -2.2, 0])))
        self.at(A("s12", .02), FadeIn(outs, shift=LEFT * .2), run_time=.45)
        boom_c = np.array([3.1, -2.55, 0])
        star = Star(n=9, outer_radius=.36, inner_radius=.18).set_fill(BAD, .9).set_stroke(width=0).move_to(boom_c)
        star.overlap_ok = True
        star.transient = True
        self.at(A("s12", .25), GrowFromCenter(star), run_time=.35, sfx="thud", gain=.55)
        edge_x = FENCE_C[0] + FENCE_WH[0] / 2 - .25
        wave = VGroup(*[Arc(radius=.32, start_angle=-PI / 5, angle=2 * PI / 5).set_stroke(BAD, 5).move_to(boom_c + RIGHT * (.3 + .28 * k)) for k in range(3)])
        for m in [wave, *wave]:
            m.overlap_ok = m.cross_ok = True
            m.transient = True
        self.at(A("s12", .32), FadeIn(wave), run_time=.15)
        self.at(A("s12", .4), wave.animate.shift(RIGHT * (edge_x - wave.get_right()[0])), FadeOut(star), run_time=.8, rate_func=rate_functions.ease_in_cubic)
        self.at(A("s12", .65), FadeOut(wave), Indicate(fc.line, color=GOOD, scale_factor=1.0), run_time=.6)
        self.at(A("s12", .85), Indicate(outs, color=TXT_STRONG, scale_factor=1.06), run_time=.6)
        # s13 權限和執行邊界：兩道獨立的防線
        self.at(A("s13", .2), Highlight(gg, color=TXT_STRONG, scale_factor=1.2, inner=False), run_time=.7)
        self.at(A("s13", .45), ShowPassingFlash(fc.line.copy().set_stroke(GOOD, 8), time_width=.4), run_time=1.1)
        self.at(A("s13", .85), FadeOut(VGroup(user, ulab, outs, gg, mode)), run_time=.5)
        self.finish()


def sc07_end():
    d = stage(rows=8)
    d["rows"] = VGroup(*[row(t, k, i) for i, (t, k) in enumerate(ROWS)], row("拒絕：不刪", "obs", 7))
    d["fence"] = fence()
    return d


def add_d(scene, d):
    add_stage(scene, d)
    for k in ("gauge", "fence"):
        if k in d:
            scene.add(d[k])


# ---------------- sc08：紙卷滿了 ----------------
MORE = [("Read config", "obs"), ("Grep 結果", "obs")]


def mini_loop(c, r=.75):
    ring = Circle(r).set_stroke(LINE, 3).move_to(c)
    ball = glass_model(c, .38)
    ball.lab.set_opacity(0)
    g = VGroup(ring, ball)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    return g


class Sc08(Sheet4):
    SID = "sc08"

    def construct(self):
        A = self.A
        self.cam_set(WIDE_C, WIDE_W)
        d = sc07_end()
        add_d(self, d)
        for m in [d["gate"], *d["gate"].family_members_with_points(), d["tb"], *d["tb"].family_members_with_points()]:
            m.nocheck = True
        rows = d["rows"]
        # c1 每跑一圈，紙卷就長一截
        self.at(A("c1", 0), self.cam(SCR_C, SCR_W), FadeOut(d["fence"]), run_time=1.1, rate_func=SINE)
        new = [row(t, k, 8 + i) for i, (t, k) in enumerate(MORE)]
        self.at(A("c1", .65), FadeIn(new[0], shift=DOWN * .2), run_time=.4, sfx="slide", gain=.25)
        # c2 context window 有上限
        y_lim = row_y(LIMIT_ROWS) - ROW_H / 2 + .5
        lim = DashedLine(np.array([SCROLL_X - SCROLL_W / 2 - .35, y_lim, 0]), np.array([SCROLL_X + SCROLL_W / 2 + .35, y_lim, 0]), dash_length=.15).set_stroke(BAD, 4)
        lim_l = T("上限", .05, BAD).next_to(lim, LEFT, buff=.15)
        lim.overlap_ok = lim.cross_ok = True
        self.at(A("c2", .3), Create(lim), FadeIn(lim_l), run_time=.7)
        self.at(A("c2", .7), FadeIn(new[1], shift=DOWN * .2), run_time=.4, sfx="slide", gain=.25)
        allr = VGroup(*rows, *new)
        self.at(A("c2", .9), Wiggle(allr[-1], scale_value=1.05), run_time=.5)
        # c3 不盲目截掉：較早的對話摘要成精簡的版本
        old = VGroup(*allr[1:8])
        summ = row("摘要：修測試", "sum", 1)
        self.at(A("c3", .22), *[r.animate.move_to(summ).scale(np.array([1, .2, 1])).set_opacity(0) for r in old], run_time=1.4, rate_func=SINE, sfx="swoosh", gain=.35)
        self.at(A("c3", .55), FadeIn(summ, scale=1.2), *[r.animate.move_to(np.array([SCROLL_X, row_y(2 + i), 0])) for i, r in enumerate(new)], run_time=.8)
        self.remove(*old)
        self.at(A("c3", .85), FadeOut(VGroup(lim, lim_l)), run_time=.4)
        lst = VGroup(allr[0], summ, *new)
        # c4 對話接著走
        r4 = row("Edit config.py", "obs", 4)
        self.at(A("c4", .2), FadeIn(r4, shift=DOWN * .2), run_time=.4, sfx="slide", gain=.25)
        self.at(A("c4", .55), ShowPassingFlash(track_glow(GOLD, 7), time_width=.35), run_time=1.3, rate_func=SINE)
        lst.add(r4)
        # c5 最前面釘著 CLAUDE.md
        pin = row("CLAUDE.md", "pin", 0)
        self.at(A("c5", .3), *[r.animate.shift(DOWN * ROW_H) for r in lst], run_time=.6)
        self.at(A("c5", .5), FadeIn(pin, shift=DOWN * .4), run_time=.5, sfx="click", gain=.4)
        tack = Dot(pin.box.get_left() + RIGHT * .12, radius=.08, color=BAD)
        self.at(A("c5", .75), GrowFromCenter(tack), run_time=.3)
        # c6 不屬於任何一次對話，大家共用
        team = VGroup(*[person(np.array([SCROLL_X - SCROLL_W / 2 - 1.0, 1.6 - .95 * k, 0]), USER).scale(.9) for k in range(3)])
        self.at(A("c6", .3), LaggedStart(*[FadeIn(p, shift=RIGHT * .2) for p in team], lag_ratio=.25), run_time=.8)
        links = VGroup(*[Line(p.get_right() + RIGHT * .1, pin.box.get_left() + LEFT * .05).set_stroke(USER, 2.5, .7) for p in team])
        self.at(A("c6", .65), *[Create(l_) for l_ in links], run_time=.5)
        # c7–c8 Subagent：大範圍搜尋交給分身
        self.at(A("c7", 0), FadeOut(VGroup(team, links)), run_time=.4)
        mc = np.array([SCROLL_X - SCROLL_W / 2 - 2.1, 1.0, 0])
        ml = mini_loop(mc)
        lab_s = T("Subagent（Task）", .05, TOOL).next_to(ml, UP, buff=.15)
        self.at(A("c7", .4), FadeIn(ml, scale=.5), Write(lab_s), run_time=.7, sfx="pop", gain=.35)
        mess = VGroup(*[Rectangle(width=1.5, height=.22).set_fill(MUTED, .5).set_stroke(width=0) for _ in range(9)]).arrange(DOWN, buff=.06)
        mess.next_to(ml, DOWN, buff=.3)
        task_sl = slip("Task").move_to(LOOP_C)
        task_sl.transient = True
        for m in task_sl.get_family():
            m.overlap_ok = m.cross_ok = True
        self.at(A("c8", .1), FadeIn(task_sl, scale=.5), run_time=.3)
        self.at(A("c8", .25), task_sl.animate.move_to(mc).scale(.4).set_opacity(0), run_time=1.0, rate_func=SINE)
        self.at(A("c8", .6), Rotate(ml[0], angle=-TAU, about_point=mc), Indicate(ml[1], color=TXT_STRONG, scale_factor=1.15), run_time=1.0)
        self.at(A("c9", .02), LaggedStart(*[FadeIn(m_, shift=DOWN * .1) for m_ in mess], lag_ratio=.12), run_time=1.2)
        # c9 雜亂的輸出留在分身那裡；c9b 只送回摘要
        self.at(A("c9", .62), Indicate(mess, color=TXT_STRONG, scale_factor=1.04), run_time=.7)
        back = chip("分身的摘要", "sum").move_to(ml)
        for m in back.family_members_with_points():
            m.overlap_ok = True
        r5 = row("分身的摘要", "sum", 6)
        self.at(A("c9b", .1), FadeIn(back, scale=.6), run_time=.35)
        self.at(A("c9b", .35), back.animate.move_to(r5.get_left() + LEFT * (back.width / 2 + .3)), run_time=.6, sfx="slide", gain=.3)
        self.at(A("c9b", .65), ReplacementTransform(back, r5), run_time=.5)
        lst.add(r5)
        # c10 長度變成鋸齒狀
        self.at(A("c10", 0), FadeOut(VGroup(ml, lab_s, mess)), run_time=.5)
        axes, ylab, poly, cap = sawtooth()
        self.at(A("c10", .3), Create(axes), FadeIn(ylab), Create(cap), run_time=.6)
        self.at(A("c10", .55), Create(poly), run_time=1.6, rate_func=linear)
        self.at(A("c10b", .45), ShowPassingFlash(poly.copy().set_stroke(TXT_STRONG, 8), time_width=.4), run_time=1.3)
        self.finish()


def sawtooth():
    ax_o = np.array([SCROLL_X - SCROLL_W / 2 - 5.0, -2.5, 0])
    axes = VGroup(Arrow(ax_o, ax_o + RIGHT * 3.7, buff=0, stroke_width=4, tip_length=.16), Arrow(ax_o, ax_o + UP * 3.6, buff=0, stroke_width=4, tip_length=.16)).set_color(LINE)
    ylab = T("長度", .05, TXT).next_to(axes[1], UP, buff=.1)
    pts = [(0, 1), (.5, 4), (1.0, 7), (1.5, 9), (1.5, 3.5), (2.0, 6), (2.5, 8.6), (2.5, 4), (3.2, 6.5)]
    poly = VMobject().set_points_as_corners([ax_o + np.array([.15 + x, .32 * y, 0]) for x, y in pts]).set_stroke(TEAL_L, 6)
    cap = DashedLine(ax_o + np.array([0, .32 * 9.3, 0]), ax_o + np.array([3.6, .32 * 9.3, 0]), dash_length=.14).set_stroke(BAD, 3)
    for m in (axes, poly, cap):
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    return axes, ylab, poly, cap


def sc08_rows():
    ents = [("CLAUDE.md", "pin"), ROWS[0], ("摘要：修測試", "sum"), *MORE, ("Edit config.py", "obs"), ("分身的摘要", "sum")]
    return VGroup(*[row(t, k, i) for i, (t, k) in enumerate(ents)])


def sc08_end():
    d = sc07_end()
    d["rows"] = sc08_rows()
    pin = d["rows"][0]
    d["tack"] = Dot(pin.box.get_left() + RIGHT * .12, radius=.08, color=BAD)
    del d["fence"]
    d["chart"] = VGroup(*sawtooth())
    return d


# ---------------- sc09：三個配件 ----------------
SHELF_C = np.array([-2.55, 3.35, 0])  # 書架底板的中心
HOOK_PTS = [GATE_BOOTH + UP * 1.15, LOOP_C + DOWN * (R + TRACK_W / 2 + .45), np.array([SCROLL_X - 1.2, 3.75, 0])]
MCP_X = 8.6
SKILL_VC, SKILL_VW = np.array([-4.45, .82, 0]), 16.0
PAGE_C = np.array([SCROLL_X, .9, 0])
HOOK_VC, HOOK_VW = PANO_C, PANO_W
MCP_VC, MCP_VW = np.array([5.2, .45, 0]), 15.5
RECAP_C = np.array([.8, -.2, 0])


def skill_shelf():
    board = Line(SHELF_C + LEFT * 1.75, SHELF_C + RIGHT * 1.75).set_stroke("#B89A67", 6)
    books = VGroup()
    for k in range(5):
        b = RoundedRectangle(corner_radius=.04, width=.5, height=.68).set_fill(["#6F8DA6", "#7C98AE", "#6A8799", "#8AA3B5", "#748FA0"][k], .55).set_stroke(TXT, 2)
        b.move_to(SHELF_C + RIGHT * (-1.4 + .7 * k) + UP * .37)
        line_ = Line(b.get_top() + DOWN * .2 + LEFT * .14, b.get_top() + DOWN * .2 + RIGHT * .14).set_stroke(INK, 3)
        books.add(VGroup(b, line_))
    lab = T("Skill", .054, TXT_STRONG).next_to(books, RIGHT, buff=.25)
    g = VGroup(board, books, lab)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = True
    g.books, g.lab = books, lab
    return g


def mcp_plugs():
    names = ["GitHub", "資料庫", "API"]
    g = VGroup()
    for k, n in enumerate(names):
        box = flow_box(n, np.array([MCP_X, .55 - 1.0 * k, 0]), TEAL_L, .054)
        g.add(box)
    lab = T("MCP", .055, TEAL_L).next_to(g, UP, buff=.25)
    out = VGroup(lab, g)
    out.plugs, out.lab = g, lab
    return out


class Sc09(Sheet4):
    SID = "sc09"

    def construct(self):
        A = self.A
        self.cam_set(SCR_C, SCR_W)
        d = sc08_end()
        add_d(self, d)
        d["chart"].transient = True
        self.add(d["tack"], d["chart"])
        G, ball, tb = d["gate"], d["ball"], d["tb"]
        for m in [G, *G.family_members_with_points(), tb, *tb.family_members_with_points()]:
            m.nocheck = True
        self.at(.01, Wait(.01), run_time=.05)
        for m in [G, *G.family_members_with_points(), tb, *tb.family_members_with_points()]:
            m.nocheck = False
        # e1 凍結的模型＋固定的工具，還是太死板
        self.at(A("e1", 0), self.cam(PANO_C, PANO_W), FadeOut(d["chart"]), run_time=1.3, rate_func=SINE)
        self.at(A("e1", .55), Highlight(ball, color=TXT_STRONG, scale_factor=1.06, inner=False), Highlight(tb, color=TXT_STRONG, scale_factor=1.03, inner=False), run_time=.8)
        # e2 三個擴充點
        self.at(A("e2", .3), ShowPassingFlash(track_glow(TEAL_L, 8), time_width=.4), run_time=1.2, rate_func=SINE)
        # e3 Skill：一個資料夾，裝著說明（鏡頭推到書架）
        sh = skill_shelf()
        booth = [m for m in G.family_members_with_points()]
        for m in [G, *booth]:
            m.nocheck = True
        self.at(A("e3", 0), self.cam(SKILL_VC, SKILL_VW), FadeOut(d["rows"]), FadeOut(d["tack"]), run_time=1.1, rate_func=SINE)
        self.at(A("e3", .2), FadeIn(sh.lab), Create(sh[0]), LaggedStart(*[FadeIn(b, shift=DOWN * .2) for b in sh.books], lag_ratio=.15), run_time=1.1)
        self.at(A("e3", .75), LaggedStart(*[Indicate(b, color=TXT_STRONG, scale_factor=1.1) for b in sh.books], lag_ratio=.15), run_time=1.0)
        # e4 一開始只看得到一行描述；e4b 要用的那一本才展開成整份說明
        self.at(A("e4", .3), LaggedStart(*[Indicate(b[1], color=TXT_STRONG, scale_factor=1.5) for b in sh.books], lag_ratio=.12), run_time=1.0)
        pick = sh.books[2]
        page = VGroup(RoundedRectangle(corner_radius=.08, width=2.0, height=2.3).set_fill(PANEL, 1).set_stroke(TXT_STRONG, 2.5),
                      *[Line(LEFT * .7, RIGHT * (.7 - .3 * (q % 2))).set_stroke(TXT, 3) for q in range(6)])
        page[1:].arrange(DOWN, buff=.22, aligned_edge=LEFT).move_to(page[0])
        page.move_to(PAGE_C)
        for m in page.get_family():
            m.overlap_ok = True
        self.at(A("e4b", .02), Indicate(pick, color=TXT_STRONG, scale_factor=1.12), run_time=.5)
        self.at(A("e4b", .2), TransformFromCopy(pick, page), run_time=.9, sfx="slide", gain=.3)
        doc = row("Skill：完整說明", "pin", 0)
        self.at(A("e4b", .6), ReplacementTransform(page, doc), run_time=.9)
        # e5 漸進式揭露
        prog = T("漸進式揭露", .055, TXT_STRONG).move_to(PAGE_C)
        self.at(A("e5", .25), Write(prog), run_time=.7)
        self.at(A("e5", .55), Indicate(doc, color=TXT_STRONG, scale_factor=1.06), run_time=.6)
        self.at(A("e5", .85), FadeOut(prog), FadeOut(doc), run_time=.4)
        # e6 Hook：固定時間點執行的 shell 指令（拉回全景看三個時間點）
        self.at(A("e6", 0), self.cam(PANO_C, PANO_W), FadeIn(d["rows"]), FadeIn(d["tack"]), run_time=1.1, rate_func=SINE)
        for m in [G, *booth]:
            m.nocheck = False
        hk = [hook_icon(p_) for p_ in HOOK_PTS]
        hlab = T("Hook", .055, TEAL_L).next_to(hk[0], LEFT, buff=.15)
        for m in VGroup(*hk).get_family():
            m.cross_ok = True
        self.at(A("e6", .4), Create(hk[0]), Write(hlab), run_time=.7)
        # e6b 工具執行前、回覆完成後、開工時
        hl = [T("動手前", .054, TEAL_L).next_to(hk[0], RIGHT, buff=.15), T("回覆後", .054, TEAL_L).next_to(hk[1], RIGHT, buff=.12),
              T("開工", .054, TEAL_L).next_to(hk[2], RIGHT, buff=.12)]
        for h, lb, f in zip(hk, hl, (.05, .38, .7)):
            self.at(A("e6b", f), Create(h) if h is not hk[0] else Indicate(h, color=TXT_STRONG), FadeIn(lb, shift=DOWN * .1), run_time=.45, sfx="tick", gain=.3)
        # e7 一般的程式碼，不是模型（鏡頭推到收費站上方的 Hook）
        self.at(A("e7", .55), Indicate(hk[0], color=TXT_STRONG, scale_factor=1.4), run_time=.7)
        self.at(A("e7b", .3), Wiggle(VGroup(hk[0], hlab), scale_value=1.15), run_time=.9)
        # e8 擋下受保護路徑的寫入、編輯後自動排版
        bad = slip("Write", "受保護路徑").move_to(P(90))
        self.at(A("e8", .05), FadeIn(bad, scale=.6), run_time=.3)
        self.at(A("e8", .15), run_slip(bad, 90, GATE_A + 42, run=1), run_time=.6)
        stop_x = cross_mark(BAD, .3).move_to(bad)
        stop_x.cross_ok = stop_x.overlap_ok = True
        bad.transient = stop_x.transient = True
        self.at(A("e8", .3), Create(stop_x), hk[0].animate.scale(1.8), Flash(bad.get_center(), color=BAD, line_length=.35, num_lines=10, flash_radius=.9), run_time=.4, sfx="thud", gain=.5)
        self.at(A("e8", .45), VGroup(bad, stop_x).animate.shift(LEFT * 1.6 + UP * 1.0).rotate(.9).set_opacity(0), hk[0].animate.scale(1 / 1.8), run_time=.9, rate_func=rate_functions.ease_out_cubic)
        self.remove(bad, stop_x)
        ed = slip("Edit", "calc.py").move_to(P(25))
        self.at(A("e8", .7), FadeIn(ed, scale=.6), run_time=.3)
        spark = VGroup(*[Line(ORIGIN, .3 * np.array([np.cos(a), np.sin(a), 0])).shift(ed.get_center() + .5 * np.array([np.cos(a), np.sin(a), 0])) .set_stroke(GOOD, 4) for a in np.linspace(0, TAU, 8, endpoint=False)])
        ed.transient = True
        self.at(A("e8", .85), ShowPassingFlash(spark, time_width=.6), FadeOut(ed), run_time=.6)
        # e10 MCP：共通介面接上 GitHub、資料庫、API（鏡頭推到工具箱右邊）
        mp = mcp_plugs()
        self.at(A("e10", 0), self.cam(MCP_VC, MCP_VW), FadeOut(VGroup(*hk, hlab, sh, *hl)), run_time=1.1, rate_func=SINE)
        self.at(A("e10", .25), Write(mp.lab), run_time=.5)
        for b, f in zip(mp.plugs, (.5, .66, .82)):
            self.at(A("e10", f), FadeIn(b, shift=LEFT * .4), run_time=.35, sfx="click", gain=.3)
        # e11 每個 server 宣告工具；e11b 和內建工具一樣交給模型
        self.at(A("e11", .3), LaggedStart(*[Highlight(b, color=TXT_STRONG, scale_factor=1.12, inner=False) for b in mp.plugs], lag_ratio=.3), run_time=1.0)
        extra = VGroup(*[icon_globe(np.array([TOOL_X - 1.0 + .7 * k, tool_y(4) - .78, 0]), .45, TOOL) for k in range(3)])
        self.at(A("e11b", .05), *[TransformFromCopy(a_, b_) for a_, b_ in zip(mp.plugs, extra)], run_time=1.0, sfx="slide", gain=.3)
        xlab = T("＋MCP 工具", .052, TOOL).next_to(extra, RIGHT, buff=.2)
        self.at(A("e11b", .35), Indicate(extra, color=TXT_STRONG, scale_factor=1.1), FadeIn(xlab, shift=LEFT * .1), run_time=.6)
        self.at(A("e11b", .55), self.cam(PANO_C, PANO_W), run_time=1.2, rate_func=SINE)
        self.at(A("e11b", .86), Indicate(ball, color=TXT_STRONG, scale_factor=1.05), run_time=.6)
        self.finish()


def sc09_end():
    d = sc08_end()
    extra = VGroup(*[icon_globe(np.array([TOOL_X - 1.0 + .7 * k, tool_y(4) - .78, 0]), .45, TOOL) for k in range(3)])
    d["ext"] = VGroup(mcp_plugs(), extra, T("＋MCP 工具", .052, TOOL).next_to(extra, RIGHT, buff=.2))
    return d


# ---------------- sc10：三點回顧 ----------------
class Sc10(Sheet4):
    SID = "sc10"
    END_BRAND = True

    def end_clear(self):
        tgt = self.pl.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.get_top()[1] + 1.2 - tgt.bodyg.get_bottom()[1]))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(self.pl, tgt, rate_func=rate_functions.ease_in_cubic), FadeOut(self.art)]

    def construct(self):
        A = self.A
        self.cam_set(PANO_C, PANO_W)
        d = sc09_end()
        add_d(self, d)
        self.add(d["tack"], d["ext"])
        trk, G, ball, rows = d["trk"], d["gate"], d["ball"], d["rows"]
        # r1 把整條跑道再看一次：收掉配件，只留迴圈、收費站、紙卷
        ghost = flowchart(op=.35, extra=False)
        for m in [ghost, *ghost.family_members_with_points()]:
            m.transient = True
        self.at(A("r1", .02), self.cam(RECAP_C, PANO_W), FadeOut(d["ext"]), ShowPassingFlash(track_glow(GOLD, 9), time_width=.4), run_time=1.1, rate_func=SINE, sfx="swoosh", gain=.3)
        self.at(A("r1", .45), FadeIn(ghost, rate_func=there_and_back_with_pause), run_time=1.3)
        self.remove(ghost)
        def dim(ms, op=.35):
            return [m.animate.set_stroke(opacity=op) for m in ms]
        RY = -3.7
        def item(n, s_, x, y=RY):
            g = VGroup(T(n, .07, GOLD), T(s_, .07, TXT_STRONG)).arrange(RIGHT, buff=.2)
            return g.move_to(np.array([x, y, 0]), aligned_edge=LEFT)
        # r2 ① 一個迴圈
        f1 = Circle(R + TRACK_W / 2 + .15).move_to(LOOP_C).set_stroke(TXT_STRONG, 2.2)
        f1.overlap_ok = f1.dots_ok = True
        i1 = item("①", "一個迴圈", -7.6, -2.6)
        self.at(A("r2", .05), Create(f1), run_time=.6, sfx="ding", gain=.35)
        self.at(A("r2", .3), FadeIn(i1, shift=UP * .15), run_time=.5)
        self.at(A("r2", .65), ShowPassingFlash(track_glow(GOLD, 8), time_width=.35), run_time=1.2, rate_func=SINE)
        # r3 ② 開單才能動手；r4 犯錯也只是輸入
        f2 = recap_frame(G, buff=.15)
        i2 = item("②", "開單才能動手", -7.6, -3.25)
        self.at(A("r3", .05), *dim([f1]), Create(f2), run_time=.6, sfx="ding", gain=.35)
        self.at(A("r3", .3), FadeIn(i2, shift=UP * .15), run_time=.5)
        e = chip("FAILED", "err").move_to(LOOP_C + DOWN * 1.55)
        self.at(A("r4", .1), FadeIn(e, scale=.6), run_time=.3)
        self.at(A("r4", .35), e.animate.move_to(LOOP_C).scale(.2).set_opacity(0), ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.4), run_time=.9)
        # r5 ③ 紙卷會被整理
        f3 = recap_frame(rows, buff=.15)
        i3 = item("③", "紙卷會整理", -7.6, -3.9)
        self.at(A("r5", .05), *dim([f2]), Create(f3), run_time=.6, sfx="ding", gain=.35)
        self.at(A("r5", .3), FadeIn(i3, shift=UP * .15), run_time=.5)
        self.at(A("r5", .8), *dim([f1, f2], 1), Indicate(VGroup(i1, i2, i3), color=TXT_STRONG, scale_factor=1.05), run_time=.7)
        # r6 錘錘：更多細節在說明欄
        pc = np.array([8.6, -1.1, 0])
        pl, drop = self.plumb_in(pc, .42)
        art = VGroup(T("完整文章", .06, TXT_STRONG), T("在說明欄", .06, TXT_STRONG)).arrange(DOWN, buff=.1)
        art.move_to(np.array([8.4, -2.75, 0]))
        self.at(A("r6", 0), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("r6", .3), FadeIn(art, shift=DOWN * .15), *pl.look(DOWN), run_time=.7)
        self.at(A("r6", .55), *pl.hop(-.22), run_time=.45)
        self.at(A("r6", .8), *pl.hop(-.22), run_time=.45)
        self.pl, self.art = pl, art
        self.finish()
