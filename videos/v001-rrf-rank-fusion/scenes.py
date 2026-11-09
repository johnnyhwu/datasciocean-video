"""v001 RRF 第四版：一張大圖（混合搜尋管線），鏡頭跟著走。設計：design-v4.md。

世界座標（不是畫面座標）：
  查詢 Q ─┬─ 向量搜尋 RV ── 向量榜（橫排卡片，第 1 名在左）──┐
          └─ 全文搜尋 RF ── 全文榜 ───────────────────────────┴─ Σ 融合 ── 總榜（直排）──（sc08）reranker ── 新總榜
  工作台：sc03 的數線（BENCH1）、sc06 的 k 旋鈕（BENCH2）、sc07/08 的投影片源頭（BENCH3）。

場景之間沒有淡出：每場開頭用 restore 直接擺出上一場最後一格的樣子（lib/checks/seams.py 驗證）。
動作語彙（研究結論）：公式與數字用 Write；線用 Create；框用 DrawBorderThenFill；由別的東西變來的用 TransformFromCopy／ReplacementTransform；
同一組用 LaggedStart 錯開；淡入只給殘影。畫面不放句子，句子交給字幕。
"""
from kit import *  # noqa: F401,F403

VEC, FTS, RANK, SCORE, KC = C["向量"], C["全文"], C["名次"], C["分數"], C["k"]
ANS = GOOD                       # 正確答案（全片只有它是綠色）
CARD_FILL = SEA
SW = 2.6                         # 細線粗細

# ---------------- 世界的位置 ----------------
Q = np.array([-7.4, 0, 0])
RV, RF = np.array([-5.4, 1.85, 0]), np.array([-5.4, -1.85, 0])
ROW_X = [-3.85 + i * 1.25 for i in range(4)]
ROW_Y = {"v": 1.85, "f": -1.85}
SIG = np.array([2.3, 0, 0])
TOT_X = 4.4
TOT_Y = [1.6 - 0.8 * i for i in range(5)]
STAGE, STAGE_W = np.array([-1.29, 0.05, 0]), 15.2   # 整條管線（Q 到總榜）在畫面中的中心與鏡頭寬度
BENCH1 = np.array([-1.7, -6.9, 0])        # sc03：數線
BENCH2 = np.array([4.4, -6.9, 0])         # sc06：k 旋鈕
BENCH3 = np.array([-10.9, -7.5, 0])       # sc07/08：投影片源頭
RR = np.array([6.72, 0, 0])                # sc08：reranker（總榜右邊先接一個大括號）
FIN_X = 8.3


def lane_color(k):
    return VEC if k == "v" else FTS


# ---------------- 元件 ----------------
def card(letter, color=TXT, w=.92, h=.66, star=False):
    """一份文件：圓角卡片＋襯線字母（正確答案是一顆綠星）。"""
    r = RoundedRectangle(corner_radius=.1, width=w, height=h).set_stroke(ANS if star else color, 2.2).set_fill(CARD_FILL, 1)
    if star:
        g = Star(5, outer_radius=.2, inner_radius=.085).set_fill(ANS, 1).set_stroke(width=0)
    else:
        g = M(letter, .055, color)
    g.move_to(r)
    c = VGroup(r, g)
    c.box, c.glyph, c.letter = r, g, ("★" if star else letter)
    return c


def ans_card(h=.66):
    return card("", ANS, h=h, star=True)


def node(color, r=.32, fill=.14):
    return Circle(r).set_stroke(color, 3).set_fill(color, fill)


def vec_icon(color=VEC, s=.17):
    """向量搜尋：兩支從同一點出發的箭頭（夾角＝像不像）。"""
    o = np.array([-s * .8, -s * .7, 0])
    a1 = Arrow(o, o + np.array([s * 1.9, s * .5, 0]), buff=0, stroke_width=3, max_tip_length_to_length_ratio=.35).set_color(color)
    a2 = Arrow(o, o + np.array([s * 1.2, s * 1.6, 0]), buff=0, stroke_width=3, max_tip_length_to_length_ratio=.35).set_color(color)
    return VGroup(a1, a2)


def fts_icon(color=FTS):
    return M("Aa", .05, color)


def retriever(k):
    p = RV if k == "v" else RF
    c = lane_color(k)
    n = node(c).move_to(p)
    ic = (vec_icon() if k == "v" else fts_icon()).move_to(p)
    lab = T("向量搜尋" if k == "v" else "全文搜尋", .05, c)
    lab.next_to(n, UP if k == "v" else DOWN, buff=.16)
    g = VGroup(n, ic, lab)
    g.node, g.icon, g.lab = n, ic, lab
    return g


def query_node():
    n = Circle(.34).set_stroke(TXT_STRONG, 2.6).set_fill(TXT_STRONG, .08).move_to(Q)
    ring = Circle(.11).set_stroke(TXT_STRONG, 2.4).move_to(Q + UL * .04)
    handle = Line(ring.get_center() + DR * .08, ring.get_center() + DR * .2).set_stroke(TXT_STRONG, 2.8)
    lab = T("查詢", .05, TXT_STRONG).next_to(n, DOWN, buff=.16)
    g = VGroup(n, VGroup(ring, handle), lab)
    g.node, g.lens, g.lab = n, g[1], lab
    return g


def bend(a, b, k=.25, color=LINE, w=SW, op=.85):
    """a→b 的平滑曲線（朝法向彎 k）。只畫線，不填色。"""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    nrm = np.array([-d[1], d[0], 0]) / (np.linalg.norm(d) + 1e-9)
    m = (a + b) / 2 + nrm * k * np.linalg.norm(d)
    return VMobject().set_points_smoothly([a, (a + m) / 2 + nrm * k * .12 * np.linalg.norm(d), m,
                                           (m + b) / 2 + nrm * k * .12 * np.linalg.norm(d), b]) \
        .set_stroke(color, w, op).set_fill(opacity=0)


def seg(a, b, color=LINE, w=SW, op=.85):
    return Line(a, b).set_stroke(color, w, op)


def q_links():
    return VGroup(bend(Q + RIGHT * .34, RV + LEFT * .32, .1, VEC), bend(Q + RIGHT * .34, RF + LEFT * .32, -.1, FTS))


def row_pos(k, i):
    return np.array([ROW_X[i], ROW_Y[k], 0])


def lane_in(k):
    """檢索器 → 該路第 1 張卡。"""
    p = RV if k == "v" else RF
    return seg(p + RIGHT * .32, row_pos(k, 0) + LEFT * .5, lane_color(k))


def lane_out(k):
    """該路最後一張卡 → Σ。"""
    a = row_pos(k, 3) + RIGHT * .5
    b = SIG + (UL if k == "v" else DL) * .31
    return bend(a, b, -.14 if k == "v" else .14, lane_color(k))


def sigma_node():
    n = Circle(.44).set_stroke(GOLD, 3).set_fill(GOLD, .1).move_to(SIG)
    s = M("Σ", .07, TXT_STRONG).move_to(SIG)
    g = VGroup(n, s)
    g.node, g.sym = n, s
    return g


def rrf_label():
    return M("RRF", .052, GOLD).next_to(SIG, DOWN, buff=.66)


def tot_slot(i):
    return np.array([TOT_X, TOT_Y[i], 0])


def slot_box(p, h=.6):
    return DashedVMobject(RoundedRectangle(corner_radius=.1, width=.92, height=h), num_dashes=26) \
        .set_stroke(LINE, 1.6, .7).move_to(p)


def tot_frame():
    """總榜：五個虛線空位＋左側名次＋標題＋從 Σ 接過來的線。"""
    slots = VGroup(*[slot_box(tot_slot(i)) for i in range(5)])
    nums_ = VGroup(*[M(str(i + 1), .05, RANK).next_to(slots[i], RIGHT, buff=.2) for i in range(5)])
    head = T("總榜", .05, TXT).next_to(slots, UP, buff=.22)
    link = seg(SIG + RIGHT * .44, np.array([TOT_X - .5, SIG[1], 0]), GOLD, SW, .8)
    g = VGroup(link, slots, nums_, head)
    g.link, g.slots, g.nums, g.head = link, slots, nums_, head
    return g


def tot_card(letter, i):
    c = ans_card(.6) if letter == "*" else card(letter, h=.6)
    return c.move_to(tot_slot(i))


def row_cards(k, letters):
    """一排卡片（'*'＝正確答案）。"""
    g = VGroup()
    for i, L in enumerate(letters):
        c = ans_card() if L == "*" else card(L)
        g.add(c.move_to(row_pos(k, i)))
    return g


def row_ranks(k, n=4):
    return VGroup(*[M(str(i + 1), .05, RANK).move_to(row_pos(k, i) + UP * .6) for i in range(n)])


def row_scores(k, vals):
    return VGroup(*[M(v, .046, SCORE).move_to(row_pos(k, i) + DOWN * .6) for i, v in enumerate(vals)])


def pulse_path(k):
    """查詢 → 檢索器 → 第 1 張卡 的路徑（脈衝沿它走）。"""
    a = q_links()[0 if k == "v" else 1]
    b = lane_in(k)
    path = VMobject()
    path.set_points(np.vstack([a.points, b.points]))
    return path


def pdot(color):
    d = Dot(radius=.06, color=color).set_z_index(5)
    d.transient = d.overlap_ok = d.nocheck = True
    return d


def travel(x, path, fade=.2):
    """點沿路徑走，最後一段淡掉。走完直接 self.remove() 會「跳」一下（2026-11-10 逐格檢查）。"""
    def upd(m, a):
        m.move_to(path.point_from_proportion(a))
        m.set_opacity(min(1.0, (1 - a) / fade))
    return UpdateFromAlphaFunc(x, upd, rate_func=linear)


class Live(VGroup):
    """跟著 ValueTracker 每格重算的讀數。fmt(v) → 字串；place(t) 擺位置。"""

    def __init__(self, tracker, fmt, frac=.05, color=TXT, place=None, italic=False):
        super().__init__()
        self.tr, self.fmt, self.fr, self.col, self.it = tracker, fmt, frac, color, italic
        self.place = place or (lambda t: t)
        self.add(self._make())
        self.add_updater(lambda m: m[0].become(m._make()))

    def _make(self):
        t = M(self.fmt(self.tr.get_value()), self.fr, self.col, self.it)
        self.place(t)
        return t


# ---------------- 場景基底：大圖的狀態 ----------------
class Sheet(Timed):
    BG = "flat"

    def plumb_in(self, p, scale=.42):
        """錘錘從畫面上方垂下來，停在世界座標 p。回傳 (錘錘, 動畫)。"""
        top = self.camera.frame.get_top()[1] + .6
        pl = Plumb(scale, top_y=top).place(p + UP * 4)
        pl.set_mood("neutral")
        target = pl.copy().place(p)
        return pl, [Transform(pl, target, rate_func=rate_functions.ease_out_back)]

    def plumb_out(self, pl):
        tgt = pl.copy()
        tgt.bodyg.shift(UP * 4.5)
        tgt.rope.become(tgt._straight_rope())
        return [Transform(pl, tgt, rate_func=rate_functions.ease_in_cubic)]


def dots_more(k):
    """第 4 個位置的「⋯」（後面還有更多結果）。"""
    return M("⋯", .05, MUTED).move_to(row_pos(k, 3))


def doc_d():
    """開場那份文件：卡片上一個斜體 d（就是之後公式 RRF(d) 的 d）。"""
    c = card("d", TXT_STRONG)
    c.glyph.become(M("d", .055, TXT_STRONG, italic=True).move_to(c.box))
    return c.scale(1.35).move_to(SIG)


# 開場鏡頭：近拍融合站
HOOK_C, HOOK_W = np.array([2.2, 0, 0]), 9.6


def hook_end():
    """sc01 最後一格：文件 d、兩條接進來的線、兩個暫時的通道名、RRF。"""
    d = doc_d()
    lv, lf = lane_out("v"), lane_out("f")
    nv = T("向量搜尋", .046, VEC).scale(.62).next_to(lv.get_start(), LEFT, buff=.15)
    nf = T("全文搜尋", .046, FTS).scale(.62).next_to(lf.get_start(), LEFT, buff=.15)
    return d, lv, lf, nv, nf, rrf_label().scale(.75, about_edge=UP)


