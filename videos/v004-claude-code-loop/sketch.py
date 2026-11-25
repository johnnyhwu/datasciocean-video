"""全景草圖：把大圖所有元件一次擺出來（不設 YTV_VIDEO 也能跑）。"""
import os, sys
from pathlib import Path
os.environ.setdefault("YTV_VIDEO", "v004-claude-code-loop")
sys.path.insert(0, str(Path(__file__).parent))
from world import *  # noqa


class Pano(MovingCameraScene):
    def construct(self):
        self.camera.frame.move_to(WORK_C + DOWN * .55).set(width=WORK_W)
        self.add(track(), glass_model(look=LEFT), station_words(), gate(), toolbox(names=True))
        self.add(scroll_top(), scroll_rows([("任務：修好沒過的測試", "task"), ("Read test_calc.py", "call"), ("（檔案內容）", "obs"),
                                            ("Edit calc.py", "call"), ("Bash: pytest", "call"), ("FAILED  1 個測試沒過", "err")]))
        self.add(read_beam(6, .8))
        s = slip("Bash", "pytest", mood="sweat").move_to(P(-40)); self.add(s)
        self.add(code_mountain(np.array([8.2, -2.3, 0]), s=.9))
