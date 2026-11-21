"""v002 CER 的大圖元件：一張選票（問題 → 五條推理路徑各三步 → 天平）。設計：design.md。

世界座標：
  問題 Q ─┬─ ① ── ② ── ③ ─ 分數 ┐
          ├─ …                   ┼─ 天平（左盤 375／右盤 400）
          └─ …                   ┘
  工作台 1（BENCH1，主圖下方左）：第二步那句話的 token 與機率。
  工作台 2（BENCH2，主圖下方右）：數學與問答、兩根提升幅度。

每一場的最後一格都由這裡的 builder 擺出來，下一場開頭呼叫同一個 builder（lib/checks/seams.py 驗證一格不差）。
"""
from kit import *  # noqa: F401,F403

CONF, KEY, WT, PATHC, HES = C["信心"], C["關鍵字"], C["權重"], C["路徑"], C["猶豫"]
ANS = GOLD                       # 正確答案 400：全片只有它是金色
CARD_FILL = SEA
SW = 2.6

# ---------------- 例子（旁白都有說「假設」「舉個例子」） ----------------
# 每條路徑：最終答案、三步的信心
PATHS = [("375", (.9, .2, .7)), ("400", (.9, .9, .96)), ("375", (.8, .3, .7)), ("375", (.9, .3, .6)), ("400", (.9, .96, .96))]
MIDS = {"375": ("500", "125", "375"), "400": ("500", "100", "400")}
LEFT_I = [i for i, p in enumerate(PATHS) if p[0] == "375"]      # 左盤：375
RIGHT_I = [i for i, p in enumerate(PATHS) if p[0] == "400"]     # 右盤：400


def path_score(c):
    """C_path = Σ j·c_j / Σ j（j＝步驟序號）。"""
    return sum((j + 1) * x for j, x in enumerate(c)) / sum(range(1, len(c) + 1))


SCORES = [round(path_score(c), 2) for _, c in PATHS]            # 0.57 0.93 0.58 0.55 0.95
LASTS = [c[-1] for _, c in PATHS]                               # 只看最後一步：0.7 0.96 0.7 0.6 0.96

# ---------------- 世界的位置 ----------------
QP = np.array([-8.05, 0, 0])
STEP_X = [-5.0, -2.7, -0.4]
ROW_Y = [2.3, 1.15, 0, -1.15, -2.3]
SCORE_X = 1.46
HEAD_Y = 3.42
PIV = np.array([5.08, 1.25, 0])          # 天平支點
BEAM, HANG, PLATE = 1.58, 1.7, 2.5    # 橫樑半長、吊線長、秤盤寬
BASE_Y = -2.7
STAGE, STAGE_W = np.array([-0.55, 0.2, 0]), 19.0     # 整張圖
HOOK_C, HOOK_W = np.array([5.08, -0.2, 0]), 13.4        # 開場：只看天平
ROW_C, ROW_W = np.array([-1.98, 2.95, 0]), 8.8        # sc05：最上面那條路徑
BENCH1 = np.array([-3.4, -7.4, 0])
BENCH2 = np.array([3.4, -7.4, 0])
BENCH_W = 12.6
BENCH1_C = BENCH1 + np.array([0, 0, 0])
RECAP_C, RECAP_W = np.array([-0.55, -0.05, 0]), 20.0
RECAP_Y = -3.75
NODE_W, NODE_H = 1.05, .58
BAR_W, BAR_H, BAR_DY = .9, .11, -.44


def P(i, j):
    """第 i 條路徑第 j 步（0 起算）的位置。"""
    return np.array([STEP_X[j], ROW_Y[i], 0])


# ---------------- 元件 ----------------
def seg(a, b, color=LINE, w=SW, op=.85):
    return Line(a, b).set_stroke(color, w, op)


def step_node(i, j):
    """一步的中間答案：圓角框＋數字。400 那兩條的最終答案是金色。"""
    ans = PATHS[i][0]
    gold = ans == "400" and j == 2
    col = ANS if gold else TXT
    r = RoundedRectangle(corner_radius=.12, width=NODE_W, height=NODE_H).set_stroke(ANS if gold else PATHC, 2.2, 1 if gold else .8) \
        .set_fill(CARD_FILL, 1)
    t = M(MIDS[ans][j], .06, col).move_to(r)
    g = VGroup(r, t).move_to(P(i, j))
    g.box, g.num = r, t
    return g


