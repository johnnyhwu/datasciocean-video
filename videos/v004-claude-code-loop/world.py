"""v004 Claude Code：大圖元件（一圈跑道）。設計在 design.md。

世界座標（鏡頭在上面走）：
  (0, 0)        跑道圓心：結霜的玻璃球（凍結的模型）；跑道半徑 R，順時針：上「想」→ 右「做」（收費站）→ 下工具箱 → 左「看」
  x≈-6.3        紙卷（transcript／context）：從 y=SCROLL_TOP 往下長
  y≈-3.9        工具箱：放大鏡、鉛筆、逃生門、分身、地球
  y≈4.4         跑道上方的空地：sc04 對照小卡、sc06 流水線、sc08 鋸齒曲線、sc09 Skills 書架（不同時出現）
  x≈6.6         收費站右邊：sc09 MCP 插座；右上 Subagent 小跑道
"""
from kit import *  # noqa: F401,F403

SINE = rate_functions.ease_in_out_sine
POP = rate_functions.ease_out_back

MODEL, TOOL, OBS, USER = C["模型"], C["工具"], C["觀察"], C["使用者"]
INK = TXT_STRONG
PAPER, PAPER_INK = "#EFE3C8", "#1D2B2E"

# ---------------- 位置 ----------------
LOOP_C = np.array([0., 0., 0.])
R = 2.05                      # 跑道半徑
TRACK_W = .55                 # 跑道寬
BALL_R = .95
SCROLL_X, SCROLL_TOP, SCROLL_W = -5.65, 2.4, 4.0
ROW_H = .6
TOOL_X = 6.1                  # 工具箱（跑道右邊一直排）
GATE_A = 45                   # 收費站在跑道上的角度（度）
TOP_Y = 4.4                   # 上方空地
PANO_C, PANO_W = np.array([0.0, .9, 0]), 19.5
WORK_C, WORK_W = np.array([.1, .12, 0]), 17.8               # 紙卷＋跑道＋工具箱


def P(deg, r=R):
    a = np.deg2rad(deg)
    return LOOP_C + r * np.array([np.cos(a), np.sin(a), 0])


# ---------------- 跑道 ----------------
def track(op=1.0):
    """一圈跑道：內外兩條邊線、中間的虛線、四個順時針箭頭。"""
    outer = Circle(R + TRACK_W / 2).set_stroke(LINE, 2.2, .7 * op).move_to(LOOP_C)
    inner = Circle(R - TRACK_W / 2).set_stroke(LINE, 2.2, .7 * op).move_to(LOOP_C)
    band = Annulus(inner_radius=R - TRACK_W / 2, outer_radius=R + TRACK_W / 2).set_fill(TEAL_M, .16 * op).set_stroke(width=0).move_to(LOOP_C)
    mid = DashedVMobject(Circle(R).move_to(LOOP_C), num_dashes=44, dashed_ratio=.45).set_stroke(TXT, 1.6, .3 * op)
    arrows = VGroup()
    for d in (135, 45, -45, -135):
        a = np.deg2rad(d)
        tip = P(d)
        tan = np.array([np.sin(a), -np.cos(a), 0])          # 順時針的切線
        arrows.add(Triangle().scale(.13).set_fill(TXT, .7 * op).set_stroke(width=0)
                   .rotate(np.arctan2(tan[1], tan[0]) - PI / 2).move_to(tip))
    g = VGroup(band, outer, inner, mid, arrows)
    for m in g.family_members_with_points():
        m.overlap_ok = m.dots_ok = m.cross_ok = m.nocheck = True
    g.band, g.mid, g.arrows, g.outer, g.inner = band, mid, arrows, outer, inner
    return g


def track_glow(color=GOLD, width=8):
    """沿跑道跑一圈的光（ShowPassingFlash 用）。從上方出發順時針。"""
    c = Arc(radius=R, start_angle=PI / 2, angle=-TAU, arc_center=LOOP_C).set_stroke(color, width)
    return c


def lap_arc(a0, a1):
    """順時針從 a0 度跑到 a1 度（a1 < a0）。"""
    return Arc(radius=R, start_angle=np.deg2rad(a0), angle=np.deg2rad(a1 - a0), arc_center=LOOP_C)


