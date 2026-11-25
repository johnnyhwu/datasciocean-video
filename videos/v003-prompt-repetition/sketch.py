"""關卡 2 的全景草圖（靜態）：一條只能回頭看的長廊。
YTV_VIDEO=v003-prompt-repetition PYTHONPATH=lib uv run python -m manim -ql -s --media_dir out/v003-prompt-repetition/sketch videos/v003-prompt-repetition/sketch.py Panorama
"""
from kit import *  # noqa: F401,F403

POOL = S["concept_pool"]
P1C, P2C, LIGHT, QC, DEC = POOL[1], POOL[5], POOL[2], POOL[0], POOL[3]


def reader(word, color, w=1.05, clear=None):
    """一個戴半邊眼罩的小讀者：左眼張開、右眼被眼罩蓋住。"""
    body = RoundedRectangle(corner_radius=.18, width=w, height=.95).set_fill(color, .22).set_stroke(color, 3)
    eye = Dot(radius=.07, color=TXT_STRONG).move_to(body.get_top() + DOWN * .28 + LEFT * .2)
    patch = RoundedRectangle(corner_radius=.05, width=.26, height=.16).set_fill(DIM, 1).set_stroke(width=0).move_to(body.get_top() + DOWN * .28 + RIGHT * .2)
    lab = T(word, .04, TXT_STRONG).move_to(body.get_center() + DOWN * .14)
    return VGroup(body, eye, patch, lab)


class Panorama(MovingCameraScene):
    def construct(self):
        self.camera.frame.set(width=FW * 1.9).move_to(RIGHT * 0.2 + DOWN * .5)
        words = ["The", "bark", "was", "rough", "."]
        p1 = VGroup(*[reader(w, P1C) for w in words]).arrange(RIGHT, buff=.3)
        p2 = VGroup(*[reader(w, P2C) for w in words]).arrange(RIGHT, buff=.3)
        row = VGroup(p1, p2).arrange(RIGHT, buff=1.0).move_to(UP * 1.6)
        seam = Line(row.get_top() + UP * .5, row.get_bottom() + DOWN * .3).set_stroke(GOLD, 6).move_to(
            (p1.get_right() + p2.get_left()) / 2 + UP * .1)
        lab1 = T("第一遍 P1", .042, P1C).next_to(p1, UP, buff=1.9)
        lab2 = T("第二遍 P2", .042, P2C).next_to(p2, UP, buff=1.9)
        # 光：P1 的 rough 只照到 P1 開頭；P2 的 bark 照穿整個 P1
        beam1 = Arrow(p1[3].get_left() + DOWN * .55, p1[0].get_left() + DOWN * .55, buff=0, stroke_width=5, color=LIGHT).set_opacity(.8)
        beam2 = Arrow(p2[1].get_left() + DOWN * .75, p1[0].get_left() + DOWN * .75, buff=0, stroke_width=7, color=LIGHT)
        # 想法泡泡
        fog = VGroup(T("狗叫？", .04, BG), T("樹皮？", .04, BG)).arrange(DOWN, buff=.05).set_opacity(.5)
        b1 = think(fog).next_to(p1[1], UP, buff=.12).scale(.8)
        b2 = think(B("樹皮", .05, "#8A5A10")).next_to(p2[1], UP, buff=.12).scale(.8)
        # 下層工作站
        pre = VGroup(*[RoundedRectangle(corner_radius=.05, width=.32, height=.55).set_fill(P2C, .35).set_stroke(P2C, 2) for _ in range(14)]).arrange(RIGHT, buff=.08)
        pre_lab = T("Prefill：一次同時讀完（可平行）", .04, TXT).next_to(pre, UP, buff=.25)
        prefill = VGroup(pre, pre_lab).move_to(LEFT * 4.6 + DOWN * 2.6)
        tw = RoundedRectangle(corner_radius=.1, width=1.6, height=1.0).set_fill(DEC, .25).set_stroke(DEC, 3)
        paper = VGroup(*[Square(.3).set_fill(DEC, .5).set_stroke(DEC, 1) for _ in range(4)]).arrange(RIGHT, buff=.05).next_to(tw, RIGHT, buff=.1)
        dec_lab = T("Decode：一個字一個字吐出", .04, TXT).next_to(VGroup(tw, paper), UP, buff=.25)
        decode = VGroup(tw, paper, dec_lab).move_to(RIGHT * 4.6 + DOWN * 2.6)
        # 儀表
        meter = VGroup(T("NameIndex", .04, MUTED), VGroup(T("21%", .06, TXT), T("→", .05, TXT), T("97%", .06, GOLD)).arrange(RIGHT, buff=.2)).arrange(DOWN, buff=.15)
        meter.move_to(RIGHT * 7.2 + UP * 4.2)
        plumb = Plumb(.45).place(LEFT * 8.3 + UP * 2.6)
        boxes = VGroup(
            SurroundingRectangle(p1, color=MUTED, buff=.2), SurroundingRectangle(VGroup(seam, p2), color=MUTED, buff=.2),
            SurroundingRectangle(prefill, color=MUTED, buff=.2))
        nums = VGroup(*[T(s, .04, MUTED).next_to(b, DOWN, buff=.12) for s, b in zip(["①", "②", "③"], boxes)])
        self.add(lab1, lab2, row, seam, beam1, beam2, b1, b2, prefill, decode, meter, plumb, boxes, nums)