def row_links(i):
    """一條路徑的連線：問題 → ① → ② → ③。"""
    a = QP + RIGHT * 1.05
    b = P(i, 0) + LEFT * NODE_W / 2
    mid = np.array([-6.15, ROW_Y[i], 0])
    fan = VMobject().set_points_smoothly([a, a + RIGHT * .25 + UP * ROW_Y[i] * .25, mid + LEFT * .15 + DOWN * ROW_Y[i] * .12, mid, b]) \
        .set_stroke(PATHC, SW, .7).set_fill(opacity=0)
    l1 = seg(P(i, 0) + RIGHT * NODE_W / 2, P(i, 1) + LEFT * NODE_W / 2, PATHC, SW, .7)
    l2 = seg(P(i, 1) + RIGHT * NODE_W / 2, P(i, 2) + LEFT * NODE_W / 2, PATHC, SW, .7)
    return VGroup(fan, l1, l2)


def row_path(i):
    """脈衝走的路：問題 → 最終答案。"""
    L = row_links(i)
    p = VMobject()
    p.set_points(np.vstack([L[0].points, L[1].points, L[2].points]))
    return p


def question():
    """問題卡。回傳 (框, 題目兩行)；題目寫出來之前框裡是一個「?」（qmark()）。"""
    r = RoundedRectangle(corner_radius=.16, width=2.1, height=2.1).set_stroke(TXT_STRONG, 2.4).set_fill(CARD_FILL, 1).move_to(QP)
    tx = VGroup(T("100 元", .055, TXT_STRONG), T("× 5 本", .055, TXT_STRONG), T("打八折", .055, TXT_STRONG)).arrange(DOWN, buff=.17).move_to(r)
    return r, tx


def qmark():
    return M("?", .09, TXT_STRONG).move_to(QP)


HEADS = ["原價", "折扣", "相減"]


def header(j):
    n = M("①②③"[j], .058, MUTED)
    t = T(HEADS[j], .055, MUTED)
    return VGroup(n, t).arrange(RIGHT, buff=.14).move_to(np.array([STEP_X[j], HEAD_Y, 0]))


def bar_track(i, j):
    return Rectangle(width=BAR_W, height=BAR_H).set_stroke(CONF, 1.2, .45).set_fill(opacity=0).move_to(P(i, j) + UP * BAR_DY)


def bar_fill(i, j, v=None, h=BAR_H):
    v = PATHS[i][1][j] if v is None else v
    left = P(i, j) + UP * BAR_DY + LEFT * BAR_W / 2
    return Rectangle(width=max(.001, BAR_W * v), height=h).set_stroke(width=0).set_fill(CONF, .95).move_to(left, aligned_edge=LEFT)


def score_num(i, val=None, color=None):
    v = SCORES[i] if val is None else val
    return M(f"{v:.2f}", .06, color or CONF).move_to(np.array([SCORE_X, ROW_Y[i], 0]))


TITLE_P = PIV + UP * 2.12
SUB_P = PIV + UP * 1.42


def title(s="CER"):
    return M(s, .08, TXT_STRONG).move_to(TITLE_P)


def one_tag(i):
    """sc03～sc06：每條路徑都算 1 票。"""
    return M("1", .06, MUTED).move_to(np.array([SCORE_X, ROW_Y[i], 0]))


# ---------------- 票：每條路徑一顆有表情的球 ----------------
HES_I = set(LEFT_I)             # 例子裡猶豫的三條路徑（算出 375 的那三條）
VR = .34                        # 票停在路徑終點時的半徑


def PARK(i):
    """第 i 條路徑的票走完之後停的位置（最終答案右邊）。"""
    return np.array([.66, ROW_Y[i], 0])