class Sc01(Sheet):
    SID = "sc01"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(HOOK_C, HOOK_W)
        d, lv, lf, nv, nf, rrf = hook_end()
        self.add(d)                                     # 開場：一份文件，靜靜的 1 秒
        # h1 同一個問題，丟給兩種搜尋：兩條線從左邊接進文件
        self.at(A("h1", .35), Create(lv), Create(lf), run_time=1.2)
        self.at(A("h1", .7), Write(nv), Write(nf), run_time=.8)
        # h2 / h3 兩個分數，各自寫在自己那條線旁
        sv = M("0.83", .06, SCORE).scale(.8).move_to(SIG + UP * .82)
        sf = M("12.4", .06, SCORE).scale(.8).move_to(SIG + DOWN * .82)
        self.at(A("h2", .55), Write(sv), lv.animate.set_stroke(width=SW * 1.6), run_time=.7, sfx="tick")
        self.at(A("h2", .85), lv.animate.set_stroke(width=SW), run_time=.4)
        self.at(A("h3", .5), Write(sf), lf.animate.set_stroke(width=SW * 1.6), run_time=.7, sfx="tick")
        self.at(A("h3", .85), lf.animate.set_stroke(width=SW), run_time=.4)
        # h4（錘錘）它總共幾分？：兩個分數複製出去，組成算式
        eq = VGroup(M("0.83", .05, SCORE), M("+", .05), M("12.4", .05, SCORE), M("=", .05), M("?", .05, TXT_STRONG)) \
            .arrange(RIGHT, buff=.14).scale(.74).move_to(SIG + RIGHT * 2.3)
        pl, drop = self.plumb_in(SIG + RIGHT * 2.45 + DOWN * 1.4, .24)
        self.at(A("h3", .9), *drop, run_time=.7)
        self.lipsync(pl)
        self.at(A("h4", .25), TransformFromCopy(sv, eq[0]), TransformFromCopy(sf, eq[2]), Write(eq[1]), Write(eq[3]), *pl.curl(),
                run_time=.9)
        self.at(A("h4", .8), Write(eq[4]), *pl.look(UP + LEFT), run_time=.5, sfx="pop")
        # h5 公尺加公斤：同一條算式長出單位
        eq2 = VGroup(M("0.83", .05, SCORE), M("m", .05, MUTED, italic=True), M("+", .05), M("12.4", .05, SCORE),
                     M("kg", .05, MUTED, italic=True), M("=", .05), M("?", .05, TXT_STRONG))
        eq2.arrange(RIGHT, buff=.12).scale(.7).move_to(eq)
        eq2[1].shift(LEFT * .05); eq2[4].shift(LEFT * .05)
        self.at(A("h5", .45), ReplacementTransform(eq[0], eq2[0]), ReplacementTransform(eq[1], eq2[2]), ReplacementTransform(eq[2], eq2[3]),
                ReplacementTransform(eq[3], eq2[5]), ReplacementTransform(eq[4], eq2[6]), run_time=.8)
        self.at(A("h5", .62), Write(eq2[1]), Write(eq2[4]), run_time=.6)
        # h6 算得出來，但沒有意義：算式變暗，一條細線劃掉
        st = Line(eq2.get_left() + LEFT * .1, eq2.get_right() + RIGHT * .1).set_stroke(MUTED, 2.2, .9)
        st.cross_ok = True
        self.at(A("h6", .35), eq2.animate.set_opacity(.45), Create(st), *pl.shake_head(), run_time=.8)
        # h7 RRF：分數，不看了
        self.at(A("h7", .3), FadeOut(sv, shift=DOWN * .15), FadeOut(sf, shift=DOWN * .15), FadeOut(eq2, shift=DOWN * .15),
                FadeOut(st, shift=DOWN * .15), *pl.straighten(), run_time=.7)
        self.at(A("h7", .55), Write(rrf), *pl.mood("happy"), run_time=.8, sfx="ding", gain=.5)
        self.at(A("h7", .9), *self.plumb_out(pl), run_time=.7)
        self.remove(pl)
        self.finish()


# ---------------- sc02：拉遠，整條管線 ----------------
ROWS2 = {"v": "ABC", "f": "BAC"}


def pipe_base(rows=ROWS2, more=True):
    """sc02 最後一格的管線（總榜空著）。回傳 dict。"""
    w = dict(q=query_node(), ql=q_links(), rv=retriever("v"), rf=retriever("f"),
             iv=lane_in("v"), if_=lane_in("f"), ov=lane_out("v"), of=lane_out("f"),
             sig=sigma_node(), rrf=rrf_label(), tot=tot_frame(),
             cv=row_cards("v", rows["v"]), cf=row_cards("f", rows["f"]))
    if more:
        w["mv"], w["mf"] = dots_more("v"), dots_more("f")
    return w


class Sc02(Sheet):
    SID = "sc02"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(HOOK_C, HOOK_W)
        d, lv, lf, nv, nf, rrf = hook_end()
        self.add(d, lv, lf, nv, nf, rrf)
        W = pipe_base()
        # i1 拉遠：文件縮成 Σ，暫時的通道名飛回各自的檢索器，管線一路往左長出來
        slots_v = VGroup(*[slot_box(row_pos("v", i), .66) for i in range(3)])
        slots_f = VGroup(*[slot_box(row_pos("f", i), .66) for i in range(3)])
        build = Succession(Wait(.5), AnimationGroup(
            LaggedStart(*[Create(s) for s in [*slots_v[::-1], *slots_f[::-1]]], lag_ratio=.12),
            FadeIn(W["mv"]), FadeIn(W["mf"]), Create(W["iv"]), Create(W["if_"])),
            AnimationGroup(DrawBorderThenFill(W["rv"].node), DrawBorderThenFill(W["rf"].node),
                           FadeIn(W["rv"].icon, scale=.6), FadeIn(W["rf"].icon, scale=.6)))
        self.at(A("i1", .05), self.cam(STAGE, STAGE_W), ReplacementTransform(d, W["sig"]), ReplacementTransform(rrf, W["rrf"]),
                ReplacementTransform(nv, W["rv"].lab), ReplacementTransform(nf, W["rf"].lab), build, run_time=3.2,
                sfx="swoosh", gain=.5)
        # i2 快轉一眼：總榜上，正確答案從第 1 名被擠到第 4 名
        tot = W["tot"]
        self.at(A("i2", .0), Create(tot.link), LaggedStart(*[Create(s) for s in tot.slots], lag_ratio=.1), Write(tot.head),
                LaggedStart(*[Write(n) for n in tot.nums], lag_ratio=.1), run_time=1.1)
        fut = [tot_card("*", 0), tot_card("C", 1), tot_card("D", 2), tot_card("N", 3)]
        self.at(A("i2", .2), LaggedStart(*[FadeIn(c, shift=LEFT * .25) for c in fut], lag_ratio=.15), run_time=1.0)
        fut[0].set_z_index(3)        # 往下掉的正確答案從其他卡前面經過，整段都看得到（不要被擋住）
        self.at(A("i2", .55), fut[0].animate.move_to(tot_slot(3)), *[fut[i].animate.move_to(tot_slot(i - 1)) for i in (1, 2, 3)],
                run_time=1.4, sfx="slide")
        self.at(A("i2", .8), Highlight(fut[0], color=ANS, scale_factor=1.15), run_time=.8)
        # w1 為什麼會有兩個分數？倒帶：總榜清空；兩條線各送一個分數到 Σ
        self.at(A("w1", .1), *[FadeOut(c, shift=RIGHT * .25) for c in fut], run_time=.7)
        self.at(A("w1", .45), ShowPassingFlash(W["ov"].copy().set_stroke(VEC, 7, 1), time_width=.4),
                ShowPassingFlash(W["of"].copy().set_stroke(FTS, 7, 1), time_width=.4), run_time=1.1)
        # w2 不只用一種搜尋：查詢點，岔成兩條
        self.at(A("w2", .2), DrawBorderThenFill(W["q"].node), Create(W["q"].lens), Write(W["q"].lab), run_time=.9)
        self.at(A("w2", .5), Create(W["ql"][0]), Create(W["ql"][1]), run_time=1.0)
        # w3 Cerebras：好幾種檢索器（第三條：IDF 加權，淡）
        idf_n = node(MUTED, .26, .08).move_to(np.array([-5.4, 0, 0]))
        idf_l = seg(Q + RIGHT * .34, idf_n.get_left(), MUTED, 2, .6)
        idf_t = T("IDF 加權", .04, MUTED).next_to(idf_n, RIGHT, buff=.18)
        cer = T("Cerebras 內部知識庫", .05, TXT).move_to(np.array([-.75, .05, 0]))
        self.at(A("w3", .1), Write(cer), run_time=1.0)
        self.at(A("w3", .55), Create(idf_l), DrawBorderThenFill(idf_n), Write(idf_t), run_time=.9)
        self.at(A("w3", .7), Indicate(W["rv"].node, color=VEC), Indicate(W["rf"].node, color=FTS), run_time=.8)
        # w4 比的東西不一樣
        mv_ = T("意思像不像", .04, VEC).set_opacity(.85).move_to(np.array([-2.6, 2.6, 0]))
        mf_ = T("字面有沒有對上", .04, FTS).set_opacity(.85).move_to(np.array([-2.6, -2.6, 0]))
        self.at(A("w4", .05), FadeOut(idf_t), FadeOut(idf_n), FadeOut(idf_l), run_time=.6)
        self.at(A("w4", .15), Write(mv_), Wiggle(W["rv"].icon, scale_value=1.15), run_time=1.0)
        self.at(A("w4", .6), Write(mf_), Wiggle(W["rf"].icon, scale_value=1.15), run_time=1.0)
        # w5 每天超過一萬五千次：脈衝不停從查詢流進兩條通道，結果卡片落進榜單
        cnt = ValueTracker(0)
        # 數字靠右對齊（像計數器），「+」最後另外淡入。原本置中、數到 15,000 時多一個「+」，整串往左跳一下（2026-11-10 逐格檢查）
        full = M("15,000+", .085, TXT_STRONG).move_to(np.array([-1.5, .22, 0]))
        anchor = np.array([full[-2].get_right()[0], full[-2].get_top()[1], 0])
        num_ = Live(cnt, lambda v: f"{int(v):,}", .085, TXT_STRONG, place=lambda t: t.move_to(anchor, aligned_edge=UR))
        plus = full[-1].copy()
        unit = T("次／天", .05, TXT).move_to(np.array([-1.5, -.55, 0]))
        self.at(A("w5", .02), FadeOut(cer), FadeIn(num_), run_time=.5)          # 計數器先以 0 淡入（不要直接跳出來）
        pd = {k: [pdot(lane_color(k)) for _ in range(4)] for k in "vf"}
        self.at(A("w5", .12), cnt.animate(rate_func=lambda u: 1.8 * u - .8 * u * u).set_value(15000), FadeIn(unit), *[
            LaggedStart(*[travel(x, pulse_path(k)) for x in pd[k]], lag_ratio=.3) for k in "vf"],
            run_time=2.6)
        self.remove(*pd["v"], *pd["f"])
        self.at(A("w5", .65), *[ReplacementTransform(s, c) for s, c in zip(slots_v, W["cv"])],
                *[ReplacementTransform(s, c) for s, c in zip(slots_f, W["cf"])], FadeIn(plus, shift=LEFT * .1), run_time=1.0, sfx="tick")
        # w6 好幾份結果，得合成一份：兩排卡片往 Σ 送，總榜空位亮一下
        self.at(A("w6", .0), FadeOut(mv_), FadeOut(mf_), run_time=.4)
        self.at(A("w6", .2), ShowPassingFlash(W["ov"].copy().set_stroke(VEC, 7, 1), time_width=.4),
                ShowPassingFlash(W["of"].copy().set_stroke(FTS, 7, 1), time_width=.4), run_time=.8)
        self.at(A("w6", .55), ShowPassingFlash(tot.link.copy().set_stroke(GOLD, 7, 1), time_width=.5),
                Indicate(tot.slots, color=GOLD, scale_factor=1.04), run_time=.8)
        self.at(A("w6", .95), FadeOut(num_), FadeOut(plus), FadeOut(unit), run_time=.6)
        self.remove(num_)
        self.finish()


# ---------------- sc03：分數放到數線上，橡皮尺 ----------------
SCV = {"A": .83, "B": .61, "C": .32}
SCF = {"B": 12.4, "A": 9.7, "C": 3.1}
SV_TXT, SF_TXT = ["0.83", "0.61", "0.32"], ["12.4", "9.7", "3.1"]
AX_L = 8.4
VY, FY = BENCH1[1] + 1.45, BENCH1[1] - 1.35
B1_C, B1_W = BENCH1 + RIGHT * .4 + DOWN * .05, 14.0      # sc03 工作台的鏡頭


