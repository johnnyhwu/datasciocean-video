"""v002 CER：sc01～sc04。大圖元件在 world.py，設計在 design.md。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa: E402,F401,F403

SINE = rate_functions.ease_in_out_sine
BOUNCE = rate_functions.ease_out_bounce
HOOK_CER = np.array([9.5, .35, 0])


def hook_cer():
    return M("CER", .1, TXT_STRONG).move_to(HOOK_CER)


def stage(ttl="SC", sub="多數決", ones=False, bars=False, scores=False, walk=None, ticks=None):
    """主圖在各場交界的樣子：五條路徑、票、標題、（每條 1 票｜分數）、待答的問題。天平另外放。"""
    W = sheet(bars=bars, scores=scores, walk=walk)
    W["title"], W["sub"] = title(ttl), sub_label(sub, CONF if ttl == "CER" else MUTED)
    if ones:
        W["ones"] = [one_tag(i) for i in range(5)]
    if ticks is not None:
        W["asks"] = asks(ticks)
    return W


def calm(bal=None, vs=()):
    """場景最後一個動作一起做：發抖停下來（下一場第一格要和這一格一格不差）。"""
    return ([bal.amp.animate.set_value(0)] if bal is not None else []) + [Act(v, set=dict(amp=0)) for v in vs]


def jump(v, h=.3):
    return Act(v, to=v.p.copy(), hop=h)


# ---------------- sc01：五票 ----------------
class Sc01(Sheet):
    SID = "sc01"

    def construct(self):
        A = self.A
        self.cam_set(HOOK_C, HOOK_W)
        bal = Balance(a=[0] * 5)
        self.add(bal)
        # h1 同一題算五次：五顆票浮在天平上方
        self.at(A("h1", .4), LaggedStart(*[bal.a[i].animate.set_value(.2) for i in range(5)], lag_ratio=.18), run_time=1.3)
        # h2 三次 375、兩次 400：依序落進兩個盤子
        self.at(A("h2", .04), LaggedStart(*[bal.a[i].animate(rate_func=BOUNCE).set_value(1) for i in LEFT_I], lag_ratio=.3),
                run_time=1.3, sfx="pop", gain=.5)
        self.at(A("h2", .56), LaggedStart(*[bal.a[i].animate(rate_func=BOUNCE).set_value(1) for i in RIGHT_I], lag_ratio=.35),
                run_time=1.1, sfx="pop", gain=.5)
        # h3 少數服從多數：兩邊的票數寫出來
        r0, r1 = bal.readout(0), bal.readout(1)
        self.at(A("h3", .08), Write(r0), Write(r1), run_time=.8, sfx="tick", gain=.5)
        self.at(A("h3", .6), Indicate(bal.labels[0], color=TXT_STRONG, scale_factor=1.25), run_time=.9)
        # h4（錘錘）那三票好像不太確定：左盤的三顆開始冒汗、發抖
        pl, drop = self.plumb_in(np.array([1.2, -.7, 0]), .5)
        self.at(A("h3", .92), *drop, run_time=.7)
        self.lipsync(pl)
        self.at(A("h4", .2), *pl.curl(), *pl.look(RIGHT), LaggedStart(*[bal.hes[i].animate.set_value(1) for i in LEFT_I], lag_ratio=.25),
                bal.amp.animate.set_value(1), run_time=1.4, sfx="slide", gain=.3)
        self.at(A("h4", .75), *pl.tilt(.2), run_time=.8)
        # h5 多數決只數票數
        self.at(A("h5", .5), Indicate(r0, color=GOLD, scale_factor=1.3), Indicate(r1, color=GOLD, scale_factor=1.3), *pl.tilt(-.2),
                run_time=1.0)
        # h6 讓猶豫的票變輕，它叫 CER
        self.at(A("h6", .12), *pl.straighten(), bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.07), run_time=1.0)
        bal.wob.set_value(0)
        cer = hook_cer()
        self.at(A("h6", .62), Write(cer), *pl.mood("happy"), run_time=.8, sfx="ding", gain=.5)
        self.at(A("h6", .92), *self.plumb_out(pl), *calm(bal), run_time=.7)
        self.remove(pl)
        self.finish()


# ---------------- sc02：拉遠，整張選票 ----------------
class Sc02(Sheet):
    SID = "sc02"

    def construct(self):
        A = self.A
        self.cam_set(HOOK_C, HOOK_W)
        bal = Balance(hes=HES_ON)
        r0, r1 = self.bal_set(bal)
        cer = hook_cer()
        self.add(cer)
        W = stage()
        qm = qmark()
        boxes = [n.box for row in W["nodes"] for n in row]
        nums = [[W["nodes"][i][j].num for i in range(5)] for j in range(3)]
        # 片頭音樂裡拉遠：問題卡、五條路徑、每一步的空格一路長出來
        build = Succession(Wait(.5), AnimationGroup(
            DrawBorderThenFill(W["qb"]), Write(qm),
            LaggedStart(*[Create(W["links"][i][0]) for i in range(5)], lag_ratio=.1),
            Succession(Wait(.5), LaggedStart(*[AnimationGroup(Create(W["links"][i][1]), Create(W["links"][i][2])) for i in range(5)],
                                             lag_ratio=.1)),
            Succession(Wait(.35), LaggedStart(*[DrawBorderThenFill(b) for b in boxes], lag_ratio=.05))))
        self.at(.2, FadeOut(cer), bal.amp.animate.set_value(1), run_time=.5)
        self.at(.7, self.cam(STAGE, STAGE_W), build, run_time=3.5, rate_func=SINE)
        # i1 頻道介紹：五個點各走一條路
        dots = [pdot(PATHC) for _ in range(5)]
        self.at(A("i1", .3), LaggedStart(*[travel(d, row_path(i)) for i, d in enumerate(dots)], lag_ratio=.15), run_time=2.6)
        self.remove(*dots)
        # i2 最後會看到它的局限：天平晃一下
        self.at(A("i2", .12), bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.09), run_time=1.5)
        bal.wob.set_value(0)
        self.at(A("i2", .7), Indicate(qm, color=GOLD, scale_factor=1.4), run_time=.9)
        # s1 原本的做法：SC
        self.at(A("s1", .08), bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.06), run_time=1.0)
        bal.wob.set_value(0)
        self.at(A("s1", .6), Write(W["title"]), run_time=.8, sfx="ding", gain=.4)
        # s2 最主流的方法
        self.at(A("s2", .45), Indicate(W["title"], color=TXT_STRONG, scale_factor=1.2), run_time=.9)
        # s3 同一個問題，K 條不同的推理路徑
        kl = T("K 條路徑", .055, PATHC).move_to(np.array([STEP_X[1], -3.12, 0]))
        dots = [pdot(PATHC) for _ in range(5)]
        self.at(A("s3", .3), LaggedStart(*[travel(d, row_path(i)) for i, d in enumerate(dots)], lag_ratio=.15),
                Succession(Wait(.5), Write(kl)), run_time=1.9)
        self.remove(*dots)
        # s4 多數決：選出現次數最多的答案
        self.at(A("s4", .12), Write(W["sub"]), run_time=.7)
        self.at(A("s4", .55), Indicate(r0, color=GOLD, scale_factor=1.3), Indicate(bal.labels[0], color=TXT_STRONG, scale_factor=1.2),
                run_time=1.0, sfx="tick", gain=.5)
        # s5 舉個例子：一本書 100 元，買 5 本，打八折
        self.at(A("s5", .08), FadeOut(kl), FadeOut(qm), run_time=.6)
        for k, fr in enumerate((.36, .6, .82)):
            self.at(A("s5", fr), Write(W["qt"][k]), run_time=.6)
        # s6 三步：五顆票從題目出發，各走各的路，每到一步寫下中間答案；猶豫的三顆在第二步抖得最厲害
        vs = [Voter(QP, .28, hes=HES_ON[i], op=0, ph=i * 2.1) for i in range(5)]
        self.add(*vs)
        up = LEFT * (NODE_W / 2 + .38)   # 停在方框左邊的連線上，不蓋數字和標題
        self.at(A("s6", .04), LaggedStart(*[Act(v, to=P(i, 0) + up, hop=.2, set=dict(op=1)) for i, v in enumerate(vs)], lag_ratio=.08),
                run_time=.9, sfx="pop", gain=.3)
        self.at(A("s6", .3), Write(W["heads"][0]), LaggedStart(*[Write(n) for n in nums[0]], lag_ratio=.1), run_time=.8, sfx="tick", gain=.4)
        self.at(A("s6", .5), *[Act(v, to=P(i, 1) + up, hop=.22, set=dict(amp=1.6 * HES_ON[i])) for i, v in enumerate(vs)],
                Succession(Wait(.3), AnimationGroup(Write(W["heads"][1]), LaggedStart(*[Write(n) for n in nums[1]], lag_ratio=.1))),
                run_time=1.0, sfx="tick", gain=.4)
        self.at(A("s6", .74), *[Act(v, to=P(i, 2) + up, hop=.22, set=dict(amp=1.0 * HES_ON[i])) for i, v in enumerate(vs)],
                Succession(Wait(.3), AnimationGroup(Write(W["heads"][2]), LaggedStart(*[Write(n) for n in nums[2]], lag_ratio=.1))),
                run_time=1.0, sfx="tick", gain=.4)
        self.at(A("s6", .74) + 1.05, *[Act(v, to=PARK(i), hop=.18, set=dict(amp=0, r=VR)) for i, v in enumerate(vs)], *calm(bal), run_time=.5)
        self.finish()


# ---------------- sc03：每一票都一樣重 ----------------
class Sc03(Sheet):
    SID = "sc03"

    def construct(self):
        A = self.A
        self.cam_set(STAGE, STAGE_W)
        bal = Balance(hes=HES_ON)
        W = stage(walk=True)
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        N, vs = W["nodes"], W["walk"]
        ones = [one_tag(i) for i in range(5)]
        # b1 SC 的假設：每條路徑都平等，各算 1 票
        self.at(A("b1", 0), Indicate(W["title"], color=TXT_STRONG, scale_factor=1.2), *self.wake(bal, vs), run_time=.9)
        self.at(A("b1", .45), LaggedStart(*[ShowPassingFlash(row_path(i).set_stroke(PATHC, 6).set_fill(opacity=0), time_width=.5)
                                           for i in range(5)], lag_ratio=.1), run_time=1.1)
        self.at(A("b1", .7), LaggedStart(*[Write(o) for o in ones], lag_ratio=.15), run_time=1.2, sfx="tick", gain=.4)
        # b2 嚴謹、有信心的路徑：算一票（那顆票得意地跳兩下）
        self.at(A("b2", .05), ShowPassingFlash(row_path(1).set_stroke(TXT_STRONG, 7).set_fill(opacity=0), time_width=.5),
                Succession(Wait(.6), jump(vs[1], .32)), run_time=1.5)
        self.at(A("b2", .7), Indicate(ones[1], color=TXT_STRONG, scale_factor=1.5), jump(vs[1], .22), run_time=.8)
        # b3 充滿猶豫、剛好湊出來的路徑：也算一票（那顆票抖個不停）
        self.at(A("b3", .05), ShowPassingFlash(row_path(0).set_stroke(HES, 7).set_fill(opacity=0), time_width=.5),
                Succession(Wait(.5), Wiggle(N[0][1], scale_value=1.3, rotation_angle=.04 * TAU)), Act(vs[0], set=dict(amp=2.6)),
                run_time=1.9, sfx="scratch", gain=.25)
        self.at(A("b3", .72), Indicate(ones[0], color=TXT_STRONG, scale_factor=1.5), Act(vs[0], set=dict(amp=1)), run_time=.8)
        # b4 很有信心地、反覆給出同一個錯誤答案：三個 375 一起亮，三顆票一起跳
        dw = [pdot(HES) for _ in LEFT_I]
        self.at(A("b4", .02), LaggedStart(*[travel(x, row_path(i)) for x, i in zip(dw, LEFT_I)], lag_ratio=.2), run_time=1.3)
        self.remove(*dw)
        self.at(A("b4", .45), LaggedStart(*[AnimationGroup(Highlight(N[i][2], color=HES, scale_factor=1.18), jump(vs[i], .26))
                                           for i in LEFT_I], lag_ratio=.22), run_time=1.5, sfx="pop", gain=.4)
        # b5 SC 只看數量不看品質：照樣選 375
        self.at(A("b5", .08), Indicate(W["title"], color=TXT_STRONG, scale_factor=1.2), run_time=.8)
        self.at(A("b5", .72), Indicate(r0, color=GOLD, scale_factor=1.35), Indicate(bal.labels[0], color=TXT_STRONG, scale_factor=1.25),
                *calm(bal, vs), run_time=1.1, sfx="thud", gain=.4)
        self.finish()


NOTE6 = np.array([PIV[0], BASE_Y - .42, 0])
PLUMB6 = np.array([2.42, 3.0, 0])


# ---------------- sc04：讓票有輕重（先看到結果，再問分數怎麼來） ----------------
class Sc04(Sheet):
    SID = "sc04"

    def construct(self):
        A = self.A
        self.cam_set(STAGE, STAGE_W)
        bal = Balance(hes=HES_ON)
        W = stage(ones=True, walk=True)
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        N, vs, ones = W["nodes"], W["walk"], W["ones"]
        scores = [score_num(i) for i in range(5)]
        # c1 一樣是投票，但每一票的重量不一樣：SC 換成 CER
        cer = title("CER")
        self.at(.1, *self.wake(bal, vs), run_time=.4)
        self.at(A("c1", .1), Indicate(W["title"], color=TXT_STRONG, scale_factor=1.15), run_time=.7)
        self.at(A("c1", .36), ReplacementTransform(W["title"], cer), FadeOut(W["sub"]), run_time=.8, sfx="click", gain=.5)
        self.at(A("c1", .66), bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.08), run_time=1.2)
        bal.wob.set_value(0)
        # c2 替每條路徑算一個信心分數，越有把握分數越高：有把握的兩顆票變成紫色
        self.at(A("c2", .3), *[Act(vs[i], set=dict(sure=1)) for i in RIGHT_I], *[bal.sure[i].animate.set_value(1) for i in RIGHT_I],
                run_time=.9, sfx="ding", gain=.35)
        self.at(A("c2", .68), *[jump(vs[i], .28) for i in RIGHT_I], run_time=.6)
        # v2 SC 只算每個答案出現了幾次
        self.at(A("v2", .3), Indicate(r0, color=GOLD, scale_factor=1.4), Indicate(r1, color=GOLD, scale_factor=1.4),
                *[Indicate(o, color=TXT_STRONG, scale_factor=1.6) for o in ones], run_time=1.0)
        # v3 CER 把支持同一個答案的路徑，信心全部加起來
        sub2 = sub_label("信心加總", CONF)
        self.at(A("v3", .1), Indicate(cer, color=TXT_STRONG, scale_factor=1.2), run_time=.8)
        self.at(A("v3", .62), Write(sub2), run_time=.8)
        # v4 假設五條路徑算出來的分數是這樣
        self.at(A("v4", .4), LaggedStart(*[ReplacementTransform(ones[i], scores[i]) for i in range(5)], lag_ratio=.2), run_time=1.4,
                sfx="tick", gain=.4)
        # v5 375 那邊三票，加起來 1.70：三顆票縮成各自的分數（橫樑先扣住）
        self.at(A("v5", .08))
        bal.hold()
        bal.mode.set_value(1)

        def fly(ids):
            ds = [pdot(CONF) for _ in ids]
            return ds, [travel(d, Line(scores[i].get_right() + RIGHT * .1, bal.slot(i)[0])) for d, i in zip(ds, ids)]
        ds, tr = fly(LEFT_I)
        self.at(A("v5", .08), *[bal.w[i].animate.set_value(SCORES[i]) for i in LEFT_I], LaggedStart(*tr, lag_ratio=.15), run_time=1.3,
                sfx="slide", gain=.4)
        self.remove(*ds)
        self.at(A("v5", .72), Indicate(r0, color=TXT_STRONG, scale_factor=1.3), run_time=.8)
        # v6 400 那邊只有兩票，加起來卻有 1.88
        ds, tr = fly(RIGHT_I)
        self.at(A("v6", .08), *[bal.w[i].animate.set_value(SCORES[i]) for i in RIGHT_I], LaggedStart(*tr, lag_ratio=.15), run_time=1.2,
                sfx="slide", gain=.4)
        self.remove(*ds)
        note = calc_note(NOTE6, .055)
        self.at(A("v6", .6), Indicate(r1, color=GOLD, scale_factor=1.3), Write(note), run_time=.8)
        # 放開橫樑：兩票那邊重重砸下去，三顆小票被彈起來
        pl, drop = self.plumb_in(PLUMB6, .45)
        self.at(A("v6", .88), *self.slam(bal), *drop, run_time=1.0, sfx="bell", gain=.5)
        bal.wob.set_value(0)
        self.lipsync(pl)
        # v7（錘錘）票比較少的那邊，反而贏了！
        self.at(A("v7", .15), *pl.light_on(), *pl.mood("wow"), *pl.look(RIGHT + DOWN), run_time=.5)
        self.at(A("v7", .45), *pl.hop(.3), *[jump(vs[i], .3) for i in RIGHT_I], run_time=.5)
        self.at(A("v7", .75), *pl.hop(.22), run_time=.45)
        # v8 猶豫的路徑貢獻很小；每一步都有把握的路徑才有決定性的影響
        self.at(A("v8", .05), FadeOut(note), *[Act(vs[i], set=dict(amp=2.4)) for i in LEFT_I], run_time=.9)
        self.at(A("v8", .3), LaggedStart(*[Indicate(scores[i], color=HES, scale_factor=1.3) for i in LEFT_I], lag_ratio=.2),
                *[Act(vs[i], set=dict(amp=1)) for i in LEFT_I], run_time=1.1)
        self.at(A("v8", .64), LaggedStart(*[AnimationGroup(Highlight(N[i][2], color=ANS, scale_factor=1.2), jump(vs[i], .28),
                                                           Indicate(scores[i], color=TXT_STRONG, scale_factor=1.3)) for i in RIGHT_I],
                                          lag_ratio=.3), run_time=1.0)
        # c3（錘錘）等一下，這個分數是怎麼算出來的？
        self.at(A("c3", .0), *pl.mood("think"), *pl.look(LEFT + DOWN), *pl.tilt(.22), run_time=.5)
        self.at(A("c3", .4), LaggedStart(*[Indicate(s, color=GOLD, scale_factor=1.35) for s in scores], lag_ratio=.12), run_time=1.2,
                sfx="tick", gain=.4)
        # c4 要回答兩個問題：看哪幾步？每一步怎麼量？
        Q = asks(0)
        self.at(A("c4", .0), *self.plumb_out(pl), run_time=.7)
        self.remove(pl)
        self.at(A("c4", .36), Create(Q[0].box), Write(Q[0].txt), run_time=.8, sfx="tick", gain=.4)
        self.at(A("c4", .7), Create(Q[1].box), Write(Q[1].txt), *calm(bal, vs), run_time=.8, sfx="tick", gain=.4)
        self.finish()


# ---------------- sc05：看哪幾步（只看最後一步會被騙 → 每一步都算） ----------------
LAST_P = np.array([SCORE_X + .55, HEAD_Y, 0])


class Sc05(Sheet):
    SID = "sc05"

    def construct(self):
        A = self.A
        self.cam_set(STAGE, STAGE_W)
        bal = Balance(w=SCORES, mode=1, hes=HES_ON, sure=SURE_ON)
        W = stage("CER", "信心加總", scores=True, walk="sure", ticks=0)
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        N, vs, scores, Q, heads = W["nodes"], W["walk"], W["scores"], W["asks"], W["heads"]
        tracks = [[bar_track(i, j) for j in range(3)] for i in range(5)]
        fills = [[bar_fill(i, j) for j in range(3)] for i in range(5)]
        fresh = sheet(bars=True)
        # q0 先回答第一個：看哪幾步？
        self.at(.1, *self.wake(bal, vs), run_time=.4)
        self.at(A("q0", .2), Highlight(Q[0], color=GOLD, scale_factor=1.12), run_time=1.0)
        # p1 一條路徑有好幾步，每一步都有一個信心：每一步底下長出一根信心長條
        self.at(A("p1", .3), LaggedStart(*[AnimationGroup(Create(tracks[i][j]), GrowFromEdge(fills[i][j], LEFT))
                                          for j in range(3) for i in range(5)], lag_ratio=.07), run_time=1.9, sfx="tick", gain=.35)
        # q1 最直覺的想法：看最後一步就好 → 前兩步變暗
        early = [m for i in range(5) for j in range(2) for m in (N[i][j], tracks[i][j], fills[i][j])]
        self.at(A("q1", .2), Indicate(heads[2], color=TXT_STRONG, scale_factor=1.25), run_time=.8)
        self.at(A("q1", .55), *[m.animate.set_opacity(.22) for m in early], heads[0].animate.set_opacity(.3), heads[1].animate.set_opacity(.3),
                run_time=.9, sfx="scratch", gain=.3)
        # e5 回到剛才假設的例子，如果只看最後一步的信心
        lasts = [M(f"{LASTS[i]}", .06, CONF).move_to(scores[i]) for i in range(5)]
        self.at(A("e5", .2), LaggedStart(*[Indicate(fills[i][2], color=TXT_STRONG, scale_factor=1.3) for i in range(5)], lag_ratio=.12),
                run_time=1.1)
        self.at(A("e5", .6), LaggedStart(*[ReplacementTransform(scores[i], lasts[i]) for i in range(5)], lag_ratio=.15), run_time=1.3,
                sfx="tick", gain=.4)
        # e6 375 那邊 2.0，400 那邊 1.92：又被騙過去了（天平砸回 375）
        self.at(A("e6", .04))
        bal.hold()
        self.at(A("e6", .04), *[bal.w[i].animate.set_value(LASTS[i]) for i in range(5)], run_time=1.0, sfx="slide", gain=.4)
        self.at(A("e6", .3), Indicate(r0, color=TXT_STRONG, scale_factor=1.3), run_time=.6)
        self.at(A("e6", .52), Indicate(r1, color=TXT_STRONG, scale_factor=1.3), run_time=.6)
        note = calc_note(NOTE6, .055)
        self.at(A("e6", .68), *self.slam(bal, to_left=True), Write(note), *[Act(vs[i], set=dict(amp=2.2)) for i in LEFT_I],
                run_time=1.0, sfx="thud", gain=.5)
        bal.wob.set_value(0)
        # p2 為什麼不只看最後一步？錯誤往往發生在中間：中間那一步亮回來
        mid = [(N[i][1], fresh["nodes"][i][1]) for i in range(5)] + [(tracks[i][1], fresh["tracks"][i][1]) for i in range(5)] \
            + [(fills[i][1], fresh["fills"][i][1]) for i in range(5)]
        self.at(A("p2", .12), Indicate(heads[2], color=TXT_STRONG, scale_factor=1.2), *[Act(vs[i], set=dict(amp=1)) for i in LEFT_I], run_time=.8)
        self.at(A("p2", .6), *[Transform(a, b) for a, b in mid], heads[1].animate.set_opacity(1), run_time=.8, sfx="click", gain=.4)
        # p3 第二步算錯了，後面再完美，最終答案也是錯的
        self.at(A("p3", .08), Wiggle(N[0][1], scale_value=1.35, rotation_angle=.04 * TAU),
                Indicate(fills[0][1], color=HES, scale_factor=1.5), run_time=.9)
        l2 = W["links"][0][2].copy().set_stroke(HES, 6, 1)
        self.at(A("p3", .5), ShowPassingFlash(l2, time_width=.6), run_time=.7)
        self.at(A("p3", .76), Indicate(N[0][2].num, color=HES, scale_factor=1.35), run_time=.8, sfx="thud", gain=.4)
        # e4 最後很有自信地答錯，中間卻早就露出猶豫
        self.at(A("e4", .15), LaggedStart(*[Indicate(fills[i][2], color=TXT_STRONG, scale_factor=1.3) for i in LEFT_I], lag_ratio=.2),
                run_time=1.1)
        self.at(A("e4", .6), LaggedStart(*[AnimationGroup(Wiggle(N[i][1], scale_value=1.3, rotation_angle=.03 * TAU),
                                                          Indicate(fills[i][1], color=HES, scale_factor=1.5)) for i in LEFT_I], lag_ratio=.2),
                *[Act(vs[i], set=dict(amp=2.4)) for i in LEFT_I], run_time=1.3)
        # e1 論文也做了這個對照
        self.at(A("e1", .1), *[Act(vs[i], set=dict(amp=1)) for i in LEFT_I], Indicate(heads[2], color=TXT_STRONG, scale_factor=1.2), run_time=.8)
        # e2 對照組 CER-LAST：只算最後一個答案的信心
        last_l = T("CER-LAST", .055, TXT_STRONG).move_to(LAST_P)
        self.at(A("e2", .12), Write(last_l), run_time=.8, sfx="tick", gain=.4)
        self.at(A("e2", .6), LaggedStart(*[Indicate(x, color=TXT_STRONG, scale_factor=1.3) for x in lasts], lag_ratio=.12), run_time=1.1)
        # e3 就這組比較，考慮所有步驟的 CER 都明顯比較好：每一步都算回來，天平砸回 400
        first = [(N[i][0], fresh["nodes"][i][0]) for i in range(5)] + [(tracks[i][0], fresh["tracks"][i][0]) for i in range(5)] \
            + [(fills[i][0], fresh["fills"][i][0]) for i in range(5)]
        back = [score_num(i) for i in range(5)]
        self.at(A("e3", .05))
        bal.hold()
        self.at(A("e3", .05), *[Transform(a, b) for a, b in first], heads[0].animate.set_opacity(1), FadeOut(last_l), FadeOut(note),
                *[ReplacementTransform(lasts[i], back[i]) for i in range(5)], *[bal.w[i].animate.set_value(SCORES[i]) for i in range(5)],
                run_time=1.2, sfx="slide", gain=.4)
        self.at(A("e3", .42), *self.slam(bal), Indicate(W["title"], color=GOLD, scale_factor=1.3), run_time=1.0, sfx="bell", gain=.5)
        bal.wob.set_value(0)
        self.at(A("e3", .78), LaggedStart(*[AnimationGroup(Highlight(N[i][2], color=ANS, scale_factor=1.2), jump(vs[i], .28))
                                           for i in RIGHT_I], lag_ratio=.3), run_time=1.0)
        # p4a 所以 CER 把每一步都算進來：三步的長條一欄一欄亮，第一個問題打勾
        self.at(A("p4a", .1), LaggedStart(*[AnimationGroup(*[Indicate(fills[i][j], color=TXT_STRONG, scale_factor=1.35) for i in range(5)])
                                           for j in range(3)], lag_ratio=.35), run_time=1.0)
        self.at(A("p4a", .5), Create(Q[0].tick), Indicate(Q[0].txt, color=KEY, scale_factor=1.1), run_time=.7, sfx="ding", gain=.45)
        # m2（錘錘）那每一步的信心，要怎麼量呢？
        pl, drop = self.plumb_in(PLUMB6, .45)
        self.at(A("m2", -.3), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("m2", .1), *pl.mood("think"), *pl.look(LEFT + DOWN), *pl.tilt(.22), run_time=.5)
        self.at(A("m2", .5), Highlight(Q[1], color=GOLD, scale_factor=1.12), run_time=.9)
        self.at(A("m2", 1.0) + .1, *self.plumb_out(pl), *calm(bal, vs), run_time=.65)
        self.remove(pl)
        self.finish()


# ---------------- 工作台 1：第二步那句話的 token 與機率（sc06 用） ----------------
TOKENS = [("Therefore", .99), ("the", .98), ("discount", .97), ("is", .99), ("12", .5), ("5", .4)]
BX, BY = BENCH1[0], BENCH1[1]
TOK_Y, TOK_H, BAR_S = BY - .9, .62, 1.9
BASE = TOK_Y + TOK_H / 2 + .08
DIM = .22


def tok_box(s, key=False):
    t = T(s, .05, TXT)
    r = RoundedRectangle(corner_radius=.1, width=t.width + .36, height=TOK_H).set_stroke(LINE, 2, 1).set_fill(SEA, 1)
    t.set_z_index(2)
    g = VGroup(r, t.move_to(r))
    g.box, g.txt = r, t
    return g


def bench1(final=True):
    """工作台 1。final=True＝sc04 最後一格（插入 Answer: 標籤、其他詞變暗、只剩關鍵字與算式）。
    final=False＝剛寫出來的樣子（沒有標籤、全亮）。"""
    toks = [tok_box(s) for s, _ in TOKENS]
    tag = tok_box("Answer:")
    tag.box.set_stroke(KEY, 2)
    tag.txt.set_color(KEY)
    row = VGroup(*toks[:4], tag, *toks[4:]).arrange(RIGHT, buff=.12).move_to(np.array([BX, TOK_Y, 0]))
    d = (tag.width + .12) / 2
    bars, nums, faces = [], [], []
    for g, (_, p) in zip(toks, TOKENS):
        b = Rectangle(width=.5, height=p * BAR_S).set_stroke(width=0).set_fill(CONF, .95)
        b.move_to(np.array([g.get_center()[0], BASE, 0]), aligned_edge=DOWN)
        n = M(f"{p}", .048, CONF).next_to(b, UP, buff=.12)
        bars.append(b), nums.append(n)
        faces.append(bare_face(np.array([g.get_center()[0], BASE + p * BAR_S - .27, 0]), .2, hes=1.0 if p < .6 else 0.0))
    non = VGroup(*toks[:4])
    key = VGroup(*toks[4:], *bars[4:], *nums[4:], *faces[4:])
    frame = RoundedRectangle(corner_radius=.14, width=VGroup(*toks[4:]).width + .3, height=2.35).set_stroke(KEY, 2.4).set_fill(opacity=0)
    frame.move_to(np.array([VGroup(*toks[4:]).get_center()[0], TOK_Y - TOK_H / 2 - .12, 0]), aligned_edge=DOWN)
    regex = T("Regex", .045, KEY).next_to(frame, DOWN, buff=.16)
    kw = T("關鍵字", .045, KEY).next_to(frame, UP, buff=.16)
    # 下方一排：Prompt → Answer: [數值]　Response: [短語]
    chip_t = T("Prompt", .045, TXT_STRONG)
    chip = VGroup(RoundedRectangle(corner_radius=.12, width=chip_t.width + .4, height=.6).set_stroke(TXT_STRONG, 2).set_fill(SEA, 1), chip_t)
    chip_t.move_to(chip[0])

    def slot(s):
        t = T(s, .042, MUTED)
        r = DashedVMobject(RoundedRectangle(corner_radius=.08, width=t.width + .34, height=.52), num_dashes=22).set_stroke(MUTED, 1.8)
        return VGroup(r, t.move_to(r))
    ta, sa, tr, sr = T("Answer:", .045, KEY), slot("數值"), T("Response:", .045, KEY), slot("短語")
    arrow = Line(ORIGIN, RIGHT * .5).set_stroke(TXT_STRONG, 2, .8)
    prow = VGroup(chip, arrow, VGroup(ta, sa).arrange(RIGHT, buff=.14), VGroup(tr, sr).arrange(RIGHT, buff=.14)).arrange(RIGHT, buff=.3)
    prow[3].shift(RIGHT * .25)
    prow.move_to(np.array([BX - .9, BY - 2.15, 0]))
    # 算式：c = ∏ p，0.5 × 0.4 = 0.2
    fx = BX - 1.9
    formula = VGroup(M("c", .07, CONF, italic=True), M("=", .065), M("∏", .075), M("p", .07, CONF, italic=True)).arrange(RIGHT, buff=.16)
    formula.move_to(np.array([fx, BY + 1.75, 0]))
    calc = VGroup(M("0.5", .06, CONF), M("×", .055), M("0.4", .06, CONF), M("=", .055), M("0.2", .068, CONF)).arrange(RIGHT, buff=.16)
    calc.move_to(np.array([fx, BY + .9, 0]))
    note = calc_note(np.array([fx, BY + .32, 0]), .042)
    B = dict(toks=toks, tag=tag, bars=bars, nums=nums, faces=faces, frame=frame, regex=regex, kw=kw, chip=chip, arrow=arrow, ta=ta, sa=sa, tr=tr, sr=sr,
             formula=formula, calc=calc, note=note)
    B["d"] = d
    for g in toks[4:]:
        g.box.set_stroke(KEY, 2)
        g.txt.set_color(KEY)
    if final:
        for g in toks[:4]:
            g.set_opacity(DIM)
        B.pop("bars"), B.pop("nums"), B.pop("faces")
        B["kbars"], B["knums"], B["kfaces"] = bars[4:], nums[4:], faces[4:]
    else:
        non.shift(RIGHT * d)
        VGroup(*bars[:4], *nums[:4], *faces[:4]).shift(RIGHT * d)
        key.shift(LEFT * d)
        for g in toks[4:]:
            g.box.set_stroke(LINE, 2)
            g.txt.set_color(TXT)
    return B


def bench_items(B):
    out = []
    for k, v in B.items():
        if k == "d":
            continue
        out.extend(v if isinstance(v, list) else [v])
    return out


