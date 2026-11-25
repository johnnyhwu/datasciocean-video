"""v004 Claude Code：sc01～sc05。大圖元件在 world.py，設計在 design.md。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa: E402,F401,F403

HOOK_W = 13.6
BALL_W = 9.2
HARN_C, HARN_W = np.array([1.8, .35, 0]), 16.0
TOOL_C, TOOL_W = np.array([8.9, -.05, 0]), 10.8
CARDS_C, CARDS_W = np.array([.1, 1.5, 0]), 18.0

ROWS = [("任務：修好測試", "task"), ("test_calc.py", "obs"), ("改好 calc.py", "obs"),
        ("FAILED 沒過", "err"), ("再改 calc.py", "obs"), ("PASSED 通過", "ok"), ("回答：修好了", "task")]
TOOL_IDX = {"Read": 0, "Glob": 0, "Grep": 0, "Edit": 1, "Write": 1, "Bash": 2, "Task": 3, "WebFetch": 4, "WebSearch": 4}


def stage(rows=0, arrows_op=1.0, harness=False, words=False, names=False, look=ORIGIN):
    """跑道上的固定陣容（每場的 builder 都從這裡組）。"""
    d = dict(trk=track(), ball=glass_model(look=look), gate=gate(), tb=toolbox(names=names))
    d["trk"].arrows.set_fill(opacity=.7 * arrows_op)
    if harness:
        d["har"] = T("Harness", .05, TXT_STRONG).move_to(np.array([0, -1.33, 0]))
    if words:
        d["words"] = station_words()
    if rows:
        d["stop"] = scroll_top()
        d["rows"] = VGroup(*[row(t, k, i) for i, (t, k) in enumerate(ROWS[:rows])])
    return d


def add_stage(scene, d):
    for k in ("trk", "ball", "gate", "tb", "har", "words", "stop", "rows"):
        if k in d:
            scene.add(d[k])


def person(c, color=MUTED):
    head = Circle(.2).set_fill(color, .9).set_stroke(width=0).move_to(c + UP * .32)
    body = Arc(radius=.34, start_angle=0, angle=PI, arc_center=c + DOWN * .22).set_stroke(color, 5)
    g = VGroup(head, body)
    g.overlap_ok = True
    return g


class Sheet4(Sheet):
    """這支片的共用動作：小單跑一圈。"""

    def lap(self, ts, tool, arg, rtext, rkind, ri, back="ok", sfx_row=None, gain=.45):
        """ts＝五個時間點：讀紙卷＋開單、到收費站、到工具、回到左邊、接進紙卷。各段依序播放，不重疊。"""
        G, ball, tb = self.G, self.ball, self.tb
        t0, t1, t2, t3, t4 = ts
        fit = lambda a_, b_, cap: max(.22, min(cap, b_ - a_ - .03))
        sl = slip(tool, arg).scale(.35).move_to(LOOP_C + UP * .3)
        beam = read_beam(ri)
        beam.transient = True
        r_gate = min(.8, (t1 - t0) * .45)
        tA = t1 - r_gate
        self.at(t0, FadeIn(beam, rate_func=there_and_back), ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.3),
                sl.animate.scale(1 / .35).move_to(P(90, SLIP_R)), run_time=fit(t0, tA, 1.0), sfx="pop", gain=.3)
        self.at(tA, run_slip(sl, 90, GATE_A + 42, run=1), run_time=fit(tA, t1, r_gate))
        up = gate(arm_up=1).arm
        r_up = fit(t1, t2, .35) if t2 - t1 > .8 else .2
        self.at(t1, Transform(G.arm, up), G.lamp.animate.set_fill(GOOD), run_time=r_up, sfx="click", gain=.35)
        t1b = t1 + r_up + .02
        self.at(t1b, run_slip(sl, GATE_A + 42, -35, run=1), Succession(Wait(1.2), AnimationGroup(Transform(G.arm, gate().arm), G.lamp.animate.set_fill(MUTED), run_time=1)), run_time=fit(t1b, t2, .9))
        it = tb.items[TOOL_IDX[tool]]
        res = chip(rtext, rkind)
        res.next_to(P(-35, 2.6), DOWN, buff=.72)
        moodsl = slip(tool, arg, mood=back).move_to(P(-35, 2.6))
        r_back = min(1.1, (t3 - t2) * .55)
        t3m = t3 - r_back
        self.at(t2, Highlight(it, color=TXT_STRONG, scale_factor=1.18, inner=False), FadeIn(res, shift=LEFT * .3), Transform(sl, moodsl), run_time=fit(t2, t3m, .7))
        trav = VGroup(sl, res)
        ret = Arc(radius=1, start_angle=np.deg2rad(-35), angle=-PI + np.deg2rad(35), arc_center=LOOP_C).stretch(2.85, 0, about_point=LOOP_C).stretch(2.1, 1, about_point=LOOP_C).shift(DOWN * .25)
        rpath = VMobject()
        rpath.set_points_as_corners([trav.get_center(), ret.get_start()])
        rpath.append_points(ret.points)
        self.at(t3m, MoveAlongPath(trav, rpath, rate_func=SINE), run_time=fit(t3m, max(t3, t4 - .2), r_back))
        dst = row(rtext, rkind, ri)
        tE = max(t3, t4 - .2)
        self.at(tE, ReplacementTransform(res, dst), FadeOut(sl, scale=.5, shift=LEFT * .5), run_time=.5, sfx=sfx_row, gain=gain)
        self.rows.add(dst)
        return dst


# ---------------- sc01：一個圈 ----------------
class Sc01(Sheet4):
    SID = "sc01"

    def construct(self):
        A = self.A
        self.cam_set(LOOP_C, HOOK_W)
        # h1 讀程式、改程式、跑測試、修好了
        xs = [-4.2, -1.45, 1.3, 4.2]
        play = Triangle().rotate(-PI / 2).scale(.3).set_fill(TOOL, .5).set_stroke(TOOL, 3)
        ok = speech("修好了", ORIGIN, .05)
        play.scale(1.4)
        ok = speech("修好了", ORIGIN, .062)
        ics = [icon_magnifier(ORIGIN, 1.9), icon_pencil(ORIGIN, 1.9), play, ok]
        labs = ["讀", "改", "測試", ""]
        acts = VGroup()
        for x, ic, lb in zip(xs, ics, labs):
            ic.move_to(np.array([x, .25, 0]))
            g = VGroup(ic)
            if lb:
                g.add(T(lb, .06, TXT).next_to(ic, DOWN, buff=.35))
            acts.add(g)
        for a, f in zip(acts, (0, .3, .5, .82)):
            self.at(max(0, A("h1", f) - (.3 if f == 0 else 0)), FadeIn(a, shift=UP * .25, scale=.8), run_time=.45, sfx="tick" if f < .8 else "pop", gain=.35)
        # h2 規劃器、執行器、檢查器……
        fc = flowchart()
        self.at(A("h2", 0), FadeOut(acts, shift=UP * .3), run_time=.5)
        for i, f in enumerate((.12, .34, .55, .72)):
            self.at(A("h2", f), FadeIn(fc.boxes[i], scale=.7), run_time=.35, sfx="tick", gain=.3)
        self.at(A("h2", .87), LaggedStart(*[FadeIn(b, scale=.6) for b in fc.more], lag_ratio=.25),
                LaggedStart(*[GrowArrow(a) for a in fc.arrows], lag_ratio=.08), run_time=1.3)
        # h3 沒有規劃模組，也沒有執行模組 → 整張圖塌掉
        self.at(A("h3", .3), Wiggle(fc, scale_value=1.04, rotation_angle=.02 * TAU, n_wiggles=5), run_time=.7)
        rng = np.random.default_rng(7)
        falls = [m.animate(rate_func=rate_functions.ease_in_quad).shift(DOWN * rng.uniform(4.5, 6) + RIGHT * rng.uniform(-1, 1)).rotate(rng.uniform(-2, 2)).set_opacity(0)
                 for m in list(fc.arrows) + list(fc.more) + list(fc.boxes)]
        trk = track()
        self.at(A("h3", .62), AnimationGroup(LaggedStart(*falls, lag_ratio=.03), AnimationGroup(Create(trk.outer), Create(trk.inner), FadeIn(trk.band)), lag_ratio=.45),
                run_time=2.2, sfx="thud", gain=.55)
        # h4 規劃和執行，都在同一個迴圈裡
        self.at(A("h4", .05), Create(trk.mid), LaggedStart(*[FadeIn(a, scale=.5) for a in trk.arrows], lag_ratio=.2), run_time=.9)
        hero = slip("讀").move_to(P(90))
        self.at(A("h4", .3), FadeIn(hero, scale=.5), run_time=.4, sfx="pop", gain=.35)
        self.at(A("h4", .45), MoveAlongPath(hero, Arc(radius=R, start_angle=PI / 2, angle=-TAU, arc_center=LOOP_C)), ShowPassingFlash(track_glow(GOLD, 9), time_width=.35), run_time=2.0, rate_func=SINE, sfx="swoosh", gain=.35)
        # h5 錘錘：就一個迴圈？
        pl, drop = self.plumb_in(np.array([4.6, -.6, 0]), .45)
        self.at(A("h5", 0), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("h5", .15), *pl.curl(), *pl.look(LEFT), run_time=.9)
        self.at(A("h5", .45), MoveAlongPath(hero, Arc(radius=R, start_angle=PI / 2, angle=-TAU, arc_center=LOOP_C)), run_time=1.6, rate_func=SINE)
        self.at(A("h5", .84), *self.plumb_out(pl), FadeOut(hero, scale=.5), run_time=.6)
        self.finish()


# ---------------- sc02：模型沒有手 ----------------
class Sc02(Sheet4):
    SID = "sc02"

    def construct(self):
        A = self.A
        self.cam_set(LOOP_C, HOOK_W)
        trk = track()
        self.add(trk)
        # 片頭音樂：一道光繞圈
        self.at(.15, ShowPassingFlash(track_glow(TEAL_L, 8), time_width=.4), run_time=2.1, rate_func=SINE)
        # i1 Claude Code；i2 命令列裡的 agent
        ttl = T("Claude Code", .064, TXT_STRONG).move_to(UP * .35)
        term = RoundedRectangle(corner_radius=.1, width=1.6, height=.8).set_fill(PANEL, 1).set_stroke(TXT, 2)
        prompt_ = T(">_", .05, TEAL_L).move_to(term.get_left() + RIGHT * .45)
        termg = VGroup(term, prompt_).next_to(ttl, DOWN, buff=.4)
        self.at(A("i1", .5), Write(ttl), run_time=1.0)
        self.at(A("i2", .1), Indicate(ttl, color=TEAL_L, scale_factor=1.06), run_time=.7)
        self.at(A("i2", .55), FadeIn(termg, shift=UP * .2), run_time=.5)
        cur = Rectangle(width=.2, height=.36).set_fill(TEAL_L, 1).set_stroke(width=0).next_to(prompt_, RIGHT, buff=.12)
        self.at(A("i2", .7), FadeIn(cur, rate_func=there_and_back_with_pause), run_time=1.0)
        # i3 中心是一個凍結的模型
        ball = glass_model()
        self.at(A("i3", .05), AnimationGroup(AnimationGroup(FadeOut(VGroup(ttl, termg), shift=UP * .4), FadeOut(trk), self.cam(LOOP_C, BALL_W)), GrowFromCenter(ball), lag_ratio=.45),
                run_time=1.9, sfx="pop", gain=.4)
        self.at(A("i3", .82), Indicate(ball.lab, color=TXT_STRONG, scale_factor=1.15), run_time=.7)
        # i3b 讀進一段字、吐出一段字
        cin = chip("一段字", "obs", .062).move_to(LEFT * 2.9)
        cout = chip("另一段字", "task", .062).move_to(RIGHT * 2.55)
        self.at(A("i3b", .25), FadeIn(cin, shift=RIGHT * .4), run_time=.4)
        self.at(A("i3b", .42), cin.animate.move_to(LOOP_C).scale(.2).set_opacity(0), ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.35), run_time=.7)
        self.at(A("i3b", .7), FadeIn(cout, shift=RIGHT * .6, scale=.4), run_time=.5)
        # i4 沒有手：開不了檔案、按不了執行
        fil = VGroup(RoundedRectangle(corner_radius=.05, width=.7, height=.9).set_fill(PANEL, 1).set_stroke(TXT, 2),
                     *[Line(LEFT * .2, RIGHT * .2).set_stroke(TXT, 2).shift(UP * (.2 - .15 * q)) for q in range(3)]).move_to(np.array([2.75, .55, 0]))
        run_b = VGroup(Circle(.36).set_fill(PANEL, 1).set_stroke(TXT, 2), Triangle().rotate(-PI / 2).scale(.14).set_fill(TXT, 1).set_stroke(width=0)).move_to(np.array([2.75, -.75, 0]))
        self.at(A("i4", .12), FadeOut(cout), FadeIn(fil, shift=LEFT * .3), FadeIn(run_b, shift=LEFT * .3), run_time=.5)
        self.at(A("i4", .32), ball.animate(rate_func=there_and_back).shift(RIGHT * .35), run_time=.5)
        x1, x2 = cross_mark(BAD, .4).move_to(fil), cross_mark(BAD, .4).move_to(run_b)
        for x in (x1, x2):
            x.cross_ok = x.overlap_ok = True
        self.at(A("i4", .52), Create(x1), run_time=.35, sfx="scratch", gain=.35)
        self.at(A("i4", .74), Create(x2), run_time=.35, sfx="scratch", gain=.35)
        # i5 不是會開檔案的聊天機器人
        chat = speech("聊天機器人", np.array([-2.55, 1.2, 0]), .045)
        self.at(A("i5", .1), FadeOut(VGroup(fil, run_b, x1, x2)), FadeIn(chat, shift=UP * .2), run_time=.5)
        strike = Line(chat.get_left() + RIGHT * .15, chat.get_right() + LEFT * .15).set_stroke(BAD, 6)
        strike.cross_ok = strike.overlap_ok = True
        self.at(A("i5", .7), Create(strike), run_time=.4, sfx="scratch", gain=.35)
        # i6 圍著模型搭起來的執行架構：Harness
        G, tb = gate(), toolbox()
        har = T("Harness", .05, TXT_STRONG).move_to(np.array([0, -1.33, 0]))
        self.at(A("i6", 0), FadeOut(VGroup(chat, strike)), self.cam(HARN_C, HARN_W),
                Succession(Wait(.4), AnimationGroup(FadeIn(trk, scale=1.15), DrawBorderThenFill(G), LaggedStart(*[FadeIn(i, shift=LEFT * .2) for i in tb], lag_ratio=.15))),
                run_time=1.9, rate_func=SINE)
        self.at(A("i6", .6), Write(har), run_time=.8, sfx="ding", gain=.4)
        self.at(A("i6", .8), ShowPassingFlash(track_glow(TEAL_L, 7), time_width=.4), run_time=.9)
        self.finish()


# ---------------- sc03：修一個沒過的測試 ----------------
class Sc03(Sheet4):
    SID = "sc03"

    def construct(self):
        A = self.A
        self.cam_set(HARN_C, HARN_W)
        d = stage(harness=True)
        add_stage(self, d)
        self.G, self.ball, self.tb = d["gate"], d["ball"], d["tb"]
        self.rows = VGroup()
        # w1 任務
        task = speech("修好這個沒過的測試", np.array([-5.5, .6, 0]))
        self.at(A("w1", 0), self.cam(WORK_C, WORK_W), FadeOut(d["har"]), Succession(Wait(.6), FadeIn(task, shift=UP * .3, scale=.8)), run_time=1.4, rate_func=SINE)
        self.at(A("w1", .7), Wiggle(task, scale_value=1.05), run_time=.8)
        # w2 寫進紙卷：transcript
        st = scroll_top()
        r0 = row(*ROWS[0], 0)
        self.at(A("w2", .2), FadeIn(st.rod, shift=DOWN * .2), run_time=.5)
        self.at(A("w2", .4), ReplacementTransform(task, r0), run_time=.7, sfx="slide", gain=.35)
        self.rows.add(r0)
        self.at(A("w2", .8), Write(st.lab), run_time=.6)
        # w3–w4 第一圈：Read
        self.at(A("w3", .05), *[e.animate.shift(LEFT * .03) for e in self.ball.eyes[1::2]], run_time=.3)
        self.lap([A("w3", .3), A("w4", .02), A("w4", .3), A("w4", .6), A("w4", .85)], "Read", "test_calc.py", *ROWS[1], 1, back="happy")
        # w5 第二圈：Edit
        self.lap([A("w5", .3), A("w5", .52), A("w5", .66), A("w5", .82), A("w5", .97)], "Edit", "calc.py", *ROWS[2], 2, back="happy")
        # w6–w7 第三圈：Bash 跑測試 → 沒過
        self.lap([A("w6", .1), A("w6", .5), A("w7", .05), A("w7", .4), A("w7", .65)], "Bash", "pytest", *ROWS[3], 3, back="sweat", sfx_row="thud", gain=.5)
        # w8 中間沒有人轉述
        pp = person(np.array([-3.1, -.6, 0]), USER)
        self.at(A("w8", .1), FadeIn(pp, shift=UP * .2), run_time=.4)
        xx = cross_mark(BAD, .42).move_to(pp)
        xx.cross_ok = xx.overlap_ok = True
        self.at(A("w8", .6), Create(xx), run_time=.35, sfx="scratch", gain=.35)
        # w9 錯誤訊息直接變成下一輪的輸入
        err = self.rows[3]
        self.at(A("w9", 0), FadeOut(VGroup(pp, xx)), Highlight(err, color=TXT_STRONG, scale_factor=1.06, inner=False), run_time=.7)
        path = Line(err.get_right() + RIGHT * .05, LOOP_C + LEFT * (BALL_R + .05)).set_stroke(BAD, 6)
        arr = Arrow(err.get_right() + RIGHT * .05, LOOP_C + LEFT * (BALL_R + .1), buff=0, stroke_width=6, tip_length=.25).set_color(BAD)
        arr.overlap_ok = arr.cross_ok = True
        self.at(A("w9", .45), ShowPassingFlash(path, time_width=.6), GrowArrow(arr), self.ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.35), run_time=1.0)
        # w10 第四圈、第五圈
        self.lap([A("w10", .02), A("w10", .12), A("w10", .2), A("w10", .3), A("w10", .38)], "Edit", "calc.py", *ROWS[4], 4, back="happy")
        self.at(A("w10", .44), FadeOut(arr), run_time=.2)
        self.lap([A("w10", .5), A("w10", .6), A("w10", .68), A("w10", .78), A("w10", .88)], "Bash", "pytest", *ROWS[5], 5, back="happy", sfx_row="ding", gain=.45)
        # w11 不再開單，直接回答 → 迴圈停下來
        ans = speech("修好了", LOOP_C + UP * 1.55, .05)
        self.at(A("w11", .2), FadeIn(ans, shift=UP * .2, scale=.7), run_time=.45, sfx="pop", gain=.35)
        r6 = row(*ROWS[6], 6)
        self.at(A("w11", .45), ReplacementTransform(ans, r6), run_time=.8, sfx="slide", gain=.3)
        self.rows.add(r6)
        self.at(A("w11", .78), d["trk"].arrows.animate.set_fill(opacity=.2), run_time=.8)
        self.finish()


def cards():
    """sc04 上方的兩張對照小卡：自動補全、只能讀的助理。"""
    c1c, c2c = np.array([-3.0, 3.95, 0]), np.array([3.0, 3.95, 0])
    b1 = RoundedRectangle(corner_radius=.15, width=4.6, height=1.3).set_fill(PANEL, .9).set_stroke(LINE, 2).move_to(c1c)
    code = T("def add(a, b):", .052, TXT).move_to(c1c + np.array([-.4, .25, 0]))
    ghost = T("return a + b", .052, MUTED).move_to(c1c + np.array([-.15, -.3, 0]))
    l1 = T("自動補全", .058, TXT_STRONG).next_to(b1, UP, buff=.18)
    b2 = RoundedRectangle(corner_radius=.15, width=4.6, height=1.3).set_fill(PANEL, .9).set_stroke(LINE, 2).move_to(c2c)
    eye = VGroup(Ellipse(width=.9, height=.5).set_stroke(TXT, 3), Dot(radius=.12, color=TXT)).move_to(c2c + LEFT * .8)
    pen = icon_pencil(c2c + RIGHT * .8, 1.0)
    l2 = T("只能讀", .058, TXT_STRONG).next_to(b2, UP, buff=.18)
    x = cross_mark(BAD, .4).move_to(pen)
    x.cross_ok = x.overlap_ok = True
    g = dict(b1=b1, code=code, ghost=ghost, l1=l1, b2=b2, eye=eye, pen=pen, l2=l2, x=x)
    return g


# ---------------- sc04：做、看、再做 ----------------
class Sc04(Sheet4):
    SID = "sc04"

    def construct(self):
        A = self.A
        self.cam_set(WORK_C, WORK_W)
        d = stage(rows=7, arrows_op=.2 / .7)
        add_stage(self, d)
        trk, ball = d["trk"], d["ball"]
        # n1 把五圈疊起來
        self.at(A("n1", 0), trk.arrows.animate.set_fill(opacity=.7), run_time=.6)
        self.at(A("n1", .3), LaggedStart(*[ShowPassingFlash(track_glow(GOLD, 7), time_width=.3) for _ in range(5)], lag_ratio=.22), run_time=2.6, rate_func=linear)
        # n2 呼叫工具、觀察結果、決定下一步：做、看、想
        w = station_words()
        for i, f in ((1, .2), (2, .45), (0, .72)):
            self.at(A("n2", f), FadeIn(w[i], scale=1.4), run_time=.4, sfx="tick", gain=.3)
        # n3 一圈一圈跑，直到它判斷做完了
        self.at(A("n3", .05), ShowPassingFlash(track_glow(GOLD, 8), time_width=.35), run_time=1.4, rate_func=SINE)
        self.at(A("n3", .6), Highlight(d["rows"][6], color=TXT_STRONG, scale_factor=1.06, inner=False), run_time=.8)
        # n4 規劃在哪？在每一圈裡
        ghost = flow_box("規劃器", np.array([-2.75, 2.75, 0]), MUTED, .05)
        self.at(A("n4", .05), FadeIn(ghost, shift=DOWN * .2), run_time=.6)
        self.at(A("n4", .4), ghost.animate.move_to(LOOP_C).scale(.15).set_opacity(0), ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.4), run_time=1.0, sfx="swoosh", gain=.35)
        beam = read_beam(7)
        beam.transient = True
        self.at(A("n4", .72), FadeIn(beam, rate_func=there_and_back), run_time=1.1)
        # n5 錘錘：原來規劃不是一個模組！
        pl, drop = self.plumb_in(np.array([3.35, -1.8, 0]), .42)
        self.at(A("n5", 0), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("n5", .2), *pl.straighten(), *pl.mood("happy"), run_time=.7, sfx="bell", gain=.45)
        self.at(A("n5", .45), *pl.light_on(), run_time=.5)
        self.at(A("n5", .9), *self.plumb_out(pl), run_time=.6)
        self.remove(pl)
        # n6 觀察和行動用同一套介質：模型吐出的是一段字，讀回來的也是一段字
        err = d["rows"][3]
        act = slip("Bash", "pytest").scale(.92).move_to(LOOP_C)
        act.set_z_index(6)
        la = T("行動", .055, GOLD).move_to(LOOP_C + UP * 1.35)
        lo = T("觀察", .055, TXT_STRONG).move_to(LOOP_C + DOWN * 1.35)
        strip = err.copy()
        for m in (act, strip, la, lo):
            m.transient = True
        self.at(A("n6", .02), act.animate.move_to(np.array([-2.0, 2.5, 0])), FadeIn(la, shift=UP * .1), run_time=.8, sfx="pop", gain=.3)
        self.at(A("n6", .35), Highlight(err, color=TXT_STRONG, scale_factor=1.06, inner=False), run_time=.6)
        self.at(A("n6", .6), strip.animate.move_to(LOOP_C).scale(.3).set_opacity(0), ball.halo.animate(rate_func=there_and_back).set_fill(opacity=.45), run_time=1.0, sfx="swoosh", gain=.3)
        self.remove(strip)
        self.at(A("n6", .8), FadeIn(lo, shift=UP * .1), run_time=.4)
        self.at(A("n6", .93), Indicate(VGroup(la, lo), color=TXT_STRONG, scale_factor=1.1), run_time=.6)
        # n7–n8 自動補全：預測下一個字
        K = cards()
        self.at(A("n7", 0), self.cam(CARDS_C, CARDS_W), FadeOut(VGroup(act, la, lo)), Succession(Wait(.4), FadeIn(VGroup(K["b1"], K["code"], K["l1"]), shift=DOWN * .2)), run_time=1.1)
        self.at(A("n7", .7), FadeIn(K["ghost"], shift=RIGHT * .2), run_time=.5)
        self.at(A("n8", .15), Indicate(K["ghost"], color=TXT_STRONG, scale_factor=1.1), run_time=.8)
        self.at(A("n8", .62), ShowPassingFlash(track_glow(GOLD, 8), time_width=.35), run_time=1.3, rate_func=SINE)
        # n9 只能讀的助理
        self.at(A("n9", .15), FadeIn(VGroup(K["b2"], K["eye"], K["pen"], K["l2"]), shift=DOWN * .2), run_time=.6)
        self.at(A("n9", .55), Create(K["x"]), run_time=.35, sfx="scratch", gain=.35)
        self.at(A("n9", .8), Indicate(K["eye"], color=TXT_STRONG, scale_factor=1.15), run_time=.7)
        self.finish()


# ---------------- sc05：工具箱 ----------------
class Sc05(Sheet4):
    SID = "sc05"

    def construct(self):
        A = self.A
        self.cam_set(CARDS_C, CARDS_W)
        d = stage(rows=7, words=True)
        add_stage(self, d)
        K = cards()
        kg = VGroup(*K.values())
        self.add(kg)
        tb = d["tb"]
        for m in [d["ball"], d["gate"], *d["ball"].family_members_with_points(), *d["gate"].family_members_with_points()]:
            m.nocheck = True          # 推近工具箱時，模型和收費站只露出一角（不是文字或卡片）
        # t1 它的手：工具
        self.at(A("t1", 0), FadeOut(kg), FadeOut(d["words"]), self.cam(TOOL_C, TOOL_W), run_time=.9, rate_func=SINE)
        self.at(A("t1", .55), LaggedStart(*[Highlight(i, color=TXT_STRONG, scale_factor=1.12, inner=False) for i in tb.items], lag_ratio=.18), run_time=1.3)
        # t2 Read、Glob、Grep
        tbn = toolbox(names=True)
        self.at(A("t2", 0), ReplacementTransform(tb.shelf, tbn.shelf), ReplacementTransform(tb.items[0], tbn.items[0]), run_time=.6)
        self.at(A("t2", .45), Highlight(tbn.items[0], color=TXT_STRONG, scale_factor=1.12, inner=False), run_time=.7)
        # t3 不把整個專案塞進來，只撈需要的幾段
        mt = code_mountain(np.array([11.3, -1.75, 0]), s=.95)
        self.at(A("t3", 0), LaggedStart(*[FadeIn(f, shift=DOWN * .15) for f in mt], lag_ratio=.04), run_time=1.2)
        lens = icon_magnifier(np.array([10.8, -.4, 0]), 1.4)
        lens.set_z_index(6)
        self.at(A("t3", .35), FadeIn(lens), run_time=.3)
        self.at(A("t3", .42), lens.animate.move_to(np.array([11.7, -1.0, 0])), run_time=.6)
        pick = VGroup(mt[3], mt[10])
        self.at(A("t3", .58), *[f[0].animate.set_stroke(TOOL, 3) for f in pick], run_time=.4)
        snip = VGroup(*[f.copy() for f in pick])
        snip.transient = True
        mt.transient = True
        snip.set_z_index(6)
        self.at(A("t3", .66), snip.animate.arrange(RIGHT, buff=.15).move_to(np.array([11.2, 1.4, 0])).scale(1.3), FadeOut(lens, scale=.8), mt.animate.fade(.65), run_time=1.4, rate_func=SINE, sfx="slide", gain=.3)
        # t4 Edit、Write：在檔案裡精確換掉一行
        RX = 11.7
        fl = RoundedRectangle(corner_radius=.08, width=2.2, height=1.6).set_fill(PANEL, 1).set_stroke(TXT, 2.5).move_to(np.array([RX, .9, 0]))
        lines = VGroup(*[Line(LEFT * .75, RIGHT * (.75 - .25 * (q % 2))).set_stroke(TXT, 3).shift(fl.get_center() + UP * (.45 - .3 * q)) for q in range(4)])
        bad_l, good_l = lines[2].copy().set_stroke(BAD, 4), lines[2].copy().set_stroke(GOOD, 4)
        self.at(A("t4", 0), FadeOut(snip, shift=UP * .4), FadeOut(mt), ReplacementTransform(tb.items[1], tbn.items[1]), FadeIn(VGroup(fl, lines), shift=LEFT * .3), run_time=.6)
        self.at(A("t4", .15), Highlight(tbn.items[1], color=TXT_STRONG, scale_factor=1.12, inner=False), Transform(lines[2], bad_l), run_time=.6)
        pen = tbn.items[1].icon.copy()
        self.at(A("t4", .45), pen.animate.move_to(lines[2].get_right() + UP * .2), run_time=.6)
        self.at(A("t4", .62), pen.animate.shift(LEFT * 1.3), Transform(lines[2], good_l), run_time=.7, sfx="scratch", gain=.3)
        self.at(A("t4", .85), FadeOut(pen), run_time=.3)
        # t5 Bash：逃生門，通往任何 shell 指令
        term = VGroup(RoundedRectangle(corner_radius=.1, width=2.7, height=1.3).set_fill("#06181C", 1).set_stroke(TOOL, 2.5),
                      T(">_ make", .056, TEAL_L)).move_to(np.array([RX, -.55, 0]))
        term[1].move_to(term[0].get_left() + RIGHT * (.2 + term[1].width / 2))
        self.at(A("t5", .02), ReplacementTransform(tb.items[2], tbn.items[2]), FadeOut(VGroup(fl, lines)), run_time=.35)
        self.at(A("t5", .12), Highlight(tbn.items[2], color=TXT_STRONG, scale_factor=1.12, inner=False), run_time=.6)
        door = tbn.items[2].icon
        self.at(A("t5", .32), door[1].animate.stretch(.3, 0, about_edge=LEFT), run_time=.4, sfx="click", gain=.3)
        bs = slip("Bash").scale(.8).move_to(door)
        bs.transient = True
        self.at(A("t5", .42), FadeIn(bs, scale=.5), run_time=.25)
        self.at(A("t5", .5), bs.animate.move_to(term).scale(.6).set_opacity(0), FadeIn(term, shift=LEFT * .2), run_time=.8, rate_func=SINE)
        self.remove(bs)
        self.at(A("t5", .78), door[1].animate.stretch(1 / .3, 0, about_edge=LEFT), Indicate(term[1], color=TXT_STRONG), run_time=.6)
        # t6 Task：分身，只拿回摘要
        clone = glass_model(np.array([RX, -.6, 0]), .5)
        clone.lab.set_opacity(0)
        csc = VGroup(*[Rectangle(width=1.0, height=.16).set_fill(MUTED, .55).set_stroke(width=0) for _ in range(5)]).arrange(DOWN, buff=.05).next_to(clone, LEFT, buff=.3)
        for m in [*clone.get_family(), *csc.get_family()]:
            m.overlap_ok = True
        self.at(A("t6", .02), ReplacementTransform(tb.items[3], tbn.items[3]), FadeOut(term), run_time=.35)
        self.at(A("t6", .12), Highlight(tbn.items[3], color=TXT_STRONG, scale_factor=1.12, inner=False), TransformFromCopy(tbn.items[3].icon, clone), run_time=.8, sfx="pop", gain=.3)
        self.at(A("t6", .4), LaggedStart(*[FadeIn(r_, shift=DOWN * .08) for r_ in csc], lag_ratio=.2), run_time=.9)
        mini = chip("摘要", "sum").move_to(clone)
        self.at(A("t6", .7), FadeIn(mini, scale=.5), FadeOut(csc), run_time=.4)
        self.at(A("t6", .8), mini.animate.next_to(tbn.items[3], RIGHT, buff=.35), run_time=.6, sfx="slide", gain=.3)
        # t7 WebFetch、WebSearch：去外面找
        page = VGroup(RoundedRectangle(corner_radius=.08, width=1.9, height=1.3).set_fill(PANEL, 1).set_stroke(TEAL_L, 2.5),
                      *[Line(LEFT * .6, RIGHT * .6).set_stroke(TXT, 2.5).shift(UP * (.3 - .25 * q)) for q in range(3)]).move_to(np.array([RX + .3, -1.35, 0]))
        page[1:].move_to(page[0])
        self.at(A("t7", 0), FadeOut(VGroup(mini, clone)), ReplacementTransform(tb.items[4], tbn.items[4]), run_time=.4)
        self.at(A("t7", .1), Highlight(tbn.items[4], color=TXT_STRONG, scale_factor=1.12, inner=False), FadeIn(page, shift=LEFT * .5), run_time=.7)
        self.at(A("t7", .32), Rotate(tbn.items[4].icon[1], angle=PI, axis=UP), page.animate.move_to(tbn.items[4].get_right() + RIGHT * .9).scale(.5), run_time=.7)
        fin = toolbox()
        self.at(A("t7", .8), *[ReplacementTransform(a_, b_) for a_, b_ in zip([tbn.shelf, *tbn.items], [fin.shelf, *fin.items])], FadeOut(page), run_time=.7)
        self.finish()
