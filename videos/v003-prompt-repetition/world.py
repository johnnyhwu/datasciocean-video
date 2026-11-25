"""v003 Prompt Repetition：大圖元件（一條只能回頭看的長廊）。設計在 design.md。

世界座標（鏡頭在上面走）：
  y≈7.6   開場：提示卡、複製貼上、準確率儀表（sc01、sc02）
  y≈6.5～10  長廊上方的實驗區：sc04、sc05 的排法實驗與 NameIndex 名單；sc06 的兩種舊解法；sc08、sc09 的計分板（不同時出現）
  y=1.0   長廊：第一遍 P1（x<0）｜金色接縫（x=0）｜第二遍 P2（x>0）；讀者頭上有想法泡泡，腳下有筆記（Key/Value）
  y≈-3.6  工作站：Prefill（左）、Decode 打字機（右），緊貼長廊下方，全景一個畫面放得下
"""
from pathlib import Path
from kit import *  # noqa: F401,F403

SINE = rate_functions.ease_in_out_sine
POP = rate_functions.ease_out_back

P1C, P2C, LIGHT, QC, DEC = C["第一遍"], C["第二遍"], C["注意力"], C["問題"], C["Decode"]
INK = TXT_STRONG

# ---------------- 位置 ----------------
CORR_Y = 1.0
STEP = 1.85
WORDS = ["The", "bark", "was", "rough", "."]
P1X = [-.95 - (4 - i) * STEP for i in range(5)]      # -8.35 … -0.95
P2X = [.95 + i * STEP for i in range(5)]             # 0.95 … 8.35
RW, RH = 1.6, 1.7                                  # 讀者的身體
NOTE_DY = -1.55                                      # 筆記在讀者下方
BUB_DY = 1.8                                        # 想法泡泡在讀者上方
HOOK_C = np.array([0, 7.6, 0])
LAB_Y = 9.6
ST_Y = -3.75
PRE_C = np.array([-5.6, ST_Y, 0])
DEC_C = np.array([5.4, ST_Y, 0])
PANO_C, PANO_W = np.array([0, -.5, 0]), 21.0


def RP(k, i):
    """第 k 遍（1、2）第 i 個讀者的位置。"""
    return np.array([(P1X if k == 1 else P2X)[i], CORR_Y, 0])


# ---------------- 小讀者（每個 token 一個） ----------------
def reader(word, color, p, conf=0.0, joy=0.0, look=0.0, op=1.0, w=RW, h=RH, frac=.058):
    """戴半邊眼罩的小讀者：左眼張開往左看，右眼被眼罩蓋住。
    conf 0→1：困惑（眉毛下垂、嘴巴歪、冒汗）；joy 0→1：恍然大悟（笑、眼睛變大）。結構固定，可以直接 Transform。"""
    p = np.array(p, dtype=float)
    g = VGroup()
    body = RoundedRectangle(corner_radius=.3, width=w, height=h).set_fill(color, .26 * op).set_stroke(color, 3, op).move_to(p)
    g.add(body)
    top = p + UP * (h / 2 - .38)
    ec = top + LEFT * .3
    eye = Circle(.21 + .04 * joy).set_fill(INK, op).set_stroke(width=0).move_to(ec)
    pupil = Dot(ec + LEFT * (.07 + .03 * look), radius=.1, color=BG).set_opacity(op)
    brow = Line(ec + np.array([-.22, .3 + .06 * conf, 0]), ec + np.array([.2, .34 - .12 * conf, 0])).set_stroke(INK, 4, op)
    patch = RoundedRectangle(corner_radius=.07, width=.46, height=.32).set_fill("#20343A", op).set_stroke(INK, 2, op).move_to(top + RIGHT * .3)
    strap = Line(body.get_left(), body.get_right()).set_stroke("#20343A", 4, op)
    strap.move_to(np.array([p[0], top[1] + .04, 0]))
    xs = np.linspace(-.26, .26, 13)
    smile = -.04 - .1 * joy - .07 * (1 - (xs / .26) ** 2) * (1 + joy)
    wavy = -.08 + .045 * np.sin(xs * 34)
    ys = smile * (1 - conf) + wavy * conf
    mc = top + DOWN * .5 + LEFT * .02
    mouth = VMobject().set_points_smoothly([mc + np.array([x, y + .1, 0]) for x, y in zip(xs, ys)]).set_stroke(INK, 3.5, op)
    drop = VMobject().set_points_smoothly([np.array(q) * 1.3 for q in ([0, .13, 0], [.075, -.02, 0], [0, -.1, 0], [-.075, -.02, 0], [0, .13, 0])])
    drop.set_fill(P1C, .95 * op * conf).set_stroke(width=0).move_to(body.get_corner(UR) + np.array([.1, .02, 0]))
    lab = T(word, frac, INK).set_opacity(op).move_to(p + DOWN * (h / 2 - .3))
    for m in (strap, brow, mouth, eye, pupil, patch, drop):
        m.dots_ok = m.overlap_ok = m.cross_ok = True
    g.add(strap, eye, pupil, brow, patch, mouth, drop, lab)
    g.body, g.eye, g.patch, g.lab = body, eye, patch, lab
    g.overlap_ok = True
    return g


