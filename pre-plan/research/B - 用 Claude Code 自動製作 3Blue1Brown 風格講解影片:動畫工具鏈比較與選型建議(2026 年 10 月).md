# 用 Claude Code 自動製作 3Blue1Brown 風格講解影片:動畫工具鏈比較與選型建議(2026 年 10 月)

**結論先講:主力渲染器請選 Manim Community 版(ManimCE,v0.22.0,2026-10-08 發布,MIT 授權),並自己寫一層「版面輔助函式」把格線、安全區、字幕區與時間分配鎖死;另外用一天時間拿 Remotion 做對照組。** 理由是 ManimCE 最接近 3b1b 的動畫語彙、授權沒有任何營利門檻、公開的 LLM agent 自動生成講解影片案例幾乎都用它,而且它的主要失敗模式(文字重疊、版面跑掉)已經有可以照抄的解法。

## TL;DR

- **選 ManimCE 當主力,Remotion 當備案,其他先別碰。** ManimCE(MIT)近一年持續發版,有 Typst 公式、Pango 中文排版,社群 Claude Code skill 也最多;3b1b 版 ManimGL 自 2024-12-13 的 1.7.2 之後就沒有在 PyPI 發新版。Motion Canvas 的最後正式版停在 2024-12-14,官網也已經下線;Revideo 團隊已轉去做商業產品 Midrender。這三個都不建議當自動化主力。
- **授權:你一個人經營、會營利的頻道,目前用 Remotion 也免費。** 官方授權頁 remotion.pro/license(2026-10-18 查核,頁尾標示「© Remotion AG 2026」)原文是「Remember - Remotion is free to use for individuals and companies up to three people.」;一旦成為 4 人以上的團隊或合作關係,就需要 Company License(Creators 方案「$25/mo per seat」;自動化渲染的 Automators 方案「$0.01 per render, $100/mo minimum」,而且官方寫明「Developers working on automation projects do not require a Seat」)。ManimCE、ManimGL、Motion Canvas、Revideo 都是 MIT 授權,HeyGen 的 HyperFrames 是 Apache-2.0,這幾個都沒有營利門檻。
- **真正的風險在版面,不在渲染。** 我找到的 6 個公開案例(TheoremExplainAgent、Code2Video、PhysicsSolutionAgent、norton77930 的 video-explainer skill、Vivek Karmarkar 的 Claude Code 實驗、ManimAgent)都回報了文字重疊、元素跑出畫面、尺寸不一致這類問題。有效的解法是三件事:座標格線化(例如 6×6 錨點)、每個場景抽一張圖給視覺模型檢查、限制修正輪數。最小試驗應該優先驗證這三件事。

## 摘要與給你的建議(一頁版)

**我的推薦組合(推論,依據見下方各節):**

1. **渲染:ManimCE 0.22.x**,固定 Python 版本,用 uv 鎖定依賴(uv 是 Python 的套件與環境管理工具,ManimCE 官方安裝說明推薦用它確保環境可重現)。
2. **公式:先用 ManimCE 0.21.0 起內建的 Typst/MathTypst**(Typst 是一套比 LaTeX 輕量的排版語言,不需要安裝 TeX),真的需要 LaTeX 時再改用 MathTex。
3. **中文:用 `Text`/`MarkupText`(底層是 Pango 文字排版引擎)搭配明確指定的繁中字型**,例如 Noto Sans CJK TC 或微軟正黑體。換行由你的輔助函式自己切,不要指望自動換行。
4. **Agent 指引:安裝 `adithya-s-k/manim_skill` 的 `manimce-best-practices`**,另外自寫一份專案用的 SKILL.md(Agent Skills 是一種放在 `.claude/skills/` 的 Markdown 指令檔格式,Claude Code 會在相關任務中自動載入),內容寫死你的版面規則與禁止事項,例如禁止混用 ManimGL API。
5. **品質迴圈:低畫質預覽 → 每場景抽一格 PNG → Claude 看圖檢查重疊與裁切 → 最多修 2 輪 → 高畫質輸出。** 這個流程是 norton77930 在 2026 年 10 月實作並跑過評測的做法。
6. **對照組:Remotion 4.x 加上官方 Claude Code 外掛**,專門用來試做文字很多的段落(標題卡、程式碼、圖表),看看中文排版與迭代速度是否明顯勝過 Manim。