def face(p, r, hes=0.0, sure=0.0, look=0.0, op=1.0, ink=None, body=True):
    """一顆票。hes 0→1：眉毛下垂、嘴巴變成波浪、冒汗；sure 0→1：變成紫色（有把握）。結構固定，可以每格 become。"""
    ink = ink or TXT_STRONG
    g = VGroup()
    c = Circle(r).set_stroke(TXT_STRONG, 2.4, op if body else 0)
    c.set_fill(interpolate_color(ManimColor(TXT), ManimColor(CONF), sure), ((.16 + .26 * sure) * op) if body else 0)
    g.add(c)
    ex, ey, er = .36 * r, .12 * r, .11 * r * (1 + .25 * hes)
    for s in (-1, 1):
        e = np.array([s * ex + look * .1 * r, ey, 0])
        g.add(Dot(e, radius=er, color=ink).set_opacity(op))
        g.add(Line(e + np.array([-s * .16 * r, .30 * r, 0]), e + np.array([s * .20 * r, .17 * r, 0])).set_stroke(ink, 2.2, op * hes))
    xs = np.linspace(-.28 * r, .28 * r, 13)
    smile = -.30 * r - .13 * r * (1 - (xs / (.28 * r)) ** 2)
    wavy = -.40 * r + .06 * r * np.sin(xs / r * 18)
    ys = smile * (1 - hes) + wavy * hes
    g.add(VMobject().set_points_smoothly([np.array([x, y, 0]) for x, y in zip(xs, ys)]).set_stroke(ink, 2.3, op).set_fill(opacity=0))
    d = VMobject().set_points_smoothly([np.array(q) * r for q in ([0, .2, 0], [.11, -.02, 0], [0, -.14, 0], [-.11, -.02, 0], [0, .2, 0])])
    g.add(d.set_fill(PATHC, .9 * op * hes).set_stroke(width=0).move_to(np.array([.98 * r, .78 * r, 0])))
    g.shift(np.array(p, dtype=float))
    return g


def bare_face(p, r, hes=0.0, ink=None):
    """只有五官的臉（畫在機率長條上）。隱形的零件拿掉，之後整組改透明度才不會冒出來。"""
    f = face(p, r, hes, ink=ink or BG, body=False)
    f.remove(*[m for m in f if m.get_stroke_opacity() < .01 and m.get_fill_opacity() < .01])
    f.nocheck = f.dots_ok = True
    return f


class Voter(VGroup):
    """會動的票。位置 p、半徑 r、hes、sure、look、amp（發抖的幅度）、op 都是屬性，用 Act 動畫改。
    amp＝0 時畫出來和 face() 一格不差（接縫靠這個）。"""

    def __init__(self, p, r=.2, hes=0.0, sure=0.0, look=0.0, op=1.0, ph=0.0, **kw):
        super().__init__()
        self.p, self.r, self.hes, self.sure, self.look, self.op = np.array(p, dtype=float), r, hes, sure, look, op
        self.amp, self.t, self.ph, self.kw = 0.0, 0.0, ph, kw
        self.add(self._make())
        self.add_updater(Voter._tick)
        self.transient = self.overlap_ok = self.nocheck = self.dots_ok = True

    def _make(self):
        a = self.amp * (.4 + .6 * self.hes)
        off = np.array([.045 * a * np.sin(self.t * 26 + self.ph), .02 * a * np.sin(self.t * 33 + self.ph * 1.7), 0])
        return face(self.p + off, self.r, self.hes, self.sure, self.look, self.op, **self.kw)

    def _tick(self, dt):
        self.t += dt
        self[0].become(self._make())


class Act(Animation):
    """改一顆票的屬性：to＝走到哪（hop＝途中跳多高）、path＝沿著一條線走、其餘用 set（amp、hes、sure、r、op、look）。"""

    def __init__(self, v, to=None, hop=0.0, path=None, off=ORIGIN, set=None, **kw):
        self.to, self.h, self.path, self.off, self.tw = (None if to is None else np.array(to, dtype=float)), hop, path, np.array(off), set or {}
        super().__init__(v, **kw)

    def begin(self):
        m = self.mobject
        self.p0 = m.p.copy()
        self.v0 = {k: getattr(m, k) for k in self.tw}
        super().begin()

    def interpolate_mobject(self, alpha):
        a, m = self.rate_func(alpha), self.mobject
        if self.path is not None:
            m.p = self.path.point_from_proportion(min(max(a, 0), 1)) + self.off
        elif self.to is not None:
            m.p = self.p0 + (self.to - self.p0) * a + UP * self.h * np.sin(PI * min(max(a, 0), 1))
        for k, v in self.tw.items():
            setattr(m, k, self.v0[k] + (v - self.v0[k]) * a)
        m[0].become(m._make())


