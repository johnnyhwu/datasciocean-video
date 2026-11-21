# CLAUDE.md

這個 repo 把 DataSci Ocean 的**觀念卡**（`concept-wiki/`，唯讀 submodule）做成 **3Blue1Brown 風格的繁體中文 YouTube 講解影片**：橫式 16:9、3～15 分鐘、目標每週 1 支。

- **Claude 負責**：選題到成片的所有製作、上傳成私人、發布後追蹤成效。
- **使用者負責**：四個人審關卡，以及按下「公開」。

**頻道一句話**：用 3～15 分鐘的動畫，把一篇 AI 論文的核心機制講清楚，講給知道 LLM、但不讀論文的人（聰明的外行）。

**每支影片都要過三個問題**：

1. 這個承諾會讓目標觀眾想點進來嗎？字面為真嗎？
2. 聰明的外行跟得上嗎？哪一段最容易讓人離開？
3. 重點能用一句話說完嗎？

**使用者最在乎的**：「**動畫本身要把細節呈現出來**，讓觀眾理解整個技術到底想要表達什麼」；同時要有趣、有創意、敢誇張，讓人想看完。誇張是手段，講清楚是目的。

## 每次開始工作先做三件事

1. 和使用者一律用**繁體中文**溝通。
2. 看進度：`uv run python lib/state.py list`。有做到一半的影片就從它的狀態接續，不要從頭做。
3. 看成效有沒有到期：`uv run python lib/analytics.py --due`。標「到期」的就照 `retrospective` skill 的「成效追蹤」抓數據，並把結果講給使用者聽。這件事由 Claude 主動做，不等使用者提醒。

要做影片，從 `.claude/skills/make-video/SKILL.md` 進去，它會告訴你現在該載入哪個步驟的 skill。

## 品質基準：v001

第一支影片 `videos/v001-rrf-rank-fusion/`（https://youtu.be/vVW26HKH7n0）是使用者核准的基準。它重做了四版才到這個水準，前三版被退的原因是「像小學生做的動畫」「像投影片」「粗糙」。學到的做法都寫在各步驟的 skill 裡；新影片照同樣的結構做，換的是內容。

做新影片前先看這幾個檔，它們是最好的範例：

| 檔案 | 看什麼 |
|---|---|
| `design.md` | 一張大圖怎麼設計；每一輪使用者的回饋和對應的修改 |
| `script.json` | 腳本格式、留白、品牌音樂的設定 |
| `scenes.py` | 動畫的寫法、可以複製的元件 |
| `plan.md`、`review/`、`upload.md` | 規劃、審查包、上傳清單怎麼寫（`plan.md` 的視覺構想已被 `design.md` 取代） |

### 每支都一樣的（頻道識別）

- **一張大圖，鏡頭跟著走**：整支片是同一張圖，場景之間看不出接縫，沒有章節卡和標題卡。
- **開場先丟問題**，頻道介紹句放在鉤子之後。
- **收尾**：拉到全景 → 三點回顧 → 錘錘指說明欄 → 20 秒的頻道片尾動畫。
- **聲音**：使用者的複製聲音當旁白；品牌音樂只在片頭、章節轉場、片尾出現，不鋪在旁白下面；音效只放在轉折點。
- 吉祥物錘錘、深海配色、金色只給最重要的一個元素。

### 每支都要不同的

開場模式、骨架、大圖本身、主角、視覺手法、機制角色、標題寫法。結構指紋由程式比對最近 5 支（`lib/checks/fingerprint.py`）。最大的風險是 YouTube 的「通用或重複內容」政策。

## 硬性限制（不可違反；想放寬必須明確問使用者）

