"""全景草圖：YTV_VIDEO=<id> PYTHONPATH=lib:videos/<id> uv run python -m manim -ql -s --media_dir out/<id>/sketch videos/<id>/sketch.py Pano"""
from world import *  # noqa: F401,F403


class Pano(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG
        self.camera.frame.set(width=STAGE_W).move_to(Timed.view(STAGE, STAGE_W))
        W = sheet(bars=True, scores=True)
        bal = Balance(w=SCORES, mode=1)
        self.add(*flat(W), bal, bal.readout(0), bal.readout(1), title())


class Hook(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG
        self.camera.frame.set(width=HOOK_W).move_to(Timed.view(HOOK_C, HOOK_W))
        bal = Balance()
        self.add(bal, bal.readout(0), bal.readout(1), title())
