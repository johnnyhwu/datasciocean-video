"""已由 lib/checks/frames.py 取代（2026-11-10）。保留這個檔名，舊的指令照樣能跑。

舊做法（每秒 4 格、160×90 灰階的整體平均差 < 0.35 就算靜止）會把「寫出一個小數字」也算成靜止：
v001 因此報成 66% 靜止，用 frames.py 逐區塊重算只有 10%。frames.py 同時檢查跳出和空畫面。

用法：uv run python lib/checks/still.py <影片 ID>（等於 frames.py <影片 ID>）
"""
import runpy
import sys
from pathlib import Path

print("still.py 已由 frames.py 取代（逐區塊判斷靜止，並檢查跳出、空畫面）", file=sys.stderr)
sys.argv = [str(Path(__file__).with_name("frames.py"))] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