def v_axis():
    ax = NumberLine(x_range=[-1, 1, .5], length=AX_L, include_ticks=True, tick_size=.06, stroke_width=2.2, color=LINE)
    ax.move_to(np.array([BENCH1[0], VY, 0]))
    labs = VGroup(*[M(s, .04, MUTED).next_to(ax.n2p(v), DOWN, buff=.16) for s, v in (("−1", -1), ("0", 0), ("1", 1))])
    ttl = M("cosine", .045, VEC, italic=True).next_to(ax, LEFT, buff=.3)
    g = VGroup(ax, labs, ttl)
    g.ax, g.labs, g.ttl = ax, labs, ttl
    g.dots_ok = ax.dots_ok = True
    return g


def f_axis():
    ax = NumberLine(x_range=[0, 32, 4], length=AX_L, include_ticks=True, tick_size=.06, stroke_width=2.2, color=LINE,
                    include_tip=True, tip_width=.16, tip_height=.16)
    ax.move_to(np.array([BENCH1[0], FY, 0]), aligned_edge=LEFT).shift(LEFT * AX_L / 2)
    q = M("?", .045, MUTED).next_to(ax.get_end(), RIGHT, buff=.14)
    ttl = M("BM25", .045, FTS).next_to(ax.n2p(0), LEFT, buff=.3)
    g = VGroup(ax, q, ttl)
    g.ax, g.q, g.ttl = ax, q, ttl
    g.dots_ok = ax.dots_ok = True
    return g


def ax_doc(ax, letter, val, txt, color):
    """數線上的一份文件：點、上方的分數、再上方的字母。"""
    p = ax.n2p(val)
    d = Dot(p, radius=.11, color=color)
    s = M(txt, .046, SCORE).next_to(p, UP, buff=.18)
    L = M(letter, .046, TXT).next_to(s, UP, buff=.1)
    g = VGroup(d, s, L)
    g.dot, g.num, g.let = d, s, L
    return g


def ruler(ax, lo, hi, color=TXT_STRONG):
    """橡皮尺：數線上從 lo 拉到 hi 的半透明帶子，兩端標 0 和 1。"""
    a, b = ax.n2p(lo), ax.n2p(hi)
    band = Rectangle(width=max(.01, b[0] - a[0]), height=.3).set_stroke(color, 2, .9).set_fill(color, .16)
    band.move_to((a + b) / 2)
    ticks = VGroup(*[Line(UP * .15, DOWN * .15).set_stroke(color, 1.4, .8).move_to(a + (b - a) * u) for u in (.25, .5, .75)])
    z = M("0", .04, color).next_to(band, DOWN, buff=.12).align_to(band, LEFT).shift(LEFT * .05)
    o = M("1", .04, color).next_to(band, DOWN, buff=.12).align_to(band, RIGHT).shift(RIGHT * .05)
    g = VGroup(band, ticks, z, o)
    g.overlap_ok = True
    return g


def bench1_parts():
    va, fa = v_axis(), f_axis()
    vd = {k: ax_doc(va.ax, k, SCV[k], t, VEC) for k, t in zip("ABC", SV_TXT)}
    fd = {k: ax_doc(fa.ax, k, SCF[k], t, FTS) for k, t in zip("BAC", SF_TXT)}
    for g in [*vd.values(), *fd.values()]:
        g.overlap_ok = True
    return va, fa, vd, fd


def norm_b(mx):
    return (12.4 - 3.1) / (mx - 3.1)


def readout_pos(t):
    """B 的讀數放在兩條數線中間的右側。原本和 BM25 數線同一行，緊接在箭頭的「?」後面，讀起來像「? B 0.35」（2026-11-10）。"""
    return t.move_to(np.array([BENCH1[0] + 5.6, BENCH1[1] + .05, 0]))


def bench1_end():
    """sc03 最後一格的工作台。"""
    va, fa, vd, fd = bench1_parts()
    ed = ax_doc(fa.ax, "E", 30, "30", FTS)
    ed.remove(ed.let, ed.num)      # r12 起它代表「每一批的最高分」，字母 E 和「30」已經淡掉
    ed.overlap_ok = True
    vr = ruler(va.ax, .32, .83)
    fr = ruler(fa.ax, 3.1, 30)
    lo = T("最低", .04, MUTED).next_to(fa.ax.n2p(3.1), DOWN, buff=.62)
    hi = T("最高", .04, MUTED).next_to(fa.ax.n2p(30), DOWN, buff=.62)
    rd = M(f"B  {norm_b(30):.2f}", .065, SCORE)
    readout_pos(rd)
    ghost = M("B  1.00", .065, SCORE).set_opacity(.35).move_to(rd.get_center() + UP * .9)
    arr = Arrow(ghost.get_bottom(), rd.get_top(), buff=.08, stroke_width=2.4, max_tip_length_to_length_ratio=.3).set_color(MUTED)
    vg = VGroup(va, vr, *vd.values())
    vg.set_opacity(.3)
    return dict(va=va, fa=fa, vd=vd, fd=fd, ed=ed, vr=vr, fr=fr, lo=lo, hi=hi, rd=rd, ghost=ghost, arr=arr, vg=vg)


def pipe_scored():
    W = pipe_base()
    W["sv"], W["sf"] = row_scores("v", SV_TXT), row_scores("f", SF_TXT)
    return W


class Sc03(Sheet):
    SID = "sc03"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(STAGE, STAGE_W)
        W = pipe_base()
        self.add(*W.values())
        # r1 舉例：分數寫在卡片下面
        sv, sf = row_scores("v", SV_TXT), row_scores("f", SF_TXT)
        self.at(A("r1", .15), LaggedStart(*[Write(x) for x in [*sv, *sf]], lag_ratio=.12), run_time=1.6, sfx="tick", gain=.6)
        # r2 鏡頭往下到工作台，向量分數落到 cosine 數線上
        va, fa, vd, fd = bench1_parts()
        # 鏡頭還在往下移時就開始畫數線：鏡頭到的時候畫面上已經有東西（不要出現全空的畫面，2026-11-10）
        self.at(A("r2", .0), self.cam(B1_C, B1_W),
                Succession(Wait(.6), AnimationGroup(Create(va.ax), Write(va.ttl), Create(fa.ax.set_stroke(opacity=.25)))),
                run_time=1.7, sfx="whoosh", gain=.5)
        self.at(A("r2", .45), LaggedStart(*[Write(x) for x in va.labs], lag_ratio=.2),
                *[AnimationGroup(TransformFromCopy(sv[i], vd[k].num), FadeIn(vd[k].dot, scale=.5), Write(vd[k].let))
                  for i, k in enumerate("ABC")], run_time=1.2)
        # r3 全文分數落到 BM25 數線上：沒有上限
        self.at(A("r3", .15), fa.ax.animate.set_stroke(opacity=1), Write(fa.ttl), run_time=1.0)
        self.at(A("r3", .4), *[AnimationGroup(TransformFromCopy(sf[i], fd[k].num), FadeIn(fd[k].dot, scale=.5), Write(fd[k].let))
                              for i, k in enumerate("BAC")], run_time=1.2)
        self.at(A("r3", .75), Write(fa.q), Indicate(fa.ax.tip, color=FTS), run_time=.8)
        # r4 兩把尺不一樣
        ne = M("≠", .07, TXT_STRONG).move_to((va.ttl.get_center() + fa.ttl.get_center()) / 2)
        self.at(A("r4", .2), Write(ne), ShowPassingFlash(va.ax.copy().set_stroke(VEC, 6), time_width=.5),
                ShowPassingFlash(Line(fa.ax.get_start(), fa.ax.get_end()).set_stroke(FTS, 6), time_width=.5), run_time=1.2)
        # r5 直接相加：A 的兩個分數組成算式
        eq = VGroup(M("0.83", .06, SCORE), M("+", .06), M("9.7", .06, SCORE), M("=", .06), M("?", .06, TXT_STRONG)) \
            .arrange(RIGHT, buff=.16).move_to(np.array([BENCH1[0] + .6, BENCH1[1] + .02, 0]))
        self.at(A("r5", .1), TransformFromCopy(vd["A"].num, eq[0]), TransformFromCopy(fd["A"].num, eq[2]), Write(eq[1]), Write(eq[3]),
                run_time=1.0)
        st = Line(eq.get_left() + LEFT * .1, eq.get_right() + RIGHT * .1).set_stroke(MUTED, 2.2, .9)
        st.cross_ok = True
        self.at(A("r5", .6), Write(eq[4]), run_time=.4)
        self.at(A("r5", .85), Create(st), eq.animate.set_opacity(.45), run_time=.6)
        # r6 正規化：兩把橡皮尺，各自從最低拉到最高，標成 0 到 1
        vr, fr0 = ruler(va.ax, .32, .83), ruler(fa.ax, 3.1, 12.4)
        self.at(A("r6", .25), FadeOut(eq, shift=DOWN * .15), FadeOut(st, shift=DOWN * .15), FadeOut(ne), run_time=.6)
        self.at(A("r6", .45), GrowFromEdge(vr, LEFT), GrowFromEdge(fr0, LEFT), run_time=1.3)
        # r7 聽起來很合理：兩把尺的 0 對 0、1 對 1
        # 一道光同時從兩把尺的 0 掃到 1（只 Indicate 小小的 0、1 標籤幾乎看不出動，逐格檢查算成靜止）
        self.at(A("r7", .1), Indicate(vr[3], color=TXT_STRONG), Indicate(fr0[3], color=TXT_STRONG),
                Indicate(vr[2], color=TXT_STRONG), Indicate(fr0[2], color=TXT_STRONG),
                *[ShowPassingFlash(Line(r[0].get_left(), r[0].get_right()).set_stroke(TXT_STRONG, 6), time_width=.6) for r in (vr, fr0)],
                run_time=1.0)
        # r8 縮放靠這一批的最高與最低（焦點移到全文那把）
        V = VGroup(va, vr, *vd.values())
        lo = T("最低", .04, MUTED).next_to(fa.ax.n2p(3.1), DOWN, buff=.62)
        hi = T("最高", .04, MUTED).next_to(fa.ax.n2p(12.4), DOWN, buff=.62)
        self.at(A("r8", .1), V.animate.set_opacity(.3), run_time=.8)
        self.at(A("r8", .45), Write(lo), run_time=.6)
        self.at(A("r8", .7), Write(hi), run_time=.6)
        # r9 橡皮尺：最高 12.4，尺就拉到 12.4；B 量起來是 1.00
        mx = ValueTracker(12.4)
        fr = always_redraw(lambda: ruler(fa.ax, 3.1, mx.get_value()))
        fr.overlap_ok = True
        rd = Live(mx, lambda m: f"B  {norm_b(m):.2f}", .065, SCORE, place=readout_pos)
        self.remove(fr0)
        self.add(fr)
        self.at(A("r9", .35), Indicate(fd["B"], color=FTS), run_time=.9)
        self.at(A("r9", .65), Write(rd), Indicate(fr, color=TXT_STRONG, scale_factor=1.03), run_time=.9)
        # r10 換一批：E 拿到 30，尺被拉長
        ed = ax_doc(fa.ax, "E", 30, "30", FTS)
        ed.overlap_ok = True
        self.at(A("r10", .2), FadeIn(ed.dot, scale=.4), Write(ed.num), Write(ed.let), Flash(ed.dot, color=FTS, line_length=.25),
                run_time=.9, sfx="pop")
        self.at(A("r10", .5), mx.animate.set_value(30), hi.animate.next_to(fa.ax.n2p(30), DOWN, buff=.62), run_time=1.8, sfx="slide")
        # r11 同一份文件，值變了：留下 1.00 的殘影
        ghost = M("B  1.00", .065, SCORE).set_opacity(.35).move_to(rd.get_center() + UP * .9)
        arr = Arrow(ghost.get_bottom(), rd.get_top(), buff=.08, stroke_width=2.4, max_tip_length_to_length_ratio=.3).set_color(MUTED)
        self.at(A("r11", .2), FadeIn(ghost, shift=DOWN * .1), GrowArrow(arr), Indicate(rd, color=TXT_STRONG), run_time=1.0)
        # r12 每一批都不一樣：這一批的最高分（原本的 E）跟著換，尺、「最高」、B 的值一起飄。
        # 同一個 tracker 驅動所有東西：尺縮到 21 時，最高分的點也在 21（不能尺縮了、點還留在 30）。
        # 字母 E 和「30」淡掉：點代表「每一批的最高分」；不顯示飄動中的分數，畫面不多出新的數字（只有已查核的 B 讀數在變）
        e_dot = always_redraw(lambda: Dot(fa.ax.n2p(mx.get_value()), radius=.11, color=FTS))
        hi_l = always_redraw(lambda: T("最高", .04, MUTED).next_to(fa.ax.n2p(mx.get_value()), DOWN, buff=.62))
        for x in (e_dot, hi_l):
            x.overlap_ok = True
        self.remove(ed.dot, hi)
        self.add(e_dot, hi_l)
        drift = ValueTracker(0)
        mx.add_updater(lambda m: m.set_value(30 - 9 * np.sin(PI * drift.get_value()) ** 2 * (1 if drift.get_value() < 2 else 0)))
        self.add(mx)
        self.at(A("r12", .15), drift.animate.set_value(2),
                Succession(AnimationGroup(FadeOut(ed.let, run_time=.5), FadeOut(ed.num, run_time=.5)), Wait(4.1)), run_time=4.6,
                rate_func=linear)
        mx.clear_updaters()
        mx.set_value(30)
        self.finish()