STATION = {"想": 90, "做": GATE_A, "工具": 0, "看": 180}


def station_words(op=1.0, frac=.06):
    g = VGroup()
    for s, d, off in (("想", 90, UP * .55), ("做", 18, RIGHT * .5), ("看", 180, LEFT * .55)):
        g.add(T(s, frac, INK).set_opacity(op).move_to(P(d, R + TRACK_W / 2) + off))
    return g


# ---------------- 凍結的模型 ----------------
def glass_model(c=LOOP_C, r=BALL_R, op=1.0, look=ORIGIN, glow=0.0):
    """結霜的玻璃球：只會吃字、吐字。眼睛可以看方向（look）；glow 0→1 是讀字時發亮。"""
    c = np.array(c, dtype=float)
    halo = Circle(r * 1.35).set_fill(MODEL, .12 * glow * op).set_stroke(width=0).move_to(c)
    ball = Circle(r).set_fill(MODEL, (.2 + .15 * glow) * op).set_stroke(MODEL, 4, op).move_to(c)
    shine = Arc(radius=r * .78, start_angle=PI * .62, angle=PI * .32, arc_center=c).set_stroke(INK, 4, .55 * op)
    frost = VGroup()
    for k, (dx, dy, s) in enumerate(((.66, -.18, .14), (-.68, -.12, .11), (.32, .66, .1))):
        p0 = c + np.array([dx, dy, 0]) * r
        for i in range(3):
            a = i * PI / 3
            frost.add(Line(p0 - s * np.array([np.cos(a), np.sin(a), 0]), p0 + s * np.array([np.cos(a), np.sin(a), 0])).set_stroke(INK, 2, .5 * op))
    eyes = VGroup()
    for dx in (-.28, .28):
        ec = c + np.array([dx * r, .12 * r, 0])
        eyes.add(Circle(.13 * r).set_fill(INK, op).set_stroke(width=0).move_to(ec))
        eyes.add(Dot(ec + np.array(look) * .05 * r, radius=.06 * r, color=BG).set_opacity(op))
    lab = T("模型", .054, INK).set_opacity(op).move_to(c + DOWN * .55 * r)
    g = VGroup(halo, ball, shine, frost, eyes, lab)
    for m in g.family_members_with_points():
        m.overlap_ok = m.dots_ok = m.cross_ok = True
    g.ball, g.eyes, g.lab, g.halo = ball, eyes, lab, halo
    return g


# ---------------- 小單：會跑的工具呼叫單 ----------------
def slip(tool="Read", arg="", mood="ok", color=GOLD, s=1.0, op=1.0):
    """工具呼叫單。mood：ok／happy／sweat／proud。arg 是單子上的第二行（短）。"""
    tw = max(T(tool, .054 * s).width, T(arg, .052 * s).width if arg else 0)
    w, h = max(1.7 * s, tw + .4 * s), (1.3 if arg else 1.02) * s
    body = RoundedRectangle(corner_radius=.12 * s, width=w, height=h).set_fill("#1B3238", op).set_stroke(color, 3.2, op)
    fold = Polygon(body.get_corner(UR) + LEFT * .26 * s, body.get_corner(UR), body.get_corner(UR) + DOWN * .26 * s).set_fill(color, .55 * op).set_stroke(width=0)
    name = T(tool, .054 * s, color).set_opacity(op)
    rows = VGroup(name)
    if arg:
        rows.add(T(arg, .052 * s, TXT).set_opacity(op))
    rows.arrange(DOWN, buff=.06 * s).move_to(body).shift(DOWN * .17 * s)
    eyes = VGroup()
    ey = body.get_top()[1] - .17 * s
    for dx in (-.17, .17):
        ec = np.array([body.get_center()[0] + dx * s, ey, 0])
        if mood == "happy":
            eyes.add(Arc(radius=.07 * s, start_angle=0, angle=PI, arc_center=ec).set_stroke(INK, 3, op))
        else:
            eyes.add(Circle(.065 * s).set_fill(INK, op).set_stroke(width=0).move_to(ec))
    extra = VGroup()
    if mood == "sweat":
        d = VMobject().set_points_smoothly([np.array(q) * s for q in ([0, .14, 0], [.08, -.02, 0], [0, -.1, 0], [-.08, -.02, 0], [0, .14, 0])])
        extra.add(d.set_fill(MODEL, .95 * op).set_stroke(width=0).move_to(body.get_corner(UL) + np.array([-.1, -.05, 0]) * s))
    g = VGroup(body, fold, rows, eyes, extra)
    for m in g.family_members_with_points():
        m.overlap_ok = m.dots_ok = m.cross_ok = True
    g.body, g.name = body, name
    g.set_z_index(4)
    return g


