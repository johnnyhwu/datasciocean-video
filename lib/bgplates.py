"""產生品牌背景板（1920×1080 PNG）：深海漸層＋幾層很淡的海浪色帶＋一處金色微光＋暗角＋防色階抖動。

用法：uv run python lib/bgplates.py   → out/_assets/bg/<名稱>.png（不進 git，kit.py 缺檔時自動產生）

品牌哲學「深處的光」（rules/from-social-media/brand-and-layouts.md §2）：背景越往下越深，金光只是氛圍，
不能搶走畫面上唯一的金色重點，所以亮度壓得很低。每支影片可以換不同的背景板（反模板）。
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
W, H = 1920, 1080


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


SEA, ABYSS, TEAL, GOLD = hex2rgb("#01353F"), hex2rgb("#032027"), hex2rgb("#1F8A8D"), hex2rgb("#DDA642")


def plate(glow=(0.5, 0.62), glow_r=0.35, glow_a=0.10, waves=0.035, wave_phase=0.0, seed=0, tilt=0.0):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = x / W, y / H
    # 上淺下深
    g = np.clip(v + tilt * (u - 0.5), 0, 1)[..., None]
    img = SEA * (1 - g) + ABYSS * g
    # 海浪色帶：幾條很淡的正弦帶，越下面越淡
    for k in range(5):
        yy = 0.18 + k * 0.17 + 0.02 * np.sin(2 * np.pi * (u * (1.3 + 0.2 * k) + wave_phase + k * 0.37))
        band = np.exp(-((v - yy) / 0.012) ** 2) * (waves * (1 - k * 0.15))
        img = img + band[..., None] * (TEAL - img)
    # 金色微光
    d = np.sqrt(((u - glow[0]) * W / H) ** 2 + (v - glow[1]) ** 2)
    a = glow_a * np.exp(-(d / glow_r) ** 2)
    img = img + a[..., None] * GOLD  # 加光（screen 式），維持暖色，不和藍綠混成橄欖色
    # 暗角
    vig = 1 - 0.35 * np.clip(np.sqrt(((u - 0.5) * 1.2) ** 2 + (v - 0.5) ** 2) - 0.25, 0, 1)
    img = img * vig[..., None]
    # 抖動，避免色階
    rng = np.random.default_rng(seed)
    img = img + rng.uniform(-1.2, 1.2, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


PLATES = {
    "abyss": dict(glow=(0.5, 0.78), glow_a=0.07),
    "glow_center": dict(glow=(0.5, 0.5), glow_a=0.10, glow_r=0.4),
    "glow_left": dict(glow=(0.22, 0.6), glow_a=0.09, wave_phase=0.3),
    "glow_right": dict(glow=(0.78, 0.6), glow_a=0.09, wave_phase=0.6),
    "calm": dict(glow=(0.5, 0.9), glow_a=0.05, waves=0.02),
    "currents": dict(glow=(0.65, 0.35), glow_a=0.06, waves=0.06, tilt=0.25, wave_phase=0.15),
}

def ensure(name):
    f = ROOT / "out/_assets/bg" / f"{name}.png"
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        plate(seed=list(PLATES).index(name), **PLATES[name]).save(f)
    return f


if __name__ == "__main__":
    out = ROOT / "out/_assets/bg"
    out.mkdir(parents=True, exist_ok=True)
    for i, (name, kw) in enumerate(PLATES.items()):
        plate(seed=i, **kw).save(out / f"{name}.png", optimize=True)
        print(name)
