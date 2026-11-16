# CLAUDE.md

這個 repo 把 DataSci Ocean 的**觀念卡**（`concept-wiki/`，唯讀 submodule）做成 **3Blue1Brown 風格的繁體中文 YouTube 講解影片**：橫式 16:9、3～15 分鐘、目標每週 1 支。Claude 負責製作；使用者負責四個人審關卡，並自己發布。

**頻道一句話**：用 3～15 分鐘的動畫，把一篇 AI 論文的核心機制講清楚，講給知道 LLM、但不讀論文的人（聰明的外行）。

**每支影片都要過三個問題**：

1. 這個承諾會讓目標觀眾想點進來嗎？字面為真嗎？
2. 聰明的外行跟得上嗎？哪一段最容易讓人離開？
3. 重點能用一句話說完嗎？

**使用者最在乎的**（PoC 的原話）：「**動畫本身要把細節呈現出來**，讓觀眾理解整個技術到底想要表達什麼」；同時要有趣、有創意、敢誇張，讓人想看完。誇張是手段，講清楚是目的。

## 開始前

1. 和使用者一律用**繁體中文**溝通。
2. 看進度：`uv run python lib/state.py list`。中斷過就從那支影片的狀態接續，不要從頭做。
3. 要做影片，從 `.claude/skills/make-video/SKILL.md` 進去，它會告訴你現在該載入哪個步驟的 skill。

## 硬性限制（不可違反，回顧時也不可自行放寬；想放寬必須明確問使用者）

| 類別 | 限制 |
|---|---|
| 資料來源 | 只有 concept-wiki，而且唯讀（hook 擋寫入）。**不讀 blog、不讀原論文。** 只用 `status: normal` 與 `author_confirmed` 的主張；`pending_author_confirmation` 一律不用 |
| 知識範圍 | 影片傳達的知識不超出觀念卡。唯一例外：教科書等級的前置知識，佔比 ≤ 1/3 |
| 忠實 | 不加卡上沒有的事實、數字、比較、因果；不說得比卡更強；**限定條件不得刪除**，旁白至少完整說一次。新數字只有一種來源可以出現：**把卡上的數字代進卡上的公式**算出來（使用者 2026-11-07 同意），畫面要標「代入公式計算」，查核紀錄要寫出算式（`calc`），由程式驗算；其他自行推算一律不行 |
| 翻譯 | 英文、簡體的標題、說明、字幕只翻譯，不多加說法 |
| 論文圖 | 一律依主張文字重新製作，不放原圖，不逐筆描摹；只能估讀的只畫示意，並由旁白交代是示意 |
| 舉例 | 自己補的數字、例子，旁白要說出這是舉例（「假設」「我們來舉個例子」「比方說」），畫面不放「示意」標籤（使用者 2026-11-08）；`claims.py` 檢查 |
| 觀眾看得到的字 | 旁白、字幕、畫面、說明欄不出現內部用語：觀念卡、卡上、「作者說／作者認為」（我們就是作者）。「觀念卡」是我們內部的溝通方式，觀眾不知道也不該知道（使用者 2026-11-08）；`claims.py` 檢查 |
| 授權 | 只用允許營利的工具、字型（OFL）、音樂（使用者的曲庫）；不複製 3b1b/videos 的程式碼與素材（CC BY-NC-SA） |
| 不進 git | API 金鑰、OAuth 憑證、音檔、渲染的影片、音樂檔、使用者的聲音錄音（`.gitignore` 已排除；不論 repo 是否公開都一樣） |
| 人審關卡 | 四個關卡都要使用者核准，紀錄用 `state.py approve` 寫入，才能往下走 |
| 失敗 | 同一項失敗 3 次（查核改寫 3 輪、場景渲染 3 次、同一句 TTS 3 次）就停下來回報；**不自動換成投影片式的備援畫面** |
| 揭露 | 每支影片的「AI use」欄位都要有明確的建議答案；上傳前檢查 C2PA |
| 人設 | 旁白不設虛構的人名、頭像或專家身分。吉祥物「錘錘」與各集的機制角色可以有（使用者 2026-11-06 同意），但它們不冒充真人或專家 |
| 發布 | 不上傳、不呼叫任何上傳 API。使用者自己發布 |
| 環境 | **所有套件都裝在專案內**：`pyproject.toml` 加 `uv`（`uv run …`），不 `pip install`，不安裝任何東西到全域（使用者明確要求） |

## 不確定就停下來問

遇到以下情況，停下來問使用者，不要自己決定：

- 文件沒涵蓋的情況；
- 規則彼此衝突；
- 某條規則明顯讓內容變差；
- 句子不屬於任何查核標記；
- 需要卡上沒標的精確數字；
- 要花錢的動作。TTS 每次合成前先估金額；一支 10 分鐘的影片約 US$0.14，2027-01-01 起約加倍。

問人時用白話說清楚四件事：這是什麼、選了會怎樣、代價是什麼、我的建議。

## 要做什麼就讀什麼

