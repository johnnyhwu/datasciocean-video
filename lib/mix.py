"""混音：旁白（依 timeline）＋音效提示點＋背景音樂（使用者的曲庫）。

用法：uv run python lib/mix.py <影片 ID>

- 旁白：每句先做輕量音量一致化（有聲部分 RMS −20 dBFS），保持 48 kHz PCM，最後一步才編碼（規格 §7.6）。
- 音效：out/<id>/sfx-<場景>.json（動畫程式的 at(..., sfx=) 記錄），依種類校正響度，講話時壓低約 4 dB。
  - assets/sfx-library.yaml 有列的種類用錄音檔（CC0，assets/sfx/），同一種類的幾個變化輪流用；
    沒列或檔案不在就用 lib/sfx.py 的合成音。--synth 強制全部用合成音（對照用）。
- 音樂：場景的 `music` 欄位是 assets/music-library.yaml 的曲目代號；連續同代號的場景共用同一段播放。
  - 片頭、片尾、段落轉換有音樂；旁白時壓低 `music_duck_db`（預設 −6 dB）；音量 `music_level_db`（預設 −13 dB，相對旁白，以 200 Hz 以上計）。
    使用者 2026-11-16 聽 v001：−17／−7 加上低頻為主的曲子「幾乎聽不到」。
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
        "chime": -3, "thud": 0, "crunch": -2, "scratch": -1, "buzz": -5, "boing": -3, "knob": -5, "bell": -3}


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


def sfx_bank():
    """assets/sfx-library.yaml → {種類: [波形, …]}。檔案不齊的種類整個略過（回到合成音）。"""
    lib = ROOT / "assets/sfx-library.yaml"
    if "--synth" in sys.argv or not lib.exists():
        return {}
    import yaml
    bank = {}
    for kind, variants in ((yaml.safe_load(lib.read_text()) or {}).get("kinds") or {}).items():
        ys = []
        for spec in variants:
            layers = []
            for part in spec.split("+"):
                part, _, g = part.strip().partition("*")
                name, _, rng = part.partition("@")
                f = ROOT / "assets/sfx" / f"{name}.wav"
                if not f.exists():
                    layers = None
                    break
                y = load_mono(f)
                if rng:
                    a, b = (float(v) for v in rng.split("-"))
                    y = y[int(a * SR):int(b * SR)]
                on = int(np.argmax(np.abs(y) > 0.05 * np.abs(y).max()))      # 去掉開頭的空白，起音才會對到畫面
                y = y[max(0, on - int(0.002 * SR)):].copy()
                k = min(len(y) // 4, int(0.03 * SR))
                y[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
                y[-k:] *= np.linspace(1, 0, k)
                layers.append(y / (np.abs(y).max() + 1e-9) * float(g or 1))
            if layers is None:
                print(f"警告：音效 {kind} 的檔案 {spec} 不在 assets/sfx/，改用合成音")
                ys = []
                break
            out = np.zeros(max(len(y) for y in layers))
            for y in layers:
                out[:len(y)] += y
            ys.append(out)
        if ys:
            bank[kind] = ys
    return bank


def band_power(y, lo=1000, hi=4000):
    """1～4 kHz（子音帶）的平均功率。聽不聽得懂旁白看這一帶，不是看全頻（podcast 的 docs/MUSIC.md）。"""
    from scipy.signal import butter, sosfilt
    return float(np.mean(sosfilt(butter(4, [lo, hi], "bp", fs=SR, output="sos"), y) ** 2))


def punct_track(T, n, spec, voice):
    """音樂只當標點，不鋪底（使用者 2026-11-16：鋪底「干擾人聲」「一直持續有點吵」，改參考 podcast）。

    script.json 的 music_punct：
      intro  {"track": 代號, "after": 句 id, "lead": 秒}  那一句說完就進來（提前 lead 秒起弱起拍），下一句開始時壓低、淡出
      stings {"track": 代號, "before": [句 id…]}    這些句子的前一句說完就進來（章節轉場）
      outro  {"track": 代號, "pre": 秒}             最後一句結束前 pre 秒壓低進來，旁白結束後升回全音量
    音量：有聲部分 RMS 對齊旁白（rel dB）。壓低的幅度逐段計算，讓子音帶的音樂比旁白低 22 dB 以上（最少壓 15 dB）。
    旁白一進來就維持壓低到這一段結束，不在句子間的空檔彈回來。"""
    import yaml
    P = spec["music_punct"]
    tracks = (yaml.safe_load((ROOT / "assets/music-library.yaml").read_text()) or {}).get("tracks", {})
    sents = [s for sc in T["scenes"] for s in sc["sentences"]]
    end = {s["id"]: s["abs"] + (s["end"] - s["start"]) for s in sents}
    prev = {b["id"]: a["id"] for a, b in zip(sents, sents[1:])}
    mus, used, log = np.zeros(n), [], []

    def clip(code, rel):
        info = tracks.get(code)
        f = ROOT / "assets/music" / info["file"] if info else None
        if not f or not f.exists():
            print(f"警告：曲目 {code} 不在曲庫或檔案不存在，略過")
            return None
        y = load_mono(f)
        if not any(u["code"] == code for u in used):
            used.append({"code": code, "file": info["file"], "license": info.get("license", ""),
                         "attribution": info.get("attribution", "")})
        return y * db(-20 + rel) / rms_active(y, 0.05)   # 旁白有聲部分是 −20 dBFS

    def duck_amount(y, a, mask):
        v = voice[a:a + len(y)]
        m = mask[:len(v)]
        if not m.any() or band_power(v[m]) < 1e-12:
            return -15.0
        got = 10 * np.log10(band_power(y[:len(v)][m]) / band_power(v[m])) - 15.0
        return -15.0 + min(0.0, -22.0 - got)

    def put(y, t, kind, skip=0.0):
        a = max(0, int(t * SR))
        y = y[: n - a]
        act = follow(voice, att=0.05, rel=0.3)[a:a + len(y)] > 0.5
        act[:int(skip * SR)] = False            # 弱起拍疊在前一句的尾巴上，不算「旁白進來了」
        if kind == "outro":                       # 旁白結束前壓低，結束後 0.8 秒升回來
            last = int(np.nonzero(act)[0].max()) if act.any() else 0
            d = duck_amount(y, a, np.arange(len(y)) <= last)
            g = np.full(len(y), db(d))
            k = min(int(0.8 * SR), len(y) - last)
            g[last:last + k] = np.linspace(db(d), 1, k)
            g[last + k:] = 1
        else:                                     # 旁白進來前全音量，進來時 0.35 秒壓低，之後不再彈回
            first = int(np.argmax(act)) if act.any() else len(y)
            d = duck_amount(y, a, np.arange(len(y)) >= first)
            g = np.ones(len(y))
            r0 = max(0, first - int(0.2 * SR))
            k = min(int(0.35 * SR), len(y) - r0)
            g[r0:r0 + k] = np.linspace(1, db(d), k)
            g[r0 + k:] = db(d)
        mus[a:a + len(y)] += y * g
        log.append({"kind": kind, "at": round(a / SR, 2), "len": round(len(y) / SR, 2), "duck_db": round(d, 1)})

    if P.get("intro"):
        y = clip(P["intro"]["track"], P["intro"].get("rel", 0))
        if y is not None:
            put(y, end[P["intro"]["after"]] - P["intro"].get("lead", 0), "intro", P["intro"].get("lead", 0))   # lead：曲子開頭的弱起拍長度，讓重拍落在那一句說完的瞬間
    for sid in (P.get("stings") or {}).get("before", []):
        y = clip(P["stings"]["track"], P["stings"].get("rel", -3))
        if y is not None:
            put(y, end[prev[sid]], "sting")
    if P.get("outro"):
        y = clip(P["outro"]["track"], P["outro"].get("rel", 0))
        if y is not None:
            put(y, end[sents[-1]["id"]] - P["outro"].get("pre", 3.0), "outro")
    return mus, used, log


def calibrate(kind, samples):
    """合成音：有聲部分 RMS 校到 −30 dBFS 加種類修正（PoC 用耳朵定的平衡）。
    錄音檔：總能量對齊同種類的合成音，這樣換檔不會改變已經調好的音量平衡。
    錄音的敲擊聲只有 10～20 毫秒，只對齊 RMS 會小聲約 6 dB。增益限制在 −6～+10 dB，峰值最多比合成音高 8 dB。"""
    ref = SFX.make(kind).astype(np.float64)
    ref = ref * db(-30 + TRIM.get(kind, 0)) / rms_active(ref, 0.1)
    if not samples:
        return [ref]
    out = []
    for y in samples:
        z = y * db(-30 + TRIM.get(kind, 0)) / rms_active(y, 0.1)
        g = np.clip(np.sqrt(np.sum(ref ** 2) / (np.sum(z ** 2) + 1e-12)), db(-6), db(10))
        g = min(g, db(8) * np.abs(ref).max() / (np.abs(z).max() + 1e-12))   # 峰值最多比合成音高 8 dB（長音換成短促的錄音時）
        out.append(z * g)
    return out


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
        # 以 200 Hz 以上的音量為準：手機、筆電喇叭放不出更低的聲音。
        # v001 第一次選的曲子 91% 能量在 250 Hz 以下，用全頻 RMS 對齊後使用者「幾乎聽不到」。
        from scipy.signal import butter, sosfilt
        band = sosfilt(butter(2, 200, "hp", fs=SR, output="sos"), y)
        y = band + 0.5 * (y - band)          # 200 Hz 以下減 6 dB：不和旁白的低頻搶，耳機聽也不會轟
        y = y / (np.sqrt(np.mean(band ** 2)) + 1e-9)
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

    fx, cache, cnt, bank, seen = np.zeros(n), {}, 0, sfx_bank(), {}
    for sc in T["scenes"]:
        f = od / f"sfx-{sc['id']}.json"
        if not f.exists():
            continue
        t0 = sc["start_frame"] / T["fps"]
        for c in json.loads(f.read_text()):
            k = c["kind"]
            if k not in cache:
                cache[k] = calibrate(k, bank.get(k))
            y = cache[k][seen.get(k, 0) % len(cache[k])]
            seen[k] = seen.get(k, 0) + 1
            a = int((t0 + c["t"]) * SR)
            m = min(len(y), n - a)
            if m > 0:
                fx[a:a + m] += c.get("gain", 1.0) * y[:m]
                cnt += 1
    fx *= 1 - 0.37 * vact

    punct = None
    if spec.get("music_punct"):                   # 音樂當標點：片頭、章節轉場、片尾
        mus, used, punct = punct_track(T, n, spec, voice)
    else:                                         # 音樂鋪底
        mus, used = music_track(vid, T, n, spec)
        duck_db = spec.get("music_duck_db", -6)
        mus = mus * db(spec.get("music_level_db", -13)) * TARGET
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
            "music_below_voice_while_speaking_db": gap, "music_used": used,
            "sfx_sampled": sorted(k for k in seen if k in bank), "sfx_synth": sorted(k for k in seen if k not in bank), "music_punct": punct}
    (od / "mix.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
