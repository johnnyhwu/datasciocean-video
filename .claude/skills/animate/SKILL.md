---
name: animate
description: 影片第 6 步「動畫」：用 ManimCE 與 lib/kit.py 逐場寫動畫程式，錨定在旁白時間上；低畫質渲染→版面檢查→縮圖表→視覺檢查員→修正，最後 1080p。
---

# 第 6 步：動畫

先讀 `lib/kit.py` 開頭的說明。PoC 的範例在 `rules/from-poc/02_TECHNICAL_GUIDE.md` §8，坑在 `04_LESSONS_LEARNED.md` §三、§四。

## 工具

- **ManimCE 0.22.1**（Cairo），透過 `lib/kit.py`。環境見 `docs/setup.md`（從零建立用 `scripts/setup.sh`）。
- 畫靜態圖（草圖、縮圖、吉祥物）不需要影片：不設 `YTV_VIDEO` 就是設計模式，
  `PYTHONPATH=lib uv run python -m manim -qh -s <檔案> <場景>`。
- 不混用 ManimGL 的 API。不複製或改作 3b1b/videos 的程式碼。
- 要試其他工具（Remotion、HyperFrames、three.js）可以，但要限定時間與範圍、寫進 `experiments/`、用同一個題材比較，最後由使用者決定。

## 寫法

場景寫在 `videos/<id>/scenes.py`，可以分成多個 `scenes_*.py`。類別名＝場景 ID 首字大寫：

```python
from kit import *

class Sc03(Timed):
    SID = "sc03"; BG = "glow_left"
    def construct(self):
        self.add(self.chapter_tag(2, "名次，不是分數"))
        self.card_out()
        big = B("RRF", 0.11, C["名次"]).move_to(cell(0, 1, 0, 4))
        self.at(self.A("c1", 0.6), pop_in(big), run_time=0.4, sfx="pop")
        ...
        self.finish()
```

### 動作紀律（視覺檢查員會檢查）

- **每一個移動、變色、出現，都要錨在某一句旁白上**（`A(句 id, 比例)`）。標不出對應哪一句，就刪掉。
- 同一時間畫面只有一個焦點。
- 動畫不演和旁白不同的事。
- 不讓公式或文字無意義地移來移去。

### 版面

- 畫面分四區：安全邊界、主畫面區（上方 74%）、條件標註區（74～80%）、字幕區（80～95%，動畫不能進去）。
- 用 `cell(r, c)` 在 6×6 格線上定位，不要自己填座標。中文長句用 `wrap()` 自動換行。
- 字級用畫面高度比例。`T/B` 低於 0.03 會報錯；一般標籤 0.03～0.045，重點數字 0.06～0.14。
- 畫面文字少而短，多用數字、公式、符號、圖示。英文配音的觀眾看不懂中文字。
- 示意的數字、例子、重畫的估讀圖，都要掛 `tag("示意")`。

### 配色

- 背景是品牌深海色；換背景板用 `BG = "abyss" | "glow_center" | "glow_left" | "glow_right" | "calm" | "currents"`。
- 同一概念全片同色（`C["概念"]`），公式和圖形裡的同一個量也同色。
- 每支影片 4～5 個概念色，其餘用中性色。
- **金色只給最重要的一個元素。**
- 不只靠顏色傳達資訊，同時用形狀、標籤或位置區別。

### 角色

- 吉祥物錘錘 `Plumb(scale).place(點)`（設計與示範：`docs/mascot/`，`plumb-demo.gif`）。
  - 招牌：好奇時 `curl()` 讓繩子捲成「？」；想通時 `straighten()` 拉直成「！」，再加 `light_on()`。
  - 指標：`point_at(點)` 用尖端指重點，`upright()` 回正。收尾：`dive()`、`sample_on()`，接 `takeaway_card([...])`。
  - 表情：`mood("neutral|happy|flat|wow|squint")`、`look(方向)`、`blink()`。所有動作都回傳 list，用 `self.at(t, *p.curl(), ...)`。
  - 有台詞時，script 的 `speaker` 寫 `mascot`，場景裡呼叫 `self.lipsync(plumb)`。
- 機制角色寫在這支影片自己的 scenes 檔裡。通用而且證明好用的，回顧時再收進 `kit.py`。

### PoC 的技巧與坑

- 物理系統用 `ValueTracker` 加 `always_redraw`；兩個量連動用 `UpdateFromAlphaFunc`。
- 鏡頭推近時：`self.camera.frame.animate…`，並把 `self.zone_check = False`。
- 自訂屬性不要叫 `color`、`width`、`height`，會和 Manim 的屬性衝突，改用 `tint` 這類名字。
- 移除群組用 `self.remove(*group)`。
- 不要對子物件下 `.animate`，會被提到最上層；對整組用 `Indicate`。
- 傳 list 給 `FadeIn` 要先包成 `VGroup`。
- 長動畫會擠到下一個 `at()`。晚 0.1～0.4 秒可以接受，超過 0.5 秒要修。
- 改了腳本的句子 ID 後，先 grep 所有 `A("…")` 用到的 ID。

## 迴圈（每 2～3 場一輪）

```bash
uv run python lib/render.py <id> -q l --scenes sc01,sc02   # 480p，同時寫版面檢查
uv run python lib/checks/sheet.py <id> sc01                               # 每句結束的畫面拼成一張
```

1. **先看程式的版面檢查**（`out/<id>/layout-<場>.txt`）。不是 OK 就先修。
2. 程式通過後，**派視覺檢查員**（`.claude/agents/visual-checker.md`）。每場只給它：這張縮圖表，加上這場的規格摘要（旁白句子、這場要讓觀眾懂什麼、概念色對照、示意清單）。
3. 依它的結構化判定修，**每場最多 2 輪**，還不過就列進審查包。
4. 渲染同一場失敗 3 次就停下來回報。不要換成投影片式的畫面。

全部場景通過後：

```bash
uv run python lib/render.py <id> -q h       # 1080p30，並串接成 out/<id>/video.mp4
uv run python lib/checks/still.py <id>                      # 超過 4 秒不動的段落
```

靜止段落補上小動作（Indicate、輕晃、數字滾動），但小動作也要有目的。只重渲改過的場景：`--scenes`。

## 完成

`state.py set <id> 合成`，載入 `assemble`。
