"""Gemini 花費帳本（目前只有 TTS 會記帳）。
使用者 2026-11-21：標題和頻道說明由 Claude 寫，Gemini 只做 TTS。generate() 保留，但現在沒有用到。

用法：
  uv run python lib/gemini.py cost <影片 ID>            # 這支影片的 Gemini 總花費（TTS＋LLM），逐項列出
  uv run python lib/gemini.py backfill-tts <影片 ID>    # 補記：還沒有帳本時，用快取音檔的長度估 TTS 花費

在程式裡：
  from gemini import generate, log_usage
  text = generate(prompt, vid="v002-…", note="標題候選", schema={...})   # 回傳文字（有 schema 時是 JSON 字串）

- 帳本：videos/<id>/gemini-usage.jsonl，每次呼叫一行（模型、用途、輸入／輸出 token、美元）。tts_gemini.py 每合成一句也記一行。
- 頻道層級的呼叫（例如頻道說明）記在 state/gemini-usage.jsonl。
- 價格（每 100 萬 token，美元；2026-11-21 查 Google Cloud 價目表與第三方整理）：
  gemini-3.8-flash      輸入 0.75、輸出 3.75（思考 token 算輸出）；2027-01-01 起 1.50／7.50
  gemini-3.8-flash-tts  文字輸入 0.50、音訊輸出 9.00（音訊 25 token／秒）；2027-01-01 起 1.00／18.00
  每季跟 rules/external-rules.md 一起重查。
- 金鑰：GEMINI_API_KEY（.env）。不印出、不寫進任何檔案。
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths import ROOT  # noqa: E402

TEXT_MODEL = "gemini-3.8-flash"
AUDIO_TOK_PER_SEC = 25
PRICES = {  # (輸入, 輸出) 美元／100 萬 token；[2026 年底前, 2027-01-01 起]
    "gemini-3.8-flash": [(0.75, 3.75), (1.50, 7.50)],
    "gemini-3.8-flash-tts": [(0.50, 9.00), (1.00, 18.00)],
    "gemini-3.8-flash-lite-tts": [(0.25, 4.50), (0.50, 9.00)],
}


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("缺少 GEMINI_API_KEY（放在 .env；不要貼進對話）。")


def price(model, when=None):
    when = when or dt.date.today()
    tiers = PRICES.get(model)
    if not tiers:
        return None
    return tiers[0] if when < dt.date(2027, 1, 1) else tiers[1]


def ledger(vid):
    return (ROOT / "videos" / vid / "gemini-usage.jsonl") if vid else (ROOT / "state" / "gemini-usage.jsonl")


def log_usage(vid, model, kind, in_tok, out_tok, note="", estimated=False):
    p = price(model)
    usd = round((in_tok * p[0] + out_tok * p[1]) / 1e6, 6) if p else None
    row = {"time": dt.datetime.now().isoformat(timespec="seconds"), "kind": kind, "model": model,
           "in_tok": int(in_tok), "out_tok": int(out_tok), "usd": usd, "note": note}
    if estimated:
        row["estimated"] = True
    f = ledger(vid)
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return usd


def generate(prompt, vid=None, note="", schema=None, model=TEXT_MODEL, temperature=1.0):
    load_env()
    cfg = {"temperature": temperature}
    if schema:
        cfg["responseMimeType"] = "application/json"
        cfg["responseSchema"] = schema
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": cfg}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}")
    u = res.get("usageMetadata", {})
    out_tok = u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)
    usd = log_usage(vid, model, "llm", u.get("promptTokenCount", 0), out_tok, note)
    print(f"  Gemini {model}：輸入 {u.get('promptTokenCount', 0)}、輸出 {out_tok} token（含思考 {u.get('thoughtsTokenCount', 0)}），US${usd:.4f}")
    parts = res["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def tts_usage(res, text, seconds):
    """從 TTS 回應取 token 數；回應沒有就用字數與音訊長度估。回傳 (輸入, 輸出, 是否為估計)。"""
    u = res.get("usage") or res.get("usageMetadata") or {}
    i = u.get("total_input_tokens") or u.get("promptTokenCount") or u.get("input_tokens")
    o = u.get("total_output_tokens") or u.get("candidatesTokenCount") or u.get("output_tokens")
    if i and o:
        return int(i), int(o), False
    return max(1, len(text)), int(round(seconds * AUDIO_TOK_PER_SEC)), True


def cost(vid):
    rows = [json.loads(x) for x in ledger(vid).read_text().splitlines() if x.strip()] if ledger(vid).exists() else []
    if not rows:
        print(f"{vid} 還沒有帳本。舊影片先跑：uv run python lib/gemini.py backfill-tts {vid}")
        return
    agg = {}
    for r in rows:
        k = (r["kind"], r["model"])
        a = agg.setdefault(k, {"n": 0, "in": 0, "out": 0, "usd": 0.0, "est": False})
        a["n"] += 1
        a["in"] += r["in_tok"]
        a["out"] += r["out_tok"]
        a["usd"] += r["usd"] or 0
        a["est"] |= bool(r.get("estimated"))
    total = sum(a["usd"] for a in agg.values())
    print(f"{vid} 的 Gemini 花費")
    for (kind, model), a in agg.items():
        name = {"tts": "旁白 TTS", "llm": "文字生成"}.get(kind, kind)
        print(f"  {name}（{model}）：{a['n']} 次，輸入 {a['in']:,}、輸出 {a['out']:,} token，US${a['usd']:.3f}" + ("（含估計）" if a["est"] else ""))
    print(f"  合計 US${total:.3f}（約 NT${total * 32:.1f}，匯率以 32 估）")


def backfill_tts(vid):
    """快取資料夾裡每個音檔都是付過費的一次合成（含重骰）。音檔已修剪頭尾靜音，所以是略低的估計。"""
    if any(json.loads(x).get("kind") == "tts" for x in ledger(vid).read_text().splitlines() if x.strip()) if ledger(vid).exists() else False:
        sys.exit("帳本裡已經有 TTS 紀錄，不重複補記。")
    cache = ROOT / "out" / vid / "audio" / "cache"
    secs = []
    for f in sorted(cache.glob("*.wav")):
        with wave.open(str(f)) as w:
            secs.append(w.getnframes() / w.getframerate())
    if not secs:
        sys.exit(f"找不到 {cache} 的音檔。")
    rep = json.loads((ROOT / "out" / vid / "audio" / "report.json").read_text())
    chars = sum(len(r["text"]) for r in rep.values())
    model = next(iter(rep.values()))["model"]
    log_usage(vid, model, "tts", chars * len(secs) / max(1, len(rep)), sum(secs) * AUDIO_TOK_PER_SEC,
              f"補記：快取 {len(secs)} 個音檔共 {sum(secs):.0f} 秒（最終採用 {len(rep)} 句）", estimated=True)
    cost(vid)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cost", "backfill-tts"])
    ap.add_argument("vid")
    a = ap.parse_args()
    {"cost": cost, "backfill-tts": backfill_tts}[a.cmd](a.vid)
