"""v005 LLM-as-a-Verifier：大圖元件（評審工廠地圖）。設計在 design.md。

世界座標：2 列 × 3 站，站距 17 × 10，每站內容 ≤ 13 × 7.3（寬 14 的鏡頭剛好填滿）
  S1 考場 (-17, 5)   → S2 評審的腦袋 (0, 5)  → S3 計分板 (17, 5)
  S6 成績單 (-17,-5) ← S5 旋鈕台 (0,-5)      ← S4 期望值塔 (17,-5)
全景草圖：YTV_VIDEO=v005-llm-verifier PYTHONPATH=lib:videos/v005-llm-verifier uv run python -m manim -ql -s \
  --media_dir out/v005-llm-verifier/sketch videos/v005-llm-verifier/world.py Panorama
"""
from kit import *  # noqa: F401,F403

SINE = rate_functions.ease_in_out_sine
POP = rate_functions.ease_out_back
INK = TXT_STRONG


def _c(name, default):
    return C.get(name, default)


ARG = _c("argmax", S["concept_pool"][0])      # argmax：橘
DIST = _c("機率", S["concept_pool"][1])        # 機率分佈：藍
EV = _c("期望值", S["concept_pool"][5])        # 期望值：青綠（主角指針是金色）
GK = _c("G", S["concept_pool"][2])             # 粒度 G：紫
KK = _c("K", S["concept_pool"][3])             # 重複 K：粉
CK = _c("C", S["concept_pool"][4])             # 準則 C：黃綠
TIE = "#8FA3A8"                                # 平手：灰

# ---------------- 站 ----------------
S1 = np.array([-17., 5, 0])
S2 = np.array([0., 5, 0])
S3 = np.array([17., 5, 0])
S4 = np.array([17., -5, 0])
S5 = np.array([0., -5, 0])
S6 = np.array([-17., -5, 0])
STW, STH = 12.4, 5.5        # 每站內容的外框；字幕區在畫面下方 22%，所以內容只能放在站中心 ±2.8
PANO_C, PANO_W = np.array([0., -1.6, 0]), 52.0


def shot(st, w=14.0):
    """鏡頭參數 (中心, 寬)，給 cam／cam_set 用（kit 會自己把 st 對到主畫面中心，避開字幕區）。"""
    return (np.array(st, dtype=float), w)


# S1 版面
SCR_A, SCR_B = S1 + np.array([-4.05, -.3, 0]), S1 + np.array([4.05, -.3, 0])
JUDGE1 = S1 + np.array([0, -1.05, 0])
TASK_C = S1 + np.array([0, 2.12, 0])
# S2 版面
A_POS, B_POS = S2 + np.array([-3.3, -1.15, 0]), S2 + np.array([3.3, -1.15, 0])
TOK_Y = S2[1] + 1.95
BIN_C = S2 + np.array([0, -2.3, 0])
HMAX = 2.1

# 部落格舉例的兩組機率（ev c9）
PA = [0.02, 0.05, 0.13, 0.35, 0.45]           # 軌跡甲：argmax 5，期望值 4.16
PB_KNOWN = {4: 0.30, 5: 0.52}                  # 軌跡乙：只給 4、5 兩格，其餘 0.18 卡上沒給


def ev(ps):
    return sum((i + 1) * p for i, p in enumerate(ps))


# ---------------- 路 ----------------
def road():
    """S 形輸送帶：連接各站的邊。"""
    pts = [S1 + RIGHT * 6.7, S2 + LEFT * 6.7], [S2 + RIGHT * 6.7, S3 + LEFT * 6.7], \
          [S3 + DOWN * 3.75, S4 + UP * 3.75], [S4 + LEFT * 6.7, S5 + RIGHT * 6.7], [S5 + LEFT * 6.7, S6 + RIGHT * 6.7]
    g = VGroup()
    for a, b in pts:
        ln = DashedLine(a, b, dash_length=.22, dashed_ratio=.55).set_stroke(LINE, 5)
        d = normalize(b - a)
        tip = Triangle().set_fill(LINE, 1).set_stroke(width=0).scale(.16).rotate(np.arctan2(d[1], d[0]) - PI / 2).move_to((a + b) / 2)
        g.add(VGroup(ln, tip))
    g.nocheck = True
    return g


# ---------------- 評審「小判」 ----------------
def judge(p, s=1.0, mood="calm", score="5", score_color=INK):
    """戴領結的方臉機器人評審。mood：calm｜unsure（眼睛飄、冒汗、嘴歪）｜sweat（被迫表態）｜happy。
    .head .face .win（胸口分數窗）.score"""
    p = np.array(p, dtype=float)
    g = VGroup()
    body = RoundedRectangle(corner_radius=.22 * s, width=1.9 * s, height=1.5 * s).set_fill(PANEL, 1).set_stroke(TEAL_L, 3).move_to(p + DOWN * .85 * s)
    head = RoundedRectangle(corner_radius=.3 * s, width=1.75 * s, height=1.45 * s).set_fill(SCREEN, 1).set_stroke(TEAL_L, 3).move_to(p + UP * .75 * s)
    ant = VGroup(Line(head.get_top(), head.get_top() + UP * .3 * s).set_stroke(TEAL_L, 3),
                 Dot(head.get_top() + UP * .34 * s, radius=.07 * s, color=TEAL_L))
    hc = head.get_center()
    look = {"calm": 0, "unsure": .08, "sweat": -.06, "happy": 0}[mood]
    eyes = VGroup(*[Dot(hc + np.array([dx * s + look * s, .14 * s, 0]), radius=.11 * s, color=INK) for dx in (-.38, .38)])
    xs = np.linspace(-.32, .32, 11)
    if mood == "happy":
        ys = -.1 * (1 - (xs / .32) ** 2) - .3
    elif mood in ("unsure", "sweat"):
        ys = -.32 + .05 * np.sin(xs * 18)
    else:
        ys = -.28 - .04 * (1 - (xs / .32) ** 2)
    mouth = VMobject().set_points_smoothly([hc + np.array([x * s, y * s, 0]) for x, y in zip(xs, ys)]).set_stroke(INK, 3.5)
    face = VGroup(eyes, mouth)
    if mood in ("unsure", "sweat"):
        drop = VMobject().set_points_smoothly([np.array(q) * s for q in ([0, .16, 0], [.09, -.02, 0], [0, -.12, 0], [-.09, -.02, 0], [0, .16, 0])])
        drop.set_fill(DIST, .95).set_stroke(width=0).move_to(head.get_corner(UR) + np.array([.12, -.1, 0]) * s)
        face.add(drop)
    tie_ = VGroup(Triangle().rotate(-PI / 2), Triangle().rotate(PI / 2)).arrange(RIGHT, buff=0).set_fill(ARG, 1).set_stroke(width=0)
    tie_.scale(.2 * s).move_to(body.get_top() + DOWN * .18 * s)
    win = RoundedRectangle(corner_radius=.08 * s, width=.95 * s, height=.62 * s).set_fill(BG, 1).set_stroke(MUTED, 2).move_to(body.get_center() + DOWN * .18 * s)
    sc = B(score, .05 * s, score_color).move_to(win) if score else VGroup()
    for m in (eyes, mouth, face, tie_, win, sc, ant):
        m.overlap_ok = True
    g.add(body, head, ant, face, tie_, win, sc)
    g.head, g.face, g.win, g.score, g.body = head, face, win, sc, body
    g.overlap_ok = True
    return g