SLIP_R = R + .3                # 小單跑在跑道外緣，不壓到模型


def run_slip(sl, a0, a1, run=1.6):
    """小單沿跑道外緣順時針跑（a0 → a1 度）；先從目前位置接到起點。"""
    arc = Arc(radius=SLIP_R, start_angle=np.deg2rad(a0), angle=np.deg2rad(a1 - a0), arc_center=LOOP_C)
    path = VMobject()
    path.set_points_as_corners([sl.get_center(), arc.get_start()])
    path.append_points(arc.points)
    return MoveAlongPath(sl, path, run_time=run, rate_func=SINE)


# ---------------- 紙卷（transcript） ----------------
ROW_STYLE = {"task": (PAPER_INK, "#E8D9B5"), "obs": (PAPER_INK, "#CFE9E3"), "call": ("#5A4708", "#F4E2A6"),
             "err": ("#7A1C1C", "#F4C9C4"), "ok": ("#1E5A2E", "#CDEBC8"), "sum": (PAPER_INK, "#D9D2F0"), "pin": (PAPER_INK, "#F6D9A8")}


def scroll_top(op=1.0):
    """紙卷上端的捲軸。"""
    x0, x1 = SCROLL_X - SCROLL_W / 2 - .12, SCROLL_X + SCROLL_W / 2 + .12
    rod = RoundedRectangle(corner_radius=.12, width=x1 - x0, height=.28).set_fill("#B89A67", op).set_stroke("#6B5530", 2, op)
    rod.move_to(np.array([SCROLL_X, SCROLL_TOP + .1, 0]))
    lab = T("transcript", .052, TXT).set_opacity(op).next_to(rod, UP, buff=.16)
    g = VGroup(rod, lab)
    g.rod, g.lab = rod, lab
    return g


def row_y(i):
    return SCROLL_TOP - .12 - ROW_H * (i + .5)


def row(text, kind="obs", i=0, op=1.0, frac=.056):
    ink, fill = ROW_STYLE[kind]
    box = Rectangle(width=SCROLL_W, height=ROW_H).set_fill(fill, op).set_stroke(PAPER_INK, 1.2, .45 * op)
    box.move_to(np.array([SCROLL_X, row_y(i), 0]))
    t = T(text, frac, ink).set_opacity(op)
    if t.width > SCROLL_W - .5:
        t.scale_to_fit_width(SCROLL_W - .5)
    t.move_to(box.get_left() + RIGHT * (.25 + t.width / 2))
    g = VGroup(box, t)
    g.overlap_ok = True
    box.overlap_ok = True
    g.box, g.txt = box, t
    return g


def chip(text, kind="obs", frac=.053):
    """小單帶回來的結果：一小張紙條（之後變成紙卷上的一列）。"""
    ink, fill = ROW_STYLE[kind]
    t = T(text, frac, ink)
    box = RoundedRectangle(corner_radius=.06, width=t.width + .3, height=t.height + .24).set_fill(fill, 1).set_stroke(PAPER_INK, 1.2, .5)
    t.move_to(box)
    g = VGroup(box, t)
    g.overlap_ok = box.overlap_ok = True
    g.set_z_index(4)
    return g


def scroll_rows(entries, op=1.0):
    """entries：[(文字, 種類), …] → 一列一列的紙條。"""
    return VGroup(*[row(t, k, i, op) for i, (t, k) in enumerate(entries)])