def walkers(sure=False, op=1.0):
    """五顆票停在各自路徑的終點。猶豫的三顆從頭到尾都在冒汗；sure＝有把握的兩顆已經變成紫色。"""
    return [Voter(PARK(i), VR, hes=1.0 if i in HES_I else 0.0, sure=1.0 if (sure and i not in HES_I) else 0.0, op=op, ph=i * 2.1)
            for i in range(5)]


# ---------------- 兩個待答的問題 ----------------
ASK_P = np.array([-2.7, -3.28, 0])
ASKS = ["看哪幾步？", "每一步怎麼量？"]


def asks(ticks=0):
    """「看哪幾步？」「每一步怎麼量？」：sc04 結尾寫在五條路徑下方，答完一個打一個勾。回傳兩個 VGroup（.box .txt .tick）。"""
    out = []
    for k, s in enumerate(ASKS):
        box = RoundedRectangle(corner_radius=.06, width=.34, height=.34).set_stroke(TXT_STRONG, 2).set_fill(opacity=0)
        txt = T(s, .052, TXT_STRONG)
        g = VGroup(box, txt).arrange(RIGHT, buff=.16)
        out.append(g)
    VGroup(*out).arrange(RIGHT, buff=.75).move_to(ASK_P)
    for k, g in enumerate(out):
        c = g[0].get_center()
        tick = VMobject().set_points_as_corners([c + np.array([-.11, .0, 0]), c + np.array([-.03, -.09, 0]), c + np.array([.15, .14, 0])])
        tick.set_stroke(KEY, 4).set_fill(opacity=0)
        g.box, g.txt, g.tick = g[0], g[1], tick
        if k < ticks:
            g.add(tick)
    return out


