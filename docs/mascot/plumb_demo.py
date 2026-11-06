"""錘錘（合體版）動作示範。PYTHONPATH=lib uv run python -m manim -qh --media_dir out/_mascot docs/mascot/plumb_demo.py PlumbDemo"""
from kit import *


class PlumbDemo(Scene):
    def construct(self):
        self.add(bgplate("abyss"))
        p = Plumb(scale=.6).place([-3.2, .2, 0])
        word = pill("名次", "#FF9F5A", .05, bold=True).move_to([2.8, -1.2, 0])
        self.add(p)
        self.wait(.4)
        self.play(*p.blink(), run_time=.3)
        self.play(*p.curl(), *p.mood("squint"), run_time=.8)            # ？好奇
        self.play(FadeIn(word, shift=UP * .2), *p.look(RIGHT), run_time=.5)
        self.wait(.4)
        self.play(*p.straighten(), *p.mood("wow"), run_time=.6)          # ！想通
        self.play(*p.light_on(), run_time=.5)
        self.wait(.5)
        self.play(*p.light_off(), *p.mood("neutral"), run_time=.4)
        self.play(*p.point_at(word.get_center()), run_time=.7)          # 指
        self.play(Indicate(word, color=GOLD), run_time=.6)
        self.play(*p.upright(), run_time=.6)
        self.play(FadeOut(word), *p.dive(1.2), run_time=.8)              # 下潛
        self.play(*p.sample_on(), *p.mood("happy"), run_time=.5)        # 撈到樣本
        card = takeaway_card(["名次比分數", "更好比較"]).move_to([2.6, .3, 0])
        self.play(FadeIn(card, shift=LEFT * .3), run_time=.6)
        self.wait(1.0)