def read_beam(n_rows, glow=1.0):
    """紙卷 → 模型：每一圈開始時，模型讀整份紙卷（一道光從紙卷右緣流進玻璃球）。"""
    y_top, y_bot = SCROLL_TOP - .12, row_y(max(n_rows - 1, 0)) - ROW_H / 2
    x0 = SCROLL_X + SCROLL_W / 2 + .05
    tip = LOOP_C + LEFT * (BALL_R + .05)
    poly = Polygon(np.array([x0, y_top, 0]), np.array([x0, y_bot, 0]), tip + DOWN * .25, tip + UP * .25)
    poly.set_fill(MODEL, .16 * glow).set_stroke(MODEL, 1.5, .5 * glow)
    poly.overlap_ok = poly.cross_ok = poly.dots_ok = True
    return poly


# ---------------- 收費站 ----------------
GATE_P = P(GATE_A)


def gate(op=1.0, arm_up=0.0):
    """跑道右上的收費站：小亭子在跑道外側，橫桿橫跨跑道（arm_up 0 放下、1 抬起）。"""
    base = P(GATE_A, R + TRACK_W / 2 + 1.55)
    booth = RoundedRectangle(corner_radius=.1, width=.95, height=.9).set_fill("#20323A", op).set_stroke(TXT, 2.6, op).move_to(base)
    roof = Polygon(booth.get_corner(UL) + LEFT * .14, booth.get_corner(UR) + RIGHT * .14, booth.get_top() + UP * .33).set_fill(LINE, op).set_stroke(TXT, 2.4, op)
    win = RoundedRectangle(corner_radius=.06, width=.58, height=.32).set_fill(TEAL_L, .3 * op).set_stroke(TXT, 1.6, op).move_to(booth.get_center() + UP * .15)
    pivot = booth.get_corner(DL) + np.array([.12, .16, 0])
    down_end = P(GATE_A, R - TRACK_W / 2 - .12)
    v = down_end - pivot
    ang = np.arctan2(v[1], v[0])
    L = np.linalg.norm(v)
    a2 = ang + (PI * .55) * arm_up * (-1)
    end = pivot + L * np.array([np.cos(a2), np.sin(a2), 0])
    arm = Line(pivot, end).set_stroke("#E8E2D0", 7, op)
    stripes = VGroup(*[Line(pivot + (end - pivot) * f, pivot + (end - pivot) * (f + .1)).set_stroke("#D9534F", 7, op) for f in (.25, .55, .85)])
    lamp = Circle(.1).set_fill(MUTED, op).set_stroke(TXT, 1.5, op).move_to(booth.get_corner(UR) + np.array([-.2, -.18, 0]))
    g = VGroup(booth, roof, win, arm, stripes, lamp)
    for m in g.family_members_with_points():
        m.overlap_ok = m.dots_ok = m.cross_ok = True
    g.booth, g.arm, g.lamp, g.win = booth, VGroup(arm, stripes), lamp, win
    return g


GATE_BOOTH = P(GATE_A, R + TRACK_W / 2 + 1.55)


def stamp_mark(p, s="✓", color=GOOD):
    c = Circle(.22).set_stroke(color, 3).set_fill(color, .15).move_to(p)
    t = T(s, .04, color).move_to(p)
    g = VGroup(c, t)
    g.overlap_ok = True
    g.set_z_index(5)
    return g


# ---------------- 工具箱 ----------------
def icon_magnifier(c, s=1.0, color=TOOL):
    lens = Circle(.26 * s).set_stroke(color, 4).move_to(c + np.array([-.08, .08, 0]) * s)
    h = Line(c + np.array([.1, -.1, 0]) * s, c + np.array([.32, -.32, 0]) * s).set_stroke(color, 6)
    return VGroup(lens, h)


def icon_pencil(c, s=1.0, color=TOOL):
    body = Rectangle(width=.18 * s, height=.62 * s).set_fill(color, .35).set_stroke(color, 3).move_to(c + UP * .06 * s)
    tip = Polygon(body.get_corner(DL), body.get_corner(DR), body.get_bottom() + DOWN * .18 * s).set_fill(color, 1).set_stroke(color, 2)
    return VGroup(body, tip).rotate(-PI / 5, about_point=c)