class Balance(VGroup):
    """天平。每一票一顆有表情的球，面積＝重量（w[i]）；傾角每格由兩盤的總和算出來。
    a[i]：這顆球落下的進度（0＝還沒出現，1＝在盤上）。rel：0＝橫樑先扣住不動，1＝放開。mode：0＝讀數顯示票數，1＝顯示總和。
    hes[i]、sure[i]：表情。amp：猶豫的票發抖的幅度（場景開頭與結尾要是 0，接縫才會一格不差）。hop：輕的那一邊被彈起來。"""
    MAXA, GAIN, R0 = 12 * DEGREES, 6.0, .4

    def __init__(self, w=None, a=None, mode=0, hes=None, sure=None):
        super().__init__()
        self.w = [ValueTracker(1.0 if w is None else w[i]) for i in range(5)]
        self.a = [ValueTracker(1.0 if a is None else a[i]) for i in range(5)]
        self.hes = [ValueTracker(0.0 if hes is None else hes[i]) for i in range(5)]
        self.sure = [ValueTracker(0.0 if sure is None else sure[i]) for i in range(5)]
        self.rel, self.held, self.wob, self.mode = ValueTracker(1), 0.0, ValueTracker(0), ValueTracker(mode)
        self.amp, self.hop, self.t = ValueTracker(0), ValueTracker(0), 0.0
        self._amax = [x.get_value() for x in self.a]   # 球落下時用彈跳曲線，進度會回彈；重量只看到過的最大進度，橫樑才不會抖
        self.base = Line([PIV[0] - .75, BASE_Y, 0], [PIV[0] + .75, BASE_Y, 0]).set_stroke(TXT, 4)
        self.post = Line([PIV[0], BASE_Y, 0], PIV).set_stroke(TXT, 3.2)
        self.pivot = Dot(PIV, radius=.085, color=TXT_STRONG).set_z_index(4)
        self.pivot.dots_ok = True
        self.beam = Line(PIV + LEFT * BEAM, PIV + RIGHT * BEAM).set_stroke(TXT_STRONG, 3.6)
        self.strings = VGroup(*[Line(ORIGIN, DOWN).set_stroke(LINE, 1.8, .9) for _ in range(4)])
        self.plates = VGroup(*[Line(LEFT * PLATE / 2, RIGHT * PLATE / 2).set_stroke(TXT, 3.4) for _ in range(2)])
        self.labels = VGroup(M("375", .066, TXT), M("400", .066, ANS))
        self.balls = VGroup(*[face(ORIGIN, self.R0) for _ in range(5)])
        self.balls.nocheck = True
        self.dyn = VGroup(self.beam, self.strings, self.plates, self.labels, self.balls)
        self.add(self.base, self.post, self.dyn, self.pivot)
        for m in (self.strings, self.beam, self.post, self.base):
            m.dots_ok = True
        self.dots_ok = True
        self._th = self.aim()
        self.refresh()
        self.dyn.add_updater(lambda m, dt: self.step(dt))

    # --- 數值 ---
    @staticmethod
    def _land(a):
        x = np.clip((a - .7) / .3, 0, 1)
        return x * x * (3 - 2 * x)

    def total(self, side):
        for i in range(5):
            self._amax[i] = max(self._amax[i], self.a[i].get_value())
        return sum(self.w[i].get_value() * self._land(self._amax[i]) for i in (LEFT_I if side == 0 else RIGHT_I))

    def aim(self):
        return self.MAXA * np.tanh((self.total(0) - self.total(1)) * self.GAIN)

    def theta(self):
        """正＝左盤下沉。"""
        return self._th + self.wob.get_value()

    def goal(self):
        r = self.rel.get_value()
        return self.held * (1 - r) + self.aim() * r

    def step(self, dt):
        """橫樑有慣性：每格往目標角度靠近一點（球落下的那一格重量是突然出現的，直接套用會整根跳過去）。"""
        self.t += dt
        self._th += (self.goal() - self._th) * (1 - np.exp(-dt / .16))
        self.refresh()

    def hold(self):
        """扣住橫樑：之後重量變了也先不動，直到 rel 回到 1。"""
        self.held = self.aim()
        self.rel.set_value(0)

    def end(self, side):
        th = self.theta()
        s = -1 if side == 0 else 1
        return PIV + s * BEAM * np.array([np.cos(th), np.sin(th), 0])

    def plate_c(self, side):
        return self.end(side) + DOWN * HANG

    def slot(self, i):
        side = 0 if i in LEFT_I else 1
        grp = LEFT_I if side == 0 else RIGHT_I
        k, n = grp.index(i), len(grp)
        dx = (k - (n - 1) / 2) * (.84 if n == 3 else .9)
        r = self.R0 * np.sqrt(max(self.w[i].get_value(), 1e-4))
        return self.plate_c(side) + RIGHT * dx + UP * (r + .03), r

    def refresh(self):
        e = [self.end(0), self.end(1)]
        self.beam.put_start_and_end_on(e[0], e[1])
        for s in (0, 1):
            c = self.plate_c(s)
            self.plates[s].put_start_and_end_on(c + LEFT * PLATE / 2, c + RIGHT * PLATE / 2)
            self.strings[2 * s].put_start_and_end_on(e[s], c + LEFT * PLATE / 2)
            self.strings[2 * s + 1].put_start_and_end_on(e[s], c + RIGHT * PLATE / 2)
            self.labels[s].move_to(c + DOWN * .5)
        amp, hop = self.amp.get_value(), self.hop.get_value()
        for i in range(5):
            p, r = self.slot(i)
            a, h = self.a[i].get_value(), self.hes[i].get_value()
            p = p + UP * min(1 - min(a, 1), .8) * 2.1
            if i in LEFT_I:
                p = p + UP * hop * (.5 + .12 * LEFT_I.index(i))
            p = p + np.array([.04 * amp * h * np.sin(self.t * 26 + i * 2.1), .018 * amp * h * np.sin(self.t * 33 + i * 3.3), 0])
            op = float(np.clip(a * 5, 0, 1))
            self.balls[i].become(face(p, r, h, self.sure[i].get_value(), .5 if i in LEFT_I else -.5, op))

    def readout(self, side, frac=.066):
        """盤子上方的讀數：票數或總和；領先的那邊比較亮。"""
        def fmt(_):
            v = self.total(side)
            return f"{v:.0f}" if self.mode.get_value() < .5 else f"{v:.2f}"

        def col(_):
            return TXT_STRONG if self.total(side) >= self.total(1 - side) - 1e-6 else MUTED
        return Live(self.w[0], fmt, frac, col, place=lambda t: t.move_to(self.end(side) + UP * .48))


