"""一次性：用使用者的錄音建立 Gemini 複製聲音（store=True，取得永久 voice_… ID）。

用法：uv run python lib/voice_create.py assets/voice/reference.wav assets/voice/consent.wav

- 兩段錄音放 assets/voice/（已在 .gitignore，不進 git）。同一支麥克風、同一個環境。
- reference：10～30 秒乾淨、自然的朗讀。consent：唸官方同意聲明（中文只有簡體版，見 rules/external-rules.md）。
- 程式會先轉成 24 kHz 單聲道 16-bit WAV 再上傳（官方建議格式）。
- 成功後把 voice ID 寫進 config/voice.json 的 narrator。voice ID 不是秘密，但只能在這個 Google Cloud 專案使用。
"""
import base64
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import ROOT, ffmpeg  # noqa: E402
from tts_gemini import load_env  # noqa: E402


def to_24k(path: str) -> str:
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-ac", "1", "-ar", "24000", "-sample_fmt", "s16", "-f", "wav", "-"],
                       capture_output=True, check=True)
    return base64.b64encode(r.stdout).decode()


def main():
    ref, consent = sys.argv[1:3]
    load_env()
    from google import genai
    client = genai.Client()
    v = client.voices.create(store=True, voice={
        "model": "gemini-3.8-flash-tts", "type": "replicated", "display_name": "DataSci Ocean narrator",
        "replicated": {"source_audio": {"mime_type": "audio/wav", "data": to_24k(ref)},
                       "consent_audio": {"mime_type": "audio/wav", "data": to_24k(consent)}}})
    cfg_path = ROOT / "config/voice.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["narrator_cloned"] = {"voice": v.id, "model": "gemini-3.8-flash-tts", "style": cfg["narrator"].get("style", "")}
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    print(f"建立成功：{v.id}（寫入 config/voice.json 的 narrator_cloned；盲聽定案後再換成 narrator）")


if __name__ == "__main__":
    main()