def icon_door(c, s=1.0, color=TOOL):
    fr = Rectangle(width=.5 * s, height=.74 * s).set_stroke(color, 3.5).move_to(c)
    door = Polygon(fr.get_corner(DL), fr.get_corner(UL), fr.get_corner(UL) + np.array([.3, -.08, 0]) * s,
                   fr.get_corner(DL) + np.array([.3, .08, 0]) * s).set_fill(color, .35).set_stroke(color, 3)
    knob = Dot(door.get_center() + RIGHT * .08 * s, radius=.035 * s, color=color)
    return VGroup(fr, door, knob)


def icon_twin(c, s=1.0, color=TOOL):
    a = Circle(.2 * s).set_stroke(color, 3.5).set_fill(color, .3).move_to(c + np.array([-.15, .05, 0]) * s)
    b = Circle(.15 * s).set_stroke(color, 3).set_fill(color, .15).move_to(c + np.array([.2, -.08, 0]) * s)
    return VGroup(a, b)


def icon_globe(c, s=1.0, color=TOOL):
    o = Circle(.28 * s).set_stroke(color, 3.5).move_to(c)
    m = Ellipse(width=.24 * s, height=.56 * s).set_stroke(color, 2.5).move_to(c)
    eq = Line(c + LEFT * .28 * s, c + RIGHT * .28 * s).set_stroke(color, 2.5)
    return VGroup(o, m, eq)


TOOLS = [("找、讀", ["Read", "Glob", "Grep"], icon_magnifier), ("改", ["Edit", "Write"], icon_pencil),
         ("逃生門", ["Bash"], icon_door), ("分身", ["Task"], icon_twin), ("外面", ["WebFetch", "WebSearch"], icon_globe)]
TOOL_DY = .82


def tool_y(i):
    return (2 - i) * TOOL_DY - .05


def tool_icon_pos(i):
    return np.array([TOOL_X - .95, tool_y(i), 0])


def toolbox(op=1.0, names=False):
    """跑道右邊一直排工具：圖示＋工具名。names=True 時顯示全部工具名（sc05），否則只顯示第一個。"""
    g = VGroup()
    sw = 6.6 if names else 3.6
    shelf = RoundedRectangle(corner_radius=.18, width=sw, height=TOOL_DY * 5 + .2).set_fill(PANEL, .55 * op).set_stroke(LINE, 2, op)
    shelf.move_to(np.array([TOOL_X - 1.7 + sw / 2, tool_y(2), 0]))
    g.add(shelf)
    items = VGroup()
    for i, (_, ns, fn) in enumerate(TOOLS):
        c = tool_icon_pos(i)
        ic = fn(c, .8)
        if op < 1:
            ic.fade(1 - op)
        lab = T(" / ".join(ns) if names else ns[0], .053, TXT).set_opacity(op)
        lab.move_to(c + RIGHT * (.5 + lab.width / 2))
        it = VGroup(ic, lab)
        it.icon, it.lab = ic, lab
        items.add(it)
    g.add(items)
    for m in g.family_members_with_points():
        m.overlap_ok = m.dots_ok = m.cross_ok = True
    g.shelf, g.items = shelf, items
    return g


# ---------------- 開場的流程圖 ----------------
FLOW = [("規劃器", np.array([0, 2.3, 0])), ("執行器", np.array([3.1, 0, 0])), ("檢查器", np.array([0, -2.3, 0])), ("除錯器", np.array([-3.1, 0, 0]))]
FLOW_EXTRA = [("記憶", np.array([-2.3, 2.0, 0])), ("排程", np.array([2.4, 2.0, 0])), ("回報", np.array([2.4, -2.0, 0])), ("重試", np.array([-2.4, -2.0, 0]))]


