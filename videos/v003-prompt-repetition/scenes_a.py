"""v003 Prompt Repetition：sc01～sc05。大圖元件在 world.py，設計在 design.md。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa: E402,F401,F403

# ---------------- 開場的位置 ----------------
CARD1 = HOOK_C + LEFT * 4.4
CARD2 = HOOK_C + LEFT * .6
METER_C = HOOK_C + RIGHT * 4.3 + DOWN * .1
CORR_C = np.array([P1X[2], CORR_Y + .35, 0])       # 第一遍的中心（筆記到泡泡）
CORR_W = 12.5
CORR2_C = np.array([P1X[2], CORR_Y + .15, 0])     # sc02：只有讀者、還沒有筆記


def hook_end():
    """sc01 最後一格：兩張一樣的提示卡、97% 的儀表、標題。"""
    c1, c2 = prompt_card(CARD1), prompt_card(CARD2)
    m = Meter(METER_C, 97)
    ttl = T("Prompt Repetition", .085, TXT_STRONG).move_to(HOOK_C + DOWN * 2.25)
    return dict(c1=c1, c2=c2, m=m, ttl=ttl)


COVER_C = np.array([P1X[2], CORR_Y + .55, 0])


def prompt_strip():
    """一段 prompt（還沒切開）：五格連在一起的灰條。"""
    segs = VGroup(*[RoundedRectangle(corner_radius=.12, width=RW, height=.9).set_fill(MUTED, .25).set_stroke(MUTED, 2.5) for _ in range(5)])
    for i, sgm in enumerate(segs):
        sgm.move_to(np.array([P1X[i], CORR_Y, 0]))
    lab = T("prompt", .055, MUTED).next_to(segs, UP, buff=.7)
    return segs, lab


# ---------------- sc01：貼兩次 ----------------
class Sc01(Sheet):
    SID = "sc01"

    def construct(self):
        A = self.A
        self.cam_set(HOOK_C, FW)
        H = hook_end()
        c1, c2, m, ttl = H["c1"], H["c2"], H["m"], H["ttl"]
        m.v.set_value(0)
        m.live.update()
        self.add(c1.card)
        # h1 一張提示卡；複製、貼上
        self.at(A("h1", 0), LaggedStart(*[Create(x) for x in c1[1]], lag_ratio=.2), Write(c1[2]), run_time=1.1)
        cc = keycap("Ctrl+C", P1C, .055).next_to(c1, UP, buff=.35)
        cv = keycap("Ctrl+V", P2C, .055).next_to(c2, UP, buff=.35)
        self.at(A("h1", .45), FadeIn(cc, shift=DOWN * .15), run_time=.3)
        self.at(A("h1", .53), *press(cc), Highlight(c1, color=TXT_STRONG, scale_factor=1.05, inner=False), run_time=.4, sfx="click", gain=.5)
        self.at(A("h1", .66), FadeIn(cv, shift=DOWN * .15), run_time=.3)
        self.at(A("h1", .74), *press(cv), TransformFromCopy(c1, c2, path_arc=-.6), run_time=.8, sfx="pop", gain=.5)
        # h2 找名字的測驗：21% → 97%
        self.at(A("h2", 0), FadeOut(cc), FadeOut(cv), Create(m.arc), LaggedStart(*[Create(t) for t in m.ticks], lag_ratio=.05), FadeIn(m.live), run_time=.8)
        self.at(A("h2", .3), m.v.animate.set_value(21), run_time=.8, rate_func=SINE)
        self.at(A("h2", .66), m.v.animate(rate_func=rate_functions.ease_out_cubic).set_value(97), run_time=1.2, sfx="ding", gain=.5)
        # h3 錘錘：只是貼兩次？
        pl, drop = self.plumb_in(HOOK_C + RIGHT * 1.7 + DOWN * 1.2, .42)
        self.at(A("h2", .95), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("h3", .1), *pl.curl(), *pl.look(LEFT), run_time=1.0)
        self.at(A("h3", .6), *pl.tilt(.25), run_time=.6)
        # h4 答案藏在讀字的方式裡；Prompt Repetition
        self.at(A("h4", .1), *pl.tilt(-.25), *pl.look(RIGHT), run_time=.6)
        self.at(A("h4", .4), *self.plumb_out(pl), run_time=.6)
        self.remove(pl)
        self.at(A("h4", .62), Write(ttl), run_time=1.0, sfx="ding", gain=.35)
        self.at(A("h4", .88), Indicate(ttl, color=TXT_STRONG, scale_factor=1.06), run_time=.8)
        self.finish()


# ---------------- sc02：只能回頭看 ----------------
def sc02_end():
    return dict(rs=unlabeled(corridor(1)))


class Sc02(Sheet):
    SID = "sc02"

    def construct(self):
        A = self.A
        self.cam_set(HOOK_C, FW)
        H = hook_end()
        self.add(*H.values())
        for v in H.values():
            v.nocheck = True
        cover = paper_page(COVER_C, 3.55)
        # 片頭音樂：鏡頭往下拉，論文第 1 頁滑上來
        self.at(.25, self.cam(CORR2_C, CORR_W), Succession(Wait(1.0), FadeIn(cover, shift=UP * .6, run_time=1.4, rate_func=rate_functions.ease_out_cubic)),
                run_time=2.5, rate_func=SINE)
        self.remove(*H.values())
        # i1 這集要講的是 Prompt Repetition：標題底下畫線
        TC = cover.title_center()
        self.at(A("i1", .1), self.cam(COVER_C, 9.4), run_time=1.4, rate_func=SINE)
        u1 = cover.mark("pr", P2C)
        self.at(A("i1", .62), GrowFromEdge(u1, LEFT), run_time=.6, sfx="tick", gain=.35)
        # i2 最後也會講到什麼時候沒用：Non-Reasoning 畫線
        u2 = cover.mark("nr", DEC)
        self.at(A("i2", .35), GrowFromEdge(u2, LEFT), run_time=.6, sfx="tick", gain=.35)
        # r1 GPT-4、Gemini、Llama：封面退場
        chips = VGroup(*[T(s_, .06, TXT_STRONG) for s_ in ["GPT-4", "Gemini", "Llama"]]).arrange(RIGHT, buff=.9).move_to(CORR2_C + UP * 1.85)
        self.at(A("r1", 0), FadeOut(Group(cover, u1, u2), shift=UP * .4, run_time=.7), self.cam(CORR2_C, CORR_W),
                Succession(Wait(.45), LaggedStart(*[FadeIn(c, shift=DOWN * .2) for c in chips], lag_ratio=.3, run_time=1.3)), run_time=1.5, sfx="tick", gain=.4)
        # r2 Decoder-only
        dec = T("Decoder-only", .065, TXT_STRONG).move_to(CORR2_C + UP * 1.85)
        self.at(A("r2", .1), ReplacementTransform(chips, dec), run_time=.9)
        # r3 你的 prompt 切成一個一個 token：灰條裂成五個讀者（還沒有字）
        rs = unlabeled(corridor(1))
        segs, plab = prompt_strip()
        tok = T("token", .055, MUTED).move_to(np.array([P1X[2], CORR_Y - 1.35, 0]))
        self.at(A("r3", 0), FadeIn(segs, shift=UP * .15), FadeIn(plab), run_time=.6)
        self.at(A("r3", .4), *[ReplacementTransform(sg, r.body) for sg, r in zip(segs, rs)],
                LaggedStart(*[FadeIn(VGroup(*r[1:]), shift=UP * .1) for r in rs], lag_ratio=.18),
                Succession(Wait(.9), FadeIn(tok, shift=UP * .1, run_time=.5)), run_time=1.5, sfx="pop", gain=.4)
        self.remove(*[r.body for r in rs])
        self.add(*rs)
        self.at(A("r3", .8), FadeOut(plab), run_time=.4)
        # r4 只看得到自己和前面：一個讀頭由左走到右，每個讀者往左打光
        bms = [Beam(RP(1, i), P1X[0] - RW / 2) for i in range(5)]
        for b in bms:
            self.add(b)
        self.at(A("r4", 0), LaggedStart(*[b.reach.animate.set_value(1) for b in bms], lag_ratio=.35), run_time=2.4)
        # r5 後面的，一個都看不到：was 想往右看，眼罩擋住；右邊全暗
        was = rs[2]
        curtain = Rectangle(width=5.0, height=2.9).set_fill(BG, .78).set_stroke(width=0).move_to(np.array([P1X[3] + .3, CORR_Y, 0]))
        curtain.overlap_ok = curtain.nocheck = True
        self.at(A("r5", .05), FadeIn(curtain), shake(was.patch, n=4, amp=.05), *[b.reach.animate.set_value(0) for k, b in enumerate(bms) if k != 2],
                run_time=.8, sfx="thud", gain=.5)
        self.at(A("r5", .6), Wiggle(was.patch, scale_value=1.6), run_time=.8)
        # r6 半邊眼罩：只能回頭看
        lab = T("只能回頭看", .065, TXT_STRONG).move_to(CORR2_C + UP * 1.85)
        self.at(A("r6", .1), FadeOut(curtain), FadeOut(dec), *[b.reach.animate.set_value(1) for k, b in enumerate(bms) if k != 2], run_time=.8)
        self.at(A("r6", .35), LaggedStart(*[Wiggle(r.patch, scale_value=1.5, rotation_angle=.04 * TAU) for r in rs], lag_ratio=.12), Write(lab), run_time=1.3)
        self.at(A("r6", .9), FadeOut(lab), FadeOut(tok), *[b.reach.animate.set_value(0) for b in bms], run_time=.5)
        self.remove(*bms)
        self.finish()


# ---------------- sc03：模糊的筆記 ----------------
BARK = RP(1, 1)
ROUGH = RP(1, 3)
DOT_ = RP(1, 4)
BOWL_C = np.array([P1X[4] + 2.75, CORR_Y + NOTE_DY + .15, 0])     # 長廊右邊、和筆記同高
MIX_C, MIX_W = np.array([-3.1, 1.05, 0]), 14.8


def sc03_end():
    rs = corridor(1)
    rs[1] = reader("bark", P1C, BARK, conf=1)
    ns = [note(RP(1, i), "blur" if i == 1 else "plain") for i in range(5)]
    bb = bubble_at(BARK, meaning(0, 1.25))
    return dict(rs=rs, ns=ns, bb=bb)


def bowl(murk=0.0):
    b = Arc(radius=1.15, start_angle=PI, angle=PI, arc_center=BOWL_C + UP * .3).set_stroke(TXT_STRONG, 5)
    lid = Line(BOWL_C + UP * .3 + LEFT * 1.15, BOWL_C + UP * .3 + RIGHT * 1.15).set_stroke(TXT_STRONG, 2, .5)
    soup = Sector(radius=1.06, start_angle=PI, angle=PI, arc_center=BOWL_C + UP * .26).set_fill(interpolate_color(ManimColor("#3E3A7A"), ManimColor("#7A6E48"), murk), .95).set_stroke(width=0)
    g = VGroup(soup, b, lid)
    g.overlap_ok = True
    return g


class Sc03(Sheet):
    SID = "sc03"

    def construct(self):
        A = self.A
        self.cam_set(CORR2_C, CORR_W)
        rs = corridor(1)
        labs = [r.lab for r in rs]
        unlabeled(rs)
        self.add(*rs)
        # w1 例句 The bark was rough.：字一個一個寫到讀者身上
        self.at(A("w1", 0), self.cam(CORR_C, CORR_W), run_time=1.0, rate_func=SINE)
        self.at(A("w1", .5), LaggedStart(*[Write(l) for l in labs], lag_ratio=.25), run_time=1.6, sfx="tick", gain=.35)
        for r, l in zip(rs, labs):
            r.add(l)
        self.at(A("w1", .85), LaggedStart(*[Wiggle(r, scale_value=1.06, rotation_angle=.02 * TAU) for r in rs], lag_ratio=.12), run_time=.9)
        # w2 bark 兩個意思：狗叫聲／樹皮
        sense = VGroup(VGroup(dog_icon(1.6), T("狗叫聲", .05, TXT)).arrange(DOWN, buff=.15),
                       VGroup(tree_icon(1.6), T("樹皮", .05, TXT)).arrange(DOWN, buff=.15)).arrange(RIGHT, buff=1.2).move_to(BARK + UP * 1.95 + RIGHT * 2.2)
        self.at(A("w2", .1), Highlight(rs[1], color=GOLD, scale_factor=1.1, inner=False), run_time=.8)
        self.at(A("w2", .45), FadeIn(sense[0], shift=UP * .2), run_time=.6, sfx="pop", gain=.4)
        self.at(A("w2", .75), FadeIn(sense[1], shift=UP * .2), run_time=.6, sfx="pop", gain=.4)
        # w3 每讀一個 token 就留下一份筆記：Key、Value
        # w3 負責「回頭看」的是模型裡的 attention 層：整條長廊框起來，rough 往回打光
        x0, x1 = P1X[0] - RW / 2 - .95, P1X[4] + RW / 2 + .3
        y0, y1 = CORR_Y + NOTE_DY - .42, CORR_Y + RH / 2 + .22
        att = DashedVMobject(RoundedRectangle(corner_radius=.25, width=x1 - x0, height=y1 - y0), num_dashes=70).set_stroke(LIGHT, 3, .85)
        att.move_to(np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0]))
        att.nocheck = True
        att_l = T("Attention 層", .055, LIGHT).next_to(att, UP, buff=.18).align_to(att, LEFT).shift(RIGHT * .2)
        b_r = Beam(ROUGH, P1X[0] - RW / 2)
        self.add(b_r)
        self.at(A("w3", 0), FadeOut(sense), Create(att), run_time=1.0)
        self.at(A("w3", .35), Write(att_l), b_r.reach.animate.set_value(1), run_time=1.0, sfx="click", gain=.4)
        self.at(A("w3", .8), b_r.reach.animate.set_value(0), Wiggle(att_l, scale_value=1.1), run_time=.7)
        # w3b attention 層每讀一個 token，就留下一份筆記：Key、Value
        ns = [note(RP(1, i)) for i in range(5)]
        kv = VGroup(T("Key", .045, LIGHT), T("Value", .045, LIGHT)).arrange(DOWN, buff=.06).next_to(ns[0], LEFT, buff=.2)
        self.at(A("w3b", .2), LaggedStart(*[GrowFromPoint(n, r.get_bottom()) for n, r in zip(ns, rs)], lag_ratio=.18), run_time=1.6, sfx="pop", gain=.35)
        self.at(A("w3b", .72), Write(kv), run_time=.7)
        # w4 後面的 token 回頭看，看的是這些筆記：rough 的光照在前面的筆記上
        self.at(A("w4", .1), b_r.reach.animate.set_value(1), FadeOut(kv), run_time=1.0)
        self.at(A("w4", .5), LaggedStart(*[Highlight(n, color=LIGHT, scale_factor=1.08, inner=False) for n in ns[:3]], lag_ratio=.2), run_time=1.0)
        # w5 讀到 bark 時，只看得到 The bark（鏡頭推近）
        b_b = Beam(BARK, P1X[0] - RW / 2)
        self.add(b_b)
        later = VGroup(*rs[2:], *ns[2:])
        self.at(A("w5", 0), b_r.reach.animate.set_value(0), FadeOut(att), FadeOut(att_l), self.cam(np.array([P1X[1] + .6, 1.62, 0]), 11.2),
                later.animate.set_opacity(0), run_time=1.2, rate_func=SINE)
        self.at(A("w5", .55), b_b.reach.animate.set_value(1), run_time=.7)
        # w6 不知道是哪個意思：泡泡裡狗和樹疊在一起、讀者冒汗；筆記也變糊
        bb = bubble_at(BARK, meaning(0, 1.25))
        conf = reader("bark", P1C, BARK, conf=1)
        blur = note(BARK, "blur")
        q1 = T("狗叫聲？", .05, MUTED).next_to(bb, LEFT, buff=.3)
        q2 = T("樹皮？", .05, MUTED).next_to(bb, RIGHT, buff=.3)
        self.at(A("w6", .1), FadeIn(bb, scale=.6), Transform(rs[1], conf), FadeIn(q1), FadeIn(q2), run_time=.8, sfx="pop", gain=.4)
        self.at(A("w6", .45), shake(bb, n=6, amp=.06), run_time=.9)
        self.at(A("w6", .7), Transform(ns[1], blur), run_time=.8, sfx="slide", gain=.35)
        # w7 讀到 rough：它看得到整句，恍然大悟「是樹皮」
        back = [reader(w, P1C, RP(1, i)) for i, w in enumerate(WORDS)][2:] + [note(RP(1, i)) for i in range(2, 5)]
        self.at(A("w7", 0), FadeOut(q1), FadeOut(q2), b_b.reach.animate.set_value(0), *[Transform(a, b) for a, b in zip(later, back)], self.cam(CORR_C, CORR_W),
                run_time=1.1, rate_func=SINE)
        rb = bubble_at(ROUGH, VGroup(tree_icon(1.2), T("粗糙的樹皮", .05, BG)).arrange(RIGHT, buff=.15))
        happy = reader("rough", P1C, ROUGH, joy=1)
        self.at(A("w7", .3), b_r.reach.animate.set_value(1), Transform(rs[3], happy), run_time=.8)
        self.at(A("w7", .62), FadeIn(rb, scale=.6), run_time=.6, sfx="ding", gain=.35)
        # w8 回頭拿 bark 的筆記，拿到的還是糊的：表情垮掉
        got = blur.copy()
        self.at(A("w8", .05), FadeOut(rb), got.animate.scale(1.3).move_to(ROUGH + UP * 1.55).set_z_index(4), run_time=1.1, path_arc=-.9)
        sad = reader("rough", P1C, ROUGH, conf=1)
        self.at(A("w8", .6), Transform(rs[3], sad), shake(got, n=4, amp=.05), run_time=.8, sfx="thud", gain=.5)
        # w9 錘錘：看懂了也沒用？
        pl, drop = self.plumb_in(np.array([P1X[4] + 1.2, CORR_Y + .8, 0]), .38)
        self.at(A("w8", .92), *drop, run_time=.6)
        self.lipsync(pl)
        self.at(A("w9", .05), *pl.shake_head(), run_time=1.0)
        # w10 那份筆記，當初讀到 bark 時就寫好了
        self.at(A("w10", .2), Highlight(ns[1], color=GOLD, scale_factor=1.25, inner=False), FadeOut(got), *self.plumb_out(pl), run_time=.9)
        self.remove(pl)
        self.at(A("w10", .6), Highlight(rs[1], color=TXT_STRONG, scale_factor=1.08, inner=False), run_time=.8)
        # w11 最後一個 token：看過所有內容（鏡頭拉開，右邊留給碗；句點亮一圈，光掃過整句）
        b_d = Beam(DOT_, P1X[0] - RW / 2)
        self.add(b_d)
        self.at(A("w11", 0), b_r.reach.animate.set_value(0), Transform(rs[3], reader("rough", P1C, ROUGH)), self.cam(MIX_C, MIX_W),
                run_time=1.1, rate_func=SINE)
        self.at(A("w11", .45), b_d.reach.animate.set_value(1), Highlight(rs[4], color=TXT_STRONG, scale_factor=1.12, inner=False), run_time=1.0, sfx="slide", gain=.35)
        # w12 照注意力的比重混在一起：每份筆記拉一條流到碗裡，粗細＝比重（舉例，不標數字）
        bw = bowl()
        wts = [7, 16, 6, 13, 9]
        entry = BOWL_C + UP * .45 + LEFT * .55
        flows = VGroup()
        for i, (n, w_) in enumerate(zip(ns, wts)):
            p0 = n.get_bottom() + DOWN * .02
            yb = CORR_Y + NOTE_DY - .55 - .06 * i
            f = CubicBezier(p0, np.array([p0[0], yb, 0]), np.array([entry[0] - 1.3, yb, 0]), entry)
            f.set_stroke("#9C8A55" if i == 1 else LIGHT, w_, .9)
            f.overlap_ok = f.cross_ok = f.dots_ok = True
            flows.add(f)
        self.at(A("w12", 0), FadeIn(bw, shift=UP * .3), run_time=.6)
        self.at(A("w12", .25), LaggedStart(*[Create(f) for f in flows], lag_ratio=.12), run_time=1.6)
        self.at(A("w12", .7), *[ShowPassingFlash(f.copy().set_stroke(TXT_STRONG, f.get_stroke_width() * .6, 1), time_width=.35) for f in flows],
                shake(bw, n=3, amp=.04), run_time=1.0)
        # w13 原料是糊的：猛攪，還是混濁（bark 那條是泥色）
        spoon = Line(BOWL_C + UP * 1.55 + RIGHT * .25, BOWL_C + DOWN * .25).set_stroke(TXT_STRONG, 5)
        spoon.overlap_ok = True
        murky = bowl(1.0)
        self.at(A("w13", .05), FadeIn(spoon), Transform(bw, murky), Indicate(flows[1], color="#B39A5A", scale_factor=1.0), run_time=.8)
        self.at(A("w13", .3), Rotate(spoon, .5, about_point=BOWL_C + UP * 1.55, rate_func=rate_functions.wiggle), shake(bw, n=6, amp=.05), run_time=1.6,
                sfx="slide", gain=.35)
        self.at(A("w13", .75), Rotate(spoon, .5, about_point=BOWL_C + UP * 1.55, rate_func=rate_functions.wiggle), shake(bw, n=4, amp=.05), run_time=1.1)
        # w14 Path Dependency：路徑依賴（寫在碗的上方）
        pd = VGroup(T("Path Dependency", .055, TXT_STRONG), T("路徑依賴", .055, MUTED)).arrange(DOWN, buff=.15).move_to(np.array([BOWL_C[0] - .75, CORR_Y + 1.15, 0]))
        self.at(A("w14", .2), Write(pd), Wiggle(bb, scale_value=1.12), run_time=1.1, sfx="ding", gain=.35)
        self.at(A("w14", .85), FadeOut(VGroup(pd, bw, spoon, flows)), b_d.reach.animate.set_value(0), Transform(ns[0], note(RP(1, 0))), Transform(rs[0], reader("The", P1C, RP(1, 0))), self.cam(CORR_C, CORR_W), run_time=.7)
        self.remove(b_d, b_b, b_r)
        self.finish()


# ---------------- sc04：順序怎麼擺 ----------------
XA = [-7.6, -6.0, -4.4, -2.6]          # 選項在前：選項 A、B、C、問題
XB = [.4] + [1.85 + 1.1 * k for k in range(4)]   # 問題在前：問題、資料 ×5
NAME_Y = LAB_Y - 2.05
NAME_X0, NAME_DX = -7.9, .24
QN = np.array([5.1, NAME_Y, 0])
LABV_C, LABV_W = np.array([-1.0, LAB_Y - .1, 0]), 17.0     # 實驗區全景：兩種排法＋名單
LAB_C, LAB_W = np.array([0, LAB_Y - .4, 0]), 20.0


def small(word, color, p, w=1.5, **kw):
    return reader(word, color, p, w=w, h=1.5, frac=.052, **kw)


def qmark_at(r):
    t = T("？", .075, QC).next_to(r, UP, buff=.12)
    t.overlap_ok = True
    return t


def row_a(conf=1.0):
    rs = [small(s, TXT, np.array([x, LAB_Y, 0]), conf=conf) for s, x in zip(["選項A", "選項B", "選項C"], XA[:3])]
    rs.append(small("問題", QC, np.array([XA[3], LAB_Y, 0])))
    return rs


def row_b():
    q = small("問題", QC, np.array([XB[0], LAB_Y, 0]), op=.35)
    ds = [reader("資料", TXT, np.array([x, LAB_Y, 0]), w=1.05, h=1.05, frac=.045, op=.8) for x in XB[1:]]
    return [q] + ds


def names(lit=None, gold=False):
    g = VGroup()
    for k in range(50):
        c = GOLD if (gold and k == 24) else TXT
        sq = RoundedRectangle(corner_radius=.04, width=.22, height=.55).set_fill(c, .22 if not (gold and k == 24) else .9).set_stroke(c, 1.5)
        sq.move_to(np.array([NAME_X0 + k * NAME_DX, NAME_Y, 0]))
        g.add(sq)
    return g


def name_q(conf=0.0, joy=0.0):
    return small("第 25 個？", QC, QN, w=2.1, conf=conf, joy=joy)


def lab_labels():
    a = T("選項在前", .058, MUTED).move_to(np.array([(XA[0] + XA[3]) / 2, LAB_Y + 2.1, 0]))
    b = T("問題在前", .058, MUTED).move_to(np.array([(XB[0] + XB[-1]) / 2, LAB_Y + 2.1, 0]))
    return a, b


def sc04_end():
    D = sc03_end()
    D["ra"] = row_a()
    D["qa"] = [qmark_at(r) for r in D["ra"][:3]]
    la, lb = lab_labels()
    D["la"] = la
    D["nm"] = names()
    D["nq"] = name_q(conf=1)
    return D


class Sc04(Sheet):
    SID = "sc04"

    def construct(self):
        A = self.A
        self.cam_set(CORR_C, CORR_W)
        D = sc03_end()
        self.add(*flat(D))
        # o1 順序很敏感：鏡頭往下到實驗區
        la, lb = lab_labels()
        ra = row_a(conf=0)
        pos = [r.get_center() for r in ra]
        rw_, rh_ = ra[0][0].width, ra[0][0].height
        def seg(c, col):
            return RoundedRectangle(corner_radius=.12, width=rw_, height=rh_ * .55).set_fill(col, .3).set_stroke(col, 2.5).move_to(c)
        sg = VGroup(seg(pos[0], QC), *[seg(pos[k], MUTED) for k in (1, 2, 3)])
        self.at(A("o1", 0), self.cam(np.array([-5.2, LAB_Y + .2, 0]), 14.2),
                Succession(Wait(.7), LaggedStart(*[FadeIn(x, shift=UP * .15) for x in sg], lag_ratio=.15, run_time=.8)), run_time=1.6, rate_func=SINE)
        # 順序一換：橘色（問題）從最前面跳到最後面
        self.at(A("o1", .62), sg[0].animate(path_arc=-PI * .8).move_to(pos[3]), *[sg[k].animate.move_to(pos[k - 1]) for k in (1, 2, 3)],
                run_time=1.0, sfx="swoosh", gain=.35)
        # o2 先放選項、再放問題：片段變成讀者
        self.at(A("o2", .1), Write(la), run_time=.7)
        order = [sg[1], sg[2], sg[3], sg[0]]
        self.at(A("o2", .35), *[ReplacementTransform(x, r) for x, r in zip(order, ra)], run_time=1.1, sfx="tick", gain=.4)
        # o3 讀選項時還不知道問題：頭上全是「？」、冒汗
        qa = [qmark_at(r) for r in ra[:3]]
        conf_a = row_a(conf=1)
        self.at(A("o3", .1), LaggedStart(*[AnimationGroup(Transform(r, c), GrowFromCenter(q)) for r, c, q in zip(ra[:3], conf_a[:3], qa)], lag_ratio=.2),
                run_time=1.4, sfx="pop", gain=.4)
        self.at(A("o3", .65), *[shake(r, n=3, amp=.04) for r in ra[:3]], run_time=.8)
        # o4 先放問題、再放一大段資料
        rb = row_b()
        q0 = small("問題", QC, rb[0].get_center())
        self.at(A("o4", 0), self.cam(LABV_C, LABV_W), Write(lb), GrowFromCenter(q0), run_time=1.2, rate_func=SINE)
        self.at(A("o4", .5), LaggedStart(*[FadeIn(d, shift=LEFT * .4) for d in rb[1:]], lag_ratio=.12), run_time=1.4)
        # o5 資料一長，問題被忘掉：問題讀者越來越淡、縮小
        self.at(A("o5", .35), Transform(q0, rb[0]), run_time=1.6, sfx="slide", gain=.35)
        self.at(A("o5", .75), *[shake(d, n=2, amp=.03) for d in rb[1:4]], run_time=.7)
        # o6 極端的例子：50 個名字，最後才問第 25 個
        nm = names()
        nq = name_q()
        lab50 = T("50 個名字", .058, MUTED).next_to(nm, DOWN, buff=.3).align_to(nm, LEFT)
        self.at(A("o6", 0), FadeOut(VGroup(q0, *rb[1:], lb)), run_time=.8)
        self.at(A("o6", .25), LaggedStart(*[GrowFromCenter(s) for s in nm], lag_ratio=.03), Write(lab50), run_time=1.6, sfx="tick", gain=.35)
        n25 = T("第 25 個", .045, TXT).next_to(nm[24], DOWN, buff=.3)
        self.at(A("o6", .7), GrowFromCenter(nq), run_time=.7, sfx="pop", gain=.4)
        self.at(A("o6", .88), nm[24].animate.set_stroke(TXT_STRONG, 3), FadeIn(n25, shift=UP * .1), run_time=.6)
        # o7 讀到第 25 個時不知道要找它：讀頭走過，第 25 個沒有被特別記住
        head = Triangle().scale(.14).rotate(PI).set_fill(LIGHT, 1).set_stroke(width=0).move_to(nm[0].get_top() + UP * .25)
        head.transient = True
        q25 = T("？", .06, MUTED).next_to(nm[24], UP, buff=.12)
        q25.transient = True
        self.at(A("o7", 0), FadeIn(head), run_time=.3)
        self.at(A("o7", .08), head.animate.move_to(nm[-1].get_top() + UP * .25),
                Succession(*[Indicate(nm[k], color=TXT_STRONG, scale_factor=1.15, run_time=.12) for k in range(0, 50, 3)]),
                Succession(Wait(.95), FadeIn(q25, scale=.6, run_time=.25), Wait(.6), FadeOut(q25, run_time=.35)),
                run_time=2.2, rate_func=linear)
        self.at(A("o7", .85), FadeOut(head), run_time=.3)
        # o8 讀到問題，已經來不及回頭：問題讀者冒汗、往回打的光照到的第 25 個是普通的
        b_q = Beam(QN + UP * .05, NAME_X0 - .2, op=.34)
        self.add(b_q)
        self.at(A("o8", 0), b_q.reach.animate.set_value(1), Transform(nq, name_q(conf=1)), run_time=1.1)
        self.at(A("o8", .55), Indicate(nm[24], color=QC, scale_factor=1.6), shake(nq, n=3, amp=.05), run_time=.9, sfx="thud", gain=.45)
        # o9 錘錘：怎麼讓前面也看到後面？
        pl, drop = self.plumb_in(np.array([3.6, LAB_Y + .3, 0]), .42)
        self.at(A("o9", 0), *drop, b_q.reach.animate.set_value(0), run_time=.6)
        self.lipsync(pl)
        self.at(A("o9", .2), *pl.curl(), *pl.look(LEFT), run_time=1.0)
        self.at(A("o9", .75), *pl.tilt(.2), run_time=.5)
        self.at(A("o9", .9), *pl.tilt(-.2), *self.plumb_out(pl), FadeOut(lab50), FadeOut(n25), nm[24].animate.set_stroke(TXT, 1.5), run_time=.6)
        self.remove(pl, b_q)
        self.finish()


def flat(D):
    out = []
    for v in D.values():
        if isinstance(v, (list, tuple)):
            out.extend(v)
        else:
            out.append(v)
    return out


# ---------------- sc05：貼第二遍 ----------------
SEAM_C, SEAM_W = np.array([0, CORR_Y + .5, 0]), 20.5


def sc05_end():
    D = sc04_end()
    D["sm"] = seam()
    D["rs2"] = corridor(2)
    D["rs2"][1] = reader("bark", P2C, RP(2, 1), joy=1)
    D["ns2"] = [note(RP(2, i), "gold" if i == 1 else "plain") for i in range(5)]
    D["bb2"] = bubble_at(RP(2, 1), meaning(1, 1.25))
    D["l1"], D["l2"] = pass_label(1), pass_label(2)
    D["ra2"] = row_a2()
    return D


RA2_DX = 6.9


def row_a2():
    """sc05 p11：選擇題貼第二遍（第二遍的選項已經知道問題，開心）。"""
    rs = [small(s, P2C, np.array([x + RA2_DX, LAB_Y, 0]), joy=1) for s, x in zip(["選項A", "選項B", "選項C"], XA[:3])]
    rs.append(small("問題", QC, np.array([XA[3] + RA2_DX, LAB_Y, 0])))
    return rs


class Sc05(Sheet):
    SID = "sc05"

    def construct(self):
        A = self.A
        self.cam_set(LABV_C, LABV_W)
        D = sc04_end()
        self.add(*flat(D))
        rs = D["rs"]
        # p1 Google Research，2025 年 12 月：鏡頭回到長廊，往右留出空位
        src = paper_page(np.array([P2X[2] + .5, CORR_Y - .35, 0]), 4.9)
        self.at(A("p1", 0), self.cam(SEAM_C, SEAM_W), Succession(Wait(.7), FadeIn(src, shift=UP * .2)), run_time=1.8, rate_func=SINE)
        # p2 原封不動再複製一遍：P → P ; P
        sm = seam()
        rs2 = corridor(2)
        ns2 = [note(RP(2, i)) for i in range(5)]
        l1, l2 = pass_label(1), pass_label(2)
        self.at(A("p2", 0), FadeOut(src), Write(l1), run_time=.6)
        self.at(A("p2", .25), *[TransformFromCopy(a, b, path_arc=-.5) for a, b in zip(rs, rs2)], Create(sm), run_time=1.3, sfx="pop", gain=.5)
        self.at(A("p2", .7), Write(l2), Indicate(sm, color=GOLD, scale_factor=1.05), run_time=.8)
        # p3 第一遍和平常一樣：光只照到第一遍的開頭
        bms1 = [Beam(RP(1, i), P1X[0] - RW / 2) for i in range(5)]
        for b in bms1:
            self.add(b)
        self.at(A("p3", .1), LaggedStart(*[b.reach.animate.set_value(1) for b in bms1], lag_ratio=.2), run_time=1.6)
        self.at(A("p3", .75), *[b.reach.animate.set_value(0) for b in bms1], run_time=.6)
        self.remove(*bms1)
        # p4 第二遍：每個位置都照得到整個第一遍（紫色的浪掃過去）
        bms2 = [Beam(RP(2, i), P1X[0] - RW / 2, op=.18) for i in range(5)]
        for b in bms2:
            self.add(b)
        self.at(A("p4", .1), LaggedStart(*[b.reach.animate.set_value(1) for b in bms2], lag_ratio=.15), run_time=1.8, sfx="slide", gain=.4)
        self.at(A("p4", .7), LaggedStart(*[GrowFromPoint(n, r.get_bottom()) for n, r in zip(ns2, rs2)], lag_ratio=.1), run_time=1.0)
        # p5 第二遍的 bark 回頭一看：第一遍的 rough 就在那裡
        self.at(A("p5", 0), *[b.reach.animate.set_value(0) for k, b in enumerate(bms2) if k != 1], self.cam(SEAM_C, SEAM_W),
                run_time=1.0, rate_func=SINE)
        look = ArcBetweenPoints(RP(2, 1) + UP * .95 + LEFT * .3, RP(1, 3) + UP * .95, angle=PI / 3).set_stroke(LIGHT, 7)
        look.add_tip(tip_length=.32, tip_width=.32)
        look.overlap_ok = look.cross_ok = True
        self.at(A("p5", .25), Create(look), run_time=.8)
        self.at(A("p5", .6), Highlight(rs[3], color=GOLD, scale_factor=1.18, inner=False), run_time=.8, sfx="click", gain=.5)
        # p6 第二遍寫下的筆記：看過全文的版本，金色的樹皮
        bb2 = bubble_at(RP(2, 1), meaning(1, 1.25))
        self.at(A("p6", .05), FadeOut(look), Transform(rs2[1], reader("bark", P2C, RP(2, 1), joy=1)), FadeIn(bb2, scale=.5), run_time=.9, sfx="ding", gain=.5)
        self.at(A("p6", .5), Transform(ns2[1], note(RP(2, 1), "gold")), run_time=.8)
        self.at(A("p6", .8), Wiggle(D["bb"], scale_value=1.06), Wiggle(bb2, scale_value=1.18), run_time=.6)
        # p7 錘錘：原來如此！拉直成「！」並發光
        pl, drop = self.plumb_in(np.array([P2X[3] + .6, CORR_Y + 2.6, 0]), .42)
        pl.set_curled("wow")
        self.at(A("p6", .95), *drop, run_time=.5)
        self.lipsync(pl)
        self.at(A("p7", .05), *pl.straighten(), *pl.mood("happy"), run_time=.8, sfx="bell", gain=.5)
        self.at(A("p7", .4), *pl.light_on(), *pl.hop(.25), run_time=.8)
        # p8 生成答案時高度依賴第二遍的筆記
        self.at(A("p8", 0), *self.plumb_out(pl), bms2[1].reach.animate.set_value(0), self.cam(SEAM_C + DOWN * .5, SEAM_W), run_time=1.0)
        self.remove(pl, *bms2)
        self.at(A("p8", .4), LaggedStart(*[Highlight(n, color=P2C, scale_factor=1.1, inner=False) for n in ns2], lag_ratio=.12), run_time=1.2)
        # p9、p10 不改架構就模擬雙向：偽雙向注意力
        arr = DoubleArrow(np.array([P1X[0], CORR_Y - 2.35, 0]), np.array([P2X[-1], CORR_Y - 2.35, 0]), buff=0, stroke_width=9, tip_length=.42).set_color(LIGHT)
        arr.cross_ok = arr.overlap_ok = True
        self.at(A("p9", .2), GrowFromCenter(arr), run_time=1.0)
        name_ = T("偽雙向注意力", .075, LIGHT).move_to(np.array([0, CORR_Y - 3.05, 0]))
        self.at(A("p10", .3), Write(name_), run_time=1.0, sfx="ding", gain=.4)
        # p11 選擇題：第二遍讀選項時已經知道問題
        self.at(A("p11", 0), FadeOut(VGroup(arr, name_)), self.cam(LABV_C, LABV_W), run_time=1.2, rate_func=SINE)
        ra2 = row_a2()
        self.at(A("p11", .3), *[TransformFromCopy(a, b, path_arc=-.4) for a, b in zip(D["ra"], ra2)], run_time=.9, sfx="pop", gain=.4)
        b_a = Beam(ra2[0].get_center(), XA[3] - .75, op=.4)
        self.add(b_a)
        self.at(A("p11", .6), b_a.reach.animate.set_value(1), Highlight(D["ra"][3], color=QC, scale_factor=1.15, inner=False), run_time=.8)
        self.at(A("p11", .82), b_a.reach.animate.set_value(0), LaggedStart(*[r.animate(rate_func=there_and_back).shift(UP * .2) for r in ra2[:3]], lag_ratio=.15), run_time=.7)
        self.remove(b_a)
        self.finish()
