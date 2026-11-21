"""v002 CER：sc06～sc09。大圖元件在 world.py，sc01～sc05 與工作台 1 在 scenes_a.py。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scenes_a import *  # noqa: E402,F401,F403

RUSH = rate_functions.rush_into
BACK = rate_functions.ease_out_back
TAB = rate_functions.there_and_back
K5 = ROW_W / FW          # 推近到一條路徑時：字照原本的字級做，再縮成這個比例（實際字級不變）
THICK = [1, 1.9, 2.8]    # 權重 1、2、3：信心長條變粗的倍數


def stage_cer(ticks=None):
    """sc05 結束之後的主圖：每一步的信心長條、五個分數、CER、紫色的票。"""
    return stage("CER", "信心加總", bars=True, scores=True, walk="sure", ticks=ticks)


def cer_balance():
    return Balance(w=SCORES, mode=1, hes=HES_ON, sure=SURE_ON)


# ---------------- sc06：每一步怎麼量（只看關鍵字，機率相乘） ----------------
class Sc06(Sheet):
    SID = "sc06"

    def construct(self):
        A = self.A
        self.cam_set(STAGE, STAGE_W)
        bal = cer_balance()
        W = stage_cer(ticks=1)
        self.add(*flat(W))
        self.bal_set(bal)
        B = bench1(final=False)
        d = B["d"]
        toks, bars, nums, faces = B["toks"], B["bars"], B["nums"], B["faces"]
        col = [VGroup(bars[k], faces[k]) for k in range(6)]
        # t1 模型一小塊一小塊寫字：第二步那張 125 帶著鏡頭往下，停在工作台右上；token 一塊一塊寫出來
        ref = W["nodes"][0][1].copy().set_z_index(6)
        ref_p = np.array([BX + 4.95, BY + 1.5, 0])
        a0 = ref.get_center()
        path = VMobject().set_points_smoothly([a0, a0 + LEFT * 1.1 + DOWN * 1.2, np.array([-3.85, -3.2, 0]),
                                               (np.array([-3.85, -3.2, 0]) + ref_p) / 2 + LEFT * .6, ref_p])
        ref0 = ref.copy()

        def fly(m, a):
            m.become(ref0.copy().scale(1 + .25 * a).move_to(path.point_from_proportion(a)))
        self.add(ref)
        write = Succession(Wait(1.3), LaggedStart(*[AnimationGroup(DrawBorderThenFill(g.box), Write(g.txt)) for g in toks], lag_ratio=.3))
        self.at(A("t1", 0), self.cam(BENCH1_C, BENCH_W), UpdateFromAlphaFunc(ref, fly), write, run_time=3.3, rate_func=SINE)
        tl = T("token", .045, MUTED).next_to(toks[0], DOWN, buff=.2)
        self.at(A("t1", .82), Write(tl), Highlight(toks[0], color=TXT_STRONG, scale_factor=1.12), run_time=.7)
        # t2 每個 token 都有一個機率（比方說像這樣）：長條長出來，每一根都有一張臉
        self.at(A("t2", .5), LaggedStart(*[AnimationGroup(GrowFromEdge(b, DOWN), Write(n), Succession(Wait(.25), FadeIn(f)))
                                          for b, n, f in zip(bars, nums, faces)], lag_ratio=.18), run_time=1.9, sfx="tick", gain=.4)
        # t3 CER 不用訓練，只讀這些機率
        self.at(A("t3", .45), LaggedStart(*[Indicate(n, color=TXT_STRONG, scale_factor=1.25) for n in nums], lag_ratio=.12), run_time=1.3)
        # t4 最直接：整段平均
        mean = sum(p for _, p in TOKENS) / len(TOKENS)
        x0, x1 = bars[0].get_left()[0] - .45, bars[-1].get_right()[0] + .35
        avg = DashedLine([x0, BASE + mean * BAR_S, 0], [x1, BASE + mean * BAR_S, 0], dash_length=.12).set_stroke(TXT_STRONG, 2.2, .9)
        avg.cross_ok = True
        avg_l = T("平均", .045, TXT_STRONG).next_to(avg, LEFT, buff=.15)
        self.at(A("t4", .05), FadeOut(tl), run_time=.5)
        self.at(A("t4", .5), Create(avg), Write(avg_l), run_time=1.0)
        # t5 Therefore 這種連接詞機率通常非常高：它得意地一路長到頂出畫面
        for m in (*col[0], nums[0]):
            m.nocheck = True
        self.at(A("t5", .2), Highlight(toks[0], color=TXT_STRONG, scale_factor=1.1),
                col[0].animate(rate_func=TAB).stretch(1.75, 1, about_edge=DOWN), nums[0].animate(rate_func=TAB).shift(UP * 1.45),
                run_time=1.4, sfx="slide", gain=.35)
        self.at(A("t5", .7), LaggedStart(*[c.animate(rate_func=TAB).stretch(1.3, 1, about_edge=DOWN) for c in col[1:4]], lag_ratio=.2),
                run_time=.9)
        # t6 一平均，關鍵的數字被稀釋：兩根短的縮在角落發抖
        gaps = VGroup(*[Line(nums[k].get_top() + UP * .08, [bars[k].get_center()[0], BASE + mean * BAR_S - .06, 0]).set_stroke(HES, 2.6)
                        for k in (4, 5)])
        self.at(A("t6", .1), ShowPassingFlash(Line(avg.get_start(), avg.get_end()).set_stroke(TXT_STRONG, 7), time_width=.5), run_time=.9)
        self.at(A("t6", .45), LaggedStart(*[Create(g) for g in gaps], lag_ratio=.3),
                *[Wiggle(col[k], scale_value=1.2, rotation_angle=.03 * TAU) for k in (4, 5)], run_time=1.1, sfx="scratch", gain=.25)
        # t7 假設平均大約 0.8
        avg_v = M("≈ 0.8", .055, TXT_STRONG).next_to(avg_l, DOWN, buff=.16)
        self.at(A("t7", .12), LaggedStart(*[Indicate(b, color=CONF, scale_factor=1.12) for b in bars[:4]], lag_ratio=.12), run_time=1.1)
        self.at(A("t7", .55), Write(avg_v), run_time=.8)
        # t8 最關鍵的 125，模型其實很猶豫
        self.at(A("t8", .25), *[g.box.animate.set_stroke(KEY, 2) for g in toks[4:]], *[g.txt.animate.set_color(KEY) for g in toks[4:]],
                Highlight(ref, color=KEY, scale_factor=1.12), run_time=.9)
        self.at(A("t8", .7), Wiggle(VGroup(col[4], col[5], *nums[4:]), scale_value=1.2, rotation_angle=.03 * TAU), run_time=.9,
                sfx="thud", gain=.4)
        # t9 CER 只看關鍵字，其他的詞都不算
        self.at(A("t9", .25), *[g.animate.set_opacity(DIM) for g in toks[:4]], *[c.animate.set_opacity(DIM) for c in col[:4]],
                *[n.animate.set_opacity(DIM) for n in nums[:4]], FadeOut(avg), FadeOut(avg_l), FadeOut(avg_v), FadeOut(gaps), FadeOut(ref),
                run_time=.9, sfx="scratch", gain=.35)
        self.at(A("t9", .72), *[Highlight(g, color=TXT_STRONG, scale_factor=1.25) for g in toks[4:]], run_time=.9)
        # t10 在 Prompt 裡要求固定格式
        self.at(A("t10", .12), DrawBorderThenFill(B["chip"][0]), Write(B["chip"][1]), run_time=.8)
        self.at(A("t10", .38), Create(B["arrow"]), run_time=.6)
        self.at(A("t10", .58), ShowPassingFlash(B["arrow"].copy().set_stroke(TXT_STRONG, 5, 1), time_width=.6), run_time=.8)
        self.at(A("t10", .8), Highlight(B["chip"], color=TXT_STRONG, scale_factor=1.08), run_time=.7)
        # t11 數學題：Answer 加數值；問答題：Response 加短語。標籤也寫進這一句
        self.at(A("t11", .08), Write(B["ta"]), Create(B["sa"][0]), Write(B["sa"][1]), run_time=.8)
        non = VGroup(*toks[:4], *col[:4], *nums[:4])
        key = VGroup(*toks[4:], *col[4:], *nums[4:])
        self.at(A("t11", .3), non.animate.shift(LEFT * d), key.animate.shift(RIGHT * d),
                Succession(Wait(.3), AnimationGroup(Create(B["tag"].box), TransformFromCopy(B["ta"], B["tag"].txt))), run_time=1.0,
                sfx="click", gain=.5)
        self.at(A("t11", .62), Write(B["tr"]), Create(B["sr"][0]), Write(B["sr"][1]), run_time=.8)
        # t12 Regex 抓出標籤後面的內容＝關鍵字
        self.at(A("t12", .18), Create(B["frame"]), Write(B["regex"]), run_time=.9)
        self.at(A("t12", .72), Write(B["kw"]), run_time=.7, sfx="tick", gain=.4)
        # t13 一個關鍵字可能由好幾個 token 組成
        self.at(A("t13", .1), FadeOut(VGroup(*col[:4], *nums[:4])), run_time=.6)
        self.at(A("t13", .5), Highlight(toks[4], color=TXT_STRONG, scale_factor=1.25), run_time=.5)
        self.at(A("t13", .72), Highlight(toks[5], color=TXT_STRONG, scale_factor=1.25), run_time=.5)
        # t14 機率全部相乘＝這個詞的信心
        self.at(A("t14", .3), Write(B["formula"]), run_time=1.0)
        self.at(A("t14", .78), Indicate(B["formula"][0], color=TXT_STRONG, scale_factor=1.3), run_time=.7)
        # t15 例如 0.5 × 0.4 = 0.2
        c = B["calc"]
        self.at(A("t15", .1), TransformFromCopy(nums[4], c[0]), run_time=.6)
        self.at(A("t15", .3), Write(c[1]), TransformFromCopy(nums[5], c[2]), run_time=.6)
        self.at(A("t15", .62), Write(c[3]), Write(c[4]), Write(B["note"]), run_time=.8, sfx="ding", gain=.4)
        self.at(A("t15", .9), Indicate(c[4], color=TXT_STRONG, scale_factor=1.25), run_time=.6)
        self.finish()


# ---------------- sc07：合成一張票（加權平均 → 0.57 → 回到天平） ----------------
def piece(parts, frac=.055, buff=.07):
    """一串小字：[(字串, 顏色, 斜體)]。"""
    return VGroup(*[M(s, frac, c, it) for s, c, it in parts]).arrange(RIGHT, buff=buff)


def row_extras():
    """推近到第一條路徑時多出來的東西：變粗的信心長條、數值、權重、公式與代入的算式。"""
    c = PATHS[0][1]
    tracks = [bar_track(0, j) for j in range(3)]
    fills = [bar_fill(0, j, h=BAR_H * THICK[j]) for j in range(3)]
    for j, f in enumerate(fills):
        f.align_to(tracks[j], UP)
    vals = [M(f"{c[j]}", .055, CONF).scale(K5).next_to(tracks[j], LEFT, buff=.14) for j in range(3)]
    wts = [piece([("×", TXT, False), (str(j + 1), WT, False)], .055).scale(K5).next_to(tracks[j], RIGHT, buff=.14) for j in range(3)]
    num = piece([("Σ", TXT, False), ("j", WT, True), ("·", TXT, False), ("c", CONF, True)], .06, .09)
    den = piece([("Σ", TXT, False), ("j", WT, True)], .06, .09)
    formula = VGroup(M("C", .07, CONF, italic=True), M("=", .06), fraction(num, den))
    formula.arrange(RIGHT, buff=.2)
    parts = []
    for j in range(3):
        parts += [(str(j + 1), WT, False), ("×", TXT, False), (f"{c[j]}", CONF, False)]
        if j < 2:
            parts.append(("  +  ", TXT, False))
    numv = piece(parts, .052, .05)
    denv = piece([("1", WT, False), ("+", TXT, False), ("2", WT, False), ("+", TXT, False), ("3", WT, False)], .052, .1)
    eq = VGroup(M("=", .06), fraction(numv, denv))
    eq.arrange(RIGHT, buff=.2)
    res = VGroup(M("≈", .06), M("0.57", .07, CONF))
    res.arrange(RIGHT, buff=.16)
    VGroup(formula, eq, res).arrange(RIGHT, buff=.24).scale(K5).move_to(np.array([-1.98, 4.33, 0]))
    note = calc_note(ORIGIN, .042).scale(K5).next_to(res, DOWN, buff=.2)
    return dict(fills=fills, vals=vals, wts=wts, formula=formula, eq=eq, res=res, note=note)


class Sc07(Sheet):
    SID = "sc07"

    def construct(self):
        A = self.A
        self.cam_set(BENCH1_C, BENCH_W)
        bal = cer_balance()
        bal.nocheck = True      # 推近到一條路徑時，天平的外框會擦到畫面右緣（線條本身不在畫面內）；版面在其他場都檢查過
        W = stage_cer(ticks=1)
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        F = bench_items(bench1(final=True))
        self.add(*F)
        N, heads, Q, vs, scores = W["nodes"], W["heads"], W["asks"], W["walk"], W["scores"]
        tracks, fills = W["tracks"], W["fills"]
        W["links"][0].chrome = True     # 推近後這條線從畫面外的問題卡接進來：不算進版面平衡
        X = row_extras()
        others = list(m for i in (1, 2) for m in (*N[i], W["links"][i], *tracks[i], *fills[i], scores[i]))
        for m in others:
            m.transient = True      # 推近時暫時藏起來、拉遠再放回來：不算「出現太短就被拿掉」
        # g1 現在每一步都有信心了：回到整張圖，第二個問題打勾
        self.at(A("g1", 0), self.cam(STAGE, STAGE_W), FadeOut(VGroup(*F), rate_func=RUSH), *self.wake(bal, vs), run_time=2.0, rate_func=SINE)
        self.at(A("g1", .56), Create(Q[1].tick), Indicate(Q[1].txt, color=KEY, scale_factor=1.1), run_time=.7, sfx="ding", gain=.45)
        self.at(A("g1", .84), LaggedStart(*[AnimationGroup(*[Indicate(fills[i][j], color=TXT_STRONG, scale_factor=1.35) for i in range(5)])
                                          for j in range(3)], lag_ratio=.3), run_time=.9)
        # p4 CER 的做法是加權平均：推近到最上面那條路徑
        self.at(A("p4", 0), self.cam(ROW_C, ROW_W), *[FadeOut(m) for m in others], *[Act(vs[i], set=dict(op=0)) for i in (1, 2)],
                Succession(Wait(1.0), Write(X["formula"])), run_time=2.1, rate_func=SINE)
        thin = fills[0]
        fj = [X["formula"][2].num[1], X["formula"][2].den[1]]
        # p5 權重就是步驟的序號：①②③ 掉下來變成 ×1 ×2 ×3，長條跟著變粗
        self.at(A("p5", .12), *[Indicate(m, color=TXT_STRONG, scale_factor=1.5) for m in fj], run_time=.9)
        for j, fr in enumerate((.5, .7, .88)):
            self.at(A("p5", fr), TransformFromCopy(heads[j][0], X["wts"][j]), Transform(thin[j], X["fills"][j]), run_time=.5, sfx="tick", gain=.4)
        # p6 越靠近最終答案，權重越重
        self.at(A("p6", .35), Indicate(X["wts"][2], color=TXT_STRONG, scale_factor=1.5), Indicate(thin[2], color=CONF, scale_factor=1.15),
                run_time=1.0)
        # p7 推理是累積的：最後一步依賴前面每一步
        self.at(A("p7", .2), ShowPassingFlash(row_path(0).set_stroke(TXT_STRONG, 6).set_fill(opacity=0), time_width=.4), run_time=1.5)
        self.at(A("p7", .78), Highlight(N[0][2], color=TXT_STRONG, scale_factor=1.15), run_time=.8)
        # p8 假設三步的信心是 0.9、0.2、0.7
        for j, fr in enumerate((.56, .72, .88)):
            self.at(A("p8", fr), Write(X["vals"][j]), run_time=.45)
        # p9 代進去算，大約 0.57：就是這條路徑原本的那個分數
        self.at(A("p9", .05), Write(X["eq"]), run_time=1.3)
        self.at(A("p9", .62), Write(X["res"]), Write(X["note"]), run_time=.7, sfx="ding", gain=.4)
        cp = X["res"][1].copy()
        cp.transient = cp.overlap_ok = cp.nocheck = True
        self.at(A("p9", .92), Transform(cp, scores[0].copy()), run_time=.7)
        self.remove(cp)
        # p10 中間那一步的猶豫，把整條路徑的分數拉了下來
        self.at(A("p10", .15), Indicate(thin[1], color=HES, scale_factor=1.25), Indicate(X["vals"][1], color=HES, scale_factor=1.3),
                Wiggle(N[0][1], scale_value=1.25, rotation_angle=.03 * TAU), Act(vs[0], set=dict(amp=2.6)), run_time=1.0)
        self.at(A("p10", .7), Indicate(scores[0], color=TXT_STRONG, scale_factor=1.3), Act(vs[0], set=dict(amp=1)), run_time=.9)
        # g2 五條路徑都這樣算，就是剛才假設的那五個分數：拉回整張圖
        gone = VGroup(X["formula"], X["eq"], X["res"], X["note"], *X["vals"], *X["wts"], *Q, Q[1].tick)
        self.at(A("g2", 0), self.cam(STAGE, STAGE_W), FadeOut(gone), *[FadeIn(m) for m in others], *[Act(vs[i], set=dict(op=1)) for i in (1, 2)],
                *[Transform(thin[j], bar_fill(0, j)) for j in range(3)], run_time=2.0, rate_func=SINE)
        self.at(A("g2", .55), LaggedStart(*[AnimationGroup(Indicate(scores[i], color=TXT_STRONG, scale_factor=1.3),
                                                           jump(vs[i], .2)) for i in range(5)], lag_ratio=.15), run_time=1.5, sfx="tick", gain=.4)
        # g3 再照答案加起來，猶豫的票變輕，天平就倒向另一邊（重演一次）
        self.at(A("g3", .0), *[bal.w[i].animate.set_value(1) for i in range(5)], run_time=.7, sfx="slide", gain=.3)
        self.at(A("g3", .26))
        bal.hold()
        self.at(A("g3", .26), *[bal.w[i].animate.set_value(SCORES[i]) for i in range(5)], Indicate(r0, color=TXT_STRONG, scale_factor=1.25),
                run_time=1.0, sfx="slide", gain=.4)
        self.at(A("g3", .66), *self.slam(bal), *[jump(vs[i], .3) for i in RIGHT_I], run_time=1.0, sfx="bell", gain=.5)
        self.at(A("g3", .66) + 1.02, *calm(bal, vs), Indicate(W["title"], color=GOLD, scale_factor=1.2), run_time=.5)
        bal.wob.set_value(0)
        self.finish()


# ---------------- sc08：極限 ----------------
BX2, BY2 = BENCH2[0], BENCH2[1]
GAIN_S = 4.1 / 7.4      # 提升幅度：7.4% 畫成 4.1 單位長


def gain_row(k, label, val):
    y = BY2 + (.4 if k == 0 else -.9)
    lab = T(label, .042, TXT).move_to(np.array([BX2 - 5.25, y, 0]), aligned_edge=LEFT)
    x0 = BX2 - .6
    bar = Rectangle(width=val * GAIN_S, height=.5).set_stroke(width=0).set_fill(TEAL_L, .95).move_to(np.array([x0, y, 0]), aligned_edge=LEFT)
    return lab, bar, x0, y


def bench2_end():
    """sc08 最後一格：兩根提升幅度。"""
    l1, b1, x0, y1 = gain_row(0, "MathQA · OLMo-2-7B", 7.4)
    l2, b2, _, y2 = gain_row(1, "GSM8K · Llama 3.1 8B", .4)
    n1 = M("+7.4%", .06, TXT_STRONG).next_to(b1, RIGHT, buff=.2)
    n2 = M("≈ +0.4%", .06, TXT_STRONG).next_to(b2, RIGHT, buff=.2)
    axis = Line([x0, y1 + .6, 0], [x0, y2 - .6, 0]).set_stroke(LINE, 2, .9)
    t1, t2 = [Rectangle(width=7.4 * GAIN_S, height=.5).set_stroke(LINE, 1.4, .55).set_fill(opacity=0).move_to(np.array([x0, y, 0]), aligned_edge=LEFT)
              for y in (y1, y2)]
    n1.next_to(t1, RIGHT, buff=.2)
    n2.next_to(t2, RIGHT, buff=.2)
    return dict(axis=axis, t1=t1, t2=t2, l1=l1, b1=b1, n1=n1, l2=l2, b2=b2, n2=n2)


def panels():
    """數學（一條推理鏈，每一步有信心）對 問答（一格一格的知識，缺了一格）。"""
    cx = BX2 - 2.95
    hm = T("數學", .058, TXT_STRONG).move_to(np.array([cx, BY2 + 1.85, 0]))
    xs = [cx - 1.5, cx, cx + 1.5]
    nodes = VGroup(*[RoundedRectangle(corner_radius=.12, width=.95, height=.56).set_stroke(PATHC, 2.2, .9).set_fill(SEA, 1)
                     .move_to(np.array([x, BY2 + .55, 0])) for x in xs])
    links = VGroup(*[seg(nodes[k].get_right(), nodes[k + 1].get_left(), PATHC, SW, .7) for k in range(2)])
    cbars = VGroup(*[Rectangle(width=.85 * v, height=.13).set_stroke(width=0).set_fill(CONF, .95)
                     .move_to(nodes[k].get_bottom() + DOWN * .22 + LEFT * .425, aligned_edge=LEFT) for k, v in enumerate((.9, .85, .95))])
    lm = T("邏輯推理", .045, MUTED).move_to(np.array([cx, BY2 - .75, 0]))
    qx = BX2 + 2.95
    hq = T("問答", .058, TXT_STRONG).move_to(np.array([qx, BY2 + 1.85, 0]))
    cells = VGroup(*[Square(.46).set_stroke(PATHC, 2, .9).set_fill(SEA, 1).move_to(np.array([qx + (c - 1) * .58, BY2 + .5 - (r - 1) * .58, 0]))
                     for r in range(3) for c in range(3)])
    hole = DashedVMobject(Square(.46), num_dashes=16).set_stroke(HES, 2.4).move_to(cells[5])
    lq = T("知識檢索", .045, MUTED).move_to(np.array([qx, BY2 - .95, 0]))
    VGroup(hm, nodes, links, cbars, lm, hq, cells, hole, lq).shift(DOWN * .45)
    return dict(hm=hm, nodes=nodes, links=links, cbars=cbars, lm=lm, hq=hq, cells=cells, hole=hole, lq=lq)


class Sc08(Sheet):
    SID = "sc08"

    def construct(self):
        A = self.A
        self.cam_set(STAGE, STAGE_W)
        bal = cer_balance()
        W = stage_cer()
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        vs = W["walk"]
        # e7 不過 CER 也有極限
        self.at(A("e7", .0), Indicate(W["title"], color=TXT_STRONG, scale_factor=1.25), *self.wake(bal, vs), run_time=.9)
        self.at(A("e7", .5), bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.07), run_time=1.0)
        bal.wob.set_value(0)
        # e8 數學題上的表現通常比知識問答更穩定：到工作台 2
        Pn = panels()
        build = Succession(Wait(1.1), AnimationGroup(
            Write(Pn["hm"]), LaggedStart(*[DrawBorderThenFill(n) for n in Pn["nodes"]], lag_ratio=.2), Create(Pn["links"]),
            Succession(Wait(.5), AnimationGroup(Write(Pn["hq"]), LaggedStart(*[DrawBorderThenFill(c) for c in Pn["cells"][:5]],
                                                                            *[DrawBorderThenFill(c) for c in Pn["cells"][6:]], lag_ratio=.08)))))
        self.at(A("e8", 0), self.cam(BENCH2, BENCH_W), build, *calm(bal, vs), run_time=3.0, rate_func=SINE)
        # e9 數學是邏輯推理，信心反映邏輯連不連貫：一顆有把握的票沿著推理鏈一步一步跳過去
        up = UP * .62
        m = Voter(Pn["nodes"][0].get_center() + up, .26, sure=1.0, op=0)
        self.add(m)
        self.at(A("e9", .05), Write(Pn["lm"]), Act(m, set=dict(op=1)), run_time=.6)
        self.at(A("e9", .3), Act(m, to=Pn["nodes"][1].get_center() + up, hop=.3), GrowFromEdge(Pn["cbars"][0], LEFT), run_time=.6, sfx="pop", gain=.3)
        self.at(A("e9", .55), Act(m, to=Pn["nodes"][2].get_center() + up, hop=.3), GrowFromEdge(Pn["cbars"][1], LEFT), run_time=.6, sfx="pop", gain=.3)
        self.at(A("e9", .8), jump(m, .3), GrowFromEdge(Pn["cbars"][2], LEFT), run_time=.6)
        # e10 問答是知識檢索；沒有那個知識，信心怎麼算都答不對：一樣有把握的票走到缺的那一格，掉了下去
        cells = Pn["cells"]
        q = Voter(cells[0].get_center() + UP * .55, .22, sure=1.0, op=0)
        self.add(q)
        self.at(A("e10", .05), Write(Pn["lq"]), Act(q, set=dict(op=1)), run_time=.6)
        self.at(A("e10", .26), Act(q, to=cells[2].get_center() + UP * .55, hop=.25), Create(Pn["hole"]), run_time=.8)
        self.at(A("e10", .5), Act(q, to=cells[5].get_center(), hop=.3), run_time=.6)
        self.at(A("e10", .66), Act(q, to=cells[5].get_center() + DOWN * .1, set=dict(r=.03, op=0), rate_func=rate_functions.ease_in_cubic),
                Wiggle(Pn["hole"], scale_value=1.3, rotation_angle=.03 * TAU), run_time=.8, sfx="thud", gain=.45)
        self.remove(q)
        # e11 增強的是推理能力，不是知識庫存
        self.at(A("e11", .3), LaggedStart(*[Indicate(b, color=TXT_STRONG, scale_factor=1.25) for b in Pn["cbars"]], lag_ratio=.15),
                jump(m, .3), run_time=.9)
        self.at(A("e11", .7), Indicate(Pn["hole"], color=TXT_STRONG, scale_factor=1.3), run_time=.8)
        # e12 提升幅度也不平均：換成兩根長條
        G = bench2_end()
        gone = VGroup(*Pn.values())
        self.at(A("e12", .0), FadeOut(gone), Act(m, set=dict(op=0)),
                Succession(Wait(.35), AnimationGroup(Create(G["axis"]), Create(G["t1"]), Create(G["t2"]))), run_time=1.2)
        self.remove(m)
        # e13 MathQA、OLMo-2-7B：+7.4%
        self.at(A("e13", .12), Write(G["l1"]), run_time=1.0)
        self.at(A("e13", .66), GrowFromEdge(G["b1"], LEFT), Succession(Wait(.5), Write(G["n1"])), run_time=1.2, sfx="tick", gain=.4)
        # e14 Llama 3.1 8B、GSM8K：只有約 0.4%
        self.at(A("e14", .08), Write(G["l2"]), run_time=1.8)
        self.at(A("e14", .66), GrowFromEdge(G["b2"], LEFT), Write(G["n2"]), run_time=.8, sfx="tick", gain=.4)
        # e15 強的模型原本就很有信心、錯得少，進步空間有限
        self.at(A("e15", .2), Indicate(G["l2"], color=TXT_STRONG, scale_factor=1.06), run_time=.9)
        self.at(A("e15", .72), Indicate(G["n2"], color=TXT_STRONG, scale_factor=1.25), Indicate(G["b2"], color=TXT_STRONG, scale_factor=1.3),
                run_time=.9)
        self.finish()


# ---------------- sc09：三點回顧、片尾 ----------------
PLUMB_END = np.array([-6.45, -3.3, 0])
RECAP_X = [-3.6, .7, 5.0]
RECAP = ["不只數票數", "每一步都算", "只看關鍵字"]


def recap_item(n):
    g = VGroup(M("①②③"[n], .062, TXT_STRONG), T(RECAP[n], .058, TXT_STRONG)).arrange(RIGHT, buff=.2)
    return g.move_to(np.array([RECAP_X[n], RECAP_Y, 0]))


class Sc09(Sheet):
    SID = "sc09"
    END_BRAND = True

    def end_clear(self):
        tgt = self.pl_end.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.get_top()[1] + 1.2 - tgt.bodyg.get_bottom()[1]))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(self.pl_end, tgt, rate_func=rate_functions.ease_in_cubic), FadeOut(self.art_end)]

    def construct(self):
        A = self.A
        self.cam_set(BENCH2, BENCH_W)
        bal = cer_balance()
        W = stage_cer()
        self.add(*flat(W))
        r0, r1 = self.bal_set(bal)
        G = bench2_end()
        self.add(*G.values())
        N, scores, vs, fills = W["nodes"], W["scores"], W["walk"], W["fills"]
        # f1 把整條路再看一次：拉到全景，一道光沿五條路徑流過
        self.at(A("f1", 0), self.cam(RECAP_C, RECAP_W), FadeOut(VGroup(*G.values()), rate_func=RUSH), run_time=2.2, rate_func=SINE,
                sfx="swoosh", gain=.4)
        self.at(A("f1", .62), LaggedStart(*[ShowPassingFlash(row_path(i).set_stroke(GOLD, 6).set_fill(opacity=0), time_width=.4)
                                           for i in range(5)], lag_ratio=.12), *self.wake(bal, vs), run_time=1.7)
        it = [recap_item(n) for n in range(3)]
        # f2 ① 多數決每票一樣重；CER 看的是信心：天平再砸一次
        self.at(A("f2", .08), Write(it[0]), run_time=1.0, sfx="tick", gain=.6)
        self.at(A("f2", .45), *[bal.w[i].animate.set_value(1) for i in range(5)], run_time=.7)
        self.at(A("f2", .7))
        bal.hold()
        self.at(A("f2", .7), *[bal.w[i].animate.set_value(SCORES[i]) for i in range(5)], run_time=.6)
        self.at(A("f2", .7) + .65, *self.slam(bal), run_time=.9, sfx="bell", gain=.4)
        bal.wob.set_value(0)
        # f3 ② 每一步都算，不只看最後一步；越後面越重：三步的長條一欄一欄亮，越後面跳得越大
        self.at(A("f3", .0), it[0].animate.set_opacity(.45), Write(it[1]), run_time=1.0, sfx="tick", gain=.6)
        self.at(A("f3", .42), LaggedStart(*[AnimationGroup(*[Indicate(fills[i][j], color=TXT_STRONG, scale_factor=1.25 + .25 * j)
                                                             for i in range(5)]) for j in range(3)], lag_ratio=.4), run_time=1.6)
        # f4 ③ 每一步的信心只看關鍵字：每一步的中間答案亮起來
        self.at(A("f4", .0), it[1].animate.set_opacity(.45), Write(it[2]), run_time=1.0, sfx="tick", gain=.6)
        self.at(A("f4", .45), LaggedStart(*[AnimationGroup(*[Indicate(N[i][j].num, color=KEY, scale_factor=1.3) for i in range(5)])
                                           for j in range(3)], lag_ratio=.3), run_time=1.5)
        # f5 不用訓練，但補不了模型原本沒有的知識：三點全部亮起
        self.at(A("f5", .15), it[0].animate.set_opacity(1), it[1].animate.set_opacity(1), run_time=.8)
        self.at(A("f5", .6), Indicate(W["title"], color=GOLD, scale_factor=1.2), *calm(bal, vs), run_time=1.0)
        # f6（錘錘）更多細節在說明欄的文章裡
        pl, drop = self.plumb_in(PLUMB_END, .46)
        pl.set_mood("happy")
        self.at(A("f6", -.3), *drop, run_time=.8)
        self.lipsync(pl)
        art = VGroup(T("完整文章", .054, TXT), T("在說明欄", .054, TXT)).arrange(DOWN, buff=.12, aligned_edge=RIGHT)
        art.move_to(np.array([PLUMB_END[0] - .55, RECAP_Y + .05, 0]), aligned_edge=RIGHT)
        self.at(A("f6", .2), Write(art), *pl.look(DOWN), run_time=.9)
        self.at(A("f6", .48), *pl.hop(-.22), run_time=.4)
        self.at(A("f6", .66), *pl.hop(-.22), run_time=.4)
        self.at(A("f6", .86), *pl.blink(), run_time=.3)
        self.pl_end, self.art_end = pl, art
        self.finish()