# ---------------- sc04：名次；公式寫在管線上方 ----------------
OVER_C, OVER_W = np.array([-0.55, 1.05, 0]), 17.0      # 看得到整條管線＋上方公式帶
FORM_Y = 3.85


def eq_line(i):
    """兩排之間的「i = i」（同一名次天然能比）。"""
    g = VGroup(M(str(i + 1), .05, RANK), M("=", .05, TXT), M(str(i + 1), .05, RANK)).arrange(RIGHT, buff=.12)
    return g.move_to(np.array([ROW_X[i], .05, 0]))


def term(kpart=None, frac=.06, rank=None):
    """1 / (k + 名次)：k 用 k 的顏色、名次用名次的顏色。rank 給數字時，名次換成那個數字。"""
    k = kpart or M("k", frac, KC, italic=True)
    r = M(rank, frac, RANK) if rank else T("名次", frac * .8, RANK)
    den = VGroup(k, M("+", frac), r).arrange(RIGHT, buff=.1)
    f = fraction(M("1", frac), den, frac)
    f.k = k
    return f


def formula(kval=None):
    """RRF(d) = Σ 1/(k + 名次)；kval＝"60" 時 k 換成數字。"""
    lhs = VGroup(M("RRF", .06, GOLD), M("(", .06), M("d", .06, TXT_STRONG, italic=True), M(")", .06)).arrange(RIGHT, buff=.03)
    eqs = M("=", .06)
    sig = M("Σ", .085, TXT_STRONG)
    tm = term(M(kval, .06, KC) if kval else None)
    g = VGroup(lhs, eqs, sig, tm).arrange(RIGHT, buff=.22).move_to(np.array([-1.2, FORM_Y, 0]))
    sub = T("每一路", .046, MUTED).next_to(sig, DOWN, buff=.12).align_to(sig, RIGHT).shift(RIGHT * .05)
    g.lhs, g.eq, g.sig, g.tm, g.sub = lhs, eqs, sig, tm, sub
    return g


def form_end():
    f = formula("60")
    w = M("權重 = 1", .046, MUTED).next_to(f, RIGHT, buff=.6).shift(UP * .2)
    cite = M("Cormack 等人, 2009", .042 + .004, MUTED).next_to(w, DOWN, buff=.18, aligned_edge=LEFT)
    return f, w, cite


def pipe_ranked(rows=ROWS2):
    W = pipe_base(rows)
    W["rv_"], W["rf_"] = row_ranks("v", len(rows["v"])), row_ranks("f", len(rows["f"]))
    return W


class Sc04(Sheet):
    SID = "sc04"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(B1_C, B1_W)
        W = pipe_scored()
        B = bench1_end()
        self.add(*W.values(), B["va"], B["fa"], *B["vd"].values(), *B["fd"].values(), B["ed"], B["vr"], B["fr"],
                 B["lo"], B["hi"], B["rd"], B["ghost"], B["arr"])
        for c in [*W["cv"], *W["cf"]]:
            c.set_z_index(2)
        # n1 有沒有一種東西，每一路都有？鏡頭回到管線（拉到看得見上方公式帶）
        bench = [B[k] for k in ("va", "fa", "ed", "vr", "fr", "lo", "hi", "rd", "ghost", "arr")] + [*B["vd"].values(), *B["fd"].values()]
        self.at(A("n1", .05), self.cam(STAGE, STAGE_W), *[FadeOut(b, rate_func=rate_functions.rush_into) for b in bench], run_time=2.2,
                sfx="whoosh", gain=.5)
        self.at(A("n1", .6), Indicate(W["sv"], color=SCORE, scale_factor=1.08), Indicate(W["sf"], color=SCORE, scale_factor=1.08), run_time=1.0)
        # n2 有：名次。分數從卡片後面穿過去，變成名次
        rv, rf = row_ranks("v", 3), row_ranks("f", 3)
        self.at(A("n2", .0), *[ReplacementTransform(W["sv"][i], rv[i]) for i in range(3)],
                *[ReplacementTransform(W["sf"][i], rf[i]) for i in range(3)], run_time=1.0, sfx="tick")
        # n3 第一名就是第一名：兩個 1 在兩排之間相等
        e = [eq_line(i) for i in range(3)]
        self.at(A("n3", .55), TransformFromCopy(rv[0], e[0][0]), TransformFromCopy(rf[0], e[0][2]), Write(e[0][1]), run_time=1.0)
        # n4 名次是整數，天然能比
        self.at(A("n4", .3), *[AnimationGroup(TransformFromCopy(rv[i], e[i][0]), TransformFromCopy(rf[i], e[i][2]), Write(e[i][1]))
                              for i in (1, 2)], run_time=1.1)
        self.at(A("n4", .75), Indicate(rv, color=RANK, scale_factor=1.2), Indicate(rf, color=RANK, scale_factor=1.2), run_time=.9)  # 「每個檢索器都天然有」
        # n5 不需要正規化：橡皮尺的小圖示出現又被劃掉
        mini = VGroup(Rectangle(width=1.1, height=.22).set_stroke(TXT_STRONG, 1.6, .8).set_fill(TXT_STRONG, .12),
                      M("0", .046, TXT_STRONG), M("1", .046, TXT_STRONG))
        mini[1].next_to(mini[0], LEFT, buff=.1)
        mini[2].next_to(mini[0], RIGHT, buff=.1)
        mini.move_to(np.array([ROW_X[3] + .45, .05, 0]))     # 和「3 = 3」拉開：太近會讀成「3 = 30▭1」（2026-11-10）
        x1 = Line(mini.get_corner(DL) + DL * .05, mini.get_corner(UR) + UR * .05).set_stroke(MUTED, 2.4)
        x1.cross_ok = True
        self.at(A("n5", .1), FadeIn(mini, shift=UP * .1), run_time=.6)
        self.at(A("n5", .45), Create(x1), mini.animate.set_opacity(.4), run_time=.6)
        self.at(A("n5", .85), FadeOut(mini), FadeOut(x1), run_time=.5)
        # n6 這就是 RRF：Σ 下的 RRF 複製到上方，寫出全名
        rrf2 = M("RRF", .07, GOLD).move_to(np.array([-3.4, FORM_Y + .05, 0]))
        full = M("Reciprocal Rank Fusion", .052, TXT_STRONG).next_to(rrf2, RIGHT, buff=.45)
        zh = T("倒數排名融合", .046, MUTED).next_to(full, DOWN, buff=.18, aligned_edge=LEFT)
        self.at(A("n6", .0), self.cam(OVER_C, OVER_W), TransformFromCopy(W["rrf"], rrf2), run_time=1.3, sfx="ding", gain=.4)
        self.at(A("n6", .3), Write(full), run_time=1.1)
        self.at(A("n6", .6), Write(zh), run_time=.8)
        # n7 每一路給 1/(k + 名次)
        f = formula()
        self.at(A("n7", .05), FadeOut(full, shift=UP * .2), FadeOut(zh, shift=UP * .2), ReplacementTransform(rrf2, f.lhs[0]), run_time=.8)
        self.at(A("n7", .3), Write(f.tm), run_time=1.2)
        self.at(A("n7", .7), Indicate(f.tm.den[2], color=RANK), Indicate(rv[2], color=RANK), run_time=.9)
        # n8 全部加起來
        self.at(A("n8", .05), Write(f.lhs[1:]), Write(f.eq), Write(f.sig), run_time=1.0)
        self.at(A("n8", .5), FadeIn(f.sub, shift=UP * .08), ShowPassingFlash(W["ov"].copy().set_stroke(VEC, 7), time_width=.4),
                ShowPassingFlash(W["of"].copy().set_stroke(FTS, 7), time_width=.4), run_time=1.0)
        # n9 名次越前，分母越小，拿得越多
        ineq = VGroup(term(None, .055, "1"), M(">", .055), term(None, .055, "2"), M(">", .055), M("⋯", .055))
        ineq.arrange(RIGHT, buff=.25).move_to(np.array([4.35, FORM_Y - .05, 0]))   # 和公式拉開，不要讀成同一條式子
        self.at(A("n9", .05), LaggedStart(*[Write(x) for x in ineq], lag_ratio=.2), run_time=1.6)
        self.at(A("n9", .6), *[Indicate(ineq[i].den[2], color=RANK) for i in (0, 2)], run_time=.9)
        # n10 k 是平滑常數：Cerebras 設 60，權重 1
        f60, w, cite = form_end()
        self.at(A("n10", .0), FadeOut(ineq, shift=RIGHT * .2), run_time=.6)
        self.at(A("n10", .3), Indicate(f.tm.k, color=KC, scale_factor=1.4), run_time=.8)
        self.at(A("n10", .55), ReplacementTransform(f.tm.k, f60.tm.k), *[ReplacementTransform(a, b) for a, b in
                zip([f.lhs, f.eq, f.sig, f.sub, f.tm.num, f.tm.bar, f.tm.den[1], f.tm.den[2]],
                    [f60.lhs, f60.eq, f60.sig, f60.sub, f60.tm.num, f60.tm.bar, f60.tm.den[1], f60.tm.den[2]])], run_time=.9)
        self.at(A("n10", .8), Write(w), run_time=.8)
        # n11 60 來自 Cormack 等人 2009
        self.at(A("n11", .25), Write(cite), run_time=1.0)
        self.at(A("n11", .8), Indicate(f60.tm.k, color=KC, scale_factor=1.3), run_time=.9)   # 接縫前的最後一拍（seams 空檔）
        self.finish()


# ---------------- sc05：A、B 代入公式（在兩排中間的空帶算） ----------------
ROWS5 = {"v": "BCA", "f": "CDA"}
AY, BY = .5, -.45


def calc_line(name, ra, rb, val, y):
    """name ＝ 1/(60 + ra) + 1/(60 + rb) ≈ val；回傳群組與各部件（分母裡的名次單獨拿得到）。"""
    def fr(r):
        den = VGroup(M("60", .046, KC), M("+", .046), M(r, .046, RANK)).arrange(RIGHT, buff=.07)
        return fraction(M("1", .046), den, .046, gap=.09)
    L = M(name, .055, TXT_STRONG)
    f1, f2 = fr(ra), fr(rb)
    g = VGroup(L, M("=", .05), f1, M("+", .05), f2, M("≈", .05), M(val, .055, TXT_STRONG)).arrange(RIGHT, buff=.16)
    g.move_to(np.array([-2.0, y, 0]))
    g.L, g.f1, g.f2, g.val = L, f1, f2, g[6]
    g.overlap_ok = True
    return g


def calc_note():
    return T("代入公式計算", .042, MUTED).move_to(np.array([-2.0, 1.22, 0]))


def b8_lab():
    return M("8", .05, RANK).move_to(row_pos("f", 3) + UP * .6)


def sc05_end():
    W = pipe_base(ROWS5)
    W["cf"].add(card("B").move_to(row_pos("f", 3)))
    del W["mf"]
    W["rv_"], W["rf_"] = row_ranks("v", 3), row_ranks("f", 3)
    W["b8"] = b8_lab()
    W["note"] = calc_note()
    a, b = calc_line("A", "3", "3", "0.0317", AY), calc_line("B", "1", "8", "0.0311", BY)
    a.val.set_color(GOLD)
    W["ca"], W["cb"] = a, b
    W["ta"], W["tb"] = tot_card("A", 0), tot_card("B", 1)
    return W


