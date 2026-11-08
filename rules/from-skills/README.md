# 從外部動畫 skill 學到的規則（2026-11-08）

使用者看完 v001 第二版後說：有變好，但還是**粗糙**。他具體指出三點：

1. 版面偏上，下方空間沒有好好用；
2. 線條常常蓋到其他視覺元素；
3. 換到下一段時，上一段最後介紹的東西太快被轉走，來不及吸收。

使用者請我研究三個 skill repo，有幫助的就拿來用。原文在 `vendor/`，都是 MIT 授權，各自附 LICENSE，平常不要載入：

| repo | commit | 內容 | 結論 |
|---|---|---|---|
| [cth9191/animate](https://github.com/cth9191/animate) | 7e5eb56 | 用單一 canvas 加 Playwright 做短動畫；附 story/frame grammar、math 風格（manim 式）、文字檢查工具 | **最有用**。拿了規則與「用程式檢查文字」的做法 |
| [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills) | 229022e | HTML 動態設計：16 種效果配方、Vox 式講解 | 拿了「同一個物件變形」「保留起點殘影」「錯開一拍」 |
| [artemnovitckii/claude-animation-skills](https://github.com/artemnovitckii/claude-animation-skills) | 5dbea55 | GSAP、three.js 模板（極簡線條、數字長條圖） | 只拿了美學：一張圖一個數字、沒有標籤膠囊 |

**為什麼不把 skill 直接裝進 `.claude/skills/`：**

- 三者都用 HTML、canvas 加 Node 或 Playwright 渲染，要全域安裝 `npm i -g playwright`。這違反「所有套件都裝在專案內」的硬性限制。
- 我們的管線是 ManimCE，並且以旁白時間為錨，所以引擎拿來也接不上。
- 因此做法是把規則轉寫成我們自己的規則，並把它們變成 `lib/kit.py` 的程式檢查。

## 採用的規則，以及落實的位置

### A. 版面：內容垂直置中，用滿主畫面（使用者的第 1 點）

- 來源：cth9191 FRAME.md 的「safe area and breathing room」與「Vary scale」；charlie947 的「Scale the effect up……not a small tile in a big empty canvas」。
- 做法：
  - `config/style.json` 的主畫面延伸到 78%（字幕單行頂端約 87%）；
  - `kit.Timed.check` 的**版面平衡**檢查：內容的中心偏離主畫面中心超過 12%、持續 1 秒以上，就記成問題；
  - 結論句一律放在主畫面最底的「結論列」（scenes 的 `CAP_Y`），所以下方一定會被用到；
  - 示意標籤放在結論列最右邊。

### B. 線不碰字、不穿點（使用者的第 2 點）

- 來源：cth9191 math STYLE.md 的「no label crossing a stroke」「Labels sit on the side of a segment away from the figure」；textcheck.mjs 的「Don't trust your eye for text」。
- 做法：kit 新增三項程式檢查。
  - **線穿過文字**：在每條細線上取樣 80 點，只要有點落進別人的文字框（含 0.06 的留白）就記錄。
  - **線穿過圓點**：線經過一個點，而這個點不是線的端點，就記錄。數線上的點設 `dots_ok`。
  - **字壓字**：兩段文字的框重疊。
- 錘錘的繩子也要檢查（`rope_check`），它不能穿過章節標籤。
- 刻意的情況要標：刪除線設 `cross_ok`；數線設 `dots_ok`。
- 重疊檢查改成比對「實心部件」（文字、填色形狀），不再比整組的外框，以減少誤報。

### C. 每段看夠了才轉場（使用者的第 3 點）

- 來源：cth9191 craft.md 的「Captions hold: each on screen ≥ 1.25s」「Silence before the payoff」「What existed before the step is on screen from frame 0」；charlie947 的「The hold is where people actually look」。
- 做法：
  - **停留檢查**：任何元素出現不到 1.5 秒就被拿掉，記成問題；刻意一閃而過的設 `transient`。
  - **收尾停留檢查**：每場最後一個動作結束後，至少停 2 秒才開始轉場。
  - `script.json` 的場景後置留白改成 2～3 秒。
  - 轉場改掉甩出和整面色塊掃過：先把內容淡出，章名在正中寫出；下一場把章名**變形**成左上角標籤（同一個物件，`open_chapter()`）。

### D. 質感（使用者說的「粗糙」）

- **一個物件變形，不要淡出再淡入**（charlie947：「'Make it premium' means one object changing shape」）。
  - 例：sc04 兩張分數牌延伸成兩欄名次；sc01 連到分數的線改接到 RRF；結論列用 `ReplacementTransform` 換句。
- **錯開一拍**（charlie947 的 stagger）：同一組元素用 `LaggedStart`，不要整片同時出現。
- **起點殘影**（charlie947 的 ghost）：sc03 正規化後，B 的舊位置留一個淡點，再畫金色弧線到新位置。
- **每個畫面一個焦點、顏色只代表一件事**（cth9191 FRAME.md 第 2 條）：與我們原有的規則一致。
- **Manim 的坑**：對臨時 `VGroup` 做 `Rotate` 或 `.animate`，Manim 會把它加成頂層物件，原本的群組（錘錘）就被拆散。所以 `Plumb` 改用常駐的 `bodyg` 子群組。

## 沒採用的規則，以及原因

- 動作一拍畫兩格（animate on twos）、紙張紋理、半色調：這些屬於 Vox 或剪紙風格，與 3Blue1Brown 式的乾淨數學風格衝突。
- 120 BPM 節拍格線：我們的時鐘是旁白，不是音樂。
- 8 秒循環：那是社群貼文格式。

## 第二輪（2026-11-08，v4）：結構層的做法

使用者看完 v3 後說：「還是有粗糙感，離 3blue1brown 的精緻順暢差一大截，感覺沒有仔細研究這些 skill。」

這次把三個 repo 完整 clone 到 scratchpad 重讀，包括：
- cth9191：SKILL、grammar/FORMATS、STORY、FRAME、craft、styles/math 的 STYLE 與 kit.js、demo；
- charlie947：effects.md 的 16 種效果配方、vox-explainer、animated-chart、polish；
- artemnovitckii：graph、breakdown、minimal 範本與 anim.py。

v3 漏掉的是**結構**，不是細節：

| 研究裡的規則（出處） | v3 的做法 | v4 的落實 |
|---|---|---|
| 空間型的情節用一張大圖加跟拍鏡頭，不切換（FORMATS「How the columns couple」、F1 Machine） | 8 場各自獨立，用淡出和章名卡切換 | 整支片是混合搜尋管線這一張圖，鏡頭沿著走；`Timed.cam()` |
| 用形狀變形銜接，最多一個硬切（craft「Transitions」） | 每場都淡出 | 場景接縫一格不差：`lib/checks/seams.py` |
| 禁用的預設：一切都淡入、角落標籤、置中標題卡（craft「Banned defaults」） | 大量 FadeIn、章節卡、角落示意標籤 | Write／Create／DrawBorderThenFill／TransformFromCopy；沒有章節卡與角落標籤 |
| 讀數每格由同一個 tracker 算出（math STYLE「Trackers」） | 前後兩張靜態圖 | 橡皮尺、k 旋鈕、計數器都是 ValueTracker 驅動 |
| 一個眼睛抓得住的不變物（FRAME 1、FORMATS 不變式 1） | 每場換舞台 | 管線一直都在；綠星（正確答案）從頭追到尾 |
| 結尾是被故事改變過的開頭；先快轉一眼（FORMATS 不變式 4、flash-forward） | 沒有 | 開場快轉：正確答案掉到第 4 名；結尾 reranker 把它拉回第 1 名 |
| 文字活在世界裡（FRAME 6） | 底部結論列放整句話 | 畫面不放句子，句子只在字幕 |
| 同一個物件變形，值不變（charlie947 #05、#03） | 部分做到 | 分數從卡片後面穿過去變成名次；名次掉進分母 |

**仍然不採用的**：
- 120 BPM 節拍格線、on-2s：這兩種是 beat-cut 格式用的。我們的時鐘是旁白。
- 合成配樂：等使用者的曲庫。
- Playwright 渲染：要全域安裝，違反專案限制。

另一個使用者決定：畫面不放「示意」標籤，改由旁白交代舉例（`claims.py` 規則 6）。