| 類別 | 限制 |
|---|---|
| 資料來源 | 只有 concept-wiki，而且唯讀（hook 擋寫入）。**不讀 blog、不讀原論文。**（說明欄要放原論文、官方技術部落格的連結：只查網址與標題，不讀內容，見 publish-prep） 只用 `status: normal` 與 `author_confirmed` 的主張；`pending_author_confirmation` 一律不用 |
| 知識範圍 | 影片傳達的知識不超出觀念卡。唯一例外：教科書等級的前置知識，佔比 ≤ 1/3 |
| 忠實 | 不加卡上沒有的事實、數字、比較、因果；不說得比卡更強；**限定條件不得刪除**，旁白至少完整說一次。新數字只有一種來源：**把卡上的數字代進卡上的公式**算出來，畫面標「代入公式計算」，查核紀錄寫出算式並由程式驗算 |
| 標題與縮圖 | 可以有趣、有反差，但每個字都要是影片裡真的講到的事；縮圖只用影片裡出現的元素 |
| 翻譯 | 英文、簡體的標題、說明、字幕只翻譯，不多加說法 |
| 論文圖 | 一律依主張文字重新製作，不放原圖，不逐筆描摹；只能估讀的只畫示意，並由旁白交代 |
| 舉例 | 自己補的數字、例子，旁白要說出這是舉例（「假設」「我們來舉個例子」「比方說」）；畫面不放「示意」標籤 |
| 觀眾看得到的字 | 旁白、字幕、畫面、說明欄不出現內部用語：觀念卡、卡上、「作者說／作者認為」。我們就是作者，用「我們」 |
| 授權 | 只用允許營利的工具、字型（OFL）、音樂、音效。音樂只用 `assets/music-library.yaml` 記錄的曲子，不自己找、不用 AI 生成；音效要 CC0 或允許營利，記在 `assets/sfx-library.yaml`。不複製 3b1b/videos 的程式碼與素材 |
| 不進 git | API 金鑰、OAuth 憑證（`secrets/`）、音檔、影片、音樂檔、音效檔、使用者的聲音錄音。**不讀出、不印出 `.env` 和 `secrets/` 的內容**，連遮罩過的也不行；只用程式確認有沒有值 |
| 人審關卡 | 四個關卡都要使用者核准，用 `state.py approve` 記錄後才能往下走 |
| 發布 | **公開由使用者自己按。** Claude 可以用 `lib/upload.py` 把成片上傳成**私人**並填好欄位，第一次上傳成片前要問；已上傳、還是私人的影片，標題、說明欄、縮圖、翻譯可以直接用 `upload.py` 改，改完告訴使用者（使用者 2026-11-22：「以後都可以直接改，反正最後會由我 review 然後才會設定成公開」）；已公開的影片要改先問。不得上傳成公開、不得排程、不得把私人改成公開、不得用其他方式呼叫上傳 API |
| 花錢 | 要花錢的動作先估金額、等使用者同意（TTS 一支 10 分鐘的影片約 US$0.14，2027-01-01 起約加倍） |
| 失敗 | 同一項失敗 3 次（查核改寫 3 輪、場景渲染 3 次、同一句 TTS 3 次）就停下來回報；**不換成投影片式的備援畫面** |
| 揭露 | 每支影片的「AI use」欄位都要有明確的建議答案；上傳前檢查 C2PA |
| 人設 | 旁白不設虛構的人名、頭像或專家身分。錘錘與各集的機制角色可以有，但不冒充真人或專家 |
| 環境 | **所有套件都裝在專案內**：`pyproject.toml` 加 `uv`（`uv add`、`uv run`），不 `pip install`，不安裝任何東西到全域 |
| git | 不自己 commit 或 push，使用者同意才 commit；只加明確的路徑，不用 `git add -A` |

## 工作原則

- **旁白先行**：先合成旁白、量出實際時長，才有時間軸；動畫用 `A(句 id, 比例)` 錨在旁白上，不寫絕對秒數。不要用估算的時間軸做動畫。
- **能用程式檢查的，一律交給 `lib/`**：字幕、響度、版面、接縫、逐格、字型、查核標記、數字。Claude 只做判斷。
- **Claude 看不到畫面、聽不到聲音。** 畫面靠程式檢查加上自己看縮圖；聲音只能靠量測。沒有經過人眼或人耳確認的地方要明講，不要假裝確認過。
- **上游一改，下游全部重跑**：改句子、重新合成旁白、改留白都會改時間軸。順序固定：`timeline.py` → 低畫質重渲 → 版面檢查清到全部 OK → 1080p → 接縫與逐格檢查 → 重新混音打包。
- **自己多看一輪**：交片前逐秒看完整片兩輪。使用者說「沒問題」之後再看一輪，v001 每次回看都還抓得到東西。
- **回饋是感受時，先找原因再改**：「粗糙」「吵」「沒活力」「好醜」這類回饋，先對照範例、量測、逐格看，找出具體原因，再改，並把原因告訴使用者。只調一個參數就重交，通常會再被退。
- **交東西時說清楚**：這一版改了什麼、和上一版差在哪、哪些沒有經過人眼或人耳確認、要使用者特別看哪個時間點；成片附上開啟指令。
- **問人時用白話說四件事**：這是什麼、選了會怎樣、代價是什麼、我的建議。
- **缺東西要早說**：需要使用者提供或決定的東西（聲音、字型、授權、帳號設定），在用到之前的步驟就問。
- **省額度**：skill 到該步驟才載入；程式檢查過了才看圖；查核只重查改過的句子；動畫只重渲改過的場景；狀態都寫進檔案，隨時可以開新對話接續。
- 長時間工作每個階段用一兩句話回報進度。

