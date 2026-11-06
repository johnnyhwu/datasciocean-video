"""影片 ID → 路徑。文字產物在 videos/<id>/（進 git），音檔與渲染在 out/<id>/（不進 git）。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLE = json.loads((ROOT / "config/style.json").read_text())


def video_dir(vid: str) -> Path:
    return ROOT / "videos" / vid


def out_dir(vid: str) -> Path:
    d = ROOT / "out" / vid
    d.mkdir(parents=True, exist_ok=True)
    return d


def ffmpeg() -> str:
    """專案 .venv 內的靜態 ffmpeg（imageio-ffmpeg），不依賴系統安裝。"""
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_script(vid: str) -> dict:
    return json.loads((video_dir(vid) / "script.json").read_text())


def load_timeline(vid: str) -> dict:
    return json.loads((video_dir(vid) / "timeline.json").read_text())
