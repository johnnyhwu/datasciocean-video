"""旁白先行的時間軸：script.json ＋ 音檔時長 → timeline.json、SRT（繁／簡）、章節。

用法：uv run python lib/timeline.py <影片 ID> [--estimate]

- 句子時長＝實測音檔時長（out/<id>/audio/report.json）。還沒有音檔時用 --estimate，以語速估算
  （rules/speech-rate.md：純語音約 235 單位／分鐘），只用來先做畫面。
- 場景時長＝前置留白＋各句（時長＋句間 gap＋hold）＋後置留白。最後一場另加 end_screen 秒的乾淨片尾（片尾畫面用）。
- 全片絕對時間用累計秒數，只在最後換算一次影格，避免每場各自取整的誤差累積（規格 §7.3-6）。
- 產出：videos/<id>/timeline.json、videos/<id>/chapters.txt（進 git）；out/<id>/subs.zh-TW.srt、subs.zh-CN.srt。
- 字幕檢查（規格 §7.4）：每行字數、行數、每秒字數；違反就列出，交給腳本步驟修。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import STYLE, load_script, out_dir, video_dir  # noqa: E402
from textutil import split_lines, srt_time, units, yt_time  # noqa: E402

FPS = 30
EST_UPM = 235  # 估算用的純語音語速（單位／分鐘）


def build(vid: str, estimate: bool):
    spec = load_script(vid)
    rep = {}
    if not estimate:
        rp = out_dir(vid) / "audio/report.json"
        if not rp.exists():
            sys.exit("沒有 out/<id>/audio/report.json；先跑 tts_gemini.py，或加 --estimate。")
        rep = json.loads(rp.read_text())
    gap = spec.get("gap", 0.25)
    default_pad = spec.get("scene_pad", [0.4, 0.5])
    labels = {k: v.get("label", "") for k, v in spec.get("speakers", {}).items()}
    t, cues, scenes = 0.0, [], []
    for i, sc in enumerate(spec["scenes"]):
        pre, post = sc.get("pad", default_pad)
        if i == len(spec["scenes"]) - 1:
            post += spec.get("end_screen", 20)
        s0 = t
        t += pre
        sents = []
        for s in sc["sentences"]:
            if estimate:
                d = round(units(s.get("say") or s["display"]) / EST_UPM * 60, 3)
            else:
                if s["id"] not in rep:
                    sys.exit(f"{s['id']} 沒有音檔；先跑 tts_gemini.py。")
                d = rep[s["id"]]["dur"]
            sents.append({**s, "start": round(t - s0, 3), "end": round(t - s0 + d, 3), "abs": round(t, 3)})
            cues.append((t, t + d, s["display"], s.get("speaker", "narrator")))
            t += d + gap + s.get("hold", 0)
        t += post - gap
        meta = {k: v for k, v in sc.items() if k != "sentences"}
        scenes.append({**meta, "start": round(s0, 3), "duration": round(t - s0, 3), "sentences": sents})
    out = {"video": vid, "title": spec.get("title", ""), "estimated": estimate, "fps": FPS,
           "width": 1920, "height": 1080, "duration": round(t, 3), "frames": round(t * FPS),
           "end_screen": spec.get("end_screen", 20), "scenes": scenes}
    for sc in scenes:
        sc["start_frame"] = round(sc["start"] * FPS)
    for i, sc in enumerate(scenes):
        nxt = scenes[i + 1]["start_frame"] if i + 1 < len(scenes) else out["frames"]
        sc["frames"] = nxt - sc["start_frame"]
    (video_dir(vid) / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

    # 章節：有 chapter 的場景。YouTube 規則：第一個 0:00、至少 3 段、每段 ≥ 10 秒。
    chaps = [(0.0, spec.get("chapter0", "開場"))] + [(sc["start"], sc["chapter"][1]) for sc in scenes[1:] if sc.get("chapter")]
    problems = []
    if len(chaps) < 3:
        problems.append(f"章節只有 {len(chaps)} 段（至少 3 段）")
    for (a, n), (b, _) in zip(chaps, chaps[1:] + [(out["duration"], "")]):
        if b - a < 10:
            problems.append(f"章節「{n}」只有 {b - a:.1f} 秒（至少 10 秒）")
    (video_dir(vid) / "chapters.txt").write_text("\n".join(f"{yt_time(a)} {n}" for a, n in chaps) + "\n")

    # 字幕
    import opencc
    import yaml
    from paths import ROOT
    occ = opencc.OpenCC("tw2sp")  # 台灣繁體 → 簡體，含地區用語
    fix = yaml.safe_load((ROOT / "config/zh-cn-terms.yaml").read_text()) or {}

    class conv:  # noqa: N801
        @staticmethod
        def convert(x):
            x = occ.convert(x)
            for a, b in fix.items():
                x = x.replace(a, b)
            return x
    sub = STYLE["subtitle"]
    for lang, f in [("zh-TW", lambda x: x), ("zh-CN", conv.convert)]:
        blocks = []
        for i, (a, b, txt, spk) in enumerate(cues, 1):
            show = (labels.get(spk, "") + "：" + txt) if labels.get(spk) else txt
            try:
                lines = split_lines(f(show), sub["max_units_per_line"], sub["max_lines"])
            except ValueError as e:
                problems.append(f"{lang} 第 {i} 條：{e}")
                lines = [f(show)]
            if lang == "zh-TW":
                ups = units(txt) / max(0.01, b - a)
                if ups > sub["max_units_per_sec"]:
                    problems.append(f"第 {i} 條每秒 {ups:.1f} 字（上限 {sub['max_units_per_sec']}）：{txt[:20]}")
            blocks.append(f"{i}\n{srt_time(a)} --> {srt_time(b + 0.15)}\n" + "\n".join(lines) + "\n")
        (out_dir(vid) / f"subs.{lang}.srt").write_text("\n".join(blocks))
    return out, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid")
    ap.add_argument("--estimate", action="store_true")
    a = ap.parse_args()
    out, problems = build(a.vid, a.estimate)
    tag = "（估算）" if a.estimate else ""
    print(f"片長{tag} {out['duration']:.1f} 秒＝{out['duration'] / 60:.1f} 分、{out['frames']} 格、{len(out['scenes'])} 場")
    for sc in out["scenes"]:
        print(f"  {sc['id']:6} {sc['duration']:6.1f}s  {sc.get('name', '')}")
    if not 180 <= out["duration"] <= 15 * 60 + out["end_screen"]:
        problems.append(f"片長 {out['duration'] / 60:.1f} 分，超出 3～15 分鐘")
    print("問題：" + ("無" if not problems else "\n  " + "\n  ".join(problems)))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
