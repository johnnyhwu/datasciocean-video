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

### 視覺語言（v2，2026-11-07 使用者定案：要像 3Blue1Brown 一樣專業）

v001 第一版被使用者評為「字太大、畫面空、像小學生做的動畫」。原因與規則：

| 不要（v1 的問題） | 要 |
|---|---|
| 到處是粗體大字＋膠囊框（`pill`）、徽章、印章 | 一般文字用 `T`（Regular）；標籤直接貼在物件旁邊；`pill` 只在真的需要「按鈕／方塊」語意時用 |
| 用表格、方框排行榜講機制 | 用圖講：數線、點、連線、長條、位置變化（例：三欄名次連線圖） |
| 內容擠在上半部，下半部空 | 一個**大的中心視覺**佔滿主畫面，垂直置中在主畫面區（v3 起由程式檢查） |
| 公式用黑體文字排（「1/63 + 1/63」） | 公式與數字用 `M()`（襯線 STIX Two，變數 `italic=True`），分數用 `fraction()` |
| 每個動作都 pop/boing | 音效只留給真正的轉折（翻牌、超車、拉直成「！」）；一般出現不配音效 |
| 「示意」「依卡上公式計算」做成膠囊 | `tag()`／`note()`：小字＋細底線 |

- 字級：註記 0.038；標籤 0.04～0.045；公式與重點數字 0.055～0.075；超過 0.08 只給畫面上唯一的主角數字。
- 線條 2～3px，次要連線用 `LINE` 色、低不透明度；主角線條用亮色加粗。
- 動作偏「變形」：`Transform`、`ReplacementTransform`、位置移動，少用彈出（`pop_in`）。
- 吉祥物錘錘出場時放大（scale 0.35 以上），表情小，所以要靠動作：`hop()`（擠壓伸展）、`nod()`、`shake_head()`、`tilt()`、`emote("？")`。只放在開場、招牌時刻、收尾，以及少數插話。

### 視覺語言 v4：一張大圖（2026-11-08，使用者：「還是粗糙，離 3b1b 的精緻順暢差一大截」）

**這一節優先於下面的 v2、v3。** v3 只採用了外部 skill 的表層規則，v4 採用的是它們的結構做法。研究見 `rules/from-skills/README.md`，範例是 `videos/v001-rrf-rank-fusion/scenes.py` 和 `design-v4.md`。

- **整支片是同一張大圖**，鏡頭跟著走（`self.cam(點, 寬度)`、`self.cam_set()`；`Timed.view()` 會把點放在主畫面中心）。
  - 機制本身就是一張圖（管線、流程、座標系），一站一站畫出來，最後拉到全景。
  - 不用章節卡、角落章節標籤、進度條（`Timed.CARDS = HUD = False`）。章節只寫進 YouTube 說明欄。
- **場景之間看不出接縫**：每場開頭用 builder 函式直接擺出上一場最後一格（`cam_set` 加上同一組物件），`finish()` 預設不淡出。
  - `lib/checks/seams.py` 比對前一場最後一格和下一場第一格，最大區塊差 > 6 就報錯。
  - 收尾的顏色和透明度，要和下一場的 builder 一致。
- **畫面不放句子**：句子交給字幕。畫面只放公式、數字，以及貼在物件上的短標籤（6 字以內）。不要「結論列」。
- **動作語彙**：
  - 公式與數字用 `Write`，線用 `Create`，框用 `DrawBorderThenFill`；
  - 由別的東西變來的，用 `TransformFromCopy`／`ReplacementTransform`（例：名次從卡片上掉進分母）；
  - 同一組用 `LaggedStart`；`FadeIn` 只給殘影和小配角。
- **活的數字**：會變的量用 `ValueTracker` 驅動，讀數與長條每一格都依公式重算（`Live`、`always_redraw`）。不要寫死前後兩張圖。
- **背景**：`BG = "flat"`（平面深海色）。鏡頭移動時不會露出漸層的邊。
- **字級會跟著鏡頭縮放**：檢查會乘上 `FW / 鏡頭寬度`。要拉遠看全景，標籤就要用 0.05。
- **舉例不掛「示意」標籤**，旁白要說「假設」「我們來舉個例子」（使用者 2026-11-08）。「依卡上公式計算」照舊放在算式旁邊。
- **新的坑**：
  - 對 `Live` 或 `always_redraw` 物件做 `Transform` 會壞掉（點數不同）。要讓它出現，用 `Write`。
  - `Indicate(x, color=…)` 結束時會回到原本的顏色。要改色，另開一個 `x.animate.set_color()`。
  - 停留檢查只看被 `FadeOut` 這類動畫拿掉的物件；鏡頭移開不算拿掉。
  - 只有線的物件延伸到畫面外不算越界。文字和卡片不行：鏡頭推近時，要讓它們整個在畫面外，或先淡出。

### 視覺語言 v3：細節與節奏（2026-11-08，使用者：「還是粗糙」）