class Sc05(Sheet):
    SID = "sc05"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(OVER_C, OVER_W)
        W = pipe_base()
        rv, rf = row_ranks("v", 3), row_ranks("f", 3)
        eqs = [eq_line(i) for i in range(3)]
        f60, w, cite = form_end()
        self.add(*W.values(), rv, rf, *eqs, f60.lhs, f60.eq, f60.sig, f60.sub, f60.tm, w, cite)
        # m1 舉個例子：換一個查詢，兩排的結果換了
        newv, newf = row_cards("v", ROWS5["v"]), row_cards("f", ROWS5["f"])
        bcard = card("B").move_to(row_pos("f", 3))
        b8 = b8_lab()
        self.at(A("m1", .1), *[FadeOut(e, shift=DOWN * .1) for e in eqs], FadeOut(w), FadeOut(cite), run_time=.6)
        self.at(A("m1", .35), *[Transform(W["cv"][i].glyph, newv[i].glyph) for i in range(3)],
                *[Transform(W["cf"][i].glyph, newf[i].glyph) for i in range(3)], run_time=.9, sfx="click")
        self.at(A("m1", .7), ReplacementTransform(W["mf"], bcard), FadeIn(b8, shift=DOWN * .1), run_time=.8)
        # m2 A：兩路都第 3
        ca, cb = calc_line("A", "3", "3", "0.0317", AY), calc_line("B", "1", "8", "0.0311", BY)
        aV, aF = W["cv"][2], W["cf"][2]
        self.at(A("m2", .3), Highlight(aV, color=TXT_STRONG, scale_factor=1.12), Highlight(aF, color=TXT_STRONG, scale_factor=1.12),
                Indicate(rv[2], color=RANK), Indicate(rf[2], color=RANK), run_time=1.0)
        # m3 B：一路第 1、一路第 8
        bV = W["cv"][0]
        self.at(A("m3", .3), Highlight(bV, color=TXT_STRONG, scale_factor=1.12), Highlight(bcard, color=TXT_STRONG, scale_factor=1.12),
                Indicate(rv[0], color=RANK), Indicate(b8, color=RANK), run_time=1.0)
        # m4（錘錘）拿過第一的 B，應該比較強吧？
        pl, drop = self.plumb_in(np.array([6.4, -.7, 0]), .4)
        self.at(A("m4", -.1), *drop, run_time=.7)
        self.lipsync(pl)
        self.at(A("m4", .3), *pl.look(LEFT + UP * .2), *pl.tilt(.18), run_time=.6)
        # m5 A ＝ 1/(60+3) + 1/(60+3) ≈ 0.0317：名次從卡片上方掉進分母
        note = calc_note()
        self.at(A("m4", .85), *self.plumb_out(pl), run_time=.7)
        self.remove(pl)
        fm = VGroup(f60.lhs, f60.eq, f60.sig, f60.sub, f60.tm)
        self.at(A("m5", -.05), self.cam(STAGE, STAGE_W), FadeOut(fm, rate_func=rate_functions.rush_into), Write(ca.L), Write(ca[1]),
                run_time=1.0)
        self.at(A("m5", .15), Write(VGroup(ca.f1.num, ca.f1.bar, ca.f1.den[:2])), Write(ca[3]),
                Write(VGroup(ca.f2.num, ca.f2.bar, ca.f2.den[:2])), run_time=1.0)
        self.at(A("m5", .32), TransformFromCopy(rv[2], ca.f1.den[2]), TransformFromCopy(rf[2], ca.f2.den[2]), run_time=1.0)
        self.at(A("m5", .7), Write(ca[5]), Write(ca.val), FadeIn(note), run_time=.9)
        # m6 B ＝ 1/(60+1) + 1/(60+8) ≈ 0.0311
        self.at(A("m6", .0), Write(cb.L), Write(cb[1]), Write(VGroup(cb.f1.num, cb.f1.bar, cb.f1.den[:2])), Write(cb[3]),
                Write(VGroup(cb.f2.num, cb.f2.bar, cb.f2.den[:2])), run_time=1.0)
        self.at(A("m6", .25), TransformFromCopy(rv[0], cb.f1.den[2]), TransformFromCopy(b8, cb.f2.den[2]), run_time=1.0)
        self.at(A("m6", .6), Write(cb[5]), Write(cb.val), run_time=.8)
        # m7 A 贏，只贏一點點：A 進總榜第 1、B 第 2
        ta, tb = tot_card("A", 0), tot_card("B", 1)
        self.at(A("m7", .05), Indicate(ca.val, color=GOLD, scale_factor=1.15), run_time=.8, sfx="ding", gain=.4)
        self.at(A("m7", .4), ca.val.animate.set_color(GOLD), TransformFromCopy(ca.L, ta), TransformFromCopy(cb.L, tb), run_time=1.0,
                sfx="slide")
        # m8 常常是 A 贏
        self.at(A("m8", .2), Highlight(aV, color=TXT_STRONG, scale_factor=1.08), Highlight(aF, color=TXT_STRONG, scale_factor=1.08),
                run_time=.9)
        # m9 兩邊都穩 vs 單邊很強
        self.at(A("m9", .1), Circumscribe(VGroup(aV, aF, rv[2], rf[2]), color=TXT_STRONG, buff=.12), run_time=1.4)
        self.at(A("m9", .45), Highlight(bV, color=TXT_STRONG), b8.animate.set_opacity(.45), run_time=.9)
        self.at(A("m9", .82), b8.animate.set_opacity(1), Highlight(ta, color=GOLD), run_time=.8)
        self.finish()


# ---------------- sc06：k 旋鈕（活的：每一格依公式重算） ----------------
DIAL = BENCH2 + np.array([-5.0, .35, 0])
BARS0 = BENCH2 + np.array([-2.05, -.95, 0])     # 五根直條的左下（往左移，和右邊 A、B 的標籤「(3, 3) A」拉開）
BAR_H, BAR_DX = 2.7, .66
AB0 = BENCH2 + np.array([3.2, .2, 0])          # A、B 橫條的左端
AB_W = 1.7
LK = np.log(200)


def k_angle(lk):
    return (225 - 270 * lk / LK) * DEGREES


def dial_static():
    ring = Arc(radius=1.05, start_angle=-45 * DEGREES, angle=270 * DEGREES).set_stroke(LINE, 3).move_arc_center_to(DIAL)
    ticks, labs = VGroup(), VGroup()
    for k in (1, 10, 60, 200):
        a = k_angle(np.log(k))
        d = np.array([np.cos(a), np.sin(a), 0])
        ticks.add(Line(DIAL + d * .92, DIAL + d * 1.18).set_stroke(TXT if k == 60 else LINE, 2.4))
        labs.add(M(str(k), .042, MUTED).move_to(DIAL + d * 1.5))
    hub = Circle(.13).set_fill(KC, 1).set_stroke(width=0).move_to(DIAL)
    name = M("k", .07, KC, italic=True).move_to(DIAL + UP * 2.2)   # 太靠近刻度「10」會讀成 10 的 k 次方（2026-11-10）
    g = VGroup(ring, ticks, labs, hub, name)
    g.dots_ok = True
    return g


def dial_needle(lk):
    a = k_angle(lk)
    return Line(DIAL, DIAL + np.array([np.cos(a), np.sin(a), 0]) * .85).set_stroke(KC, 5)


def k_readout(t):
    return t.move_to(DIAL + DOWN * 1.55)


def rank_bars(lk):
    k = np.exp(lk)
    vals = [1 / (k + r) for r in range(1, 6)]
    g = VGroup()
    for i, v in enumerate(vals):
        h = max(.02, BAR_H * v / vals[0])
        g.add(Rectangle(width=.4, height=h).set_stroke(SCORE, 1.5).set_fill(SCORE, .55)
              .move_to(BARS0 + RIGHT * (i * BAR_DX + .2) + UP * h / 2))
    return g


def rank_bars_static():
    base = Line(BARS0 + LEFT * .15, BARS0 + RIGHT * (5 * BAR_DX)).set_stroke(LINE, 2)
    labs = VGroup(*[M(str(i + 1), .046, RANK).move_to(BARS0 + RIGHT * (i * BAR_DX + .2) + DOWN * .3) for i in range(5)])
    head = term(None, .05).next_to(BARS0 + RIGHT * 1.45 + UP * BAR_H, UP, buff=.3)
    return VGroup(base, labs, head)


def ab_bars(lk):
    k = np.exp(lk)
    a, b = 2 / (k + 3), 1 / (k + 1) + 1 / (k + 8)
    m = max(a, b)
    g = VGroup()
    for v, y in ((a, .45), (b, -.45)):
        w = AB_W * v / m
        g.add(Rectangle(width=w, height=.42).set_stroke(SCORE, 1.5).set_fill(SCORE, .55).move_to(AB0 + UP * y + RIGHT * w / 2))
    return g


def ab_score(lk_value, which):
    k = np.exp(lk_value)
    return 2 / (k + 3) if which == "a" else 1 / (k + 1) + 1 / (k + 8)


def ab_vals(lk):
    """A、B 合併分數的即時讀數：和長條同一個 tracker，每格依公式重算，放在各自長條的右端。"""
    def mk(which, y):
        def place(t):
            v = lk.get_value()
            w = AB_W * ab_score(v, which) / max(ab_score(v, "a"), ab_score(v, "b"))
            return t.next_to(AB0 + UP * y + RIGHT * w, RIGHT, buff=.18)
        return Live(lk, lambda v: f"{ab_score(v, which):.4f}", .046, SCORE, place=place)
    g = VGroup(mk("a", .45), mk("b", -.45))
    g.overlap_ok = True
    return g


def ab_note():
    return T("代入公式計算", .042, MUTED).move_to(AB0 + DOWN * 1.05 + RIGHT * .85)


def ab_static():
    base = Line(AB0 + UP * .8, AB0 + DOWN * .8).set_stroke(LINE, 2)
    la = M("A", .052, TXT_STRONG).next_to(AB0 + UP * .45, LEFT, buff=.2)
    lb = M("B", .052, TXT_STRONG).next_to(AB0 + DOWN * .45, LEFT, buff=.2)
    ra = VGroup(M("(3, 3)", .05, RANK)).next_to(la, LEFT, buff=.25)
    rb = VGroup(M("(1, 8)", .05, RANK)).next_to(lb, LEFT, buff=.25)
    return VGroup(base, la, lb, ra, rb)


def bench2_live(lk):
    """lk：log k 的 ValueTracker。回傳 (靜態部分, 會動的部分)。"""
    needle = always_redraw(lambda: dial_needle(lk.get_value()))
    bars = always_redraw(lambda: rank_bars(lk.get_value()))
    ab = always_redraw(lambda: ab_bars(lk.get_value()))
    rd = Live(lk, lambda v: f"k = {int(round(np.exp(v)))}", .055, KC, place=k_readout, italic=False)
    for x in (needle, bars, ab):
        x.overlap_ok = True
    return needle, bars, ab, rd


B2_C, B2_W = BENCH2 + UP * .45 + LEFT * .1, 14.6


class Sc06(Sheet):
    SID = "sc06"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(STAGE, STAGE_W)
        W = sc05_end()
        self.add(*W.values())
        lk = ValueTracker(np.log(60))
        ds, rs, abs_ = dial_static(), rank_bars_static(), ab_static()
        needle, bars, ab, rd = bench2_live(lk)
        # k1 k 在做什麼？鏡頭往下到旋鈕；鏡頭還在移動時就開始畫旋鈕（不要出現全空的畫面）
        self.at(A("k1", 0), self.cam(B2_C, B2_W),
                Succession(Wait(.7), AnimationGroup(Create(ds[0]), LaggedStart(*[Create(x) for x in ds[1]], lag_ratio=.2), Write(ds[2]),
                                                    DrawBorderThenFill(ds[3]), Write(ds[4]), Create(needle))),
                run_time=2.0, sfx="whoosh", gain=.5)
        # 直條從底線長出來（直接 self.add 會整排跳出來；kit.at() 會在 GrowFromEdge 期間暫停 always_redraw）
        self.at(A("k1", .55), Write(rd), Create(rs[0]), Write(rs[2]), LaggedStart(*[Write(x) for x in rs[1]], lag_ratio=.15),
                GrowFromEdge(bars, DOWN), run_time=1.1)
        # k2 k 越大（例如 200）：前幾名的差距被壓平
        self.at(A("k2", .3), lk.animate.set_value(np.log(200)), run_time=2.6, sfx="slide")
        # k3 偏好多路累積：A、B 的合併長條
        self.at(A("k3", .05), Create(abs_[0]), Write(abs_[1]), Write(abs_[2]), Write(abs_[3]), Write(abs_[4]), run_time=1.0)
        av = ab_vals(lk)
        self.at(A("k3", .3), GrowFromEdge(ab, LEFT), run_time=.6)                # 長條先從左邊長出來，讀數再寫在長條末端
        self.at(A("k3", .42), Write(av), FadeIn(ab_note()), run_time=.6)
        self.at(A("k3", .7), Indicate(abs_[1], color=TXT_STRONG), run_time=.8)
        # k4 k 越小（例如 1）：第一名的獎勵懸殊
        self.at(A("k4", .25), lk.animate.set_value(0), run_time=2.8, sfx="slide")
        # k5 相信單一路的強訊號：B 領先
        self.at(A("k5", .3), Indicate(abs_[2], color=TXT_STRONG), Indicate(abs_[4], color=RANK), run_time=1.0)
        # k6 選 60
        self.at(A("k6", .25), lk.animate.set_value(np.log(60)), run_time=2.2, sfx="slide")
        self.at(A("k6", .85), Indicate(rd, color=KC, scale_factor=1.15), run_time=.7)
        # k7 寧可相信共識
        self.at(A("k7", .3), Circumscribe(VGroup(abs_[1], abs_[3]), color=TXT_STRONG, buff=.1), run_time=1.4)
        self.at(A("k7", .82), Indicate(abs_[4], color=RANK), run_time=.9)                   # 「不要被單一路的巧合命中牽著走」
        self.finish()


