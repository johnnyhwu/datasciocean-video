"""旁白回聽檢查：每句音檔用 Whisper 轉回文字，和唸法稿比對。

比對規則來自 datasciocean-podcast 的 pipeline/verify.py（同一位使用者的專案，實戰驗證過）。
- 模型（走 mlx_audio，不需要 torch；權重在本機共用的 ~/.cache/huggingface，設 HF_HUB_OFFLINE=1 不連網）：
  - 預設 qwen：mlx-community/Qwen3-ASR-1.7B-bf16（Apache-2.0，中文與中英混雜比 Whisper 準；使用者 2026-11-10 要求換強一點的）。
    hotwords 只放專有名詞（Cerebras、reranker…），不放整句稿子，否則等於把答案告訴它，念錯也聽不出來。
  - --model whisper：openai/whisper-large-v3-turbo（podcast 用的）。temperature=0、condition_on_previous_text=False、
    hallucination_silence_threshold=2.0 三個一起設，否則會自己編字（「請訂閱轉發打賞」）。
- **STT 是篩選器，不是判官**：低分只代表「這句要人耳確認」，不代表 TTS 一定念錯。同音字不算錯。

用法：uv run python lib/checks/stt.py <影片 ID> [--only h1,h2]
輸出：out/<id>/audio/stt.json；有標記的句子列出來，exit 1。
"""
import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import out_dir  # noqa: E402

os.environ.setdefault("HF_HUB_OFFLINE", "1")
MODELS = {"qwen": "mlx-community/Qwen3-ASR-1.7B-bf16", "whisper": "openai/whisper-large-v3-turbo"}


def hotwords(rep):
    """稿子裡出現的英文專有名詞（每支影片自動取），只給名詞、不給句子。"""
    words = {w.strip() for r in rep.values() for w in re.findall(r"[A-Za-z][A-Za-z0-9]*(?: [A-Z][A-Za-z0-9]*)*", r["text"])}
    return sorted(w for w in words if len(w) > 1)
# 語速和「這支影片的中位數」比，不用 podcast 的絕對門檻（4.0～9.5 字/秒）：
# podcast 是長段落、預設聲音；影片是短句、使用者的複製聲音（中位數約 4.1），用絕對門檻會把一半的句子誤標成偏慢（v001 實測）。
SPEED_REL = (0.6, 1.6)
LONG_PAUSE = 1.0   # 句中靜音超過 1 秒才算失控（短句的標點停頓約 0.3～0.45 秒）

_CC = None
_NUM = {"零": "0", "一": "1", "二": "2", "兩": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}


def _trad(s):
    global _CC
    if _CC is None:
        from opencc import OpenCC
        _CC = OpenCC("s2twp")
    return _CC.convert(s)


def _zh_digits(s):
    """十五 → 15、零點八三 → 0.83、萬/千/百保留原字（Whisper 寫 15,000 時另外處理千分位）。"""
    def rep(m):
        t = m.group(0)
        if t == "十":
            return "10"
        if "十" in t:
            a, b = t.split("十")
            return (_NUM.get(a, "1") if a else "1") + (_NUM.get(b, "0") if b else "0")
        return "".join(_NUM.get(c, c) for c in t)
    s = re.sub(r"[零一二兩三四五六七八九]?十[零一二兩三四五六七八九]?|[零一二兩三四五六七八九]+", rep, s)
    s = s.replace("百分之", "%").replace("點", ".")
    return re.sub(r"(\d+)分之(\d+)", r"\2/\1", s)


def norm(s):
    """只留『字有沒有念對』：簡繁、數字寫法、標點空白、大小寫都拉齊。"""
    s = _trad(s)
    s = re.sub(r"(?<=\d),(?=\d)", "", s)
    s = re.sub(r"(?<!\d)\.(?!\d)", "", s)
    s = re.sub(r"[,，。、!！?？:：;；(（)）\[\]「」『』\"'\s—~…＋+]", "", s)
    s = re.sub(r"[-負]", "", s)
    s = _zh_digits(s)
    s = re.sub(r"%(\d+(?:\.\d+)?)", r"\1%", s)
    return s.lower()


