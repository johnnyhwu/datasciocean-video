"""成片：畫面＋混音 → 兩段式 loudnorm → 軟字幕 MP4，並做程式檢查（規格 §4.2、§7.6）。

用法：uv run python lib/package.py <影片 ID> [--nomusic]

- 響度：全片一次兩段式 loudnorm，目標 −14 LUFS integrated、−1 dBTP、LRA 11；再用 ebur128 驗證（±1 LU）。
- 48 kHz，AAC-LC 256k。影片串流直接複製（render.py 已經是 H.264 1080p30）。
- 字幕：繁中、簡中兩軌 mov_text（軟字幕，不燒入），另外交付 SRT 檔。
- 檢查：響度、真峰值、取樣率、影音長度差 ≤ 0.3 秒、格數＝timeline、C2PA 殘留。
- 產出：out/<id>/deliver/<id>.mp4、subs.*.srt、chapters.txt、checks.json。
- --preview：審查用的預覽版（out/<id>/deliver/<id>-preview.mp4）：字幕燒入（subs.ass），聲音用 mix_preview.wav，
  不做響度正規化與成片檢查。給使用者在手機上看畫面與節奏，不能上傳。
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import ROOT, ffmpeg, load_timeline, out_dir, video_dir  # noqa: E402

I, TP, LRA = -14.0, -1.0, 11.0


def run(args, **kw):
    return subprocess.run([ffmpeg(), "-hide_banner", *args], capture_output=True, text=True, **kw)


def measure_loudnorm(wav):
    r = run(["-i", str(wav), "-af", f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"])
    return json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])


def ebur128(path):
    r = run(["-nostats", "-i", str(path), "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    peak = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1))
    return i, peak


def probe(path):
    """用 ffmpeg -i 的輸出讀時長與取樣率（專案裡沒有 ffprobe）。"""
    r = run(["-i", str(path)])
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    secs = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    sr = re.search(r"Audio:.*?(\d+) Hz", r.stderr)
    return secs, int(sr.group(1)) if sr else None


def stream_durations(path):
    """分別解出影像與聲音的實際長度（秒）。"""
    out = {}
    r = run(["-i", str(path), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"])
    out["frames"] = int(re.findall(r"frame=\s*(\d+)", r.stderr)[-1])
    out["video"] = round(out["frames"] / 30, 3)
    r = run(["-i", str(path), "-map", "0:a:0", "-c", "copy", "-f", "null", "-"])
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", r.stderr)
    if m:
        h, mi, s = m[-1]
        out["audio"] = int(h) * 3600 + int(mi) * 60 + float(s)
    return out


def c2pa_check(path):
    """粗查：MP4 內是否有 C2PA／JUMBF 標記（manifest 會以 'c2pa' 或 'jumb' box 出現）。"""
    data = Path(path).read_bytes()
    hits = [k for k in (b"c2pa", b"jumb", b"jumd") if k in data]
    return {"found": bool(hits), "markers": [h.decode() for h in hits]}


def preview(vid):
    od = out_dir(vid)
    dl = od / "deliver"
    dl.mkdir(exist_ok=True)
    final = dl / f"{vid}-preview.mp4"
    fonts = ROOT / "assets/fonts"
    ass = str(od / "subs.ass").replace(":", r"\:")
    r = run(["-y", "-i", str(od / "video.mp4"), "-i", str(od / "mix_preview.wav"), "-map", "0:v", "-map", "1:a",
             "-vf", f"ass={ass}:fontsdir={fonts}", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(final)])
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    print("預覽版：", final)


def main():
    vid = sys.argv[1]
    if "--preview" in sys.argv:
        return preview(vid)
    nomusic = "--nomusic" in sys.argv
    od, T = out_dir(vid), load_timeline(vid)
    video = od / "video.mp4"
    wav = od / ("mix_nomusic.wav" if nomusic else "mix.wav")
    dl = od / "deliver"
    dl.mkdir(exist_ok=True)
    m = measure_loudnorm(wav)
    norm = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    final = dl / f"{vid}{'-nomusic' if nomusic else ''}.mp4"
    r = run(["-y", "-i", str(video), "-i", str(wav), "-i", str(od / "subs.zh-TW.srt"), "-i", str(od / "subs.zh-CN.srt"),
             "-map", "0:v", "-map", "1:a", "-map", "2", "-map", "3", "-c:v", "copy", "-af", norm + ",alimiter=limit=0.84:level=false,aresample=48000",  # 限制在約 −1.5 dBFS：AAC 編碼後峰值會多 0.2～0.5 dB
             "-c:a", "aac", "-b:a", "256k", "-c:s", "mov_text",
             "-metadata:s:s:0", "language=zho", "-metadata:s:s:0", "title=繁體中文",
             "-metadata:s:s:1", "language=zho", "-metadata:s:s:1", "title=简体中文", str(final)])
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    for f in ("subs.zh-TW.srt", "subs.zh-CN.srt"):
        shutil.copy(od / f, dl / f)
    shutil.copy(video_dir(vid) / "chapters.txt", dl / "chapters.txt")

    li, peak = ebur128(final)
    durs = stream_durations(final)
    _, sr = probe(final)
    want = T["frames"] / T["fps"]
    checks = {
        "loudness_lufs": li, "loudness_ok": abs(li - I) <= 1.0,
        "peak_dbfs": peak, "peak_ok": peak <= TP + 0.1,
        "sample_rate": sr, "sample_rate_ok": sr == 48000,
        "video_s": durs.get("video"), "audio_s": durs.get("audio"), "timeline_s": round(want, 3),
        "av_diff_ok": abs(durs.get("video", 0) - durs.get("audio", 0)) <= 0.3,
        "frames": durs.get("frames"), "frames_ok": durs.get("frames") == T["frames"],
        "c2pa": c2pa_check(final),
    }
    (dl / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=1))
    bad = [k for k, v in checks.items() if k.endswith("_ok") and not v]
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    print("成片：", final, "；檢查：", "全部通過" if not bad else f"未通過 {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
