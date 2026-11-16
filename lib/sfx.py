# 音效產生器（numpy 合成，沒有外部素材、沒有授權問題）。來源：PoC final_xhigh v4/sfx.py，2026-11-06 複製。
# 每個音效要對應一個畫面事件（規格 §7.5）。
"""Procedural sound effects (numpy only). sfx.make(kind) -> float32 mono @ SR."""
import numpy as np
SR = 48000
rng = np.random.default_rng(7)

def env(n, a=0.003, d=0.1):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR)); e[:na] *= np.linspace(0, 1, na)
    return e

def tone(f0, f1, dur, d, harm=(1,), amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(ph * h) / (k + 1) for k, h in enumerate(harm))
    return amp * x * env(n, 0.002, d)

def noise(dur, lo, hi, d, a=0.005):
    n = int(dur * SR); x = rng.standard_normal(n)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    X[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(X, n) * env(n, a, d)

def sweep_noise(dur, f0, f1, q=0.25):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n)
    seg = 1024
    for i in range(0, n, seg):
        c = f0 * (f1 / f0) ** (i / n)
        X = np.fft.rfft(x[i:i + seg]); fr = np.fft.rfftfreq(len(x[i:i + seg]), 1 / SR)
        X *= np.exp(-((np.log(fr + 1) - np.log(c)) ** 2) / (2 * q ** 2))
        out[i:i + seg] = np.fft.irfft(X, len(x[i:i + seg]))
    w = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return out * w

def add(*xs):
    n = max(len(x) for x in xs); out = np.zeros(n)
    for x in xs: out[:len(x)] += x
    return out

def make(kind):
    k = {"knob": "click", "bell": "chime"}.get(kind, kind)   # 只有錄音檔的種類，沒有檔案時的替代
    if k == "pop":    x = add(tone(900, 380, 0.12, 0.035, (1, 2)), 0.3 * noise(0.03, 2000, 6000, 0.008))
    elif k == "tick": x = tone(2400, 2200, 0.05, 0.012) * 0.6
    elif k == "click": x = add(noise(0.04, 1500, 7000, 0.006) * 0.8, tone(1500, 1400, 0.04, 0.01) * 0.4)
    elif k == "thud": x = add(tone(140, 55, 0.4, 0.12, (1, 2)) * 1.3, noise(0.08, 80, 900, 0.03) * 0.8)
    elif k == "ding": x = tone(1320, 1320, 1.2, 0.35, (1, 2.76, 5.4)) * 0.7
    elif k == "chime":
        x = np.zeros(int(1.4 * SR))
        for i, f in enumerate([1047, 1319, 1568, 2093]):
            y = tone(f, f, 1.0, 0.3, (1, 2.76)) * 0.45; o = int(i * 0.07 * SR); x[o:o + len(y)] += y
    elif k == "boing":
        n = int(0.45 * SR); t = np.arange(n) / SR
        f = 260 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / 0.2)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.18)
    elif k == "crunch":
        x = np.zeros(int(0.7 * SR))
        for i in range(14):
            y = noise(0.06, 800, 9000, 0.015) * rng.uniform(0.4, 1); o = int(rng.uniform(0, 0.55) * SR); x[o:o + len(y)] += y
        x += noise(0.7, 60, 500, 0.15) * 0.6
    elif k == "whoosh": x = sweep_noise(0.45, 400, 3500) * 2.2
    elif k == "swoosh": x = sweep_noise(1.2, 200, 5000, 0.3) * 2.2
    elif k == "rise":
        x = tone(300, 900, 0.7, 10, (1, 2)) * np.sin(np.linspace(0, np.pi, int(0.7 * SR))) * 0.45
    elif k == "slide":
        n = int(1.0 * SR); x = tone(220, 330, 1.0, 10, (1, 3)) * np.sin(np.linspace(0, np.pi, n)) * 0.25
    elif k == "scratch": x = sweep_noise(0.25, 3000, 900, 0.4) * 2.5
    elif k == "buzz":
        n = int(0.35 * SR); t = np.arange(n) / SR
        x = np.sign(np.sin(2 * np.pi * 110 * t)) * env(n, 0.005, 0.15) * 0.35
    else: raise KeyError(kind)
    x = np.asarray(x, dtype=np.float64)
    return (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32)

KINDS = ["pop", "tick", "click", "thud", "ding", "chime", "boing", "crunch", "whoosh", "swoosh", "rise", "slide", "scratch", "buzz"]
if __name__ == "__main__":
    for k in KINDS: print(k, len(make(k)) / SR)
