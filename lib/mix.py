"""混音：旁白（依 timeline）＋音效提示點＋背景音樂（使用者的曲庫）。

用法：uv run python lib/mix.py <影片 ID>

- 旁白：每句先做輕量音量一致化（有聲部分 RMS −20 dBFS），保持 48 kHz PCM，最後一步才編碼（規格 §7.6）。
- 音效：out/<id>/sfx-<場景>.json（動畫程式的 at(..., sfx=) 記錄），依種類校正響度，講話時壓低約 4 dB。
- 音樂：場景的 `music` 欄位是 assets/music-library.yaml 的曲目代號；連續同代號的場景共用同一段播放。
  - 片頭、片尾、段落轉換有音樂；旁白時壓低 `music_duck_db`（預設 −7 dB，旁白實驗用耳朵定案）。
  - 曲庫只有授權紀錄進 git，音樂檔在 assets/music/（不進 git）。找不到檔案就不放音樂並警告。
  - 不得使用曲庫以外的音樂（規格 §7.5）。
- 產出：out/<id>/mix.wav、mix_nomusic.wav（48 kHz 立體聲 float32），以及 mix.json（各軌量測）。
- --preview：還沒有旁白時的預覽（timeline 可以是估算版）。缺的旁白音檔就是靜音，只輸出 mix_preview.wav。
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

sys.path.insert(0, str(Path(__file__).parent))
import sfx as SFX  # noqa: E402
from paths import ROOT, load_script, load_timeline, out_dir  # noqa: E402

SR = 48000
TRIM = {"tick": -6, "click": -4, "pop": -3, "whoosh": -2, "swoosh": -3, "slide": -4, "rise": -4, "ding": -2,
        "chime": -3, "thud": 0, "crunch": -2, "scratch": -1, "buzz": -5, "boing": -3}


def db(x):
    return 10 ** (x / 20)


def rms_active(x, thr=0.02):
    a = np.abs(x)
    m = a > thr * (a.max() + 1e-12)
    return float(np.sqrt(np.mean(x[m] ** 2))) if m.any() else 1e-9


def load_mono(path, sr_out=SR):
    x, sr = sf.read(path, always_2d=True)
    x = x.mean(1)
    if sr != sr_out:
        from math import gcd
        g = gcd(sr, sr_out)
        x = resample_poly(x, sr_out // g, sr // g)
    return x


def follow(sig, att=0.03, rel=0.35, hop=480):
    fr = np.sqrt(np.convolve(sig ** 2, np.ones(hop) / hop, mode="same")[::hop])
    on = (fr > db(-40)).astype(float)
    out = np.zeros_like(on)
    a_, r_ = np.exp(-hop / SR / att), np.exp(-hop / SR / rel)
    for i in range(1, len(on)):
        k = a_ if on[i] > out[i - 1] else r_
        out[i] = k * out[i - 1] + (1 - k) * on[i]
    return np.interp(np.arange(len(sig)), np.arange(len(out)) * hop, out)


def music_track(vid, T, n, spec):
    lib_path = ROOT / "assets/music-library.yaml"
    if not lib_path.exists():
        print("警告：沒有 assets/music-library.yaml，不放背景音樂")
        return np.zeros(n), []
    import yaml
    lib = yaml.safe_load(lib_path.read_text()) or {}
    tracks = lib.get("tracks", {})
    mus, used = np.zeros(n), []
    # 依連續相同代號分段，每段從曲子開頭播、必要時循環，段與段之間交叉淡化 1.2 秒
    segs, cur = [], None
    for sc in T["scenes"]:
        code = sc.get("music")
        a = int(sc["start"] * SR)
        if cur and cur[0] == code:
            cur[2] = a + int(sc["duration"] * SR)
        else:
            cur = [code, a, a + int(sc["duration"] * SR)]
            segs.append(cur)
    xf = int(1.2 * SR)
    for code, a, b in segs:
        if not code:
            continue
        info = tracks.get(code)
        f = ROOT / "assets/music" / info["file"] if info else None
        if not f or not f.exists():
            print(f"警告：曲目 {code} 不在曲庫或檔案不存在，該段不放音樂")
            continue
        y = load_mono(f)
        y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9)
        L = min(n, b + xf) - max(0, a - xf)
        reps = int(np.ceil(L / len(y)))
        seg = np.tile(y, reps)[:L]
        env = np.ones(L)
        k = min(xf, L // 2)
        env[:k] = np.linspace(0, 1, k)
        env[-k:] = np.linspace(1, 0, k)
        s0 = max(0, a - xf)
        mus[s0:s0 + L] += seg * env
        used.append({"code": code, "file": info["file"], "license": info.get("license", ""),
                     "attribution": info.get("attribution", "")})
    return mus, used


def main():
    vid = sys.argv[1]
    preview = "--preview" in sys.argv
    T, spec, od = load_timeline(vid), load_script(vid), out_dir(vid)
    if T.get("estimated") and not preview:
        sys.exit("timeline 是估算版（--estimate），不能混音；先合成旁白再重跑 timeline.py（或用 --preview 做無旁白預覽）。")
    n = int(T["frames"] / T["fps"] * SR)
    TARGET = db(-20)
    voice = np.zeros(n)
    for sc in T["scenes"]:
        for s in sc["sentences"]:
            f = od / f"audio/{s['id']}.wav"
            if preview and not f.exists():
                continue
            x = load_mono(f)
            x = x * TARGET / rms_active(x)
            pk = np.abs(x).max()
            if pk > 0.95:
                x *= 0.95 / pk
            a = int(s["abs"] * SR)
            voice[a:a + len(x)] += x[: max(0, n - a)]
    vact = follow(voice)

    fx, cache, cnt = np.zeros(n), {}, 0
    for sc in T["scenes"]:
        f = od / f"sfx-{sc['id']}.json"
        if not f.exists():
            continue
        t0 = sc["start_frame"] / T["fps"]
        for c in json.loads(f.read_text()):
            k = c["kind"]
            if k not in cache:
                y = SFX.make(k).astype(np.float64)
                cache[k] = y * db(-30 + TRIM.get(k, 0)) / rms_active(y, 0.1)
            y = cache[k]
            a = int((t0 + c["t"]) * SR)
            m = min(len(y), n - a)
            if m > 0:
                fx[a:a + m] += c.get("gain", 1.0) * y[:m]
                cnt += 1
    fx *= 1 - 0.37 * vact

    mus, used = music_track(vid, T, n, spec)
    duck_db = spec.get("music_duck_db", -7)
    mus = mus * db(spec.get("music_level_db", -17)) * TARGET
    mus *= 1 - (1 - db(duck_db)) * vact

    outs = (("mix_preview", (voice, fx, mus)),) if preview else (("mix", (voice, fx, mus)), ("mix_nomusic", (voice, fx)))
    for name, parts in outs:
        mix = sum(parts)
        mix = mix / max(1.0, np.abs(mix).max() / 0.97)
        sf.write(od / f"{name}.wav", np.stack([mix, mix], 1).astype(np.float32), SR)

    def r(x):
        return round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
    speak = vact > 0.5
    gap = r(voice[speak]) - r(mus[speak]) if speak.any() and mus.any() else None
    info = {"seconds": round(n / SR, 2), "sfx_cues": cnt, "rms_db": {"voice": r(voice), "sfx": r(fx), "music": r(mus)},
            "music_below_voice_while_speaking_db": gap, "music_used": used}
    (od / "mix.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
