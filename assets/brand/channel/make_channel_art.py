"""頻道頭像（800×800）與橫幅（2560×1440，所有裝置都看得到的安全區 1546×423 在正中間）。
uv run python assets/brand/channel/make_channel_art.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
BOLD = str(ROOT / "assets/fonts/NotoSansCJKtc-Bold.otf")
REG = str(ROOT / "assets/fonts/NotoSansCJKtc-Regular.otf")

# 頭像：logo 的海和錘錘，不放字（頭像在手機上只有約 40px，字看不到）
logo = Image.open(ROOT / "assets/brand/logo.png").convert("RGB")
logo.crop((337, 520, 917, 1100)).resize((800, 800), Image.LANCZOS).save(OUT / "avatar.png")

# 橫幅
W, H = 2560, 1440
deep, beige, gold = (3, 32, 39), (242, 224, 192), (221, 166, 66)
img = Image.new("RGB", (W, H), deep)
d = ImageDraw.Draw(img)
cols = [(105, 180, 170), (54, 163, 161), (30, 136, 144), (16, 112, 124), (10, 90, 102), (7, 70, 82), (5, 52, 62)]
xs = np.linspace(0, W, 300)
rng = np.random.default_rng(3)
for i, c in enumerate(cols):
    ph = rng.uniform(0, 6.28)
    y0 = 1010 + i * 64
    ys = y0 + 18 * np.sin(xs / 260 + ph) + 8 * np.sin(xs / 97 + ph * 2)
    d.polygon(list(zip(xs, ys)) + [(W, H), (0, H)], fill=c)
# 錘錘的光：海面下一團金光
glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse((W / 2 - 200, 1120, W / 2 + 200, 1420), fill=120)
glow = glow.filter(ImageFilter.GaussianBlur(90))
img = Image.composite(Image.new("RGB", (W, H), gold), img, glow)
d = ImageDraw.Draw(img)
# 安全區（1546×423，置中）：頻道名＋一句話
cy = H / 2
t1 = ImageFont.truetype(BOLD, 150)
t2 = ImageFont.truetype(REG, 62)
d.text((W / 2, cy - 70), "DataSci Ocean", font=t1, fill=beige, anchor="mm")
d.text((W / 2, cy + 95), "用動畫，把一篇 AI 論文的核心機制講清楚", font=t2, fill=gold, anchor="mm")
img.save(OUT / "banner.png")
print("ok")