def corridor(k=1, color=None, words=WORDS, op=1.0, **kw):
    return [reader(w, color or (P1C if k == 1 else P2C), RP(k, i), op=op, **kw) for i, w in enumerate(words)]


# ---------------- 注意力的光：從眼睛往左打 ----------------
def beam(src, left_x, color=LIGHT, op=.26, spread=.42):
    """從讀者的眼睛往左照到 left_x 的光錐（只能往左）。"""
    e = np.array(src, dtype=float) + np.array([-RW / 2 + .02, RH / 2 - .38, 0])
    L = max(.05, e[0] - left_x)
    tip = e + LEFT * L
    sp = spread * min(1, L / 4)
    poly = Polygon(e + UP * .07, tip + UP * sp, tip + DOWN * sp, e + DOWN * .07)
    poly.set_fill(color, op).set_stroke(color, 2.5, min(1, op * 3))
    poly.overlap_ok = poly.nocheck = True
    return poly


class Beam(VGroup):
    """會伸長的光：reach 0→1，從眼睛延伸到 left_x。"""

    def __init__(self, src, left_x, color=LIGHT, op=.44, reach=0.0):
        super().__init__()
        self.src, self.left_x, self.c, self.op = np.array(src, dtype=float), left_x, color, op
        self.reach = ValueTracker(reach)
        self.add(self._make())
        self.add_updater(lambda m: m[0].become(m._make()))
        self.overlap_ok = self.nocheck = True
        self.set_z_index(2)                  # 光永遠蓋在讀者上（動畫會把讀者提到最上層，不設會跳一下）

    def _make(self):
        e0 = self.src[0] - RW / 2 + .02
        x = e0 - (e0 - self.left_x) * self.reach.get_value()
        return beam(self.src, x, self.c, self.op * min(1, self.reach.get_value() * 6))


# ---------------- 想法泡泡與筆記 ----------------
def tree_icon(s=1.0, color=GOOD):
    trunk = Rectangle(width=.12 * s, height=.28 * s).set_fill("#9A6B3F", 1).set_stroke(width=0)
    crown = Triangle().set_fill(color, 1).set_stroke(width=0).stretch(.38 * s, 0).stretch(.42 * s, 1)
    crown.next_to(trunk, UP, buff=-.02)
    return VGroup(trunk, crown)