**為什麼不是 Remotion 當主力(推論):** Remotion 的 agent 生態最成熟,有官方 skills 和官方 Claude Code 外掛,中文換行也直接繼承瀏覽器的 CSS 排版。但它在形狀變形、公式逐項轉換這類 3b1b 招牌動畫上沒有原生元件,而且官方文件沒有 LaTeX、KaTeX、MathJax 的整合頁(查不到)。再加上授權有「團隊超過 3 人就要付費」的門檻,你的頻道未來如果找剪輯或合作者,就會碰到這條線。

## 主要發現

### 1. 版本、維護狀態、授權(對個人營利頻道的影響)

| 工具 | 目前版本(日期) | 維護狀態 | 授權 | 對「個人、營利的 YouTube 頻道」的限制 |
|---|---|---|---|---|
| **ManimCE**(社群版) | 0.22.0(2026-10-08,PyPI);0.21.0(2026-08-10);0.20.1(2026-02-27) | 活躍,約每 2 個月一版 | MIT | 無。MIT 授權允許商用,只要保留版權聲明 |
| **ManimGL**(3b1b 版) | 1.7.2(2024-12-13,PyPI 最新) | 3b1b 本人自用為主;ManimCE 官方 FAQ 說它「實驗性功能較多,版本間的破壞性變更沒有文件記錄」 | MIT | 無 |
| **Remotion** | 4.0.532(2026-10-01,據第三方網站 snapcn 2026-10-01 查核) | 非常活躍 | 原始碼公開的自訂授權(不是開源授權) | 個人,或員工 ≤3 人的營利組織:免費且可商用。4 人以上要買 Company License |
| **Motion Canvas** | v3.17.2(2024-12-14,最後正式版);v3.18.0-alpha.0(2025-02-16) | **實質停止維護**:官網 motioncanvas.io 已下線(GitHub issue #1225,2026-02-18) | MIT | 無,但不建議新專案採用 |
| **Canvas Commons**(Motion Canvas 社群分支) | @canvas-commons/2d 0.4.0 | 活躍的社群分支,API 與 Motion Canvas 相同,只改了套件名稱 | MIT(繼承) | 無 |
| **Revideo** | 0.11.0(2026-07-10,據 snapcn) | 官方說明:團隊「現在主要開發 Midrender」,引擎的新改動「尚未回饋到開源倉庫」 | MIT | 無,但開源版前景依附於商業產品 |
| **HTML/CSS/JS + 無頭瀏覽器**(自建 Puppeteer/Playwright 加 FFmpeg) | 不適用 | 看你自己 | 看你用的函式庫,例如 GSAP 的授權要另外查 | 自建時無限制 |
| **HyperFrames**(HeyGen,建議額外比較) | v0.8.169(2026-10-17,GitHub releases) | 非常活躍,幾乎每天發版 | Apache-2.0 | 無。官方 README 寫明「沒有按次渲染費、沒有商用門檻」 |

**Remotion 授權細節(來源:remotion.pro/license 與 GitHub LICENSE.md,2026-10-18 查核,頁面版權標示 2026):**
- **免費授權的資格(來源明說):**「a for-profit organization with up to 3 employees」可免費使用,而且可以「non-commercially or commercially」。授權頁標語寫的是「For individuals and companies of up to 3 people … Commercial use allowed … Unlimited use … Must upgrade when your team grows」。
- **Company License 的適用對象與價格(來源明說):**「For collaborations and companies of 4+ people」。Remotion for Creators 每席每月 25 美元;Remotion for Automators 每次渲染 0.01 美元,每月最低 100 美元;Enterprise「Starting at $500 per month」。
- **怎麼算人數(第三方解讀,不是官方原文):** GenMotion(2026-10-05)與 rendercomp 指出,3 人門檻算的是整個組織的所有人,不只是寫程式的人;另外,如果客戶擁有或營運這個 Remotion 專案,雙方人數要合併計算。依授權 FAQ,Studio 和 Player 裡的預覽不算渲染次數。
- **對你的意義(推論):** 你一個人經營,目前屬於免費授權範圍,連自動化渲染也包括在內(免費授權頁寫「Create and automate」)。之後如果聘了 1 位剪輯加 2 位寫手,總人數變成 4 人,就要買授權。
- **尚待確認:** 第三方網站 autoae.online(2026-09-11)提到 Remotion 有「upcoming v5 Terms」。我查不到 v5 條款的具體內容,建議在正式上線前再看一次官方 LICENSE。

### 2. 對 AI agent 的友善度

| 面向 | ManimCE | Remotion | HyperFrames | Motion Canvas / Revideo |
|---|---|---|---|---|
| **輸出確定性**(同樣輸入產生同樣影片) | 來源明說:0.19.1 加入 `random_color` 的 seed,讓顏色可以確定性產生。推論:除了亂數之外,同一份程式碼在同一環境下應該輸出相同畫面,但我查不到官方「逐位元相同」的保證 | 來源明說:官方文件把 `Math.random()` 列為反模式,因為渲染時會開多個平行的頁面實例,每個實例的值都不同;要改用 `random(seed)`。第三方 recut.video 指出,4.0.247 起會自動下載並鎖定特定版本的 Chrome Headless Shell | 官方宣稱「same input, same frames, same output」;第三方 pyshine 轉述為跨機器逐位元相同(未獨立驗證) | 以產生器函式依序播放的腳本模型。我查不到確定性方面的官方聲明 |
| **錯誤訊息** | Python traceback(Python 的錯誤堆疊),agent 很容易讀懂。主要風險是 LLM「幻覺出不存在的 API」(TheoremExplainAgent 指出這是最大宗的失敗類別) | TypeScript 編譯錯誤加瀏覽器錯誤。程式「能編譯但畫面錯」的情況很常見,例如用 CSS transition 或 `Date.now()`,不會報錯,只會閃爍或卡住(snapcn 整理) | 有內建 lint(靜態檢查)步驟,CLI 預設非互動式,適合 agent 直接呼叫 | 一般 TypeScript 錯誤 |
| **快速預覽或出圖** | `-ql`(854×480、15fps)可以快速預覽(manim_skill 的 cli.md)。推論:可以再用 FFmpeg(開源影音轉檔工具)從預覽影片中抽格 | Remotion Studio 可即時預覽;推論:官方 CLI 有輸出單張靜態圖的指令,可以給 agent 看圖,需在試驗中確認 | 有 lint、preview、render 三段式流程 | 有編輯器可預覽;Revideo 另有無頭渲染 API |

**推論:** 在「agent 能不能自己修好」這件事上,ManimCE 和 Remotion 的程度差不多。ManimCE 的錯誤偏向「API 用錯就直接報錯」,好修;Remotion 的錯誤偏向「沒報錯但畫面不對」,難抓。所以不管選哪一個,都必須有「抽格看圖」這一步。

### 3. 官方與社群的 Claude Code skill、MCP server、範例

MCP 的全名是 Model Context Protocol(模型上下文協定),是讓 AI agent 透過標準介面呼叫外部工具的協定。

| 資源 | 類型 | 對應工具 | 狀態與品質評估 |
|---|---|---|---|
| **remotion-dev/skills**(`npx skills add remotion-dev/skills`) | **官方** Agent Skills | Remotion | 2026-01-20 由 Remotion 官方 X 帳號發布。GitHub 倉庫頁顯示 5.3k 星、583 個 fork(2026-10-18)。內容是時間軸、素材、合成規則。**品質高** |
| **remotion-dev/claude-code-plugin** | **官方** Claude Code 外掛 | Remotion | 官方文件有安裝頁,提供 `/remotion:remotion-create` 指令。**品質高** |
| **adithya-s-k/manim_skill**(manimce-best-practices、manimgl-best-practices、manim-composer) | 社群 skill | ManimCE 與 ManimGL | MIT,GitHub 倉庫頁顯示 1.2k 星、96 個 fork、23 個 commit(2026-10-18),最後推送 2026-01-23。內容按主題分成多個 rules 檔(動畫、時序、CLI 等),而且明確區分兩個版本的 import 寫法。**品質中上**;要留意它停更了大約 9 個月,不一定涵蓋 0.21 起的 Typst |
| **Yusuke710/manim-skill**(以及 Manimate) | 社群 Claude Code 外掛 | ManimCE | MIT,145 星,2026-10-04 仍有更新。流程是 旁白 → TTS(文字轉語音)→ 寫程式 → 渲染 → 合併音訊 → 檢視,並附瀏覽器版的時間戳回饋工具。**品質中**,適合拿來參考流程 |
| **norton77930/understanding-ai-outputs 的 video-explainer** | 社群 skill(附規格書與評測) | ManimCE 0.21 | 2026-10-07 開規格,2026-10-10 結案,隨 v1.0.0 出貨。**已處理繁中**(edge-tts 台灣腔、繁中字型偵測)。**對你最有參考價值** |
| **do-gongil/manimgl-skill** | 社群 skill | ManimGL | 2026-07-28 更新,我沒有細讀內容 |
| **daedalus/mcp-manimgl** | 社群 MCP server | ManimGL | 2026-05-15 更新,我沒有細讀內容 |
| **heygen-com/hyperframes**(`npx skills add heygen-com/hyperframes`) | **官方** skills | HyperFrames | 第三方 themenonlab 統計有 21 個 skill,內建 lint/preview/render 流程。**品質高**,但專案很新 |
| **Midrender MCP** | 官方 MCP server | Midrender(Revideo 商業版) | 綁商業產品,不適合你的流程 |
| **haidrrrry/claude-remotion-skill**、**wilwaldon/Claude-Code-Video-Toolkit** | 社群 skill 合集 | Remotion / Manim | 前者會「渲染 → 用 FFmpeg 抽格 → 檢查 → 修正」,思路正確。品質未驗證 |

**推論:** Remotion 的官方支援最完整;Manim 只有社群 skill,但數量多,而且已經有人做出繁中版本。不管用哪個 skill,都要再補一份你自己的「版面規則 skill」,因為 Karmarkar 的實驗指出,通用 Manim skill 涵蓋了語法和動畫慣例,唯獨沒有涵蓋版面(原文是「Animation best practices (except layout)」)。

### 4. 公式、圖表、程式碼高亮、繁體中文

| 能力 | ManimCE | Remotion | HyperFrames / HTML 路線 | Canvas Commons |
|---|---|---|---|---|
| **公式** | 有兩條路:`MathTex`(要安裝 LaTeX);0.21.0 起有 `Typst`/`MathTypst`(`pip install "manim[typst]"`,不需要 TeX)。0.22.0 修正了 MathTypst 群組的版面。0.20 重寫了 MathTex 的切分邏輯 | **查不到官方 LaTeX/KaTeX/MathJax 整合頁**;官方 resources 頁的整合清單沒有列(子代理查核,2026-10-18)。只能自己接 KaTeX 這類 React 函式庫 | 可以直接用 KaTeX/MathJax(推論:瀏覽器原生支援) | 有 `<Latex>`,0.4.0 起可以逐片段做補間轉換 |
| **圖表** | 有座標系、函數圖、`Graph` 等原生元件,這是 3b1b 風格的強項 | 可以用任何 React/D3/SVG 圖表(推論) | 同 Remotion(推論) | 有基本形狀與版面元件 |
| **程式碼高亮** | 有 `Code` mobject(基於 Pygments),0.21.0 修正了語言參數 | 可以用 Shiki/Prism 這類網頁高亮函式庫(推論) | 同上(推論) | 有 Code 元件(推論) |
| **繁中字型** | 用 Pango 排版,官方 MarkupText 範例本身就有「臂猿「黛比」帶著孩子」這段繁中字串。norton77930 的原型實測微軟正黑體可以正確渲染繁中 | 走瀏覽器字型與 CSS,另有 @remotion/fonts | 走瀏覽器字型 | 走瀏覽器字型 |
| **中文換行** | **弱**。我只查到 2021 年 RFC #2355 提議讓 `Text` 依寬度自動斷行,沒有確認是否已實作。另外 ManimPango issue #130 指出小字級時字距不均,常見解法是先放大渲染再縮小 | **強**。直接使用 CSS 的中日韓斷行規則(推論) | **強**(推論) | 有 flex 版面(推論) |

**推論:** 你的觀眾是一般人,內容是 AI 論文,這類影片裡「中文說明文字加示意圖」的比重,會比「純數學公式」高。這正是 ManimCE 最弱的地方。解法是讓輔助函式負責斷行:每行字數上限搭配字級換算寬度,超過就切行或拆成兩個場景。norton77930 的作法是把每個繁中場景的旁白限制在約 30 字。

### 5. 渲染速度與資源(1080p、5 分鐘)

**來源明說的數據:**
- **ManimCE:** ManimGX 的 README(這是競品自己做的評測,請視為偏慢的上限)寫道:「36.2 seconds of video … at 1080p60 on an Apple M4 Pro … ManimCE 278.83 s」,同一測試中 ManimGL 是 35.28 s。換算下來,ManimCE 每秒影片約需 7.7 秒渲染。
- **ManimCE 用不用 GPU:** 預設的 Cairo 渲染器主要吃 CPU,只有 OpenGL 渲染器會用 GPU(slama.dev)。但 ManimCE issue #1957 回報過 OpenGL 版約 36 秒、比 Cairo 的約 24 秒還慢,所以換成 OpenGL 不保證比較快。
- **Remotion 本機:** 第三方 PR(mahmoudemad68/Your_Editor #12)寫道:「fixed 60-second 1080×1920 composition … median of three measured Remotion runs is 139.644 seconds (2.327 seconds per output second)」,這是在雲端虛擬機上跑的。Orshot(競品,2026-10-15)的測試中,一支 10 秒 1080p 影片重複渲染時,Remotion 3.2 秒、HyperFrames 8.5 秒。
- **Remotion Lambda(AWS 的無伺服器運算服務):** 官方成本範例頁(Remotion 4.0.381、2048 MB、us-east-1):1 分鐘影片暖啟動 0.017 美元、18.91 秒;10 分鐘 HD 影片 0.103 美元、56.09 秒,約每分鐘 0.01 美元。官方 Lambda 頁寫「Cost per minute from $0.01」。這些數字不含 S3 儲存、流量與授權費,而且測試內容是嵌入現成影片,不是動畫。

**換算到 5 分鐘 1080p(推論,未實測):**

| 工具 | 估計時間 | 需要 GPU 嗎 | 成本 |
|---|---|---|---|
| ManimCE 1080p60 | 約 38 分鐘(7.7 秒 × 300 秒,用 M4 Pro 等級 CPU) | 不需要 | 本機電費,可以忽略 |
| ManimCE 1080p30 | 約 20 分鐘(幀數減半的粗估) | 不需要 | 同上 |
| Remotion 本機 | 約 12 分鐘(2.33 × 300 秒) | 不需要,吃 CPU 與 Chrome | 個人免費 |
| Remotion Lambda | 約 1 分鐘 | 不需要 | 約 0.05 美元起,另加 AWS 雜費 |

ManimCE 的快取機制只重渲染改動過的動畫片段,所以迭代修正時的實際等待時間會遠低於上表的完整渲染時間(推論)。**對你的意義(推論):** 3 到 15 分鐘的影片,在本機用 ManimCE 一晚就能渲染完,不需要 GPU,也不需要雲端。真正花時間的是「低畫質預覽 + 抽格檢查」的迭代輪數,不是最後的成片渲染。

### 6. 公開案例與失敗模式

我找到 6 個案例,超過你要求的 3 個。其中 3 個是學術論文,3 個是個人或開源專案。

| # | 案例(日期) | 工具 | 回報的失敗模式 | 解法 |
|---|---|---|---|---|
| 1 | **TheoremExplainAgent**(arXiv 2502.19400,2025-02;ACL 2025 主會議) | ManimCE + GPT-4o、Claude 3.5 Sonnet 等模型 | 論文 §4.2 原文:「The most common issue was Manim code hallucinations, which accounted for the majority of failures」(函式簽名錯、參數錯),其次是 LaTeX 渲染錯誤;Claude 3.5 Sonnet v1 的整體成功率只有 2.1%,加 RAG 後是 14.6%(Table 1)。版面方面有「misaligned text, overlapping shapes, and inconsistent sizes」。版面分數(Table 2):8 種 agent 設定(4 個模型,各有加與不加 RAG)的 Element Layout 落在 0.57–0.65,「Human-made Manim Videos」是 0.73 | 用 RAG(檢索增強生成,即先查文件再生成)查 Manim 文件,但論文說效果「inconsistent」;例如 Claude 3.5 Sonnet 加 RAG 後,總分從 0.79 降到 0.71 |
| 2 | **Code2Video**(arXiv 2510.01174,2025-10-01,新加坡國立大學 Show Lab) | ManimCE v0.19.0 | 空間版面錯誤、元素互相遮擋 | 規劃、寫程式、評論三個 agent 分工:寫程式的 agent 會依錯誤範圍(單行、區塊、全域)自動修正;評論的 agent 用 **6×6 視覺錨點格線**,Coder 提示詞原文寫「NEVER use .to_edge(), .move_to(), or manual positioning!」;附錄 A.1.3 的消融實驗中,6×6 的 Element Layout 是 82.8,4×4 是 76.1,8×8 是 77.2,不用錨點是 45.2。在 MMMC 基準(456 個單元,由 117 支 3B1B 長片加 339 個分段片段組成,涵蓋 13 個領域)上,論文原文寫「Our full Planner–Coder–Critic pipeline further delivers a stable 40% gain」;以 Claude Opus 4.1 為例,TeachQuiz 從 40.0 升到 86.0(Table 1)。(有一篇二手綜述寫成 10×10 格線,與論文原文 6×6 衝突,以原文為準) |
| 3 | **PhysicsSolutionAgent**(arXiv 2601.13453,2026-01) | ManimCE | 元素重疊、文字難讀、內容被畫面邊緣裁掉,也有 Manim 幻覺與 LaTeX 錯誤 | 渲染後交給 VLM(視覺語言模型,能看圖的 LLM)依評分表檢查,再把問題回傳給寫程式的 agent 修正 |
| 4 | **norton77930 video-explainer**(GitHub issue #14,2026-10-07 到 10-10) | ManimCE 0.21,搭配 Claude Code 這類 agent | 字幕在同一位置交叉淡入淡出時出現殘影;繁中影片太短(目標 90–120 秒,實際 58.8 秒,因為 8 個場景、每場景約 30 字的上限把長度卡在 60 秒左右);中文旁白比英文長約 25%;混用 ManimGL API 被列為已知失敗 | 由輔助函式掌管格線、安全區、字幕區與時長;以音訊為準,用量到的旁白長度決定場景長度,實測影片只比音訊長 0.1–0.18 秒;每場景抽一張預覽圖檢查,最多修 2 輪;同一場景渲染失敗 3 次就換成「標題 + 條列」的備援畫面。首輪評測 4 個主題全部成功渲染 |
| 5 | **Vivek Karmarkar 的 Medium 文章**(日期未標示,作者署名為 Claude Sonnet 4.5 代筆) | Claude Code + manim skill | 7 支物理與數學影片都失敗在「教學洞見」:例如圓面積的「啊哈」時刻只被標註出來,沒有真正被揭示;sin 導數的幾何證明三角形畫錯 | 作者的結論是要先由人寫好分鏡與教學意圖(作者稱為 Phase 1),再交給 agent 寫程式 |
| 6 | **ManimAgent**(arXiv 2606.30296,2026-06) | Manim | 前人系統把每次任務當孤立問題,修正經驗無法累積 | 文字與視覺雙重反思,並把「這次為什麼修得好」累積成可跨任務重用的經驗 |

**失敗模式整理:**
- **案例 1–4 都回報了文字重疊或版面問題。** 這是最普遍的失敗。
- **API 幻覺**:案例 1、3 回報,案例 4 回報的是版本混用。
- **時間軸對不上**:只有案例 4 明確處理,解法是以音訊為準。
- **教學品質不足**:案例 5 回報,這部分無法靠工具解決。

**我沒找到的:** 用 Remotion、Motion Canvas 或 HyperFrames 自動生成**數學或技術講解**影片,而且有詳細失敗報告的公開案例。Remotion 相關的公開材料多半是行銷片或產品展示。這是本研究的缺口。

### 7. 學習曲線

**查不到**有實測數據的來源。以下是推論:
- 你會寫程式,而且由 Claude Code 寫程式碼、你負責審片。ManimCE 預計 **1 天內可以做出第一支 30 秒、能看的片段**,**1 到 2 週可以做出第一支 3 到 5 分鐘、能上架的成品**。
- 花最多時間的會是三件事:建版面輔助函式、調繁中字型與換行、做旁白對時,不是學 Manim API 本身。
- Remotion 的上手時間差不多;如果你本來就會 React,會更快。
- 依據:Code2Video 和 norton77930 的 pipeline 都是由幾個模組加輔助函式構成;norton77930 從開規格到結案只花了 4 天(2026-10-07 到 10-10),但那是具備 agent 開發經驗的維護者。

## 總比較表

| 項目 | ManimCE | ManimGL | Remotion | Motion Canvas / Canvas Commons | Revideo | HTML + 無頭瀏覽器(自建) | HyperFrames |
|---|---|---|---|---|---|---|---|
| 版本與維護 | 0.22.0(2026-10),活躍 | 1.7.2(2024-12),破壞性變更無文件 | 4.0.532(2026-10),非常活躍 | MC 停更、官網下線;CC 活躍 | 0.11.0(2026-07),重心轉往 Midrender | 不適用 | 0.8.169(2026-10-17),非常活躍 |
| 授權與營利限制 | MIT,無限制 | MIT,無限制 | 個人或 ≤3 人免費;4 人以上要付費 | MIT,無限制 | MIT,無限制 | 看你用的函式庫 | Apache-2.0,無限制 |
| 確定性 | 高(推論) | 高(推論) | 高,前提是遵守 `random(seed)` 規則 | 中高(推論) | 中高(推論) | 要自己處理 | 官方宣稱逐格相同 |
| 錯誤可讀性 | 高(Python traceback) | 中 | 中(常見「沒報錯但畫面錯」) | 中 | 中 | 低到中 | 高(有 lint) |
| 快速預覽 | `-ql`,加上抽格 | 互動視窗 | Studio,加上靜態圖輸出 | 編輯器 | 播放器 | 截圖 | preview |
| Skill / MCP | 多個社群 skill,含繁中案例 | 社群 skill 加 MCP | 官方 skills 加官方外掛 | 少 | Midrender MCP(商業) | 無 | 官方 skills |
| 公式 | 強(Typst 與 LaTeX) | 強 | 弱(要自己接) | 中強(Latex 元件) | 中 | 中(KaTeX) | 中(KaTeX) |
| 中文換行 | 弱(要自己切) | 弱 | 強 | 中 | 中 | 強 | 強 |
| 5 分鐘 1080p 渲染 | 約 20–38 分鐘,只用 CPU(推論) | 約快 8 倍(競品評測) | 約 12 分鐘本機,或約 1 分鐘 Lambda(推論) | 查不到 | 查不到 | 查不到 | 查不到 |
| 3b1b 風格貼合度 | 最高 | 最高 | 中 | 中高 | 中高 | 中 | 中 |
| 公開的 agent 講解影片案例 | 6 個 | 0 個 | 0 個(只有行銷片) | 0 個 | 0 個 | 0 個 | 0 個 |

## 建議

1. **採用 ManimCE 0.22.x。** 理由有四:授權零風險;3b1b 風格最貼合;公開的 agent 案例與修正方法最多;渲染只需要 CPU。
2. **不要讓 Claude 自由擺位置。** 照 Code2Video 的做法,把畫面切成格線錨點,只允許 `place_at_grid` 這類輔助函式定位;字幕區和安全區由輔助函式保留,agent 寫的程式碼碰不到。
3. **以音訊為準。** 先產生旁白、量出長度,再決定每個場景的動畫時長。
4. **人工把關分鏡。** 依 Karmarkar 的教訓,你在審稿階段最該看的是分鐘級的「這一段要讓觀眾理解什麼」,不是程式碼。
5. **避開 ManimGL、Motion Canvas 原版、Revideo。** 如果日後真的需要網頁式工具,優先考慮 Remotion(你目前免費)或 HyperFrames(Apache-2.0,沒有人數門檻)。
6. **TTS 授權另外查。** norton77930 特別提醒:edge-tts 走的是非官方端點,對營利頻道有風險;官方的替代方案是 Azure Speech。這不在本次研究範圍內,但上線前要確認。

## 最小試驗設計:一天內做出 30 秒測試片

**題材:** 「Attention 機制在做什麼」的 30 秒片段,分 3 個場景。
1. 句子裡的詞變成方塊(中文標題加詞語標籤)。
2. 方塊之間連出粗細不同的線,代表注意力權重。
3. 出現公式 softmax(QKᵀ/√d)V,並逐項高亮。

**要測的項目與成功標準:**

| # | 測試項目 | 方法 | 成功標準 |
|---|---|---|---|
| 1 | 環境可重現 | 用 uv 鎖定 ManimCE 0.22.x;開新的 shell 重新安裝 | 一個指令就能裝好;`manim checkhealth` 通過 |
| 2 | 確定性 | 同一份程式碼渲染兩次,比對每格的雜湊值 | 每格雜湊完全相同。如果不同,要能找出是哪個亂數或時間來源造成的 |
| 3 | 繁中字型 | 標題、標籤、字幕都用 Noto Sans CJK TC 或微軟正黑體 | 沒有缺字或豆腐字,沒有誤用簡體字形,小字級也沒有字距不均 |
| 4 | 繁中換行 | 故意放一段 40 字的說明文字 | 輔助函式會自動切行,而且不超出安全區 |
| 5 | 公式 | 先用 MathTypst,再試 MathTex | 至少一條路能正確渲染,並且能逐項變色 |
| 6 | 版面自檢 | `-ql` 預覽 → 每場景抽 1 格 PNG → Claude 看圖列出問題 → 修正 | 最多 2 輪就沒有重疊和裁切;你人工看圖也同意 |
| 7 | 錯誤自修 | 故意在提示詞中誘導使用 ManimGL 寫法 | Claude 能從錯誤訊息自行修好,或 skill 事先就擋下,3 次以內解決 |
| 8 | 時間軸 | 用任一 TTS 產生旁白,依量到的長度分配動畫 | 影片和音訊長度相差 ≤ 0.3 秒(沿用 norton77930 的標準) |
| 9 | 渲染效能 | 1080p30 輸出最終版 | 記錄實際秒數,換算成「每分鐘影片需要幾分鐘」,作為 15 分鐘影片的排程依據 |
| 10 | 人工體感 | 你以觀眾角度看一遍 | 30 秒內看懂「每個詞會去看其他詞」這件事;畫面不像投影片 |

**時間配置(建議):**
- 上午:第 1–5 項,建好輔助函式與字型。
- 下午:第 6–9 項,跑完整迴圈。
- 傍晚:選做對照組,用 Remotion 官方外掛做同一支片的場景 1 與場景 3,比較中文排版品質、迭代次數與公式處理成本。

**判定方式:**
- 第 2、3、6、8 項全部通過,就正式採用 ManimCE。
- 第 3、4 項怎麼做都不行,而 Remotion 對照組明顯更好:改採「Remotion 負責文字段落、Manim 負責數學段落、FFmpeg 拼接」的混合方案(推論)。

## 注意事項

- **Remotion 版本號(4.0.532)與 Revideo 版本號(0.11.0)來自第三方網站 snapcn(2026-10-01 查核),不是官方頁面。** HyperFrames 版本以 GitHub releases 為準;非官方網域 hyperframes.video 顯示的 v0.9.2 與此衝突,我不採用。
- **渲染速度數字都不是中立評測。** ManimCE 的數據來自競品 ManimGX;Remotion 的數據來自單一使用者 PR 與競品 Orshot。5 分鐘的換算是我的推論,請以試驗中第 9 項的實測為準。
- **TheoremExplainAgent 的資料是 2025 年 2 月**,早於你要求的「2025 下半年以後」,而且用的是 Claude 3.5 Sonnet 這類舊模型。新模型的 API 幻覺率很可能比較低,但我查不到更新的量化數據。
- **我沒有實際讀完 do-gongil/manimgl-skill、daedalus/mcp-manimgl、haidrrrry/claude-remotion-skill 的原始碼**,表中只依它們的描述評估。
- **Remotion 的「upcoming v5 Terms」查不到內容。** 授權條款可能變動,上線前請再確認 remotion.dev/license。