使用者具體指出三個問題：版面偏上、下方空著；線條蓋到別的東西；上一段最後介紹的東西太快被轉走。研究了三個外部 skill 之後的對策，見 `rules/from-skills/README.md`。以下由 `kit.Timed.check` 自動檢查，`layout-<場>.txt` 不是 OK 就要修：

| 檢查 | 規則 | 刻意例外 |
|---|---|---|
| 版面平衡 | 內容中心離主畫面中心 ≤ 12%（每場的「舞台」垂直置中；結論句放最底的結論列 `CAP_Y`） | 標成 `chrome` 的不算（章節標籤、示意、圖例） |
| 線穿過文字 | 細線（連線、軸、箭頭、錘錘的繩子）不能經過任何文字框 | 刪除線設 `cross_ok` |
| 線穿過圓點 | 線只能接在點上，不能從別的點中間穿過 | 數線設 `dots_ok` |
| 字壓字、實心重疊 | 文字或填色形狀之間不能部分重疊 | 刻意疊上去的（印章）設 `overlap_ok` |
| 停留 | 元素出現後至少停 1.5 秒才能拿掉 | 一閃而過的設 `transient` |
| 收尾停留 | 每場最後一個動作結束後，至少停 2 秒才開始轉場 | 沒有。場景後置留白設 2～3 秒（`script.json` 的 `pad`） |

寫法：

- **舞台**：一場一張大圖，佔滿主畫面（y 約 3.3 ～ -2.2）。左上角的章節標籤上方不放東西，錘錘的繩子也不能經過它。
- **結論列**：一場的結論、條件、換句說法都放在 `CAP_Y`，用 `ReplacementTransform` 換句，不要另開位置。
- **線**：用 `link()`（兩端各留 gap）或 `curve()`，只接在點上。標籤放在線的另一側。一個節點有好幾條線進來時，標籤放在沒有線的那一側；連最左邊節點的標籤放在它的左邊。
- **換內容**：優先讓同一個物件變形（牌延伸成欄、線改接新目標），少用整片淡出再淡入。同一組元素用 `LaggedStart` 錯開一拍。
- **轉場**：`finish()` 會自動處理：內容淡出，下一章章名在正中寫出。下一場開頭呼叫 `self.open_chapter()`，把章名縮成左上角標籤。
- **坑**：
  - 曲線不要用 `.set_opacity()` 調淡：它會連填色一起打開，變成色塊。要用 `set_stroke(opacity=…)`。
  - 不要用 `self.add(子群組)` 把某個群組的一部分加成頂層：原本的群組會被拆散。要調整一部分時，用 `*[m.animate… for m in 部分]`。
  - `Text.text` 會去掉空白，不能拿來重建字串。

### 版面

- 畫面分四區（v3）：安全邊界、主畫面區（上方 6～78%）、條件標註區（78～82%）、字幕區（82～95%，動畫不能進去）。
- 用 `cell(r, c)` 在 6×6 格線上定位，不要自己填座標。中文長句用 `wrap()` 自動換行。
- 字級用畫面高度比例（2026-11-07 手機校準）。`T/B` 低於 0.038 會報錯；條件標註與小標籤 0.038、一般標籤 0.04～0.045、重點數字 0.06～0.14。概念色最多 5 個；橘、粉不要和「錯誤」紅用在同一個畫面。
- 畫面文字少而短，多用數字、公式、符號、圖示。英文配音的觀眾看不懂中文字。
- 示意的數字、例子：v4 起不掛 `tag("示意")`，由旁白交代是舉例（`claims.py` 檢查）。

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

1. **先看程式的版面檢查**（`out/<id>/layout-<場>.txt`）。不是 OK 就先修。它每個 `at()` 之後檢查三件事：
   - 越界：超出安全邊界或壓到字幕區；
   - **元素重疊**：兩個頂層元素部分重疊 4%～85%（完全包含不算，例如框住的字）。刻意的重疊（印章蓋上去）在物件上設 `overlap_ok = True`；
   - **實際字級**：字被 `scale` 縮到低於下限也會被抓。
2. 程式通過後，**派視覺檢查員**（`.claude/agents/visual-checker.md`）。每場只給它：這張縮圖表，加上這場的規格摘要（旁白句子、這場要讓觀眾懂什麼、概念色對照、哪些是舉例）。
3. 依它的結構化判定修，**每場最多 2 輪**，還不過就列進審查包。
4. 渲染同一場失敗 3 次就停下來回報。不要換成投影片式的畫面。

全部場景通過後：

```bash
uv run python lib/checks/seams.py <id>      # 場景接縫（480p 渲染後就可以先跑）
uv run python lib/render.py <id> -q h       # 1080p30，並串接成 out/<id>/video.mp4
uv run python lib/checks/still.py <id>                      # 超過 4 秒不動的段落
```

靜止段落補上小動作（Indicate、輕晃、數字滾動），但小動作也要有目的。只重渲改過的場景：`--scenes`。

## 完成

`state.py set <id> 合成`，載入 `assemble`。