def dog_icon(s=1.0, color="#D9B48A"):
    head = Circle(.17 * s).set_fill(color, 1).set_stroke(width=0)
    ear1 = Ellipse(width=.1 * s, height=.22 * s).set_fill("#9A6B3F", 1).set_stroke(width=0).next_to(head, LEFT, buff=-.06).shift(UP * .04 * s)
    ear2 = ear1.copy().next_to(head, RIGHT, buff=-.06).shift(UP * .04 * s)
    nose = Dot(radius=.035 * s, color=BG).move_to(head.get_center() + DOWN * .05 * s)
    e1 = Dot(radius=.025 * s, color=BG).move_to(head.get_center() + np.array([-.06, .05, 0]) * s)
    e2 = e1.copy().shift(RIGHT * .12 * s)
    return VGroup(ear1, ear2, head, nose, e1, e2)


def meaning(clear=0.0, s=1.0):
    """bark 的意思。clear=0：狗和樹疊在一起、半透明（模糊的混合體）；clear=1：清楚的金色「樹皮」。"""
    d = dog_icon(s).shift(LEFT * .16 * s * (1 - clear)).set_opacity(.55 * (1 - clear))
    t = tree_icon(s, GOLD if clear > .5 else GOOD).shift(RIGHT * .16 * s * (1 - clear)).set_opacity(.55 + .45 * clear)
    return VGroup(d, t)


def bubble_at(p, content, op=1.0):
    """想法泡泡（kit.think），放在讀者 p 的上方。"""
    b = think(content.scale(.78), pad=.16, toward=DOWN)     # 泡泡正對讀者，小圓點垂直往下
    b.move_to(np.array(p) + UP * BUB_DY)
    if op < 1:
        b.set_opacity(op)
    b.overlap_ok = True
    return b


def note(p, kind="plain", op=1.0):
    """讀者腳下的筆記（Key／Value）。kind：plain（普通）、blur（模糊的 bark）、gold（看過全文的 bark）。"""
    p = np.array(p, dtype=float) + UP * NOTE_DY
    card = RoundedRectangle(corner_radius=.08, width=1.05, height=.62).set_fill(SEA, op).set_stroke(GOLD if kind == "gold" else LINE, 2.2, op).move_to(p)
    kv = VGroup(*[Line(LEFT * .2, RIGHT * (.2 - .1 * j)).set_stroke(MUTED, 3, .7 * op) for j in range(3)]).arrange(DOWN, buff=.1, aligned_edge=LEFT).move_to(p + LEFT * .2)
    g = VGroup(card, kv)
    if kind != "plain":
        m = meaning(1.0 if kind == "gold" else 0.0, .62).move_to(p + RIGHT * .22)
        m.set_opacity(op if kind == "gold" else op * .8)
        g.add(m)
    g.card, g.kv = card, kv
    g.overlap_ok = True
    return g


def unlabeled(rs):
    """還沒寫上字的讀者（sc02：只知道是 token，例句到 sc03 才出現）。"""
    for r in rs:
        r.remove(r.lab)
    return rs


PAPER_INK = "#13252A"


def paper_cover(c, s=1.0):
    """重畫的論文封面（不是截圖）：標題、Google Research、日期；下面三條灰線只代表內文。"""
    c = np.array(c, dtype=float)
    pr = T("Prompt Repetition", .062, "#0F6E73")
    imp = T("Improves", .062, PAPER_INK)
    nr = T("Non-Reasoning", .062, PAPER_INK)
    llm = T("LLMs", .062, PAPER_INK)
    l1 = VGroup(pr, imp).arrange(RIGHT, buff=.2)
    l2 = VGroup(nr, llm).arrange(RIGHT, buff=.2)
    title = VGroup(l1, l2).arrange(DOWN, buff=.14)
    meta = VGroup(T("Google Research", .058, "#2C6E73"), T("2025 年 12 月", .058, "#5A6A6A")).arrange(RIGHT, buff=.5)
    lines = VGroup(*[Line(LEFT * 2.5, RIGHT * (2.5 - .9 * (k == 2))).set_stroke("#B8AF9C", 5) for k in range(3)]).arrange(DOWN, buff=.2, aligned_edge=LEFT)
    body = VGroup(title, meta, lines).arrange(DOWN, buff=.34).move_to(c)
    page = RoundedRectangle(corner_radius=.14, width=max(6.4, title.width + .9), height=body.height + .8).set_fill("#EEE7D8", 1).set_stroke("#C9BFA8", 2).move_to(c)
    g = VGroup(page, title, meta, lines)
    g.scale(s, about_point=c)
    g.page, g.pr, g.nr, g.meta, g.lines = page, pr, nr, meta, lines
    for m in g.family_members_with_points():
        m.overlap_ok = True
    g.overlap_ok = True
    return g