# ---------------- sc07：共識的盲點 ----------------
ROWS7 = {"v": "*CDN", "f": "CDEN"}
GHOST_P = np.array([ROW_X[2], -2.5, 0])
SY, NY = .5, -.45


def ghost_star():
    g = ans_card().scale(.8).move_to(GHOST_P)
    g.box.set_stroke(opacity=.4)
    g.glyph.set_opacity(.35)
    lab = T("沒撈到", .046, MUTED).next_to(g, RIGHT, buff=.22)
    out = VGroup(g, lab)
    out.card, out.lab = g, lab
    return out


def star_line():
    den = VGroup(M("60", .046, KC), M("+", .046), M("1", .046, RANK)).arrange(RIGHT, buff=.07)
    f = fraction(M("1", .046), den, .046, gap=.09)
    s = Star(5, outer_radius=.17, inner_radius=.07).set_fill(ANS, 1).set_stroke(width=0)
    g = VGroup(s, M("=", .05), f, M("+", .05), M("0", .05, FTS), M("≈", .05), M("0.0164", .055, TXT_STRONG)).arrange(RIGHT, buff=.16)
    g.move_to(np.array([-2.55, SY, 0]), aligned_edge=ORIGIN)
    g.f, g.zero, g.val = f, g[4], g[6]
    g.overlap_ok = True
    return g


def noise_line():
    g = calc_line("N", "4", "4", "0.0313", NY)
    g.align_to(star_line(), LEFT)
    return g


def calc_note7():
    return T("代入公式計算", .042, MUTED).move_to(np.array([-2.0, 1.22, 0]))


def pin(p):
    """權宜解法的圖釘：一個小圓頭＋針。"""
    head = Circle(.16).set_fill(TXT_STRONG, 1).set_stroke(width=0)
    needle = Line(ORIGIN, DOWN * .3).set_stroke(TXT_STRONG, 3.5).next_to(head, DOWN, buff=0)
    return VGroup(head, needle).move_to(p)


# 投影片源頭（BENCH3）
SLIDE_P = BENCH3 + np.array([-4.0, 0, 0])
VLM_P = BENCH3 + np.array([-1.65, 0, 0])
SUM_P = BENCH3 + np.array([.85, 0, 0])
MV_P, MF_P = BENCH3 + np.array([3.15, 1.2, 0]), BENCH3 + np.array([3.15, -1.2, 0])


def slide_icon():
    fr = RoundedRectangle(corner_radius=.08, width=1.9, height=1.25).set_stroke(TXT, 2).set_fill(PANEL, 1)
    bars = VGroup(*[Rectangle(width=.22, height=h).set_fill(MUTED, .8).set_stroke(width=0) for h in (.3, .48, .62)]) \
        .arrange(RIGHT, buff=.12, aligned_edge=DOWN)
    bars.move_to(fr).shift(DOWN * .12 + LEFT * .35)
    lines = VGroup(*[Line(LEFT * .28, RIGHT * .28).set_stroke(MUTED, 2.5) for _ in range(3)]).arrange(DOWN, buff=.13)
    lines.move_to(fr).shift(RIGHT * .45)
    ttl = Line(LEFT * .6, RIGHT * .6).set_stroke(TXT, 3).move_to(fr.get_top() + DOWN * .2)
    g = VGroup(fr, bars, lines, ttl).move_to(SLIDE_P)
    lab = T("投影片", .046, TXT).next_to(g, DOWN, buff=.2)
    out = VGroup(g, lab)
    out.icon, out.lab = g, lab
    return out


def vlm_node():
    n = node(TXT_STRONG, .48, .06).move_to(VLM_P)
    t = M("VLM", .046, TXT_STRONG).move_to(VLM_P)
    lab = T("視覺語言模型", .04, MUTED).next_to(n, DOWN, buff=.2)
    return VGroup(n, t, lab)


def summary_doc(word="revenue growth"):
    fr = RoundedRectangle(corner_radius=.08, width=2.5, height=1.3).set_stroke(TXT, 2).set_fill(CARD_FILL, 1).move_to(SUM_P)
    ls = VGroup(*[Line(LEFT * w, RIGHT * w).set_stroke(MUTED, 2.5) for w in (.85, .6)]).arrange(DOWN, buff=.14, aligned_edge=LEFT)
    ls.move_to(fr).shift(UP * .3 + LEFT * .1)
    wd = M(word, .042, TXT_STRONG, italic=True).move_to(fr).shift(DOWN * .3)
    lab = T("摘要", .046, TXT).next_to(fr, DOWN, buff=.2)
    g = VGroup(fr, ls, wd, lab)
    g.fr, g.word, g.lab = fr, wd, lab
    return g


def mini_lane(k):
    p = MV_P if k == "v" else MF_P
    n = node(lane_color(k), .3).move_to(p)
    ic = (vec_icon() if k == "v" else fts_icon()).move_to(p)
    lab = T("向量搜尋" if k == "v" else "全文搜尋", .046, lane_color(k)).next_to(n, RIGHT, buff=.2)
    return VGroup(n, ic, lab)


def bench3_links():
    return VGroup(*[Arrow(SUM_P + RIGHT * 1.27 + (UP if k == "v" else DOWN) * .35, (MV_P if k == "v" else MF_P) + LEFT * .32, buff=.05, stroke_width=3,
                          max_tip_length_to_length_ratio=.12).set_color(lane_color(k)) for k in "vf"])


def bench3_base():
    s, v, sm = slide_icon(), vlm_node(), summary_doc()
    a1 = Arrow(SLIDE_P + RIGHT * 1.0, VLM_P + LEFT * .5, buff=.05, stroke_width=3, max_tip_length_to_length_ratio=.15).set_color(LINE)
    a2 = Arrow(VLM_P + RIGHT * .5, SUM_P + LEFT * 1.28, buff=.05, stroke_width=3, max_tip_length_to_length_ratio=.15).set_color(LINE)
    return dict(slide=s, vlm=v, sum=sm, a1=a1, a2=a2, mv=mini_lane("v"), mf=mini_lane("f"), links=bench3_links())


B3_C, B3_W = BENCH3 + DOWN * .25 + RIGHT * .5, 14.2


def sc07_end():
    W = pipe_base(ROWS7, more=False)
    W["cv"], W["cf"] = row_cards("v", ROWS7["v"]), row_cards("f", ROWS7["f"])
    W["rv_"], W["rf_"] = row_ranks("v", 4), row_ranks("f", 4)
    W["gh"] = ghost_star()            # 兩條算式在 t8 已經淡掉（讓位給錘錘）
    W["tot_cards"] = VGroup(tot_card("*", 0), tot_card("C", 1), tot_card("D", 2), tot_card("N", 3))
    W["pins"] = VGroup(pin(tot_slot(0) + LEFT * .72), pin(tot_slot(1) + LEFT * .72))
    return W