HES_ON = [1.0 if i in HES_I else 0.0 for i in range(5)]
SURE_ON = [0.0 if i in HES_I else 1.0 for i in range(5)]


class Live(VGroup):
    """每格重算的讀數。fmt(v) → 字串；place(t) 擺位置。"""

    def __init__(self, tracker, fmt, frac=.05, color=TXT, place=None, italic=False):
        super().__init__()
        self.tr, self.fmt, self.fr, self.col, self.it = tracker, fmt, frac, color, italic
        self.place = place or (lambda t: t)
        self.add(self._make())
        self.add_updater(lambda m: m[0].become(m._make()))

    def _make(self):
        v = self.tr.get_value()
        t = M(self.fmt(v), self.fr, self.col(v) if callable(self.col) else self.col, self.it)
        self.place(t)
        return t


def pdot(color):
    d = Dot(radius=.1, color=color).set_z_index(5)
    d.transient = d.overlap_ok = d.nocheck = True
    return d


def travel(x, path, fade=.2):
    """點沿路徑走，最後一段淡掉。"""
    def upd(m, a):
        m.move_to(path.point_from_proportion(a))
        m.set_opacity(min(1.0, (1 - a) / fade))
    return UpdateFromAlphaFunc(x, upd, rate_func=linear)


def sheet(bars=False, scores=False, heads=True, walk=None):
    """主圖（不含天平）。回傳 dict：q、links[i]、nodes[i][j]、heads、tracks、fills、scores。"""
    qb, qt = question()
    W = dict(qb=qb, qt=qt, links=[row_links(i) for i in range(5)], nodes=[[step_node(i, j) for j in range(3)] for i in range(5)])
    if heads:
        W["heads"] = VGroup(*[header(j) for j in range(3)])
    if bars:
        W["tracks"] = [[bar_track(i, j) for j in range(3)] for i in range(5)]
        W["fills"] = [[bar_fill(i, j) for j in range(3)] for i in range(5)]
    if scores:
        W["scores"] = [score_num(i) for i in range(5)]
    if walk is not None:
        W["walk"] = walkers(sure=(walk == "sure"))
    return W


def flat(W):
    """dict → 可以 self.add(*flat(W)) 的清單。"""
    out = []
    for v in W.values():
        if isinstance(v, list):
            for x in v:
                out.extend(x if isinstance(x, list) else [x])
        else:
            out.append(v)
    return out


def sub_label(s, color=MUTED):
    return T(s, .055, color).move_to(SUB_P)


def calc_note(p, frac=.052):
    return T("代入公式計算", frac, MUTED).move_to(p)


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
        tgt.bodyg.shift(UP * (self.camera.frame.height * .75))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(pl, tgt, rate_func=rate_functions.ease_in_cubic)]

    def wake(self, bal=None, vs=()):
        """場景開頭：猶豫的票開始發抖。"""
        return ([bal.amp.animate.set_value(1)] if bal is not None else []) + [Act(v, set=dict(amp=1)) for v in vs if v.hes > .5]

    def settle(self, bal=None, vs=(), lead=1.7, extra=()):
        """場景結尾：發抖停下來（下一場開頭要和這一格一格不差），留一段靜止給接縫。"""
        t = self.sc["frames"] / config.frame_rate - lead
        an = ([bal.amp.animate.set_value(0)] if bal is not None else []) + [Act(v, set=dict(amp=0)) for v in vs] + list(extra)
        self.at(t, *an, run_time=.4)

    def slam(self, bal, to_left=False):
        """放開橫樑，重的那邊重重砸下去：輕的那邊的票被彈起來，鏡頭震一下。"""
        an = [bal.rel.animate(rate_func=rate_functions.ease_out_back).set_value(1),
              bal.wob.animate(rate_func=rate_functions.wiggle).set_value(.1 if to_left else -.1),
              self.camera.frame.animate(rate_func=rate_functions.wiggle).shift(DOWN * .16)]
        if not to_left:
            an.append(bal.hop.animate(rate_func=rate_functions.there_and_back).set_value(1))
        return an

    def bal_set(self, bal, mode=0):
        """把天平和兩個讀數放上場。回傳 (左讀數, 右讀數)。"""
        r0, r1 = bal.readout(0), bal.readout(1)
        self.add(bal, r0, r1)
        return r0, r1