# ---- 論文第 1 頁截圖（arXiv:2512.14982，CC BY 4.0；使用者 2026-11-22 同意放截圖）----
# 只取第 1 頁中間那一欄（標題 → 第一節開頭），整頁清楚呈現（使用者 2026-11-23：不用打碼，論文是公開的）。
PAPER_URL = "https://arxiv.org/pdf/2512.14982"
_PAPER_DIR = Path(__file__).resolve().parents[2] / "out" / "v003-prompt-repetition" / "paper"
PAGE_SCALE = 4                         # 渲染倍率：頁面 612pt → 2448px
PAGE_CROP = (380, 250, 2068, 1330)     # 只留中間那一欄：標題 → 第一節開頭（整頁像素座標）
TITLE_BOX = {"pr": (470, 1014), "nr": (1328, 1776), "y": (405, 465)}   # 標題字的像素範圍（整頁座標，程式量測）


def page_png():
    out = _PAPER_DIR / "page1_cut3.png"
    if out.exists():
        return out
    _PAPER_DIR.mkdir(parents=True, exist_ok=True)
    pdf = _PAPER_DIR / "paper.pdf"
    if not pdf.exists():
        import urllib.request
        req = urllib.request.Request(PAPER_URL, headers={"User-Agent": "Mozilla/5.0 (research-tool)"})
        pdf.write_bytes(urllib.request.urlopen(req).read())
    import pypdfium2 as pdfium
    im = pdfium.PdfDocument(str(pdf))[0].render(scale=PAGE_SCALE).to_pil().convert("RGB")
    im = im.crop(PAGE_CROP)
    im.save(out)
    return out


def paper_page(c, h=5.0):
    """論文第 1 頁截圖。.px(x, y) 把截圖像素座標換成場景座標；.mark(key, color) 回傳螢光筆色塊。"""
    c = np.array(c, dtype=float)
    img = ImageMobject(str(page_png()))
    img.height = h
    img.move_to(c)
    w = img.width
    sh = Rectangle(width=w, height=h).set_fill("#000000", .45).set_stroke(width=0).move_to(c + np.array([.12, -.14, 0]))
    sh.nocheck = True
    g = Group(sh, img)
    x0, y0, x1, y1 = PAGE_CROP

    def px(x, y):
        return c + np.array([((x - x0) / (x1 - x0) - .5) * w, (.5 - (y - y0) / (y1 - y0)) * h, 0])

    def mark(key, color):
        x0, x1 = TITLE_BOX[key]
        y0, y1 = TITLE_BOX["y"]
        a, b = px(x0 - 12, y0 - 14), px(x1 + 12, y1 + 14)
        r = Rectangle(width=b[0] - a[0], height=a[1] - b[1]).set_fill(color, .38).set_stroke(width=0).move_to((a + b) / 2)
        r.nocheck = True
        return r

    def title_center():
        return (px(TITLE_BOX["pr"][0], TITLE_BOX["y"][0]) + px(TITLE_BOX["nr"][1], TITLE_BOX["y"][1])) / 2

    g.img, g.px, g.mark, g.title_center = img, px, mark, title_center
    return g