class Sc07(Sheet):
    SID = "sc07"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(B2_C, B2_W)
        W = sc05_end()
        self.add(*W.values())
        lk = ValueTracker(np.log(60))
        ds, rs, abs_ = dial_static(), rank_bars_static(), ab_static()
        needle, bars, ab, rd = bench2_live(lk)
        b2 = [ds, rs, abs_, needle, bars, ab, rd, ab_vals(lk), ab_note()]
        self.add(*b2)
        # t1 獎勵共識藏著一個假設：回到管線，清掉上一個例子
        old = [W["ca"], W["cb"], W["note"], W["ta"], W["tb"], W["b8"]]
        self.at(A("t1", .0), self.cam(STAGE, STAGE_W), *[FadeOut(x, rate_func=rate_functions.rush_into) for x in b2],
                *[FadeOut(x) for x in old], run_time=1.6, sfx="whoosh", gain=.5)
        self.remove(*b2)
        # t2 假設每一路都看得到正確答案：新的例子，正確答案（綠星）兩排都有
        nv, nf = row_cards("v", "*CDN"), row_cards("f", "CD*N")
        rv4, rf4 = row_ranks("v", 4), row_ranks("f", 4)
        cv, cf = W["cv"], W["cf"]          # cf 有 4 張（第 4 張是 B）
        self.at(A("t2", .05), ReplacementTransform(cv[0], nv[0]), ReplacementTransform(cv[1], nv[1]), ReplacementTransform(cv[2], nv[2]),
                ReplacementTransform(W["mv"], nv[3]),
                *[ReplacementTransform(cf[i], nf[i]) for i in range(4)],
                ReplacementTransform(W["rv_"], rv4[:3]), FadeIn(rv4[3]), ReplacementTransform(W["rf_"], rf4[:3]), FadeIn(rf4[3]),
                run_time=1.1, sfx="click")
        self.at(A("t2", .55), Highlight(nv[0], color=ANS, scale_factor=1.15), Highlight(nf[2], color=ANS, scale_factor=1.15), run_time=1.0)
        self.at(A("t2", .85), Indicate(rv4[0], color=RANK, scale_factor=1.35), Indicate(rf4[2], color=RANK, scale_factor=1.35),
                run_time=.8)                                                                   # 「只是名次高低不同」：第 1 和第 3
        # t3 正確答案在一路完全沒被撈到：全文那排的綠星掉出去，E 補進來
        gh = ghost_star()
        ecard = card("E").move_to(row_pos("f", 2))
        self.at(A("t3", .35), ReplacementTransform(nf[2], gh.card), run_time=1.0, sfx="thud", gain=.6)
        self.at(A("t3", .6), Write(gh.lab), FadeIn(ecard, shift=DOWN * .2), run_time=.8)
        # t4 那一路貢獻 0：綠星 ＝ 1/(60+1) + 0 ≈ 0.0164
        sl, nl, note = star_line(), noise_line(), calc_note7()
        self.at(A("t4", .05), TransformFromCopy(nv[0].glyph, sl[0]), Write(sl[1]), Write(VGroup(sl.f.num, sl.f.bar, sl.f.den[:2])),
                run_time=.9)
        self.at(A("t4", .25), TransformFromCopy(rv4[0], sl.f.den[2]), run_time=.8)
        self.at(A("t4", .45), Write(sl[3]), TransformFromCopy(gh.card, sl.zero), run_time=.9)
        self.at(A("t4", .7), Write(sl[5]), Write(sl.val), FadeIn(note), run_time=.8)
        # t6 比方說，兩路都排第 4 的雜訊文件 N
        self.at(A("t6", .2), Highlight(nv[3], color=TXT_STRONG, scale_factor=1.15), Highlight(nf[3], color=TXT_STRONG, scale_factor=1.15),
                run_time=.9)
        self.at(A("t6", .38), Write(nl.L), Write(nl[1]), Write(VGroup(nl.f1.num, nl.f1.bar, nl.f1.den[:2])), Write(nl[3]),
                Write(VGroup(nl.f2.num, nl.f2.bar, nl.f2.den[:2])), TransformFromCopy(rv4[3], nl.f1.den[2]),
                TransformFromCopy(rf4[3], nl.f2.den[2]), run_time=1.1)
        self.at(A("t6", .62), Write(nl[5]), Write(nl.val), run_time=.7)
        tc = [tot_card("C", 0), tot_card("D", 1), tot_card("N", 2), tot_card("*", 3)]
        self.at(A("t6", .82), LaggedStart(*[FadeIn(c, shift=RIGHT * .3) for c in tc], lag_ratio=.18), run_time=1.1, sfx="slide")
        # t7 獎勵共識變成懲罰
        self.at(A("t7", .3), Highlight(tc[3], color=ANS, scale_factor=1.2), Indicate(nl.val, color=TXT_STRONG), run_time=1.0)
        # t8（錘錘）等等，所以正確答案被排到後面了？算式功成身退；錘錘從 C、D 兩張卡的空隙垂到中間，看向總榜第 4 名。
        # 原本擠在算式和 Σ 之間、身體壓在線上（2026-11-10 逐格檢查）
        pl, drop = self.plumb_in(np.array([(ROW_X[1] + ROW_X[2]) / 2, -.15, 0]), .3)
        self.at(A("t8", -.15), FadeOut(sl, shift=DOWN * .1), FadeOut(nl, shift=DOWN * .1), FadeOut(note), *drop, run_time=.8)
        self.lipsync(pl)
        self.at(A("t8", .2), *pl.curl(), *pl.mood("wow"), run_time=.8)
        self.at(A("t8", .55), *pl.look(RIGHT + DOWN * .3), run_time=.4)
        self.at(A("t8", .9), *self.plumb_out(pl), run_time=.7)
        self.remove(pl)
        # t9 我們自己做投影片檢索時遇過：鏡頭到源頭；鏡頭還在移動時就開始畫投影片
        B3 = bench3_base()
        self.at(A("t9", .0), self.cam(B3_C, B3_W),
                Succession(Wait(1.15), AnimationGroup(DrawBorderThenFill(B3["slide"].icon), Write(B3["slide"].lab))),
                run_time=2.2, sfx="whoosh", gain=.5)
        # t10 VLM 寫成文字摘要，再做混合檢索
        self.at(A("t10", .1), GrowArrow(B3["a1"]), DrawBorderThenFill(B3["vlm"][0]), Write(B3["vlm"][1]), run_time=1.0)
        self.at(A("t10", .3), Write(B3["vlm"][2]), run_time=.7)
        self.at(A("t10", .5), GrowArrow(B3["a2"]), DrawBorderThenFill(B3["sum"].fr), Create(B3["sum"][1]), Write(B3["sum"].word),
                Write(B3["sum"].lab), run_time=1.2)
        self.at(A("t10", .78), *[GrowArrow(a) for a in B3["links"]], *[FadeIn(m, shift=RIGHT * .2) for m in (B3["mv"], B3["mf"])],
                run_time=1.0)
        # t12 向量第 1、全文沒撈到；反過來也會
        r1 = M("1", .055, RANK).next_to(B3["mv"], RIGHT, buff=.3)
        nf_ = T("沒撈到", .046, MUTED).next_to(B3["mf"], RIGHT, buff=.3)
        self.at(A("t12", .15), Write(r1), run_time=.6)
        self.at(A("t12", .35), Write(nf_), run_time=.6)
        r1b = r1.copy().next_to(B3["mf"], RIGHT, buff=.3)
        nfb = nf_.copy().next_to(B3["mv"], RIGHT, buff=.3)
        self.at(A("t12", .75), Transform(r1, r1b), Transform(nf_, nfb), run_time=1.0)
        # t13 融合之後排名反而不好
        self.at(A("t13", .1), Transform(r1, r1.copy().next_to(B3["mv"], RIGHT, buff=.3)),
                Transform(nf_, nf_.copy().next_to(B3["mf"], RIGHT, buff=.3)), run_time=.8)
        self.at(A("t13", .55), Indicate(nf_, color=TXT_STRONG, scale_factor=1.15), run_time=.8)     # 排名不好的原因：這一路沒撈到
        # t14 兩路共用同一份摘要
        self.at(A("t14", .2), Highlight(B3["sum"].fr, color=TXT_STRONG, scale_factor=1.06), run_time=.9)
        self.at(A("t14", .45), *[ShowPassingFlash(a.copy().set_stroke(width=8), time_width=.5) for a in B3["links"]], run_time=1.0)
        self.at(A("t14", .8), Wiggle(B3["sum"].word, scale_value=1.08, rotation_angle=.02 * TAU), run_time=.8)   # 「摘要的用詞不穩定」
        # t15 同一張圖：revenue growth 或 sales increase
        w2 = M("sales increase", .042, TXT_STRONG, italic=True).move_to(B3["sum"].word)
        B3["sum"].word._h0 = w2.height
        self.at(A("t15", .45), Transform(B3["sum"].word, w2), run_time=.9)
        # t16 全文搜尋掛零
        zero = M("0", .07, FTS).move_to(nf_.get_center())
        self.at(A("t16", .3), Indicate(B3["mf"][0], color=FTS), ReplacementTransform(nf_, zero), run_time=1.0, sfx="thud", gain=.5)
        # t17 源頭一樣，破壞了「正交」
        perp = M("⊥", .09, TXT_STRONG).move_to(SUM_P + RIGHT * 1.95)
        x2 = Line(perp.get_corner(DL) + DL * .08, perp.get_corner(UR) + UR * .08).set_stroke(BAD, 3)
        x2.cross_ok = True
        self.at(A("t17", .3), Write(perp), run_time=.7)
        self.at(A("t17", .6), Create(x2), *[a.animate.set_stroke(opacity=.5) for a in B3["links"]], run_time=.7)
        # t18 權宜解法：兩排的第 1 名都釘在總榜最前面
        pins = VGroup(pin(tot_slot(0) + LEFT * .72), pin(tot_slot(1) + LEFT * .72))
        self.at(A("t18", .0), self.cam(STAGE, STAGE_W), run_time=1.8, sfx="whoosh", gain=.5)
        star_t, c_t = tot_card("*", 0), tot_card("C", 1)
        self.at(A("t18", .4), tc[3].animate.move_to(tot_slot(0)), tc[0].animate.move_to(tot_slot(1)), tc[1].animate.move_to(tot_slot(2)),
                tc[2].animate.move_to(tot_slot(3)), run_time=1.2, sfx="slide")
        self.at(A("t18", .8), LaggedStart(FadeIn(pins[0], shift=DOWN * .2), FadeIn(pins[1], shift=DOWN * .2), lag_ratio=.4),
                Highlight(nv[0], color=ANS), Highlight(nf[0], color=TXT_STRONG), run_time=1.0, sfx="click")
        self.finish()


# ---------------- sc08：由淺到深，三層補救；最後拉到全景 ----------------
STRIP_Y, STRIP_X0, STRIP_X1 = -3.45, -4.3, 1.3
DEEP_C, DEEP_W = np.array([-1.3, -.72, 0]), 17.0
RIGHT_C, RIGHT_W = np.array([6.75, .25, 0]), 11.6
ALL_C, ALL_W = np.array([.55, .02, 0]), 18.6
STAR_RANK = 37                                   # 正確答案在全文的深處（舉例，畫面不標數字）


def strip_x(r):
    return STRIP_X0 + (STRIP_X1 - STRIP_X0) * (r - 1) / 99


def deep_strip():
    base = Line([STRIP_X0, STRIP_Y, 0], [STRIP_X1, STRIP_Y, 0]).set_stroke(FTS, 3, .9)
    ticks = VGroup(*[Line(UP * .1, DOWN * .1).set_stroke(FTS, 1.6, .7).move_to([strip_x(r), STRIP_Y, 0]) for r in range(5, 101, 5)])
    lab = VGroup(M("①", .055, TXT_STRONG), T("拉深召回", .05, TXT_STRONG)).arrange(RIGHT, buff=.15).next_to(base, LEFT, buff=.4)
    g = VGroup(base, ticks, lab)
    g.dots_ok = base.dots_ok = True
    g.base, g.lab = base, lab
    return g


def cutoff(r):
    x = strip_x(r) + .03
    ln = DashedLine([x, STRIP_Y + .32, 0], [x, STRIP_Y - .32, 0], dash_length=.07).set_stroke(TXT_STRONG, 2.2)
    ln.cross_ok = True
    return ln


def star_dot(lit=False):
    s = Star(5, outer_radius=.2, inner_radius=.085).set_fill(ANS, 1 if lit else .35).set_stroke(width=0)
    return s.move_to([strip_x(STAR_RANK), STRIP_Y + .32, 0])


def bench3_end():
    B3 = bench3_base()
    w2 = M("sales increase", .042, TXT_STRONG, italic=True).move_to(B3["sum"].word)
    B3["sum"].word.become(w2)
    B3["sum"].word._h0 = w2.height
    B3["r1"] = M("1", .055, RANK).next_to(B3["mv"], RIGHT, buff=.3)
    B3["zero"] = M("0", .07, FTS).move_to(T("沒撈到", .046).next_to(B3["mf"], RIGHT, buff=.3).get_center())
    perp = M("⊥", .09, TXT_STRONG).move_to(SUM_P + RIGHT * 1.95)
    x2 = Line(perp.get_corner(DL) + DL * .08, perp.get_corner(UR) + UR * .08).set_stroke(BAD, 3)
    x2.cross_ok = True
    B3["perp"], B3["x2"] = perp, x2
    for a in B3["links"]:
        a.set_stroke(opacity=.5)
    return B3


def tot_brace(W):
    """總榜整份接到 reranker：大括號框住五個名次，從尖端拉線。原本的線從第 3 名旁邊出發，看起來像只有 N 送進去（2026-11-10）。"""
    b = Brace(VGroup(W["tot"].slots, W["tot"].nums), RIGHT, buff=.1).set_fill(LINE, .9).set_stroke(width=0)
    b.overlap_ok = True
    return b


def rr_node():
    # 底色不透明：f9 卡片從節點「後面」穿過去，像被 reranker 重新處理（透明的話會看到卡片疊在字上）
    n = Circle(.5).set_stroke(TXT_STRONG, 3).set_fill(CARD_FILL, 1).move_to(RR)
    t = T("語意", .05, TXT_STRONG).move_to(RR)
    lab = VGroup(M("③", .05, TXT_STRONG), M("reranker", .05, TXT_STRONG)).arrange(DOWN, buff=.08).next_to(n, UP, buff=.18)
    return VGroup(n, t, lab)


RECAP_C, RECAP_W = np.array([.8, -.4, 0]), 19.2       # 收尾全景：管線＋下方三點回顧
RECAP_Y = -3.45
PLUMB_END = np.array([-6.72, -3.25, 0])   # 左下角；字在它右邊、比「全文搜尋」低一截


def dim_sig(W, a):
    """Σ 與 RRF 變暗或回復：只調線和字，不打開圓的填色（set_opacity 會把填色也設成 a）。"""
    sg = W["sig"]
    return [sg.node.animate.set_stroke(opacity=a).set_fill(opacity=.1 * a), sg.sym.animate.set_opacity(a), W["rrf"].animate.set_opacity(a)]


def recap_frame(x0, x1, y0, y1):
    """回顧時框住圖上的一個元件（細線圓角框，不填色）。"""
    r = RoundedRectangle(corner_radius=.25, width=x1 - x0, height=y1 - y0).set_stroke(TXT_STRONG, 2, .9).set_fill(opacity=0)
    return r.move_to(np.array([(x0 + x1) / 2, (y0 + y1) / 2, 0]))


def recap_item(n):
    """三點回顧：① 只看名次、② Σ 1/(60 + 名次)、③ 小心單路缺席。放在各自元件的正下方。"""
    badge = M("①②③"[n - 1], .062, TXT_STRONG)
    if n == 1:
        body = VGroup(T("只看", .06, TXT_STRONG), T("名次", .06, RANK)).arrange(RIGHT, buff=.06)
        x = -2.05
    elif n == 2:
        k = M("60", .065, KC)
        body = VGroup(M("Σ", .08, TXT_STRONG), term(k, .065)).arrange(RIGHT, buff=.14)
        body.k = k
        x = 2.3
    else:
        body = T("小心單路缺席", .06, TXT_STRONG)
        x = 7.4          # 寬約 4：再往右會超出安全邊界（全景鏡頭右緣 9.44）
    g = VGroup(badge, body).arrange(RIGHT, buff=.22).move_to(np.array([x, RECAP_Y, 0]))
    g.k = getattr(body, "k", None)
    return g


def recap_link(fr, it):
    x = fr.get_center()[0]
    return Line([x, fr.get_bottom()[1] - .08, 0], [x, it.get_top()[1] + .12, 0]).set_stroke(TXT_STRONG, 1.6, .6)


def fin_slot(i):
    return np.array([FIN_X, TOT_Y[i], 0])