def flow_box(s, p, color=TXT, frac=.05, op=1.0):
    t = T(s, frac, color).set_opacity(op)
    b = RoundedRectangle(corner_radius=.1, width=t.width + .5, height=t.height + .36).set_fill(PANEL, .9 * op).set_stroke(color, 2.4, op).move_to(p)
    t.move_to(b)
    g = VGroup(b, t)
    g.box = b
    return g


def flowchart(op=1.0, extra=True):
    """觀眾想像中的 agent：一堆模組、箭頭亂竄。"""
    boxes = VGroup(*[flow_box(s, p + LOOP_C, op=op) for s, p in FLOW])
    more = VGroup(*[flow_box(s, p + LOOP_C, MUTED, .045, op) for s, p in FLOW_EXTRA]) if extra else VGroup()
    allb = list(boxes) + list(more)
    pairs = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)] + ([(4, 0), (5, 1), (6, 2), (7, 3), (4, 6), (5, 7), (4, 1), (6, 1)] if extra else [])
    arrows = VGroup()
    for i, j in pairs:
        a, b = allb[i], allb[j]
        ar = Arrow(a.get_center(), b.get_center(), buff=.5, stroke_width=3.5, max_tip_length_to_length_ratio=.1, tip_length=.16).set_color(LINE).set_opacity(.9 * op)
        arrows.add(ar)
    g = VGroup(arrows, boxes, more)
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    g.boxes, g.more, g.arrows = boxes, more, arrows
    return g


# ---------------- 其他小東西 ----------------
def speech(text, p, frac=.053):
    t = T(text, frac, PAPER_INK)
    b = bubble(t, pad=.22, tail=DL, fill="#F2E0C0").move_to(p)
    b.overlap_ok = True
    return b


def code_mountain(c, n=14, s=1.0, op=1.0):
    """一座程式碼山：一堆疊起來的檔案。"""
    g = VGroup()
    rng = np.random.default_rng(4)
    rows_ = [5, 4, 3, 2]
    k = 0
    for r_, cnt in enumerate(rows_):
        for j in range(cnt):
            x = (j - (cnt - 1) / 2) * .5 * s
            f = RoundedRectangle(corner_radius=.04, width=.42 * s, height=.54 * s).set_fill(PANEL, op).set_stroke(MUTED, 1.6, op)
            f.move_to(c + np.array([x + rng.uniform(-.03, .03), r_ * .4 * s, 0]))
            ln = VGroup(*[Line(f.get_left() + RIGHT * .07 * s + UP * (.12 - .08 * q) * s, f.get_left() + RIGHT * (.07 + rng.uniform(.14, .26)) * s + UP * (.12 - .08 * q) * s)
                          .set_stroke(MUTED, 1.4, op) for q in range(4)])
            g.add(VGroup(f, ln))
            k += 1
    for m in g.family_members_with_points():
        m.overlap_ok = m.cross_ok = m.dots_ok = True
    return g


def recap_frame(m, buff=.12):
    r = SurroundingRectangle(m, buff=buff, corner_radius=.15).set_stroke(TXT_STRONG, 2.2)
    r.overlap_ok = r.dots_ok = True
    return r


def recap_item(frame, num_, s, frac=.06, dy=.4):
    t = VGroup(T(num_, frac, GOLD), T(s, frac, TXT_STRONG)).arrange(RIGHT, buff=.18)
    t.next_to(frame, DOWN, buff=dy)
    return t


def recap_link(frame, item):
    x = item.get_center()[0]
    return Line(np.array([x, frame.get_bottom()[1], 0]), item.get_top() + UP * .06).set_stroke(TXT_STRONG, 2)


class Sheet(Timed):
    BG = "flat"

    def plumb_in(self, p, scale=.45):
        top = self.camera.frame.get_top()[1] + .6
        pl = Plumb(scale, top_y=top).place(np.array(p) + UP * 4)
        target = pl.copy().place(p)
        return pl, [Transform(pl, target, rate_func=POP)]

    def plumb_out(self, pl):
        tgt = pl.copy()
        tgt.bodyg.shift(UP * (self.camera.frame.height * .8))
        tgt.rope.become(tgt._straight_rope())
        return [Transform(pl, tgt, rate_func=rate_functions.ease_in_cubic)]