def underline(m, color, w=5, dy=.08):
    ln = Line(m.get_corner(DL) + DOWN * dy, m.get_corner(DR) + DOWN * dy).set_stroke(color, w)
    ln.overlap_ok = ln.cross_ok = True
    return ln


def seam(op=1.0):
    ln = Line(np.array([0, CORR_Y + 1.25, 0]), np.array([0, CORR_Y - 2.05, 0])).set_stroke(GOLD, 6, op)
    return ln


def pass_label(k, op=1.0):
    xs = P1X if k == 1 else P2X
    s = "第一遍" if k == 1 else "第二遍"
    t = T(s, .065, P1C if k == 1 else P2C).set_opacity(op).move_to(np.array([xs[2] + .35, CORR_Y + 1.52, 0]))
    return t


# ---------------- 開場：提示卡與儀表 ----------------
def prompt_card(p, label="第 25 個是誰？", w=3.3, h=2.1, color=P1C):
    p = np.array(p, dtype=float)
    card = RoundedRectangle(corner_radius=.14, width=w, height=h).set_fill(SEA, 1).set_stroke(color, 3).move_to(p)
    lines = VGroup(*[Line(LEFT * (w / 2 - .35), RIGHT * (w / 2 - .35 - .5 * (i % 2))).set_stroke(MUTED, 4, .6) for i in range(3)]).arrange(DOWN, buff=.24, aligned_edge=LEFT)
    lines.move_to(p + UP * .25)
    q = T(label, .045, QC).move_to(p + DOWN * (h / 2 - .38))
    g = VGroup(card, lines, q)
    g.card = card
    return g