| 要做的事 | 讀 |
|---|---|
| 做影片（任何步驟） | `.claude/skills/make-video/SKILL.md`，它再指到各步驟的 skill |
| 發布後回顧、修改規則 | `.claude/skills/retrospective/SKILL.md` |
| 卡的格式、怎麼用卡 | `rules/card-format.md`；錨點類型的寫法在 `rules/from-social-media/anchor-writing-rules.md` |
| 片長字數門檻 | `rules/speech-rate.md` |
| 固定句 | `rules/fixed-lines.md` |
| 研究結論（敘事、手法、政策、授權） | `rules/research-distilled.md`。原文在 `pre-plan/research/`，平常不要載入 |
| 外部規則現況（YouTube、Gemini） | `rules/external-rules.md`（每季重查） |
| PoC 的經驗（使用者滿意的兩支試做） | `rules/from-poc/`：`03_CREATIVE_PLAYBOOK.md`（哪些創意有效）、`04_LESSONS_LEARNED.md`（踩過的坑） |
| 外部動畫 skill 的研究（版面、線條、停留的規則從哪來） | `rules/from-skills/README.md`。原文在 `vendor/`（MIT），平常不要載入 |
| 原始規劃書 | `pre-plan/spec/for_claude_code.md`（背景用；和本 repo 的規則衝突時，以本 repo 為準） |

## 跨步驟原則

- **旁白先行**：先有聲音才有時間軸，動畫用 `A(句 id, 比例)` 錨在旁白上，不寫絕對秒數。
- **能用程式檢查的，一律交給 `lib/`**：字幕、響度、版面、字型、標記、數字、狀態都由程式檢查。LLM 只做判斷。
- **Claude 看不到畫面、聽不到聲音。** 每次都要跑程式檢查並看縮圖；沒經過人耳確認的地方要明講，不要假裝確認過。
- **品質基準是 v001 第四版**（使用者 2026-11-08：「相當滿意」）。做法寫在 `.claude/skills/animate/SKILL.md` 的「視覺語言 v4」與「收尾」，範例是 `videos/v001-rrf-rank-fusion/`（`design-v4.md`、`scenes.py`）。每次都要守住的四件事：
  - 一張大圖加鏡頭跟拍；
  - 接縫一格不差，而且不停格（`seams.py`）；
  - 動畫進行中也要乾淨：沒有東西突然跳出或消失，也沒有空畫面（`frames.py` 逐格掃描）；交關卡 3 前用 `filmstrip.py` 逐秒看完整片（使用者 2026-11-10：「檢查每個 frame」）；
  - 最後一個畫面是全集的概念圖加三點回顧。
- **每支影片都要實質不同**：開場模式、骨架、視覺手法、機制角色、背景音樂都要換。結構指紋由程式比對最近 5 支。最大的風險是 YouTube 的「通用或重複內容」政策。
- **省額度**：
  - 細節放在 skill 裡，執行到該步驟才載入；
  - 程式檢查過了才送圖，每場只送 1 張縮圖表；
  - 查核只重查改過的句子；
  - 動畫只修出錯的場景；
  - 狀態寫進檔案，隨時可以開新對話接續。
- **不要自己 commit 或 push**。使用者同意後才 commit；回顧修改規則時，commit 紀錄就是規則的演變。
- 長時間工作每個階段用一兩句話回報進度。

## 目錄

```
CLAUDE.md                 跨步驟原則（本檔，保持精簡）
.claude/skills/           make-video（總流程）＋每步一份 skill；retrospective
.claude/agents/           fact-checker（查核員）、visual-checker（視覺檢查員）
.claude/hooks/            protect_wiki.py：擋寫入 concept-wiki
concept-wiki/             submodule，唯讀
config/                   style.json（版面、配色、字幕）、voice.json（TTS 聲音）、zh-cn-terms.yaml
rules/                    資料性質的規則：卡格式、語速、固定句、研究提煉、外部規則、from-social-media/、from-podcast/、from-poc/、from-skills/
lib/                      程式：kit.py（Manim 工具箱＋吉祥物）、tts_gemini.py、timeline.py、render.py、mix.py、package.py、
                          cards.py、state.py、checks/（claims、fonts、sheet、seams、frames、filmstrip、stt、fingerprint）
assets/                   fonts/（OFL）、brand/logo.png、music-library.yaml（曲庫授權紀錄）；music/、voice/ 不進 git
videos/<影片 ID>/          一支影片的文字產物：state.json、plan.md、script.json、factcheck.json、timeline.json、
                          scenes.py、fingerprint.json、review/、upload.md、d7.json、d28.json
out/<影片 ID>/             音檔、渲染、成片（不進 git）
state/                    inventory.md（題材庫存）、cards.yaml（卡的 waiting／unsuitable 與原因）
experiments/              實驗紀錄與比較報告
docs/                     給人看的：mascot/（吉祥物設計）、setup.md（環境）
pre-plan/                 原始規劃書、研究報告、PoC zip（不動）
```

影片 ID 的格式是 `v<三位數>-<主題 slug>`，例如 `v001-rrf-rank-fusion`。