def longest_pause(wav):
    """句中最長的靜音（秒），頭尾不算。"""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(str(wav))
    hop = int(sr * 0.02)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x) - hop, hop)])
    on = 20 * np.log10(e) > -40
    idx = np.where(on)[0]
    if len(idx) < 2:
        return 0.0
    gaps = np.diff(idx) - 1
    return float(gaps.max() * hop / sr)


def leaks_prompt(style, got, expected):
    """語氣提示被 TTS 念出來了（提示原句出現在轉錄裡，稿子卻沒有）。"""
    st = norm(style)
    if not st:
        return False
    m = difflib.SequenceMatcher(None, st, got, autojunk=False).find_longest_match(0, len(st), 0, len(got))
    return m.size >= min(8, len(st)) and st[m.a:m.a + m.size] not in expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid")
    ap.add_argument("--only", default="")
    ap.add_argument("--model", choices=list(MODELS), default="qwen")
    a = ap.parse_args()
    od = out_dir(a.vid) / "audio"
    rep = json.loads((od / "report.json").read_text())
    only = set(filter(None, a.only.split(",")))
    res_path = od / "stt.json"
    res = json.loads(res_path.read_text()) if res_path.exists() and only else {}

    from mlx_audio.stt.utils import load_model
    stt = load_model(MODELS[a.model])
    kw = (dict(language="Chinese", temperature=0.0, hotwords=hotwords(rep)) if a.model == "qwen" else
          dict(language="zh", temperature=0.0, condition_on_previous_text=False, hallucination_silence_threshold=2.0))
    for sid, r in rep.items():
        if only and sid not in only:
            continue
        g = stt.generate(str(od / f"{sid}.wav"), **kw)
        got = g.text if hasattr(g, "text") else str(g)
        x, y = norm(r["text"]), norm(got)
        sm = difflib.SequenceMatcher(None, x, y, autojunk=False)   # autojunk 一定要關，否則長句分數崩掉
        ratio = sm.ratio()
        cps = len(x) / r["dur"] if r["dur"] else 0
        pause = longest_pause(od / f"{sid}.wav")
        flags = []
        if pause > LONG_PAUSE:
            flags.append(f"長停頓{pause:.1f}秒")
        if ratio < 0.90:
            flags.append("STT差異大")
        if len(y) > len(x) * 1.15:
            flags.append("疑似幽靈音")
        if leaks_prompt(r.get("style", ""), y, x):
            flags.append("提示洩漏")
        diffs = [f"「{x[i1:i2]}」→「{y[j1:j2]}」" for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
        res[sid] = {"text": r["text"], "heard": got.strip(), "sim": round(ratio, 3), "cps": round(cps, 2), "pause": round(pause, 2), "model": a.model,
                    "diffs": diffs[:8], "flags": flags}
    med = sorted(v["cps"] for v in res.values())[len(res) // 2]
    for sid, v in res.items():
        v["flags"] = [f for f in v["flags"] if f not in ("偏慢", "過快")]
        if v["cps"] < med * SPEED_REL[0]:
            v["flags"].append("偏慢")
        elif v["cps"] > med * SPEED_REL[1]:
            v["flags"].append("過快")
        if only and sid not in only:
            continue
        mark = "○" if not v["flags"] else "⚠ " + ",".join(v["flags"])
        print(f"{sid:5s} {v['cps']:4.1f}字/秒 停頓{v['pause']:.1f} sim={v['sim']:.3f} {mark}"
              + (f"  {' '.join(v['diffs'][:3])}" if v['sim'] < .97 else ""), flush=True)
    print(f"語速中位數 {med:.2f} 字/秒；偏慢 < {med * SPEED_REL[0]:.2f}、過快 > {med * SPEED_REL[1]:.2f}")
    res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    bad = [k for k, v in res.items() if v["flags"]]
    avg = sum(v["sim"] for v in res.values()) / max(1, len(res))
    print(f"\n{len(res) - len(bad)}/{len(res)} 句無標記，平均 sim={avg:.3f}")
    if bad:
        print("需要人耳確認：" + ", ".join(bad))
        sys.exit(1)


if __name__ == "__main__":
    main()