class Meter(VGroup):
    """準確率儀表：半圓刻度＋指針＋讀數，接同一個 tracker（百分比）。"""

    def __init__(self, c, val=0.0, r=1.35, nd=0, color=GOLD):
        super().__init__()
        self.c, self.r, self.nd, self.col = np.array(c, dtype=float), r, nd, color
        self.v = ValueTracker(val)
        arc = Arc(radius=r, start_angle=PI, angle=-PI, arc_center=self.c).set_stroke(LINE, 10, .55)
        ticks = VGroup(*[Line(self.c + r * .82 * np.array([np.cos(a), np.sin(a), 0]), self.c + r * .96 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(MUTED, 2)
                         for a in np.linspace(PI, 0, 11)])
        self.arc, self.ticks = arc, ticks
        self.live = always_redraw(self._live)
        self.add(arc, ticks, self.live)

    def _live(self):
        x = self.v.get_value()
        a = PI - PI * x / 100
        fill = Arc(radius=self.r, start_angle=PI, angle=-PI * max(x, .2) / 100, arc_center=self.c).set_stroke(self.col if x > 50 else TXT, 10)
        needle = Line(self.c, self.c + self.r * .8 * np.array([np.cos(a), np.sin(a), 0])).set_stroke(INK, 4)
        hub = Dot(self.c, radius=.08, color=INK)
        s = f"{x:.{self.nd}f}%"
        rd = M(s, .07, self.col if x > 50 else TXT).move_to(self.c + DOWN * .55)
        g = VGroup(fill, needle, hub, rd)
        g.overlap_ok = True
        return g


# ---------------- 計分板（sc08 70 格、sc09 28 格） ----------------
def score_grid(n, cols, wins, losses, c, cell_=.46, gap=.1, lit=None):
    """n 格：前 wins 格綠、接著 losses 格紅、其餘灰。lit＝已經亮的格數（None＝全亮）。只表示數量，不對應特定模型。"""
    g = VGroup()
    for k in range(n):
        col = GOOD if k < wins else (BAD if k < wins + losses else NEUTRAL)
        on = lit is None or k < lit
        sq = RoundedRectangle(corner_radius=.05, width=cell_, height=cell_).set_fill(col if on else SEA, .9 if on else 1).set_stroke(col if on else LINE, 1.5)
        g.add(sq)
    g.arrange_in_grid(cols=cols, buff=gap).move_to(c)
    return g


# ---------------- 工作站 ----------------
SK = 1.3                       # 工作站（Prefill、Decode）放大倍數
ROW_DY, TW_DX, ST_DY = .37 * SK, 1.4 * SK, 1.25 * SK


def machines(n, c, color=P2C, on=0.0, cols=None, k=1.0):
    cols = cols or n
    g = VGroup(*[RoundedRectangle(corner_radius=.06 * k, width=.42 * k, height=.62 * k).set_fill(color, .15 + .55 * on).set_stroke(color, 2.4) for _ in range(n)])
    g.arrange_in_grid(cols=cols, buff=.08 * k).move_to(c)
    return g


def typewriter(c, color=DEC, k=1.0):
    c = np.array(c, dtype=float)
    base = RoundedRectangle(corner_radius=.14, width=2.0, height=1.0).set_fill(color, .22).set_stroke(color, 3).move_to(c)
    keys = VGroup(*[Circle(.07).set_fill(color, .7).set_stroke(width=0) for _ in range(12)]).arrange_in_grid(rows=2, buff=.12).move_to(c + DOWN * .12)
    roller = RoundedRectangle(corner_radius=.06, width=1.7, height=.18).set_fill(INK, .8).set_stroke(width=0).move_to(c + UP * .58)
    return VGroup(base, keys, roller).scale(1.3 * k, about_point=c)


def paper(c, n, color=DEC, q=0, k=1.0):
    """打字機吐出的紙帶（往右），n 格；前 q 格是橘色（先把問題重說一遍）。"""
    g = VGroup(*[Square(.42 * k).set_fill(QC if j < q else color, .5 if j >= q else .75).set_stroke(QC if j < q else color, 1.5) for j in range(max(n, 1))]).arrange(RIGHT, buff=.06 * k)
    g.next_to(np.array(c, dtype=float) + RIGHT * 1.36 * k + UP * .75 * k, RIGHT, buff=.06 * k)
    if n == 0:
        g.set_opacity(0)
    return g


def station_label(s, c, dy=1.05, color=TXT):
    return T(s, .058, color).move_to(np.array(c, dtype=float) + UP * dy)


# ---------------- 收尾的回顧框（照 v001） ----------------
def keycap(s, color, frac=.05):
    """鍵盤按鍵：底座＋鍵面＋字。按下去＝鍵面與字往下移到底座上（press）。"""
    t = T(s, frac, TXT_STRONG)
    w, h = t.width + .5, t.height + .42
    base = RoundedRectangle(corner_radius=.12, width=w, height=h).set_fill("#0B1E22", 1).set_stroke(color, 2.4).shift(DOWN * .1)
    face = RoundedRectangle(corner_radius=.12, width=w, height=h).set_fill(color, .3).set_stroke(color, 2.4)
    g = VGroup(base, face, t)
    for m in g:
        m.overlap_ok = True
    g.face, g.txt = face, t
    return g


def press(k):
    return [k.face.animate(rate_func=there_and_back).shift(DOWN * .1), k.txt.animate(rate_func=there_and_back).shift(DOWN * .1)]


def recap_frame(m, buff=.12):
    r = SurroundingRectangle(m, buff=buff, corner_radius=.15).set_stroke(TXT_STRONG, 2.2)
    r.overlap_ok = r.dots_ok = True
    return r


def recap_item(frame, num_, s, frac=.06, dy=.55):
    t = VGroup(T(num_, frac, GOLD), T(s, frac, TXT_STRONG)).arrange(RIGHT, buff=.18)
    t.next_to(frame, DOWN, buff=dy)
    return t


def recap_link(frame, item):
    x = item.get_center()[0]
    ln = Line(np.array([x, frame.get_bottom()[1], 0]), item.get_top() + UP * .06).set_stroke(TXT_STRONG, 2)
    return ln


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
