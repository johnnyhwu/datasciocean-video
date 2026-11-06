"""逐句旁白合成（Gemini 3.8 Flash TTS，直連 Gemini API）。

用法：uv run python lib/tts_gemini.py <影片 ID> [--only s1,s2] [--force]

- 讀 videos/<id>/script.json：每句 `say`（唸法稿；省略就用 `display`）、`style`（語氣，可省略）、`speaker`。
- 聲音設定在 config/voice.json：{"narrator": {"voice": "voice_…或預設聲音名", "model": "gemini-3.8-flash-tts"}, ...}
- 快取：檔名 = sha256(唸法稿, 聲音, 模型, 語氣)。內容沒變就不重做（規格 §7.3）。
- 產出：out/<id>/audio/<句 id>.wav（24 kHz 單聲道，已修剪頭尾靜音）與 out/<id>/audio/report.json（每句時長）。
- 錯誤：短暫錯誤拉長間隔重試；同一句失敗 3 次就停下回報；碰到每日上限（429 且訊息含 per day / daily）
  就存檔停止，下次從同一句接續（規格 §4.3）。
- 金鑰：環境變數 GEMINI_API_KEY（可放 .env，程式自動讀；不印出、不寫進任何檔案）。
- 已知：Gemini 不回傳時間戳，seed 無效（重跑就是重骰），所以要靠快取鎖定已經滿意的版本。
"""
import argparse
import base64
import hashlib
import io
import json
import os
import sys
import time
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from paths import ROOT, load_script, out_dir  # noqa: E402

SR = 24000


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("缺少 GEMINI_API_KEY（放在 .env 或環境變數）。")


def key_of(text, voice, model, style):
    return hashlib.sha256(json.dumps([text, voice, model, style], ensure_ascii=False).encode()).hexdigest()[:20]


def to_pcm(raw: bytes) -> np.ndarray:
    """回應可能是 WAV（有 RIFF 檔頭）或裸 PCM（24 kHz 16-bit 單聲道）。"""
    if raw[:4] == b"RIFF":
        with wave.open(io.BytesIO(raw)) as w:
            assert w.getframerate() == SR and w.getnchannels() == 1, "非預期的音訊格式"
            raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def trim(x: np.ndarray, thr_db=-45, pad=0.05) -> np.ndarray:
    hop = int(0.01 * SR)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
    on = np.where(20 * np.log10(e) > thr_db)[0]
    if len(on) == 0:
        raise RuntimeError("音檔是靜音")
    a = max(0, on[0] * hop - int(pad * SR))
    b = min(len(x), (on[-1] + 1) * hop + int(pad * SR))
    return x[a:b]


def write_wav(path: Path, x: np.ndarray):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def synth_once(client, text, voice, model, style):
    content = {"type": "text", "text": text}
    if style:
        content["annotations"] = [{"type": "speech_metadata", "style": style}]
    it = client.interactions.create(
        model=model,
        input=[{"type": "user_input", "content": [content]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": voice}]},
    )
    raw = base64.b64decode(it.output_audio.data)
    if len(raw) < 2000:
        raise RuntimeError("回傳音訊過短（疑似空音訊）")
    return to_pcm(raw)


class DailyLimit(Exception):
    pass


def synth_retry(client, text, voice, model, style, tries=3):
    delay = 5
    for k in range(tries):
        try:
            return synth_once(client, text, voice, model, style)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "429" in msg and ("day" in msg.lower() or "daily" in msg.lower()):
                raise DailyLimit(msg[:200])
            print(f"    第 {k + 1} 次失敗：{msg[:160]}", flush=True)
            if k + 1 == tries:
                raise
            time.sleep(delay)
            delay *= 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid")
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true", help="忽略快取重新生成（重骰）")
    a = ap.parse_args()
    load_env()
    from google import genai
    client = genai.Client()

    spec = load_script(a.vid)
    voices = json.loads((ROOT / "config/voice.json").read_text())
    od = out_dir(a.vid) / "audio"
    (od / "cache").mkdir(parents=True, exist_ok=True)
    rep_path = od / "report.json"
    rep = json.loads(rep_path.read_text()) if rep_path.exists() else {}
    only = set(filter(None, a.only.split(",")))

    sents = [s for sc in spec["scenes"] for s in sc["sentences"]]
    todo = [s for s in sents if not only or s["id"] in only]
    t0, n_new = time.time(), 0
    for s in todo:
        v = voices[s.get("speaker", "narrator")]
        text = s.get("say") or s["display"]
        style = s.get("style") or v.get("style", "")
        k = key_of(text, v["voice"], v["model"], style)
        cache = od / "cache" / f"{k}.wav"
        if a.force and (not only or s["id"] in only):
            cache.unlink(missing_ok=True)
        if not cache.exists():
            print(f"  {s['id']}：{text[:30]}…", flush=True)
            try:
                x = trim(synth_retry(client, text, v["voice"], v["model"], style))
            except DailyLimit as e:
                rep_path.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
                sys.exit(f"碰到每日上限，已存檔；重置後再跑同一個指令會從 {s['id']} 接續。({e})")
            except Exception as e:  # noqa: BLE001
                rep_path.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
                sys.exit(f"{s['id']} 連續失敗 3 次，停下來回報使用者。最後的錯誤：{str(e)[:300]}")
            write_wav(cache, x)
            n_new += 1
        with wave.open(str(cache)) as w:
            dur = w.getnframes() / w.getframerate()
        target = od / f"{s['id']}.wav"
        target.write_bytes(cache.read_bytes())
        rep[s["id"]] = {"key": k, "dur": round(dur, 3), "text": text, "voice": v["voice"], "model": v["model"], "style": style}
    rep_path.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    total = sum(rep[s["id"]]["dur"] for s in sents if s["id"] in rep)
    print(f"完成：新生成 {n_new} 句，用時 {time.time() - t0:.0f} 秒；旁白總長 {total:.1f} 秒（不含停頓）")


if __name__ == "__main__":
    main()
