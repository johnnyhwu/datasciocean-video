# v001 製作紀錄：參考了什麼、學到什麼（給之後的回顧用）

使用者 2026-11-08 要求：把整個任務中參考的外部 skill 和資源記下來；任務完成時會再請 Claude 回顧哪些該記住、哪些該避免，再修改 CLAUDE.md 與 skill。這份是**原始紀錄**，回顧時從這裡提煉。結論性的規則已寫進 `.claude/skills/animate/SKILL.md`。

## 參考的外部資源

| 資源 | 讀了什麼 | 用在哪裡 |
|---|---|---|
| [cth9191/animate](https://github.com/cth9191/animate)（MIT，7e5eb56） | SKILL、grammar/FORMATS、STORY、FRAME、craft.md、styles/math/STYLE.md 與 kit.js、demo | 最主要的來源。一張大圖跟拍、接縫、banned defaults、tracker、結尾回到開頭、每 2～4 秒有新東西、數字用程式檢查 |
| [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills)（MIT，229022e） | prompts/effects.md 的 16 種效果、motion-effects references、vox-explainer、animated-chart、polish.md | 同一物件變形、殘影、錯開一拍；「前 3 秒要能讓人停下來」；「一次只修一件事，其他不動」 |
| [artemnovitckii/claude-animation-skills](https://github.com/artemnovitckii/claude-animation-skills)（MIT，5dbea55） | graph、breakdown、minimal 範本、anim.py | 美學：一張圖一個數字、沒有膠囊標籤 |
| PoC（`rules/from-poc/`） | 創意手法、踩過的坑 | 吉祥物、代入計算給觀眾看 |

原文摘錄放在 `rules/from-skills/vendor/`；完整 clone 只放在 scratchpad，沒有進 repo（他人的作品，留著研究用）。

## 每一版的使用者回饋與對策

| 版本 | 使用者怎麼說 | 根本原因 | 對策（落在哪裡） |
|---|---|---|---|
| v1 | 字太大、畫面空、像小學生做的 | 粗體膠囊、表格、到處 pop 音效 | 圖為主、細線、襯線公式（animate skill「視覺語言 v2」） |
| v2 | 還是粗糙：版面偏上、線蓋到東西、轉場太快 | 肉眼看縮圖抓不到 | `kit.Timed.check` 的版面平衡、線穿字、停留檢查 |
| v3 | 離 3b1b 差一大截；沒仔細研究 skill | 只抄了表層規則，結構沒變（每場各自淡出、章節卡） | v4 一張大圖、鏡頭跟拍、`seams.py` |
| v3 | 不要說「作者說」；「示意」標籤多餘 | 第三人稱轉述；免責標籤破壞畫面 | 改用「我們」；舉例由旁白交代（`claims.py` 規則 6） |
| v4 | **相當滿意**。但：轉場時會卡住定格幾秒 | 每場後置留白 1.5 秒＋最後一句 hold＋下一場前置 0.6 秒，接縫空檔 3～4 秒 | pad 改 [0.15, 0.4]、最後一句 hold ≤ 0.4；`seams.py` 檢查接縫空檔 0.8～1.6 秒 |
| v4 | 畫面上寫「卡上…」，觀眾不知道也不該知道觀念卡 | 內部用語外流到畫面 | 標註改「代入公式計算」；`claims.py` 規則 9 擋內部用語 |
| v4 | 結尾要更好記：最後一個畫面是整個方法的概念圖，三點回顧各對應圖上一個元件；說明欄由錘錘可愛地指 | 結尾只有一句話，沒有把整集收成一張圖 | sc08 f11～f16：拉到全景、三個框＋下方三點、錘錘往下指 |
| v4.1 | 「這版很棒」；最後再想哪裡可以更好，**檢查每個 frame**，優化完再進聲音合成 | 縮圖表只看句尾，動畫進行中的問題（跳出、空畫面、強調變色塊）一直沒被看到 | 新工具 `frames.py`（逐格）、`filmstrip.py`（整片逐秒縮圖）；kit `at()` 自動暫停 updater、`Highlight`；修 20 多處，見下方「最後一輪逐格檢查」 |

## 這次做對的事（v4 被使用者肯定）

- 整支片是一張大圖（混合搜尋管線），鏡頭跟著走；場景接縫逐格相同。
- 開場快轉一眼（正確答案從第 1 掉到第 4），結尾 reranker 把它拉回第 1。
- 公式 Write、線 Create、框 DrawBorderThenFill；名次從卡片上 TransformFromCopy 掉進分母。
- 會變的數字（橡皮尺、k 旋鈕、計數器）由 ValueTracker 驅動，每格依公式重算。
- 畫面不放句子；只有公式、數字、6 字以內的短標籤。

## 踩過的坑（Manim）

- 對 `Live`／`always_redraw` 物件做 `Transform` 會崩潰（點數不同）；用 `Write`。
- `Indicate(color=…)` 結束會回原色；要改色另外 `animate.set_color()`。
- 對有填色的物件 `animate.set_opacity(a)` 會把填色也設成 a（Σ 的圓變成實心）；只調 stroke 與文字。
- 曲線或數線 `set_opacity` 會打開填色；用 `set_stroke(opacity=…)`。
- 回顧框的邊不能穿過文字（「reranker」），框要讓開所有標籤。
- 全景鏡頭不能太寬：寬 20 時 0.05 的標籤實際只有 0.036，低於下限。要放更多東西，先讓物件靠攏，不要一直拉寬鏡頭。
- 錘錘從上方垂下來，繩子會穿過它上方的一切；擺位置前先找一條從頂端到身體都沒有字的直線。
- （2026-11-10）Transform 類動畫（FadeIn/FadeOut/Indicate/GrowFromEdge/`.animate`）會複製物件，**複本也帶著 updater**，
  `Animation.update_mobjects` 每格更新複本 → 被重畫回原樣：Live 讀數淡不掉（結束時一次消失）、長條直接跳出、Indicate 沒反應。
  已在 `kit.Timed.at()` 統一處理（`_pause_live`）。Write／Create 不受影響。
- （2026-11-10）`Indicate(color=…)` 用 `set_color`：不透明底色的卡片整張變成強調色，字母看不見 → `kit.Highlight`。
- （2026-11-10）點沿路徑走完 `self.remove()`、計數器置中加「+」、減速曲線尾端停住才翻最後一位，都會「跳」一下。

## 整片回顧（2026-11-08，對照三個 repo 的品質清單）

使用者要求：「把整部影片再看一次並進行優化，回顧一開始提供的 external skill repo，確保影片高品質、吸引觀眾、可以 reproduce」。逐場看縮圖表，對照 craft.md、FRAME.md、math STYLE、vox-explainer、polish.md：

| 發現 | 對照的規則 | 處理 |
|---|---|---|
| 7 個接縫有 6 個停格 1.9～4.5 秒 | craft「Transitions」、使用者回饋 | 調 pad、最後一拍、下一場第一拍；`seams.py` 加空檔檢查，7 個都在 0.8～1.6 秒 |
| sc02「IDF 加權」和「Cerebras 內部知識庫」貼在一起 | math STYLE 4：標籤不碰標籤 | 把 Cerebras 移開 |
| sc06 k＝60 時 A、B 長條看起來一樣長，看不出 A 贏 | math STYLE 3：畫面和公式一致、讀數由同一個 tracker 算出 | 長條右端加即時讀數（0.0317／0.0311…），加「代入公式計算」；查核紀錄補上停下來的四個值 |
| 結尾最後一格：錘錘的繩子穿過連線、說明文字和「全文搜尋」疊成一塊 | FRAME 6、版面檢查 | 錘錘移到左下、字放在它右邊並降低；全景鏡頭最寬只能 19.2（再寬標籤會小於 0.038） |
| 靜止 ≥ 4 秒佔 66% | craft「每 2～4 秒有新東西」 | 未處理：等真實旁白後再補；列在下面 |

## 最後一輪逐格檢查（2026-11-10，使用者：「最後再檢查一遍每個 frame」）

做法：先寫 `lib/checks/frames.py`（每格切 16×9 區塊：單格突變＝跳出、整格只剩背景＝空畫面、沒有任何區塊在動＝靜止），
再用 `lib/checks/filmstrip.py` 每秒一格、去掉重複（472 格 → 194 格、22 張 3×3），逐張看完整片。細節和做法表在 animate skill「動畫進行中的品質」。

| 項目 | 修之前（v4） | 修之後（v4.1，1080p） |
|---|---|---|
| 明顯跳出／閃爍 | 5 處（sc06 五根長條直接跳出、A/B 長條先跳出再閃一下、sc02 計數器結束時才消失、脈衝點走完消失） | 0 |
| 空畫面（鏡頭移到還沒畫的地方） | 3 處（sc03 r2、sc06 k1、sc07 t9，0.7～1.2 秒） | 0 |
| 強調時卡片變實心色塊 | 約 12 處 | 0（`Highlight`） |
| 讀錯風險（字黏在一起、線從第 3 名出發、尺和「最高」不一致、提示被讀成第四點） | 9 處 | 已修 |
| 靜止 ≥ 4 秒 | `still.py` 報 64.7%（量法太粗：寫出小數字也算靜止）；`frames.py` 重量是 10.1% | 4.8%（補了 5 個對應旁白的小動作） |
| 接縫 | 7/7 一格不差、空檔都在 0.8～1.6 秒 | 不變 |

教訓：
- **縮圖表看句尾是不夠的**。動畫進行中的跳出、空畫面、強調方式的問題，v1～v4 四版都在，直到逐格掃才看到。之後每支影片交關卡 3 前都要跑 `frames.py`＋`filmstrip.py`。
- **工具量錯會讓人追錯方向**：「66% 靜止」讓我們以為要大量加動作，其實是量法問題。新工具做出來先拿已知案例驗證（這次用已知的跳出點對照）。
- **能在 kit 層修的就不要在每個場景各自繞**（`_pause_live`、`Highlight`）：之後的影片直接受益。

## 待回顧時討論

- 靜止段落：v4.1 剩 4.8%（5 段，各 4.1～4.6 秒，都在旁白正在講的時候）。真實旁白進來後時間會變，合成後再跑一次 `frames.py`。
- 沒有配樂（等使用者曲庫）。vox-explainer：「沒有聲音的講解片感覺沒做完」。
- 開場的第一個驚喜在第 8 秒左右（0.83 + 12.4 = ?）；vox-explainer 建議 5 秒內。