### 什麼時候停下來問

- 文件沒涵蓋的情況，或規則彼此衝突；
- 某條規則明顯讓內容變差；
- 句子不屬於任何查核標記，或需要卡上沒有的精確數字；
- 想不出一張能裝下整個機制的大圖；
- 要花錢、要上傳、要刪除使用者可能還要的檔案。

## 要做什麼就讀什麼

| 要做的事 | 讀 |
|---|---|
| 做影片（任何步驟） | `.claude/skills/make-video/SKILL.md`，它再指到各步驟的 skill |
| 成效追蹤、回顧、修改規則 | `.claude/skills/retrospective/SKILL.md` |
| 卡的格式、怎麼用卡 | `rules/card-format.md`；錨點類型的寫法在 `rules/from-social-media/anchor-writing-rules.md` |
| 片長字數門檻 | `rules/speech-rate.md` |
| 固定句、發音 | `rules/fixed-lines.md`、`rules/pronunciation.md` |
| 外部規則現況（YouTube、Gemini） | `rules/external-rules.md`（每季重查） |
| 環境、聲音重建、YouTube 帳號設定 | `docs/setup.md`、`docs/voice-recording.md`、`docs/youtube-upload.md` |

背景資料，平常不用讀：`rules/research-distilled.md`（開站前的研究結論）、`pre-plan/`（原始規劃書與研究報告，不動）。它們和 skill 衝突時，以 skill 為準。

## 目錄

```
CLAUDE.md                 本檔：頻道定位、硬性限制、工作原則
.claude/skills/           make-video（總流程）＋每步一份 skill；retrospective（成效與回顧）
.claude/agents/           fact-checker（查核員）、visual-checker（視覺檢查員）
.claude/hooks/            protect_wiki.py：擋寫入 concept-wiki
concept-wiki/             submodule，唯讀
config/                   style.json（版面、配色、字幕）、voice.json（TTS 聲音）、zh-cn-terms.yaml
rules/                    卡格式、語速、固定句、發音、外部規則、研究結論；from-social-media/、from-podcast/ 是寫稿用的參考
lib/                      kit.py（Manim 工具箱、錘錘、片尾動畫）、cards.py、state.py、tts_gemini.py、timeline.py、
                          render.py、mix.py、sfx.py、package.py、upload.py、analytics.py、
                          checks/（claims、fonts、sheet、seams、frames、filmstrip、stt、fingerprint）
assets/                   fonts/（OFL）、brand/logo.png、music-library.yaml 與 sfx-library.yaml（授權紀錄）；
                          music/、sfx/ 的音檔和 voice/ 不進 git
secrets/                  YouTube 的 OAuth 憑證與授權（不進 git，不讀出）
videos/<影片 ID>/          一支影片的文字產物：state.json、plan.md、design.md、script.json、factcheck.json、timeline.json、
                          scenes.py、thumb.py、fingerprint.json、review/、upload.md、upload.json、d7.json、d28.json
out/<影片 ID>/             音檔、渲染、成片（不進 git）
state/                    inventory.md（題材庫存）、cards.yaml（卡的 waiting／unsuitable 與原因）
docs/                     給人看的：環境、聲音錄音、YouTube 設定、吉祥物設計
pre-plan/                 原始規劃書與研究報告（不動）
```

影片 ID 的格式是 `v<三位數>-<主題 slug>`，例如 `v001-rrf-rank-fusion`。