class Sc08(Sheet):
    SID = "sc08"

    def construct(self):
        A, E = self.A, self.E
        self.cam_set(STAGE, STAGE_W)
        W = sc07_end()
        self.add(*W.values())
        # f1 由淺到深，疊著用：清掉權宜解法
        self.at(A("f1", 0), FadeOut(W["pins"]), run_time=.8)
        tc = W["tot_cards"]
        self.at(A("f1", .35), tc[0].animate.move_to(tot_slot(3)), tc[1].animate.move_to(tot_slot(0)), tc[2].animate.move_to(tot_slot(1)),
                tc[3].animate.move_to(tot_slot(2)), run_time=1.0)
        self.at(A("f1", .65), ShowPassingFlash(W["of"].copy().set_stroke(FTS, 7), time_width=.4),
                ShowPassingFlash(W["ov"].copy().set_stroke(VEC, 7), time_width=.4), run_time=1.0)
        # f2 ① 拉深召回：全文的候選一路往下延伸到前 100 名
        ds = deep_strip()
        c0 = cutoff(4)
        st = star_dot()
        self.at(A("f2", .0), self.cam(DEEP_C, DEEP_W), Create(ds.base), LaggedStart(*[Create(x) for x in ds[1]], lag_ratio=.05),
                Write(ds.lab), run_time=1.4)
        self.at(A("f2", .25), Create(c0), FadeOut(W["gh"].lab), ReplacementTransform(W["gh"].card, st), run_time=1.0)
        br = Line([strip_x(50), STRIP_Y + .2, 0], [strip_x(100), STRIP_Y + .2, 0]).set_stroke(MUTED, 2)
        rng = VGroup(M("50 ~ 100", .05, MUTED)).next_to(br, UP, buff=.12)
        self.at(A("f2", .6), Create(br), Write(rng), run_time=.8)
        c1 = cutoff(100)
        self.at(A("f2", .75), Transform(c0, c1), Succession(Wait(.75), st.animate(run_time=.5).set_fill(ANS, 1).scale(1.25)),
                run_time=1.3, sfx="slide")
        # f3 很多單路缺席，其實是候選在截斷線外被切掉
        cut_lab = T("截斷線", .05, TXT_STRONG).next_to(cutoff(4), DOWN, buff=.1).shift(RIGHT * .25)   # 放在虛線下方；放右上會和綠星連成「截斷線 ★」
        ghost_c = cutoff(4).set_stroke(opacity=.35)
        self.at(A("f3", .2), FadeIn(ghost_c), Write(cut_lab), run_time=.8)
        self.at(A("f3", .55), Indicate(st, color=ANS, scale_factor=1.6), run_time=1.0)
        # f4 ② 修表示層：到源頭
        B3 = bench3_end()
        n2 = VGroup(M("②", .055, TXT_STRONG), T("修表示層", .05, TXT_STRONG)).arrange(RIGHT, buff=.15)
        n2.move_to(BENCH3 + np.array([-3.4, 1.75, 0]))
        self.at(A("f4", .0), self.cam(B3_C, B3_W), FadeIn(VGroup(*B3.values()), rate_func=lambda u: 1.0), run_time=2.0,
                sfx="whoosh", gain=.5)
        self.at(A("f4", .45), Write(n2), run_time=.8)
        # f5 全文也索引 OCR 抽出的原始文字：兩路的源頭分開
        ocr = VGroup(RoundedRectangle(corner_radius=.08, width=1.9, height=.7).set_stroke(FTS, 2).set_fill(CARD_FILL, 1),
                     T("OCR 原文", .046, FTS))
        ocr[1].move_to(ocr[0])
        ocr.move_to(np.array([SUM_P[0], MF_P[1] - .55, 0]))
        a_s = Arrow(SLIDE_P + DOWN * 1.2, ocr.get_left() + LEFT * .05, buff=.05, stroke_width=3,
                    max_tip_length_to_length_ratio=.1).set_color(LINE)
        a_s.cross_ok = True
        a_f = Arrow(ocr.get_right(), MF_P + LEFT * .3 + DOWN * .12, buff=.05, stroke_width=3, max_tip_length_to_length_ratio=.25).set_color(FTS)
        self.at(A("f5", .15), GrowArrow(a_s), DrawBorderThenFill(ocr[0]), Write(ocr[1]), run_time=1.1)
        self.at(A("f5", .45), GrowArrow(a_f), run_time=.8)
        self.at(A("f5", .7), FadeOut(B3["x2"]), Indicate(B3["perp"], color=GOOD), B3["zero"].animate.set_opacity(.3), run_time=.9)
        # f7 ③ 最根本的一層：reranker（接在總榜後面）
        rr = rr_node()
        brace = tot_brace(W)
        lk_ = seg(brace.get_tip() + RIGHT * .1, RR + LEFT * .5, TXT_STRONG, SW, .7)
        deep = VGroup(ds, c0, ghost_c, cut_lab, st, br, rng)
        self.at(A("f7", -.15), self.cam(RIGHT_C, RIGHT_W), FadeOut(deep, rate_func=rate_functions.rush_into), run_time=1.6,
                sfx="whoosh", gain=.5)
        self.remove(*[v for v in B3.values()], ocr, a_s, a_f, n2)
        self.at(A("f7", .62), GrowFromCenter(brace), Create(lk_), DrawBorderThenFill(rr[0]), Write(rr[2]), run_time=1.0)
        # f8 RRF 只是統計，reranker 懂語意
        self.at(A("f8", .2), *dim_sig(W, .45), run_time=.8)
        self.at(A("f8", .6), Write(rr[1]), Highlight(rr[0], color=TXT_STRONG, scale_factor=1.12), run_time=1.0)
        # f9 拉深後的聯集交給 reranker，查詢和每份文件一對一重新打分
        qchip = VGroup(Circle(.28).set_stroke(TXT_STRONG, 2.4).set_fill(TXT_STRONG, .08), T("查詢", .042, TXT_STRONG))
        qchip[1].next_to(qchip[0], RIGHT, buff=.12)
        qchip.shift(RR + DOWN * 1.45 - qchip[0].get_center())
        lens = query_node().lens.copy().move_to(qchip[0])
        qchip.add(lens)
        union_l = T("聯集", .046, MUTED).move_to(np.array([TOT_X - 1.0, -1.2, 0]))
        self.at(A("f9", .05), Write(union_l), *[Highlight(c, color=TXT_STRONG, scale_factor=1.08, inner=False) for c in tc], run_time=1.0)
        qlink = seg(qchip[0].get_top(), rr[0].get_bottom(), TXT_STRONG, 2, .6)
        self.at(A("f9", .3), FadeIn(qchip, shift=UP * .2), Create(qlink), run_time=.9)
        # 四張卡依序從總榜出發、從 reranker 節點後面穿過去，在右邊排出新名次（原本直線飛過「③ reranker」的字）
        # tc 的物件：0＝★（總榜第 4）、1＝C、2＝D、3＝N → 新名次 ★、C、D、N
        rr[0].set_z_index(4)
        rr[1].set_z_index(5)
        fin = [c.copy().set_z_index(3) for c in tc]

        def through(c, i):
            a, b = c.get_center(), fin_slot(i)
            path = VMobject().set_points_smoothly([a, (a + RR) / 2 + DOWN * .1 * (a[1] - RR[1]), RR, (RR + b) / 2, b])
            return MoveAlongPath(c, path, rate_func=smooth)
        hs = [2.0, .9, .75, .4]
        fnums = VGroup(*[M(str(i + 1), .05, RANK).next_to(fin_slot(i) + RIGHT * .46, RIGHT, buff=.2) for i in range(4)])
        fbars = VGroup(*[Rectangle(width=h * .55, height=.2).set_stroke(SCORE, 1.2).set_fill(SCORE, .6)
                         .move_to(np.array([FIN_X + 1.05 + h * .275, TOT_Y[i], 0])) for i, h in enumerate(hs)])
        self.add(*fin)
        self.at(A("f9", .55), LaggedStart(*[through(fin[i], i) for i in range(4)], lag_ratio=.25), run_time=1.8, sfx="tick")
        # f10 不管從哪一路來：進了聯集，就有機會排到最前面
        self.at(A("f10", .1), LaggedStart(*[GrowFromEdge(b, LEFT) for b in fbars], lag_ratio=.2), Write(fnums), run_time=1.2)
        self.at(A("f10", .55), Highlight(fin[0], color=ANS, scale_factor=1.2), Flash(fin[0], color=ANS, line_length=.2), run_time=1.0,
                sfx="ding", gain=.5)
        # ---- 收尾（v5，使用者 2026-11-08）：最後一個畫面是整個方法的全景圖，三點回顧各對應圖上的一個元件 ----
        # f11 把整條路再看一次：拉到全景，一道光從查詢流到最後的第 1 名
        self.at(A("f11", .0), self.cam(RECAP_C, RECAP_W), FadeOut(union_l), FadeOut(fbars), FadeOut(qchip), FadeOut(qlink),
                FadeOut(rr[2][0]), *dim_sig(W, 1.0), run_time=2.0, sfx="swoosh", gain=.4)
        flow = [*W["ql"], W["iv"], W["if_"], W["ov"], W["of"], W["tot"].link, lk_]
        self.at(A("f11", .5), LaggedStart(*[ShowPassingFlash(x.copy().set_stroke(GOLD, 6, 1), time_width=.5) for x in flow],
                                          lag_ratio=.18), run_time=1.8)
        # 三個元件的框、連到下方的回顧項目
        # fr3 左邊要夾在大括號（約 5.61）和「reranker」字（約 5.84）之間
        fr1, fr2, fr3 = recap_frame(-4.45, .3, -2.4, 2.8), recap_frame(1.55, 3.05, -1.25, .7), recap_frame(5.7, 9.3, -1.3, 2.15)
        it1, it2, it3 = recap_item(1), recap_item(2), recap_item(3)
        ln1, ln2, ln3 = recap_link(fr1, it1), recap_link(fr2, it2), recap_link(fr3, it3)
        # f12 ① 只看名次：框住兩排名次
        self.at(A("f12", .05), Create(fr1), run_time=.9)
        self.at(A("f12", .3), Create(ln1), Write(it1), run_time=1.1)
        self.at(A("f12", .65), Indicate(W["rv_"], color=RANK, scale_factor=1.15), Indicate(W["rf_"], color=RANK, scale_factor=1.15),
                run_time=1.0)
        # f13 ② 每一路 1/(k + 名次)，加總：框住 Σ
        self.at(A("f13", .0), fr1.animate.set_stroke(opacity=.3), ln1.animate.set_stroke(opacity=.3), it1.animate.set_opacity(.5),
                Create(fr2), run_time=.9)
        self.at(A("f13", .3), Create(ln2), Write(it2), run_time=1.1)
        self.at(A("f13", .7), ShowPassingFlash(W["ov"].copy().set_stroke(VEC, 7), time_width=.4),
                ShowPassingFlash(W["of"].copy().set_stroke(FTS, 7), time_width=.4), Indicate(W["sig"].sym, color=GOLD, scale_factor=1.3),
                run_time=1.0)
        # f13b k 越大越偏好共識，Cerebras 選了 60
        self.at(A("f13b", .5), Indicate(it2.k, color=KC, scale_factor=1.3), run_time=.9)
        # f14 ③ 共識的盲點：正確答案被擠到第 4；框住 reranker 與新排名
        self.at(A("f14", .0), fr2.animate.set_stroke(opacity=.3), ln2.animate.set_stroke(opacity=.3), it2.animate.set_opacity(.5),
                Highlight(tc[0], color=ANS, scale_factor=1.2), run_time=1.0)
        self.at(A("f14", .4), Create(fr3), run_time=.9)
        self.at(A("f14", .62), Create(ln3), Write(it3), run_time=1.1)
        # f15 補救：最根本的是 reranker，正確答案回到第 1；三點全部亮起＝最後的全景
        self.at(A("f15", .25), Highlight(rr[0], color=TXT_STRONG, scale_factor=1.15), run_time=.9)
        self.at(A("f15", .5), Highlight(fin[0], color=ANS, scale_factor=1.2), Flash(fin[0], color=ANS, line_length=.2), run_time=.9)
        self.at(A("f15", .75), *[f.animate.set_stroke(opacity=.75) for f in (fr1, fr2, fr3)],
                *[l_.animate.set_stroke(opacity=.6) for l_ in (ln1, ln2, ln3)], it1.animate.set_opacity(1), it2.animate.set_opacity(1),
                run_time=.9)
        # f16（錘錘）想看更多細節，完整的文章在說明欄：錘錘本身就是往下指的箭頭
        pl, drop = self.plumb_in(PLUMB_END, .38)
        pl.set_mood("happy")
        self.at(A("f16", -.3), *drop, run_time=.8)
        self.lipsync(pl)
        # 比三點回顧小一級、不用最亮的字色、位置再低一點：和回顧同大同高時會被讀成「第四點」（2026-11-10）。
        # 全景鏡頭寬 19.2，0.052 實際約 0.0385（剛好過下限）
        art = VGroup(T("完整文章", .052, TXT), T("在說明欄", .052, TXT)).arrange(DOWN, buff=.12, aligned_edge=LEFT)
        art.move_to(np.array([PLUMB_END[0] + .5, RECAP_Y - .55, 0]), aligned_edge=LEFT)
        self.at(A("f16", .2), Write(art), *pl.look(DOWN), run_time=.9)
        self.at(A("f16", .5), *pl.hop(-.22), run_time=.45)
        self.at(A("f16", .64), *pl.hop(-.22), run_time=.45)
        self.at(A("f16", .9), *pl.blink(), run_time=.3)
        self.finish()