# ---------------- 軌跡卷 ----------------
TRAJ = {
    "甲": ("軌跡甲", GOOD, ["優化查詢", "結果：做對了"]),
    "乙": ("軌跡乙", BAD, ["把資料庫複製到 /tmp", "在複製品上加索引", "在不同存取路徑上比結果", "回報：內部 diff 檢查通過"]),
}


def scroll(key, p, w=4.4, show_verdict=False):
    """一條 agent 軌跡：標題＋四行 log。.lines .title"""
    name, col, lines = TRAJ[key]
    p = np.array(p, dtype=float)
    paper = RoundedRectangle(corner_radius=.15, width=w, height=3.5).set_fill(PANEL, 1).set_stroke(MUTED, 2.5).move_to(p)
    title = B(name, .05, INK).move_to(paper.get_top() + DOWN * .42)
    ls = VGroup(*[T(s, .038, TXT) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=.3)
    ls.next_to(title, DOWN, buff=.38)
    ls.set_x(paper.get_left()[0] + .3 + ls.width / 2)
    g = VGroup(paper, title, ls)
    if show_verdict:
        mk = (check_mark if key == "甲" else cross_mark)(col, .32).next_to(title, RIGHT, buff=.25)
        g.add(mk)
    g.paper, g.title, g.lines = paper, title, ls
    return g


def station1():
    a = scroll("甲", SCR_A, show_verdict=True)
    b = scroll("乙", SCR_B, show_verdict=True)
    j = judge(JUDGE1, .9, "calm", "5", TIE)
    return VGroup(a, b, j)


# ---------------- 機率長條 ----------------
def dist_bars(ps, p, w=4.4, hmax=HMAX, color=DIST, labels=True, values=True, frac=.04, unknown=None):
    """1..G 的機率長條。ps：list（缺的格子用 None）；unknown：把剩下的機率畫成一根灰色「其他」。.bars .nums .labs"""
    p = np.array(p, dtype=float)
    G = len(ps)
    bw = w / G * .62
    base = Line(p + LEFT * w / 2, p + RIGHT * w / 2).set_stroke(LINE, 3)
    bars, nums, labs = VGroup(), VGroup(), VGroup()
    vmax = max(x for x in ps if x is not None)
    for i, x in enumerate(ps):
        cx = p[0] - w / 2 + (i + .5) * w / G
        h = 0 if x is None else max(.02, x / max(vmax, .5) * hmax)
        r = Rectangle(width=bw, height=h).set_fill(color if x is not None else TIE, .9).set_stroke(width=0)
        r.move_to(np.array([cx, p[1] + h / 2, 0]))
        bars.add(r)
        if labels:
            labs.add(T(str(i + 1), frac, MUTED).move_to(np.array([cx, p[1] - .32, 0])))
        if values and x is not None:
            nums.add(T(f"{x:.2f}", frac * .9 if frac * .9 >= S["min_text_frac"] else frac, TXT).next_to(r, UP, buff=.2))
        else:
            nums.add(VectorizedPoint(np.array([cx, p[1] + h, 0])))
    g = VGroup(base, bars, labs, nums)
    g.bars, g.nums, g.labs, g.base = bars, nums, labs, base
    if unknown is not None:
        ot = T("其餘", max(frac * .9, .038), MUTED)
        ot.move_to(np.array([p[0] - w / 2 + 1.5 * w / G, p[1] + .9, 0]))
        g.add(ot)
        g.other = ot
    return g


def press(p, w=1.6, label="argmax"):
    """argmax 壓模：一塊往下壓的鐵板＋活塞。"""
    p = np.array(p, dtype=float)
    plate = RoundedRectangle(corner_radius=.06, width=w, height=.36).set_fill(ARG, 1).set_stroke(width=0).move_to(p)
    rod = Rectangle(width=.22, height=.9).set_fill(MUTED, 1).set_stroke(width=0).next_to(plate, UP, buff=0)
    lab = B(label, .04, BG).move_to(plate)
    g = VGroup(rod, plate, lab)
    g.plate = plate
    return g


def station2():
    """評審的腦袋：頭殼外框＋兩組長條（<score_A>、<score_B>）＋壓模＋丟掉的槽。"""
    c5a, c5b = cube5(A_POS + UP * .45), cube5(B_POS + UP * .45)
    bases = VGroup(*[Line(q + LEFT * 2.2, q + RIGHT * 2.2).set_stroke(LINE, 3) for q in (A_POS, B_POS)])
    eq = B("＝", .09, TIE).move_to((c5a.get_center() + c5b.get_center()) / 2)
    pr = press(c5a.get_top() + UP * .25)
    return VGroup(skull(), bases, c5a, c5b, eq, pr, discard_bin(), score_tag("A"), score_tag("B"))


def skull():
    sk = RoundedRectangle(corner_radius=1.1, width=STW, height=STH).set_fill(SCREEN, .55).set_stroke(TEAL_L, 4).move_to(S2)
    sk.nocheck = True
    return sk


def score_tag(k):
    return token_box(f"<score_{k}>", DIST).move_to(np.array([(A_POS if k == "A" else B_POS)[0] - 1.2, TOK_Y, 0]))


def cube5(p, color=TIE):
    sq = RoundedRectangle(corner_radius=.08, width=.9, height=.9).set_fill(color, .9).set_stroke(width=0).move_to(p)
    return VGroup(sq, B("5", .06, BG).move_to(sq))


def discard_bin(chips=False, lit=None):
    box = RoundedRectangle(corner_radius=.12, width=5.0, height=.72).set_fill(BG, 1).set_stroke(MUTED, 2).move_to(BIN_C)
    lab = T("丟掉", .04, MUTED).move_to(box.get_left() + RIGHT * .55)
    g = VGroup(box, lab)
    if chips:
        cs = VGroup(*[T(f"{x:.2f}", .04, DIST).set_opacity(1 if i == lit else .5) for i, x in enumerate(PA[:4])]).arrange(RIGHT, buff=.3)
        cs.next_to(lab, RIGHT, buff=.4)
        g.add(cs)
        g.chips = cs
    return g


# ---------------- 計分板 ----------------
WAF = {"judge": (12, 88, 0), "v5": (69, 0, 31), "v20": (77, 0, 23)}
WAF_NAME = {"judge": "只取最高（5 格）", "v5": "期望值（5 格）", "v20": "期望值（20 格）"}


PANEL_P = {k: S3 + np.array([dx, -.4, 0]) for k, dx in (('judge', -4.5), ('v5', 0), ('v20', 4.5))}


def board_panel(key, p, filled=True, show_bad=True, legend=False, title=None):
    """10×10 百格板：綠＝甲排前面、灰＝平手、紅＝乙排前面。.waf .title .count；legend：數字旁邊直接寫圖例（推近時用）。"""
    p = np.array(p, dtype=float)
    cnt = WAF[key]
    w = waffle(list(cnt) if filled else [0, 0, 0], [GOOD, TIE, BAD], cell_=.22, gap=.05)
    w.move_to(p)
    title = T(title or WAF_NAME[key], .042, INK).next_to(w, UP, buff=.28)
    g = VGroup(w, title)
    if legend:
        items = [("甲排前面", cnt[0], GOOD), ("平手", cnt[1], TIE)] + ([("乙排前面", cnt[2], BAD)] if show_bad else [])
        lg = VGroup(*[VGroup(Square(.26).set_fill(c, 1).set_stroke(width=0), T(n, .042, TXT), B(str(v), .055, c)).arrange(RIGHT, buff=.22)
                      for n, v, c in items]).arrange(DOWN, aligned_edge=LEFT, buff=.35).next_to(w, RIGHT, buff=.6)
        g.add(lg)
        count = lg
    else:
        parts = [(str(cnt[0]), GOOD), ("/", MUTED), (str(cnt[1]), TIE)] + ([("/", MUTED), (str(cnt[2]), BAD)] if show_bad else [])
        if not filled:
            parts = [("?", MUTED)]
        count = VGroup(*[B(s, .05, c) for s, c in parts]).arrange(RIGHT, buff=.12).next_to(w, DOWN, buff=.25)
        g.add(count)
    g.waf, g.title, g.count = w, title, count
    return g


def board_legend(show_bad=True):
    items = [("甲排前面", GOOD), ("平手", TIE)] + ([("乙排前面", BAD)] if show_bad else [])
    lg = VGroup(*[VGroup(Square(.22).set_fill(c, 1).set_stroke(width=0), T(n, .04, TXT)).arrange(RIGHT, buff=.15) for n, c in items]).arrange(RIGHT, buff=.6)
    return lg.move_to(S3 + UP * 2.45)


def station3():
    panels = VGroup(*[board_panel(k, PANEL_P[k]) for k in ("judge", "v5", "v20")])
    return VGroup(board_legend(), panels)


# ---------------- 期望值塔 ----------------
UNIT = .85                      # 塔：1 分 = 0.85 單位高
BASE4 = S4[1] - 2.2
TX_X, TY_X = S4[0] - 3.3, S4[0] + .3
FORM_C = S4 + np.array([4.75, .55, 0])


def ruler_v(p, top=5, unit=UNIT, fine=False):
    """直立的連續直尺 0～top。"""
    p = np.array(p, dtype=float)
    ln = Line(p, p + UP * top * unit).set_stroke(INK, 3)
    ticks, labs = VGroup(), VGroup()
    for i in range(top + 1):
        y = p + UP * i * unit
        ticks.add(Line(y + LEFT * .18, y + RIGHT * .18).set_stroke(INK, 3))
        labs.add(T(str(i), .04, MUTED).next_to(y, LEFT, buff=.28))
    minor = VGroup(*[Line(p + UP * (i / 10) * unit + LEFT * .08, p + UP * (i / 10) * unit + RIGHT * .08).set_stroke(LINE, 1.5)
                     for i in range(top * 10 + 1) if i % 10])
    g = VGroup(ln, ticks, minor, labs)
    g.overlap_ok = True
    return g


def tower(ps, base, w=1.3, colors=None, partial=None):
    """每一項「分數×機率」疊成一塊，高度＝那一項的值。.blocks；partial：只疊這些分數，再加一塊灰色的其他。"""
    base = np.array(base, dtype=float)
    blocks = VGroup()
    y = base[1]
    order = range(len(ps)) if partial is None else partial
    for i in order:
        v = (i + 1) * ps[i]
        h = v * UNIT
        r = Rectangle(width=w, height=max(h, .03)).set_fill(EV, .35 + .12 * i).set_stroke(EV, 2)
        r.move_to(np.array([base[0], y + h / 2, 0]))
        blocks.add(r)
        y += h
    g = VGroup(blocks)
    g.blocks = blocks
    g.top_y = y
    return g


def pointer(p, val=None, frac=.05):
    """主角：金色的連續分數指針 ◆（尖端朝左指著直尺）。"""
    p = np.array(p, dtype=float)
    d = Polygon(p, p + np.array([.32, .2, 0]), p + np.array([.64, 0, 0]), p + np.array([.32, -.2, 0])).set_fill(GOLD, 1).set_stroke(width=0)
    g = VGroup(d)
    if val is not None:
        g.add(B(val, frac, GOLD).next_to(d, RIGHT, buff=.22))
    return g


def tower_x():
    return tower(PA, np.array([TX_X, BASE4, 0]))


def tower_y():
    t = tower([0, 0, 0, PB_KNOWN[4], PB_KNOWN[5]], np.array([TY_X, BASE4, 0]), partial=[3, 4])
    oth = Rectangle(width=1.3, height=.48 * UNIT).set_fill(TIE, .35).set_stroke(TIE, 2).move_to(np.array([TY_X, t.top_y + .24 * UNIT, 0]))
    ol = T("其餘", .038, MUTED).move_to(oth)
    ol.near_ok = True
    g = VGroup(t, oth, ol)
    g.blocks, g.oth, g.top_y = t.blocks, oth, oth.get_top()[1]
    return g


def formula(eq=True):
    terms = ["5×0.45＝2.25", "4×0.35＝1.4", "3×0.13＝0.39", "2×0.05＝0.1", "1×0.02＝0.02"]
    fx = VGroup(*[T(s, .042, TXT) for s in terms]).arrange(DOWN, aligned_edge=RIGHT, buff=.2).move_to(FORM_C)
    g = VGroup(fx)
    e = B("＝ 4.16", .055, GOLD).next_to(fx, DOWN, buff=.28).align_to(fx, RIGHT)
    if eq:
        g.add(e)
    calc = T("代入公式計算", .038, MUTED).move_to(np.array([FORM_C[0], BASE4 + .1, 0]))
    g.add(calc)
    g.fx, g.eq, g.calc = fx, e, calc
    return g


def bars_row(ps=PA, mult=True):
    """e2：X 的五根機率長條排在直尺旁，底下寫 ×1～×5（之後各自變成一塊積木）。"""
    y0 = BASE4 + .25
    g = dist_bars(ps, np.array([S4[0] - 1.6, y0, 0]), w=4.6, hmax=1.8)
    if mult:
        g.add(VGroup(*[T(f"×{i + 1}", .042, EV).move_to(np.array([lb.get_x(), y0 - .76, 0])) for i, lb in enumerate(g.labs)]))
    return g


def zoom_inset(pa_v=4.16, pb_v=4.3):
    """e6：把直尺 4.0～4.4 那一段放大，兩個指針明顯分開，間距塗金色。"""
    c = np.array([FORM_C[0] - .45, BASE4 + 2.2, 0])
    L = 3.4
    y = lambda v: c[1] - L / 2 + L * (v - 4.0) / .4
    ln = Line(np.array([c[0], y(4.0), 0]), np.array([c[0], y(4.4), 0])).set_stroke(INK, 3)
    ticks = VGroup(*[Line(np.array([c[0] - .14, y(4 + i / 10), 0]), np.array([c[0] + .14, y(4 + i / 10), 0])).set_stroke(INK, 3) for i in range(5)])
    labs = VGroup(*[T(f"4.{i}", .038, MUTED).next_to(np.array([c[0], y(4 + i / 10), 0]), LEFT, buff=.3) for i in range(5)])
    gap = Line(np.array([c[0] + .02, y(pa_v), 0]), np.array([c[0] + .02, y(pb_v), 0])).set_stroke(GOLD, 9)
    pa = pointer(np.array([c[0] + .2, y(pa_v), 0]), "4.16", .04)
    pb = pointer(np.array([c[0] + .2, y(pb_v), 0]), "約 4.3", .04)
    frame = RoundedRectangle(corner_radius=.2, width=2.8, height=L + 1.1).set_fill(BG, .6).set_stroke(GOLD, 2.5).move_to(c + RIGHT * .45)
    head = T("放大 4.0～4.4", .04, GOLD).next_to(frame, UP, buff=.18)
    g = VGroup(frame, ln, ticks, labs, gap, pa, pb, head)
    for m in (ln, ticks, gap, frame):
        m.overlap_ok = True
    return g


def station4():
    rul = ruler_v(np.array([S4[0] - 5.3, BASE4, 0]))
    ta, tb = tower_x(), tower_y()
    la = T("軌跡 X", .04, INK).next_to(np.array([TX_X, BASE4, 0]), DOWN, buff=.25)
    lb = T("軌跡 Y", .04, INK).next_to(np.array([TY_X, BASE4, 0]), DOWN, buff=.25)
    pa = pointer(np.array([TX_X + .8, ta.top_y, 0]), "4.16")
    pbp = pointer(np.array([TY_X + .8, tb.top_y, 0]), "約 4.3")
    return VGroup(rul, ta, tb, la, lb, pa, pbp, formula())


# ---------------- 旋鈕台：上排三個旋鈕，下方是共用的展示台（每個旋鈕輪流用） ----------------
KNOB_Y = S5[1] + 2.0
KNOB_X = [S5[0] - 4.3, S5[0], S5[0] + 4.3]
STAGE_C = S5 + DOWN * .75                # 展示台中心：寬 12、高 4（站中心 -2.75～+1.25）
STAGE_L, STAGE_R = STAGE_C + LEFT * 2.75, STAGE_C + RIGHT * 3.3


def knob(p, letter, color, val=None, r=.5, lit=True):
    p = np.array(p, dtype=float)
    op = 1 if lit else .35
    ring = Circle(r).set_fill(PANEL, 1).set_stroke(color, 5, op).move_to(p)
    ind = Line(p, p + UP * r * .8).set_stroke(color, 6, op).rotate(-.6, about_point=p)
    lab = B(letter, .06, color).set_opacity(op).next_to(ring, LEFT, buff=.28)
    g = VGroup(ring, ind, lab)
    if val:
        g.add(T(val, .042, TXT).next_to(ring, RIGHT, buff=.28))
    g.ring, g.ind = ring, ind
    return g


def knobs(lit=(True, True, True), vals=(None, None, None)):
    return VGroup(*[knob(np.array([x + .15, KNOB_Y, 0]), l, c, v, lit=on)
                    for x, l, c, v, on in zip(KNOB_X, "GKC", (GK, KK, CK), vals, lit)])


def panel5():
    pn = RoundedRectangle(corner_radius=.4, width=STW, height=STH).set_fill(PANEL, .35).set_stroke(MUTED, 2).move_to(S5)
    div = DashedLine(S5 + np.array([-5.9, 1.35, 0]), S5 + np.array([5.9, 1.35, 0])).set_stroke(LINE, 2)
    g = VGroup(pn, div)
    g.nocheck = True
    return g


def ruler_h(p, n, length=4.0, color=GK, nums=False, ch=.36):
    """橫的格子尺：n 個格子。.cell(i) 回傳第 i 格（0 起）的中心。"""
    p = np.array(p, dtype=float)
    cw = length / n
    cells = VGroup(*[Rectangle(width=cw, height=ch).set_fill(PANEL, 1).set_stroke(color, 2.5).move_to(p + RIGHT * (-length / 2 + (i + .5) * cw)) for i in range(n)])
    g = VGroup(cells)
    if nums:
        g.add(VGroup(*[T(str(i + 1), .038, MUTED).next_to(c, DOWN, buff=.22) for i, c in enumerate(cells)]))
    g.overlap_ok = True
    g.L, g.cells = length, cells
    return g


def readout(a, b, color, p, frac=.06):
    """兩個數字：a → b。"""
    g = VGroup(T(a, frac * .8, TXT), T("→", frac * .8, MUTED), B(b, frac, color)).arrange(RIGHT, buff=.3).move_to(p)
    return g


def stage_g(dots_split=True, show_acc=False, pair=False):
    """G：粗尺（5 格）上兩個點疊在同一格；細尺（20 格）上落在相鄰兩格。右邊是準確率讀數。"""
    GC = STAGE_C + LEFT * 1.75
    coarse = ruler_h(GC + UP * .72, 5, length=6.0, nums=True, ch=.46)
    fine = ruler_h(GC + DOWN * 1.1, 20, length=6.0, ch=.46)
    lc = T("5 格", .042, MUTED).next_to(coarse, LEFT, buff=.3)
    lf = T("20 格", .042, MUTED).next_to(fine, LEFT, buff=.3)
    c4 = coarse.cells[3]
    d1 = Dot(c4.get_top() + UP * .28, radius=.16, color=INK)
    d2 = Dot(c4.get_top() + UP * .68, radius=.16, color=INK)
    same = T("同一格", .042, INK).next_to(VGroup(d1, d2), RIGHT, buff=.3)
    g = VGroup(coarse, fine, lc, lf, d1, d2, same)
    if dots_split:
        g.add(Dot(fine.cells[14].get_top() + UP * .28, radius=.12, color=INK), Dot(fine.cells[15].get_top() + UP * .28, radius=.12, color=INK))
    if pair:
        pr = pair_icon(STAGE_R + UP * .55)
        g.add(pr, T("配對準確率", .042, TXT).next_to(pr, DOWN, buff=.3))
    if show_acc:
        vb = vbars([("5 格", 69, GOOD), ("20 格", 77, GOOD)], STAGE_R + RIGHT * .55 + DOWN * .95, h=1.8, w=.65, gap=1.0, frac=.042, fmt="{:.0f} 次")
        vb[1].set_fill(GOOD, .45)
        g.add(T("計分板：甲排前面", .042, MUTED).move_to(STAGE_R + RIGHT * .55 + UP * 1.35), vb)
    return g


def pair_icon(p):
    """兩卷小軌跡配成一對、中間一個勾。"""
    p = np.array(p, dtype=float)
    a = RoundedRectangle(corner_radius=.08, width=.8, height=1.0).set_fill(PANEL, 1).set_stroke(MUTED, 2).move_to(p + LEFT * .75)
    b = a.copy().move_to(p + RIGHT * .75)
    lines = VGroup(*[Line(LEFT * .25, RIGHT * .25).set_stroke(LINE, 2).move_to(m.get_center() + UP * (.25 - k * .2)) for m in (a, b) for k in range(3)])
    ck = check_mark(GOOD, .26).move_to(p)
    return VGroup(a, b, lines, ck)


def scale_icon(p, reading="+2 kg"):
    """一台體重計：同一顆砝碼放上去，指針每次都停在正確刻度右邊 2 格。"""
    p = np.array(p, dtype=float)
    plat = RoundedRectangle(corner_radius=.25, width=2.8, height=.9).set_fill(PANEL, 1).set_stroke(KK, 3).move_to(p + DOWN * .55)
    dial = Arc(radius=1.0, start_angle=PI * .15, angle=PI * .7, arc_center=p + DOWN * .7).set_stroke(INK, 3)
    ctr = p + DOWN * .7
    ang = lambda k: PI / 2 - (k - 5) * PI * .07
    ticks = VGroup(*[Line(ctr + 1.0 * np.array([np.cos(ang(k)), np.sin(ang(k)), 0]), ctr + .82 * np.array([np.cos(ang(k)), np.sin(ang(k)), 0])).set_stroke(INK, 2.5) for k in range(0, 11)])
    true_t = DashedLine(ctr + .5 * np.array([np.cos(ang(5)), np.sin(ang(5)), 0]), ctr + 1.15 * np.array([np.cos(ang(5)), np.sin(ang(5)), 0]), dash_length=.06).set_stroke(GOOD, 3)
    needle = Line(ctr, ctr + .95 * np.array([np.cos(ang(7)), np.sin(ang(7)), 0])).set_stroke(KK, 6)
    wt = VGroup(Polygon(LEFT * .35 + DOWN * .25, RIGHT * .35 + DOWN * .25, RIGHT * .22 + UP * .25, LEFT * .22 + UP * .25).set_fill(MUTED, 1).set_stroke(width=0))
    wt.scale(.8).move_to(plat.get_top() + UP * .22 + RIGHT * 1.0)
    rd = B(reading, .05, KK).next_to(dial, UP, buff=.2)
    g = VGroup(plat, dial, ticks, true_t, needle, wt, rd)
    g.overlap_ok = True
    g.rd = rd
    return g


def mini_judge_row(p, n=5, vals=(4.4, 3.6, 4.1, 3.8, 4.3)):
    """K 次評分：一排小評審，各自舉一個分數點，平均線落在中間。"""
    p = np.array(p, dtype=float)
    js = VGroup(*[judge(p + RIGHT * (i - (n - 1) / 2) * 1.05, .38, "calm", "") for i in range(n)])
    return js


def score_line(p, vals, truth=None, color=KK, L=4.6, lo=3.0, hi=5.0, label=None):
    """一條分數線（lo～hi），上面幾個點、一條平均線；truth：真正的值（虛線）。"""
    p = np.array(p, dtype=float)
    x = lambda v: p[0] - L / 2 + L * (v - lo) / (hi - lo)
    ln = Line(np.array([x(lo), p[1], 0]), np.array([x(hi), p[1], 0])).set_stroke(LINE, 3)
    ds = VGroup(*[Dot(np.array([x(v), p[1] + .26, 0]), radius=.09, color=color) for v in vals])
    avg = sum(vals) / len(vals)
    am = Line(np.array([x(avg), p[1] - .4, 0]), np.array([x(avg), p[1] + .06, 0])).set_stroke(KK, 6)
    g = VGroup(ln, ds, am)
    if truth is not None:
        tm = DashedLine(np.array([x(truth), p[1] - .4, 0]), np.array([x(truth), p[1] + .06, 0]), dash_length=.06).set_stroke(INK, 3)
        g.add(tm)
    if label:
        g.add(T(label, .038, MUTED).next_to(ln, LEFT, buff=.3))
    g.overlap_ok = True
    return g


def stage_k(step=1):
    """K：step 1＝一排小評審，各丟一個分數點、金色平均線；2＝晃動 vs 偏誤兩條線；3＝再加上秤；4＝對照表。"""
    g = VGroup()
    if step == 1:
        g.add(mini_judge_row(STAGE_L + DOWN * .95), score_line(STAGE_L + UP * .75, (4.4, 3.6, 4.1, 3.8, 4.3)))
        g.add(T("平均", .042, KK).move_to(STAGE_R + UP * .3), T("問 K 次，取平均", .045, TXT).move_to(STAGE_R + DOWN * .45))
    elif step in (2, 3):
        g.add(score_line(STAGE_L + UP * .85, (4.4, 3.6, 4.1, 3.8, 4.3), truth=4.04, label="晃動"),
              score_line(STAGE_L + DOWN * .65, (4.7, 4.3, 4.8, 4.5, 4.6), truth=4.04, label="偏誤", color=BAD))
        g.add(T("虛線＝真正的分數", .038, MUTED).move_to(STAGE_L + DOWN * 1.75))
        if step == 3:
            g.add(scale_icon(STAGE_R + UP * .3))
    else:
        g.add(k_table())
    return g


def k_table():
    """K 的對照（數線版）：上排一般評審、下排 verifier；空心＝問 1 次、實心＝問 16 次。
    兩條平行的斜箭頭（每個 K 的差距一樣寬）＋一條金色虛線連起兩個 74.7%。只畫卡上的四個點。"""
    cx, y0 = STAGE_C[0] + .6, S5[1]
    X = lambda v: cx + (v - 75.5) * .9
    yg, yv, ya = y0 + .45, y0 - .9, y0 - 1.95
    ax = Line(np.array([X(70), ya, 0]), np.array([X(80), ya, 0])).set_stroke(LINE, 3)
    ticks = VGroup(*[Line(np.array([X(v), ya - .08, 0]), np.array([X(v), ya + .08, 0])).set_stroke(LINE, 3) for v in range(70, 81, 2)])
    tl = VGroup(*[T(f"{v}%", .038, MUTED).next_to(np.array([X(v), ya, 0]), DOWN, buff=.2) for v in range(70, 81, 2)])
    axis = VGroup(ax, ticks, tl)
    rows = VGroup(T("一般評審", .045, TXT).move_to(np.array([STAGE_C[0] - 5.0, yg, 0])),
                  T("Verifier", .045, EV).move_to(np.array([STAGE_C[0] - 5.0, yv, 0])))

    def dot(v, y, col, filled):
        return Circle(.14).set_stroke(col, 4).set_fill(col if filled else BG, 1).move_to(np.array([X(v), y, 0]))
    # 順序同舊表：0 一般 1 次、1 一般 16 次、2 verifier 1 次、3 verifier 16 次
    pts = [(71.8, yg, TXT, False), (74.7, yg, TXT, True), (74.7, yv, EV, False), (77.5, yv, EV, True)]
    dots = VGroup(*[dot(v, y, c, f) for v, y, c, f in pts])
    vals = VGroup(*[B(f"{v}%", .045, c) for v, _, c, _ in pts])
    for k, (d, t) in enumerate(zip(dots, vals)):
        t.next_to(d, UP if k < 2 else DOWN, buff=.2)
    cells = VGroup(*[VGroup(d, t) for d, t in zip(dots, vals)])
    link = DashedLine(dots[1].get_bottom() + DOWN * .06, dots[2].get_top() + UP * .06, dash_length=.1).set_stroke(GOLD, 4)
    # 每個 K 的差距＝同一個 K 的兩點水平距離：K=1 的括號貼在 verifier 那排上方（71.8→74.7），K=16 的貼在一般評審那排下方（74.7→77.5）
    def gap(x0, x1, y, d):
        y2 = y + d * .16
        return VGroup(Line(np.array([x0, y, 0]), np.array([x0, y2, 0])), Line(np.array([x0, y2, 0]), np.array([x1, y2, 0])),
                      Line(np.array([x1, y2, 0]), np.array([x1, y, 0]))).set_stroke(MUTED, 3)
    arrows = VGroup(gap(X(71.8), X(74.7) - .2, yv + .42, 1), gap(X(74.7) + .2, X(77.5), yg - .42, -1))
    lg = VGroup(VGroup(Circle(.1).set_stroke(MUTED, 3).set_fill(BG, 1), T("問 1 次", .04, MUTED)).arrange(RIGHT, buff=.12),
                VGroup(Circle(.1).set_stroke(MUTED, 3).set_fill(MUTED, 1), T("問 16 次", .04, MUTED)).arrange(RIGHT, buff=.12)).arrange(RIGHT, buff=.4)
    lg.move_to(np.array([STAGE_C[0] + 3.6, y0 + 1.0, 0]))
    head = VGroup(lg)
    g = VGroup(head, rows, cells, link, axis)
    g.cells, g.link, g.arrows, g.axis, g.lg, g.X, g.yg, g.yv = cells, link, arrows, axis, lg, X, yg, yv
    for m in (arrows, link, axis):
        m.overlap_ok = True
    return g


def lens(p, name, color=CK):
    p = np.array(p, dtype=float)
    ring = Circle(.42).set_fill(BG, .6).set_stroke(color, 4).move_to(p)
    handle = Line(ring.point_at_angle(-PI / 4), ring.point_at_angle(-PI / 4) + np.array([.32, -.32, 0])).set_stroke(color, 6)
    lab = T(name, .04, TXT).next_to(ring, DOWN, buff=.42)
    return VGroup(ring, handle, lab)


def vbars(items, p, h=2.4, w=.55, gap=.45, vmax=100, frac=.04, err=None, fmt="{:.1f}"):
    """從 0 起的直條。items：[(標籤, 值, 顏色)]；err：示意的誤差線長度（只畫重疊的樣子，不代表數值）。"""
    p = np.array(p, dtype=float)
    g = VGroup()
    base = Line(p + LEFT * (len(items) * (w + gap)) / 2, p + RIGHT * (len(items) * (w + gap)) / 2).set_stroke(LINE, 3)
    g.add(base)
    for i, (lab, v, col) in enumerate(items):
        x = p[0] + (i - (len(items) - 1) / 2) * (w + gap)
        hh = h * v / vmax
        r = Rectangle(width=w, height=hh).set_fill(col, .9).set_stroke(width=0).move_to(np.array([x, p[1] + hh / 2, 0]))
        top = r.get_top()
        val = T(fmt.format(v), frac, TXT).next_to(r, UP, buff=.2 + (err or 0))
        lb = T(lab, frac, MUTED).next_to(np.array([x, p[1], 0]), DOWN, buff=.25)
        g.add(r, val, lb)
        if err:
            e = VGroup(Rectangle(width=w + .3, height=2 * err).set_fill(INK, .16).set_stroke(width=0).move_to(top),
                       Line(top + DOWN * err, top + UP * err).set_stroke(INK, 2.5),
                       Line(top + UP * err + LEFT * .12, top + UP * err + RIGHT * .12).set_stroke(INK, 2.5),
                       Line(top + DOWN * err + LEFT * .12, top + DOWN * err + RIGHT * .12).set_stroke(INK, 2.5))
            e.overlap_ok = True
            g.add(e)
    return g


LENS_ROWS = (0, 2, 3)   # 由上到下＝旁白順序：要求、格式、錯誤


def stage_c(step=1):
    """C：軌跡乙（左），三面放大鏡各停在它要看的那一行；step 2 加四根柱子（右）；step 3 加誤差線與兩個空位（4 個？5 個？）。"""
    sc = scroll("乙", S5 + np.array([-3.85, -.75, 0]))
    ls = VGroup()
    for i, n in zip(LENS_ROWS, ("要求", "格式", "錯誤")):
        ring = Circle(.24).set_fill(CK, .12).set_stroke(CK, 4).move_to(np.array([sc.paper.get_right()[0] + .5, sc.lines[i].get_y(), 0]))
        ring.overlap_ok = True
        handle = Line(ring.point_at_angle(-PI / 4), ring.point_at_angle(-PI / 4) + np.array([.16, -.16, 0])).set_stroke(CK, 5)
        handle.overlap_ok = True
        lab = T(n, .04, CK).next_to(ring, RIGHT, buff=.35)
        ls.add(VGroup(ring, handle, lab))
    g = VGroup(sc, ls)
    g.sc, g.ls = sc, ls
    if step >= 2:
        items = [("要求", 75.2, CK), ("格式", 76.4, CK), ("錯誤", 76.0, CK), ("三個", 78.3, CK)]
        bars = vbars(items, S5 + np.array([1.55, -2.05, 0]), h=2.0, w=.45, gap=.6, err=(.3 if step >= 3 else None))
        stride = 4 if step >= 3 else 3
        for k in range(3):
            bars[1 + stride * k].set_fill(CK, .45)
        g.add(bars)
        g.bars = bars
        if step >= 3:
            x0 = bars[0].get_right()[0] + .5
            q = VGroup(*[VGroup(DashedVMobject(RoundedRectangle(corner_radius=.06, width=.45, height=1.5), num_dashes=14).set_stroke(MUTED, 2)
                                .move_to(np.array([x0 + .2 + k * 1.15, bars[0].get_y() + .75, 0])),
                                T(s, .04, MUTED).move_to(np.array([x0 + .2 + k * 1.15, bars[0].get_y() + 1.85, 0]))) for k, s in enumerate(("4 個？", "5 個？"))])
            g.add(q, T("沒試過", .04, MUTED).move_to(np.array([x0 + .2 + .575, bars[0].get_y() - .32, 0])))
    return g


def station5(final="c"):
    st = {"g": stage_g(True, True, False), "k": stage_k(4), "c": stage_c(3)}[final]
    return VGroup(panel5(), knobs(), st)


# ---------------- 成績單（證據）與代價 ----------------
def hbar(p, label, v, vmax, color, L=3.6, frac=.042):
    """從 0 起的橫條。"""
    p = np.array(p, dtype=float)
    lab = T(label, frac, TXT).next_to(p, LEFT, buff=.25)
    r = Rectangle(width=L * v / vmax, height=.46).set_fill(color, .9).set_stroke(width=0)
    r.move_to(p + RIGHT * r.width / 2)
    val = B(f"{v:.1f}%", frac, color).next_to(r, RIGHT, buff=.2)
    g = VGroup(lab, r, val)
    g.bar = r
    return g


LX, RX = S6[0] - 3.2, S6[0] + 3.2     # 左欄：機器人；右欄：寫程式
BAR_Y = S6[1] - 2.15


def robot_icon(p, s=1.0):
    """實心的機械手臂：底座、兩節手臂、關節、夾爪。"""
    p = np.array(p, dtype=float)
    base = Polygon(p + np.array([-.6, -.2, 0]) * s, p + np.array([.6, -.2, 0]) * s, p + np.array([.4, .15, 0]) * s, p + np.array([-.4, .15, 0]) * s).set_fill(PANEL, 1).set_stroke(TEAL_L, 3)
    j0, j1, j2 = p + UP * .2 * s, p + np.array([.45, 1.15, 0]) * s, p + np.array([1.25, .85, 0]) * s

    def seg(a, b, w):
        d = b - a
        r = RoundedRectangle(corner_radius=w / 2, width=np.linalg.norm(d) + w, height=w).set_fill(TEAL_L, .85).set_stroke(width=0)
        return r.rotate(np.arctan2(d[1], d[0])).move_to((a + b) / 2)
    arm = VGroup(seg(j0, j1, .22 * s), seg(j1, j2, .18 * s))
    joints = VGroup(*[Circle(.12 * s).set_fill(BG, 1).set_stroke(INK, 3).move_to(q) for q in (j0, j1, j2)])
    claw = VGroup(Line(j2, j2 + np.array([.28, .2, 0]) * s), Line(j2, j2 + np.array([.28, -.2, 0]) * s)).set_stroke(TEAL_L, 7)
    g = VGroup(base, arm, claw, joints)
    g.overlap_ok = True
    for m in g:
        m.overlap_ok = True
    return g


def term_icon(p, s=1.0, alt=False):
    """終端機視窗；alt＝另一套 harness（外框不同：虛線、紅色）。"""
    p = np.array(p, dtype=float)
    col = MUTED if alt else TEAL_L
    win = RoundedRectangle(corner_radius=.1, width=1.5 * s, height=1.05 * s).set_fill(SCREEN, 1).set_stroke(col, 3).move_to(p)
    if alt:
        win = VGroup(win.set_stroke(width=0), DashedVMobject(win.copy().set_stroke(col, 3), num_dashes=22))
    bar = Line(p + np.array([-.75, .3, 0]) * s, p + np.array([.75, .3, 0]) * s).set_stroke(col, 2)
    pr = B(">_", .045 * s, col).move_to(p + np.array([-.35, -.12, 0]) * s)
    g = VGroup(win, bar, pr)
    g.overlap_ok = True
    return g


def evidence(step=6, left=True):
    """S6（sc09）：左欄機器人（step 2～3）、右欄寫程式（4～6）；step 7～8＝論文首頁的最佳成績與另一套 harness（左欄換掉）。"""
    g = VGroup()
    if left:
        t1 = VGroup(T("機器人：同一個模型", .042, INK), T("argmax → 期望值", .042, ARG)).arrange(DOWN, buff=.12).move_to(np.array([LX, S6[1] + 2.25, 0]))
        g.add(t1)
        if step >= 2:
            g.add(robot_icon(np.array([LX - .7, S6[1] + .35, 0]), 1.05))
        if step >= 3:
            vb = vbars([("只取最高", 70.8, ARG), ("期望值", 87.4, EV)], np.array([LX, BAR_Y, 0]), h=2.0, w=.6, gap=1.6, frac=.042)
            g.add(vb, B("+16.6", .05, EV).move_to(np.array([LX + 2.4, BAR_Y + 1.5, 0])))
    if step >= 4:
        t2 = VGroup(T("寫程式：同一批候選", .042, INK), T("只換挑法", .042, EV)).arrange(DOWN, buff=.12).move_to(np.array([RX, S6[1] + 2.25, 0]))
        g.add(t2, term_icon(np.array([RX, S6[1] + .9, 0])))
    if step >= 5:
        vb2 = vbars([("只交一次", 83.1, TIE), ("verifier 挑", 86.5, EV)], np.array([RX, BAR_Y, 0]), h=2.0, w=.6, gap=1.6, frac=.042)
        g.add(vb2)
    if step >= 6:
        g.add(B("+3.4", .055, GOLD).move_to(np.array([RX + 2.4, BAR_Y + 1.6, 0])))
    return g


def sota(step=7):
    """v5～v5c：左欄換成論文首頁（最佳成績 86.5%）＋兩台外框不同的終端機。"""
    fig = Group(Rectangle(width=1.7, height=2.2).set_fill(WHITE, 1).set_stroke(width=0), T("（首頁）", .038, BG))
    fig[1].move_to(fig[0])
    fig.move_to(np.array([LX - 1.6, S6[1] + .9, 0]))
    fig.overlap_ok = True
    t = T("論文的最佳成績 86.5%", .042, INK).move_to(np.array([LX, S6[1] + 2.45, 0]))
    g = Group(t, fig)
    if step >= 8:
        a = term_icon(np.array([LX + 1.0, S6[1] + .9, 0]), .85)
        b = term_icon(np.array([LX + 1.0, S6[1] - 1.1, 0]), .85, alt=True)
        ne = B("≠", .06, BAD).move_to(np.array([LX + 1.0, S6[1] - .1, 0]))
        la = T("最佳成績", .038, TXT).next_to(a, RIGHT, buff=.25)
        lb = T("對照的成績", .038, TXT).next_to(b, RIGHT, buff=.25)
        hp = pill("另一套 harness", BAD, .04).move_to(np.array([LX - .4, S6[1] - 2.3, 0]))
        g.add(a, b, ne, la, lb, hp)
    return g


TRAY_C = S6 + np.array([-1.6, 1.6, 0])
RED_C, RED2_C = S6 + np.array([2.3, .15, 0]), S6 + np.array([5.0, .15, 0])
JUDGE6 = S6 + np.array([-4.5, .2, 0])


def red_board(n=31, p=None, label=None):
    w = waffle([100 - n, 0, n], [DIM, TIE, BAD], cell_=.15, gap=.04).move_to(RED_C if p is None else p)
    w.cells[:100 - n].set_opacity(.25)
    if label:
        lab = B(label, .045, BAD).next_to(w, DOWN, buff=.25)
    else:
        lab = VGroup(B("期望值 5 格", .045, BAD), B(f"乙排前面 {n} 次", .045, BAD)).arrange(DOWN, buff=.12).next_to(w, DOWN, buff=.25)
    g = VGroup(w, lab)
    g.waf = w
    return g


def tie_cards(n=6, p=None, label=True):
    """平手的卡片：灰色小卡疊成一疊，上面寫「＝」。"""
    p = JUDGE6 + np.array([1.9, 1.75, 0]) if p is None else np.array(p, dtype=float)
    cs = VGroup()
    for i in range(n):
        c = RoundedRectangle(corner_radius=.06, width=.9, height=.6).set_fill(TIE, .9).set_stroke(BG, 2).move_to(p + np.array([.06 * i, .07 * i, 0]))
        cs.add(c)
    if label:
        cs.add(B("＝", .045, BG).move_to(cs[-1]))
    cs.overlap_ok = True
    return cs


def tray(p=TRAY_C):
    box = RoundedRectangle(corner_radius=.15, width=2.6, height=1.25).set_fill(PANEL, 1).set_stroke(MUTED, 2.5).move_to(p)
    lab = T("交給人審", .045, TXT).move_to(box.get_top() + DOWN * .38)
    slot = Line(box.get_left() + RIGHT * .35 + DOWN * .22, box.get_right() + LEFT * .35 + DOWN * .22).set_stroke(MUTED, 3)
    return VGroup(box, lab, slot)


def half_credit(p=None):
    """x6：平手算半分。12＋88÷2＝56 疊成一根柱子，旁邊一根 77。"""
    p = S6 + np.array([-1.1, -2.3, 0]) if p is None else np.array(p, dtype=float)
    h = 1.9 / 100
    base = Line(p + LEFT * 2.1, p + RIGHT * 2.1).set_stroke(LINE, 3)
    xa, xb = p[0] - 1.2, p[0] + 1.2
    g12 = Rectangle(width=.6, height=12 * h).set_fill(GOOD, .9).set_stroke(width=0).move_to(np.array([xa, p[1] + 6 * h, 0]))
    g44 = Rectangle(width=.6, height=44 * h).set_fill(TIE, .9).set_stroke(width=0).move_to(np.array([xa, p[1] + (12 + 22) * h, 0]))
    g77 = Rectangle(width=.6, height=77 * h).set_fill(EV, .9).set_stroke(width=0).move_to(np.array([xb, p[1] + 38.5 * h, 0]))
    va = B("56", .045, TXT).next_to(g44, UP, buff=.22)
    vb = B("77", .045, EV).next_to(g77, UP, buff=.22)
    la = T("只取最高", .04, MUTED).next_to(np.array([xa, p[1], 0]), DOWN, buff=.22)
    lb = T("期望值 20 格", .04, MUTED).next_to(np.array([xb, p[1], 0]), DOWN, buff=.22)
    eqn = VGroup(B("12", .055, GOOD), T("+", .055, TXT), B("88 ÷ 2", .055, TIE), T("= 56", .055, TXT)).arrange(RIGHT, buff=.18)
    f = VGroup(eqn, T("代入公式計算", .038, MUTED)).arrange(DOWN, buff=.18).move_to(p + UP * 3.05)
    return VGroup(base, g12, g44, g77, va, vb, la, lb, f)


def cost(step=6):
    """S6（sc10）：1 紅格；2 評審＋平手卡片；3 冒汗、20 格的 23 次；4 收件匣；5 問號；6 平手算半分 56 比 77。"""
    g = VGroup(red_board(31, label="5 格：31 次" if step >= 3 else None))
    if step >= 2:
        g.add(judge(JUDGE6, .9, "sweat" if step == 3 else "calm", "?" if step == 3 else "＝", TIE))
        if step < 4:
            g.add(tie_cards())
            mw = waffle(list(WAF["judge"]), [GOOD, TIE, BAD], cell_=.13, gap=.035).move_to(S6 + np.array([-1.35, .3, 0]))
            ml = VGroup(T("只取最高", .038, TXT), B("乙排前面 0", .042, BAD)).arrange(DOWN, buff=.32).next_to(mw, DOWN, buff=.22)
            ring = SurroundingRectangle(ml[1], color=BAD, buff=.16, corner_radius=.12)
            g.add(mw, ml, ring)
    if step >= 3:
        g.add(red_board(23, RED2_C, "20 格：23 次"), B("乙排前面", .05, BAD).move_to(np.array([(RED_C[0] + RED2_C[0]) / 2, S6[1] + 1.75, 0])))
    if 4 <= step < 6:
        tr = tray()
        g.add(tr, tie_cards(3, TRAY_C + DOWN * .32, label=False).scale(.55))
    if step == 5:
        q = VGroup(DashedVMobject(RoundedRectangle(corner_radius=.1, width=.95, height=.95), num_dashes=16).set_stroke(MUTED, 2), B("?", .06, MUTED))
        q[1].move_to(q[0])
        g.add(q.next_to(tray(), RIGHT, buff=.45))
    if step >= 6:
        g.add(half_credit())
    return g


def station6(final="cost"):
    return cost(6) if final == "cost" else evidence(6)


def world_all():
    return {"road": road(), "s1": station1(), "s2": station2(), "s3": station3(), "s4": station4(), "s5": station5(), "s6": station6()}


class Panorama(MovingCameraScene):
    """關卡 2 的全景草圖：整支片會出現的所有東西，照實際大小。"""

    def construct(self):
        self.camera.frame.set(width=PANO_W).move_to(PANO_C)
        W = world_all()
        self.add(*W.values())
        names = ["S1 考場", "S2 評審的腦袋", "S3 計分板", "S4 期望值塔", "S5 旋鈕台", "S6 成績單"]
        for n, c in zip(names, [S1, S2, S3, S4, S5, S6]):
            self.add(Rectangle(width=14, height=14 * 9 / 16).set_stroke(MUTED, 2).set_fill(opacity=0).move_to(c))
            self.add(T(n, .09, MUTED).move_to(c + UP * 4.35))
