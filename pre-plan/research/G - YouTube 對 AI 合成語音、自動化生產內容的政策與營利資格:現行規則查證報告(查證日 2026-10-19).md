# YouTube 對 AI 合成語音、自動化生產內容的政策與營利資格:現行規則查證報告(查證日 2026-10-19)

以現行官方文字來看,你的流程(通用 TTS 旁白+程式生成動畫+LLM 依你自己 blog 寫的腳本)**沒有一條官方條文明確要求勾選 AI 揭露**。真正的政策風險不在「有沒有標示」,而在 YouTube 合作夥伴計畫(YPP, YouTube Partner Program,YouTube 的營利資格計畫)的「Generic or Repetitive Content(通用或重複內容)」條款,以及社群規範 Spam Policy(垃圾內容政策)中的「Automated or synthetic mass-production(自動化或合成式大量生產)」條款。這兩條的官方範例,幾乎就是「同一套模板+AI 腳本+合成旁白、大量上傳」的寫照。

## TL;DR

- **揭露:** 官方要求揭露的,是「看起來寫實」的 AI 內容(讓真人說沒說過的話、竄改真實事件或地點、生成寫實但沒發生過的場景、以 AI 音樂為主體)。用 AI 寫腳本、標題、縮圖被官方明列為「不需揭露」;非寫實動畫也不需揭露。至於「不模仿任何真人的通用 TTS 旁白」,官方查不到明確答案,「不需揭露」與「保守勾選」兩種解讀都站得住。官方說法是,揭露標籤本身不影響推薦,也不影響營利。
- **營利:** 2025-07-15,原「repetitious content」改名為「inauthentic content」。2026 年 7 月中旬,YouTube 再把條文重組成「Generic or Repetitive Content」「Unsatisfying or Off-putting Content」「AI Personas Related to Sensitive Topics」等類別(官方稱不是新政策)。官方明說 AI 工具可以用,但成品必須展現你的創作觀點與教育價值,而且是以「整個頻道」為單位審查。
- **對你的建議(推論):** 揭露欄每支影片都明確作答,不要留空交給自動偵測。把資源放在「每支影片實質不同」和「看得出你的原創觀點」:動畫不要套同一模板、背景音樂不要每支一樣、上傳頻率不要高到像內容農場、標題縮圖由你最後把關。全自動、無差異的批量上傳,是你這條流程唯一的高風險環節。

## 一頁摘要與結論

| 問題 | 結論 | 性質 |
|---|---|---|
| 純 TTS 旁白要不要揭露? | 官方沒有直接答案。四條必須揭露的條件都不涵蓋「不模仿真人的通用旁白」,但說明頁提到「非音樂的 AI 生成音訊」若揭露,標籤會出現在說明欄展開處 | 事實+兩種解讀並列 |
| 程式生成動畫要不要揭露? | 不需要。非寫實內容官方明列不需揭露;Manim 一類程式動畫連 AI 生成都不算 | 事實+推論 |
| LLM 寫腳本、標題、縮圖要不要揭露? | 不需要。官方明列「production assistance」 | 事實 |
| 揭露會不會降推薦或影響營利? | 官方兩處明說「不會」。查不到可信的第三方量化研究 | 事實/查不到 |
| 營利最大風險? | 模板化、可互換、批量生產;頻道層級審查 | 事實 |
| 社群規範風險? | Spam Policy 的「自動化或合成式大量生產」與「惡意點擊誘餌」;可能被警告、strike、終止頻道 | 事實 |
| 2026 年主要變化? | 2026-01-21 CEO Neal Mohan 年度信(YouTube 官方部落格「From the CEO: What's coming to YouTube in 2026」)點名 AI slop、1 月底大量 AI slop 頻道被移除、5 月 AI 標籤上移並自動偵測、5 月相似度偵測開放所有成人、7 月營利條文重組、8 月宣布 2027-02-01 YPP 門檻加倍、10 月 Shorts 偏好原創 | 事實(部分為媒體轉述) |

**我的整體判讀(推論):** 你的內容類型是「教育性講解+自有 blog 觀點」,本來就落在官方「允許營利」的範例裡(例如官方允許「用 AI 編修腳本」)。風險來自「自動化流程的副作用」:視覺與聲音同質化、產量過高、metadata 浮誇。這些都可以在流程設計上控制,不必因此放棄 TTS 或自動化。

---

## 1. 「修改過或合成的內容」揭露規定

### 1.1 現行名稱與入口(查證日 2026-10-19)

- 官方說明頁現名「Disclosing use of GenAI content」:https://support.google.com/youtube/answer/14328491 。頁面上沒有標示最後更新日期;我在 2026-10-19 讀取的是現行版本。
- 上傳時的位置在 YouTube Studio 的「Attributes(屬性)」區塊,欄位叫「AI use」,選 **Yes** 或 **No**(官方原文:「In the Attributes section, under "AI use," select Yes if your content meets the disclosure requirements or No if not」)。
- 早期版本放在「Details」區塊的「Altered content」欄位,標籤寫在說明欄。網路上很多教學還沿用舊名,請以 Studio 實際介面為準。
- 舊版頁面曾寫「若創作者在標題或說明自行註明使用合成內容,YouTube 可能代為勾選」。這段**在現行版本已經看不到**,不宜再當依據。

### 1.2 必須揭露的情況(官方原文與翻譯)

官方總原則:「We require creators to disclose AI-generated or altered content that seems realistic.」(我們要求創作者揭露看起來寫實的 AI 生成或修改內容。)

必須揭露的四種情況:
1. 「Makes a real person appear to say or do something they didn't do.」(讓真人看起來說了或做了沒做過的事)
2. 「Alters footage of a real event or place.」(修改真實事件或地點的影像)
3. 「Generates a realistic scene that didn't actually occur.」(生成實際沒發生過的寫實場景)
4. 「Creates music that's the main focus of the video.」(生成作為影片主體的音樂)

範圍說明:「fully or partially altered or created using any AI audio, video, image creation or editing tools」(全部或部分以任何 AI 音訊、影像、圖像工具生成或修改)。

**注意一個內部不一致:** 第 4 條寫的是「作為主體的音樂」,但同頁「需要揭露的例子」清單直接寫「AI generated music」,沒有加「主體」限定。如果你打算用 AI 生成背景音樂,兩種讀法並存,建議保守處理(推論)。另外,YouTube 官方部落格 2026-10-14 宣布 YouTube Music 對「主要由生成式 AI 製作」的歌曲加標籤,並將擴及 YouTube 主 App:https://blog.youtube/news-and-events/youtube-music-ai-labels/ 。

### 1.3 官方明列「不需揭露」的情況(與你最相關的幾條)

- 非寫實:「Using an AI-generated or altered animation of a missile in a fully animated video」(在全動畫影片中使用 AI 生成的飛彈動畫)
- 製作輔助:「Production assistance, like using generative AI tools to create or improve a video outline, script, thumbnail, title, or infographic」(用生成式 AI 產生或改善大綱、**腳本、縮圖、標題**、資訊圖表)
- 「Caption creation」(字幕生成)、「Idea generation」(發想)
- 「Cloning one's own voice to create voice overs or dubs」(複製**自己的**聲音做旁白或配音)

### 1.4 純 TTS 旁白、程式生成動畫算不算?

**程式生成動畫(事實+推論):**
- 3Blue1Brown 式的程式動畫屬於「非寫實」,官方「全動畫影片中的 AI 飛彈動畫不需揭露」這個例子可以直接類推。
- 用 Manim 一類程式碼繪製的圖形甚至不是「AI 生成」(推論)。這部分官方文字支持「不需揭露」。

**純 TTS 旁白(不模仿任何真人):官方文字沒有明確答案。** 可能的解讀並列如下:

| 解讀 | 依據 | 弱點 |
|---|---|---|
| A:不需揭露 | 四條必須揭露的條件都不成立:旁白沒有讓真人說沒說過的話,影片也不是寫實場景。官方所有聲音相關例子都圍繞「是誰的聲音」(複製自己的聲音免揭露、讓人看起來給了沒給過的建議要揭露) | 官方沒有一個例子直接說「通用合成旁白免揭露」 |
| B:保守勾選 Yes | 說明頁寫「Labels may appear in the expanded description for non-music AI-generated audio or AI content that is non-photorealistic or animated」,表示系統設計上預期會有「非音樂 AI 音訊」被揭露;2024 年官方部落格對寫實的定義包含「a viewer could easily mistake for a real person」,擬真 TTS 可能被認為像「真人在講話」 | 這段文字描述的是「揭露後標籤出現在哪」,不是「必須揭露」的條件 |

第三方看法(非官方):
- AIR Media-Tech(YouTube 認證合作夥伴、多頻道聯播網 MCN)2026-09-30 的文章說,其翻譯營運團隊把「不模仿任何人的庫存 AI 聲音」視為免標籤;但該團隊主管 Yelyzaveta Lovtsova 同時建議合作頻道「AI 旁白或 AI 視覺就自己先標」。
- nofacetube.com 也指出 YouTube「沒有發布涵蓋通用合成旁白的明確例子」。

**我的判讀(推論):** 依現行文字,選 A(No)有文字依據。選 B(Yes)的代價很低:非寫實、動畫或非音樂 AI 音訊的標籤只出現在「說明欄展開處」,而官方說揭露本身不影響推薦與營利。兩者都屬合規範圍,差別在品牌溝通。

### 1.5 標籤呈現位置(查證日 2026-10-19)

依官方部落格「Improving AI labels for viewers and creators」(2026-05-27):https://blog.youtube/news-and-events/improving-ai-labels-viewers-creators/

- **長影片:** 寫實或經實質 AI 修改的內容,標籤「directly below the video player, above the description」(播放器正下方、說明欄上方)。
- **Shorts:** 「as an overlay on the video itself」(直接疊在影片上)。
- **非寫實、動畫或輕微修改的內容:** 「viewers can find this disclosure in the expanded description」(說明欄展開處)。
- 說明頁另寫:AI 音樂或寫實內容「a label in the video player may also appear」(播放器上也可能出現標籤)。

### 1.6 自動標示、C2PA 與不揭露的後果

- 自 2026 年 5 月起,「If a creator doesn't specify whether or not they used AI, but our systems detect significant photorealistic AI use, we will now automatically apply a label.」(創作者沒有表明是否使用 AI、但系統偵測到大量寫實 AI 內容時,會自動加標籤。)注意前提是「沒表明」加上「寫實」。
- 說明頁列出自動標示的三種來源:用 YouTube 自家 AI 工具做的內容、含 C2PA 中繼資料的內容、內部系統偵測為 AI 的內容。C2PA(Coalition for Content Provenance and Authenticity,內容來源與真實性聯盟)是一套把「這個檔案由什麼工具產生」寫進檔案的業界標準。
- **無法移除的標籤:** 用 Veo、Dream Screen 等 YouTube 自家工具做的內容、含 C2PA 且標示為完全生成式 AI 的內容、經人工審查後加上的標籤。其他誤判可以在 Studio 改回 No。
- **不揭露的後果(官方原文):** 「Creators who consistently choose not to disclose this information may be subject to manual application of a label, or penalties from YouTube, including removal of content or suspension from the YouTube Partner Program.」(持續不揭露者可能被人工加標籤,或受罰,包括移除內容或暫停 YPP。)關鍵詞是「consistently(持續)」。網路上流傳的「三階段處罰」說法**沒有官方來源**。

### 1.7 對推薦分發的影響

- **官方說法一(說明頁):** 「Disclosing AI content alone won't limit a video's audience or impact its eligibility to earn money.」
- **官方說法二(2026-05-27 部落格):** 「a disclosure label alone does not change how a video is recommended or whether it's eligible to earn money.」
- **第三方:** 查不到具方法論、具樣本數的獨立量化研究。現有第三方文章(例如 layer3labs、AIR Media-Tech)只是重述官方說法或提出意見,不是實證。

---

## 2. YPP 營利政策:大量製作、重複、非原創內容

### 2.1 名稱演變與生效日期

- **2025-07-15(官方頁面橫幅原文):** 「We're making a minor update to our "repetitious content" policy to better clarify this includes content that is repetitive or mass-produced. We are also renaming this policy from "repetitious content" to "inauthentic content."」(官方稱這是小幅更新:「repetitious content」更名為「inauthentic content」,並釐清涵蓋重複或大量生產的內容。)
- **2026 年 7 月中旬:** 條文重組。我在 2026-10-19 讀取的官方頁面 https://support.google.com/youtube/answer/1311392 ,橫幅仍是 2025-07-15 那則,但內文小節已改為:
  - Generic or Repetitive Content(通用或重複內容)
  - Reused content(重複使用內容)
  - Unsatisfying or Off-putting Content(令人不滿或反感的內容)
  - AI Personas Related to Sensitive Topics(涉及敏感主題的 AI 人設)
- 這次重組的日期依據是第三方:Google 產品專家 Peggy K 的部落格(2026-07-16)與 Tubefilter(2026-07-13),兩者都說時間在 7 月 13 至 16 日間。Peggy K 引述 YouTube 表示「this is NOT a policy change」。
- YouTube 信任與安全副總 Matt Halprin 在 Creator Insider 訪談中說,YouTube 對工具「agnostic」(不預設立場),並說明被暫停 YPP 者有 21 天可申訴、90 天後可重新申請(Engadget 2026-08-05、netinfluencer 2026-07-21 轉述)。
- **結論:** 「inauthentic content」這個名稱仍出現在官方橫幅,但現行條文的實際小節標題已是「Generic or Repetitive Content」等。查詢條文時請以小節名稱為準。

### 2.2 現行條文重點(官方原文節錄)

**總要求:**
- 內容應「Not be mass-produced, generic, repetitive, or manipulative」(不得大量生產、通用、重複或操縱性)。
- 審查員可能檢查頻道的主題、最多觀看的影片、最新影片、觀看時間占比最大的影片、**影片中繼資料(標題、縮圖、說明)**,以及「關於」頁。
- 政策「apply not only to individual videos, but also to your channel overall」(以整個頻道為單位)。

**Generic or Repetitive Content:**
- 允許:「Same intro and outro for your videos, but the bulk of your content is different」(片頭片尾相同,但主體內容不同)。
- 不允許:
  - 「Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value」(幾乎沒有敘事、評論或教育價值的圖片輪播、模板化故事線或滾動文字)
  - 「AI-generated content made with generic or unoriginal templates giving the impression of mass production without adding the creator's original, authentic insights or perspective」(用通用、非原創模板製作的 AI 內容,給人大量生產的印象,又沒有加入創作者原創的見解或觀點)

**Unsatisfying or Off-putting Content 的允許範例(與 AI 輔助的界線最直接相關):**
- 「If you use automated tools or templates to help create your content, the final product must still demonstrate your creative vision and provide educational or entertainment value.」(使用自動化工具或模板輔助時,成品仍須展現你的創作視野,並提供教育或娛樂價值。)
- 允許:「using AI to edit your video scripts or generate a unique background visual for your content」(用 AI 編修腳本,或為內容生成獨特的背景視覺)。

**Reused content(與「論文講解」直接相關):**
- 不允許:「Content that exclusively features readings of other materials you did not originally create, like text from websites or news feeds」(只是朗讀非你原創的材料,例如網站或新聞的文字)。

**AI Personas Related to Sensitive Topics:**
- 不允許用 AI 人設「presents itself as a human expert providing advice」,主題涵蓋健康、法律、財務、政治。

### 2.3 什麼樣的 AI 輔助流程算「有實質原創貢獻」?

- **官方明說:** 判斷標準是「成品」,不是工具:要有創作視野、教育價值、每支影片實質不同。官方允許用 AI 編修腳本、生成獨特背景視覺。
- **官方沒說:** 沒有量化門檻,例如人工投入比例、每週上傳上限、TTS 能不能營利的明文。網路上的「51% 人工規則」之類說法**沒有官方來源**。
- **推論:** 你的腳本來自自己 blog 的觀點,這正是官方所說「creator's original, authentic insights or perspective」的最佳證據。反過來說,如果某些影片只是把論文摘要換句話說再念一遍,就會滑向 Reused content 的「朗讀非原創材料」。

### 2.4 全自動流程的風險(推論為主)

- 官方 Spam Policy 的範例(見第 3 節)是:「Channels that use the exact same background music and repetitive AI-generated imagery across many videos, with each video reading out an AI-generated script.」(許多影片都用完全相同的背景音樂和重複的 AI 圖像,每支影片念一份 AI 腳本。)這和「全自動 AI 解說頻道」的外觀高度相似。
- 判定由審查員看頻道整體觀感,而官方說審查員「can't check every video」,會抽看熱門影片和最新影片。所以只要最新幾支看起來高度同質,就可能影響整個頻道(推論)。

---

## 3. 社群規範:誤導性中繼資料與垃圾內容

### 3.1 現行條文(查證日 2026-10-19)

官方頁面現名「Spam policy」:https://support.google.com/youtube/answer/2801973 。它是社群規範「Spam & deceptive practices」類下六個頁面的第一頁,另外五頁是 Impersonation、External links、Fake engagement、Additional policies、Playlists。頁面沒有標示更新日期。

**改版時間查不到:** 舊版標題「Spam, deceptive practices, & scams policies」,原有「Video spam」「Misleading metadata or thumbnails」等小節。新版改成九類,但我與子研究都查不到官方公告或改版日期,只能確定 2026-10-01 前已經是新版(PPC Land 2026-10-02 的報導已引用九類版本)。

新版九類:
1. Engagement manipulation(互動操縱)
2. Fake engagement(假互動)
3. Comment spam(留言垃圾)
4. Off-platform diversion(導流至站外)
5. Detection evasion(規避偵測)
6. **Automated or synthetic mass production(自動化或合成式大量生產)**
7. Scraped content(抓取內容)
8. Scams(詐騙)
9. **Malicious clickbait(惡意點擊誘餌)**

與你最相關的兩條:

- **第 6 條原文:** 「Using automated tools or AI to churn out high volumes of similar content with minimal changes. While testing out new creation tools or posting a few variations of a video is okay, we don't allow use of these tools to flood our platform with repetitive content.」(用自動化工具或 AI 大量產出差異極小的相似內容;測試新工具、發幾個版本可以,但不允許用這些工具讓重複內容淹沒平台。)
- **第 9 條原文:** 「Using maliciously misleading titles, thumbnails, descriptions or imagery to trick users into clicking on a video that does not deliver what was promised.」(用惡意誤導的標題、縮圖、說明或圖像誘騙點擊,影片卻沒有兌現承諾。)範例是標題宣稱完整球賽,影片卻只有片段。

**新舊比較(推論):**
- 舊版「Misleading metadata or thumbnails」的文字是「trick users into believing the content is something it is not」(讓使用者誤以為內容是別的東西;舊版文字取自非官方的 fandom 備份與 Google 搜尋摘要)。
- 新版加上「maliciously(惡意)」與「does not deliver what was promised(沒有兌現承諾)」,字面上判定門檻收窄。
- 「標籤(tags)」在新版沒有單獨點名。但開頭總則寫「content, metadata, or behavior」,而且官方說政策適用於縮圖、連結等所有內容形式。

### 3.2 違規後果(官方原文)

- 「If your content violates this policy, we may suspend your monetization or terminate your channel or account.」(可能暫停營利,或終止頻道/帳號。)
- 「For some violations, we may remove the content and issue a warning or a strike」(部分違規會移除內容,並給予警告或 strike(警告處分))。
- **警告與 strike 的流程:**
  - 第一次通常是警告,完成政策訓練後 90 天失效。
  - 90 天內再違反同一政策,可能升級為 strike。
  - **90 天內累積 3 次 strike,頻道可能被終止。**
- 營利面另有 YPP 規定:違反營利政策可能被限制廣告、暫停或永久停用營利、扣留收益,特殊情況下終止頻道(1311392 頁「How we enforce」段)。

---

## 4. 2026 年的政策與實務變動(時間序)

| 日期 | 事件 | 來源性質 |
|---|---|---|
| 2026-01-21 | CEO Neal Mohan 年度信點名「AI slop」(低品質 AI 內容),表示將「building on our established systems that have been very successful in combatting spam and clickbait」;並提到 12 月平均每天超過 100 萬個頻道使用 YouTube 的 AI 創作工具 | 官方部落格 https://blog.youtube/inside-youtube/the-future-of-youtube-2026/ |
| 2026-01 下旬 | Kapwing 追蹤其列出的前 100 大 AI slop 頻道(名單出自 Kapwing 2025 年 11 月對 15,000 個熱門頻道的研究,該研究找出 278 個 AI slop 頻道,合計 630 億次觀看、2.21 億訂閱、估計年廣告收入約 1.17 億美元,並發現新帳號被推薦的前 500 支影片中 21% 是 AI slop),其中 16 個受影響(11 個被刪除,其餘被清空影片),合計 47.2 億次觀看、3,500 萬訂閱、年收入約 978 萬美元,包括前 5 大中的 2 個(CuentosFacianantes 與 Imperio de Jesus)。Kapwing 內容策略師 Liam Curtis 對 Dexerto(2026-01-30)稱此舉「could represent a significant turning point in YouTube's approach to AI content」。YouTube 發言人對 Yahoo Finance 只做一般性回應:「YouTube doesn't allow spam, scams, or other deceptive practices…」 | 第三方研究+媒體;被清空的數量有「5 個」(Kapwing/Tubefilter 系)與「6 個」(Dexerto)兩種說法 |
| 2026-05-18 前後 | 相似度偵測(likeness detection)開放所有 18 歲以上創作者;目前只比對臉部,不含聲音 | 媒體轉述官方社群公告(Social Media Today、Engadget、MediaPost) |
| 2026-05-27 | AI 標籤移到播放器下方/Shorts 疊加;開始自動偵測寫實 AI 並自動標示;YouTube 自家工具與 C2PA 完全生成內容的標籤不可移除 | 官方部落格 |
| 2026-07-13~16 | 營利政策條文重組為 Generic or Repetitive、Unsatisfying or Off-putting、AI Personas 等類別;官方稱不是政策改變 | 官方頁面現行內容+Peggy K、Tubefilter、Engadget 轉述 Creator Insider 訪談 |
| 2026-08-10 | YouTube 官方部落格「New opportunities to earn and changes to the YouTube Partner Program」宣布 YPP 自 2018 年以來首次重大調整(原文:「With over 3 million creators in the program, we're making the first significant changes since 2018」),新條款「will take effect on February 1, 2027」。新申請者門檻加倍為 1,000 訂閱+365 天內 8,000 小時有效公開觀看時數,或 90 天內 2,000 萬次 Shorts 觀看;已加入者不受影響 | 生效日期為官方部落格原文;8,000 小時/2,000 萬次的具體數字我只取得 vidIQ、AIR Media-Tech 等對該文的第三方轉述,未逐字核對官方原文 |
| 2026-09(Made on YouTube) | 宣布相似度偵測將擴及聲音 | 二手轉述(nofacetube 引 MediaNama),未讀到官方原文 |
| 2026-10-01 | TeamYouTube 社群公告「Prioritizing original content on Shorts」:重新上傳的 Shorts 觸及率降低,並與 Spam Policy 連結 | 媒體轉述(PPC Land、Social Media Today) |
| 2026-10-14 | YouTube Music 對主要由 AI 生成的歌曲加標籤,將擴及主 App | 官方部落格 |
| 2026(日期不明,10-01 前) | Spam Policy 改版為九類,含「Automated or synthetic mass production」 | 官方頁面現行內容;改版日期查不到 |

**有沒有「新增的標示欄位」?**
- 官方說明頁已把欄位稱為「AI use」,放在 Attributes 區塊。
- AIR Media-Tech 稱 2026-09-03 YouTube 宣布系統也會自動標示未申報的品牌置入,但這是第三方轉述,我沒有讀到官方原文。

---

## 5. 其他 AI 頻道怎麼揭露、有沒有被處罰

### 5.1 揭露實務

- **AIR Media-Tech 自家聯播網資料(2026-09-30,MCN 自述,非官方):** 網內 116 個頻道發布 AI 生成視覺(其中 82 個同時用 AI 聲音,34 個用真人聲音或沒有旁白);110 個頻道用 AI 聲音旁白(其中 28 個搭配非 AI 視覺,82 個搭配 AI 影像)。這些數字的分母是「該聯播網內的頻道」,但聯播網總頻道數該文沒有寫,所以**算不出比例**。該團隊把「不模仿真人的庫存 AI 聲音」當作免標籤,但主管建議合作頻道主動標示。
- **系統性的「多少 AI 頻道勾選揭露」統計:查不到。**

### 5.2 公開處罰案例

| 案例 | 內容 | 來源性質 |
|---|---|---|
| Screen Culture、KH Studio(AI 假電影預告) | 2025 年初 Deadline 調查後被暫停營利;頻道在標題加上「fan trailer」「parody」後恢復營利,之後不再一致標示,2025-12 被終止頻道。Deadline 報導 YouTube 的立場是違反「spam and misleading-metadata policies」 | 媒體報導(Deadline 2025-12-18 獨家),引述 YouTube 立場 |
| 2026 年 1 月 AI slop 頻道清除 | 16 個大型頻道被刪除或清空(數字見上表) | 第三方研究(Kapwing)+媒體;YouTube 只做一般性回應,沒有逐一確認 |
| 破壞家電頻道被以「Unsatisfying or Off-Putting」停止營利 | Reddit r/PartneredYoutube 貼文 | 創作者單方說法(經 Peggy K 2026-07-16 轉述) |
| 單一模板的長篇助眠音樂、禱告合輯被以 inauthentic content 暫停 | 2026-09 觀察 | MCN 觀察(AIR Media-Tech),非官方 |

**判讀(推論):**
- 公開被重罰的案例,共同點是**誤導性 metadata**(假預告冒充官方)或**極度同質的量產**,不是「用了 TTS」。
- Screen Culture 案特別有參考價值:把揭露寫在標題裡曾幫助它恢復營利,而撤掉揭露、回到誤導性做法,則直接導致終止。

---

## (a) 現行規則檢查清單(查證日 2026-10-19)

| # | 規則 | 官方連結 | 資料日期 |
|---|---|---|---|
| 1 | 寫實 AI 內容須在 Attributes →「AI use」勾 Yes;四種必揭露情況 | https://support.google.com/youtube/answer/14328491 | 頁面沒有標更新日;2026-10-19 讀取 |
| 2 | 用 AI 寫腳本、標題、縮圖、資訊圖表屬 production assistance,不需揭露 | 同上 | 同上 |
| 3 | 非寫實或動畫內容不需揭露;若揭露,標籤在說明欄展開處 | 同上;https://blog.youtube/news-and-events/improving-ai-labels-viewers-creators/ | 2026-05-27 |
| 4 | AI 音樂需揭露(條文寫「主體」,例子沒有限定) | 1 號連結 | 2026-10-19 讀取 |
| 5 | 揭露本身不影響推薦與營利 | 1 號連結+2026-05-27 部落格 | 2026-05-27 |
| 6 | 沒有表明而被偵測到寫實 AI 會自動標示;C2PA 完全生成或 YouTube 自家工具的標籤不可移除 | 2026-05-27 部落格 | 2026-05-27 |
| 7 | 持續不揭露可能被人工加標籤、移除內容、暫停 YPP | 1 號連結 | 2026-10-19 讀取 |
| 8 | YPP:不得大量生產、通用、重複;以頻道整體審查;審查員看中繼資料與「關於」頁 | https://support.google.com/youtube/answer/1311392 | 橫幅 2025-07-15;小節 2026-07 重組 |
| 9 | YPP:用 AI 或模板輔助時,成品須展現創作視野與教育價值 | 同上 | 同上 |
| 10 | YPP:只朗讀非原創材料屬 Reused content | 同上 | 同上 |
| 11 | YPP:AI 人設冒充人類專家談健康、法律、財務、政治不得營利 | 同上 | 2026-07 |
| 12 | Spam Policy:禁止用自動化工具或 AI 大量產出相似內容 | https://support.google.com/youtube/answer/2801973 | 改版日期查不到;2026-10-01 前已生效 |
| 13 | Spam Policy:禁止惡意誤導的標題、縮圖、說明、圖像 | 同上 | 同上 |
| 14 | 違規後果:警告(可經訓練 90 天後失效)→ strike → 90 天內 3 次可能終止頻道;也可能暫停營利 | 同上 | 同上 |
| 15 | 2027-02-01 起新申請 YPP 門檻:8,000 小時或 2,000 萬次 Shorts 觀看 | https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/ (生效日期為官方原文;門檻數字為第三方轉述) | 2026-08-10 宣布 |

## (b) 風險矩陣(你的流程)

| 環節 | 揭露風險 | 營利(YPP)風險 | 社群規範風險 | 理由與依據 |
|---|---|---|---|---|
| TTS 旁白(不模仿真人) | 低(定義不明) | 中 | 低 | **官方沒有明說**是否需揭露;官方明說揭露不影響營利。TTS 本身沒有被禁止(Halprin 稱「agnostic」);但如果和固定模板、相同背景音樂、AI 腳本組合,外觀接近 Spam Policy 的官方範例(推論)。若給旁白取人名、塑造成「專家」,可能觸及 AI Personas 條款(官方明說的是健康、法律、財務、政治主題;AI 技術主題是否涵蓋,屬推論) |
| 程式生成動畫 | 很低 | 中 | 低 | 非寫實動畫官方明列免揭露。風險在「每支影片看起來一樣」:官方說「Same intro and outro」可以,但「bulk of your content」必須不同(官方明說);3B1B 式風格容易同質化(推論) |
| LLM 依你自己 blog 生成腳本 | 無 | 低 | 低 | 官方明列腳本屬 production assistance;官方允許「using AI to edit your video scripts」。自有觀點符合「original, authentic insights」。風險點:只是轉述論文內容、沒有你的評論,會接近 Reused content「朗讀非原創材料」(推論) |
| 自動化批量上傳 | 無 | **高** | **中至高** | Spam Policy 明文禁止「churn out high volumes of similar content with minimal changes」;YPP 以頻道整體審查(官方明說)。官方沒有給量化上限,所以「多少算太多」只能推論 |
| 標題、縮圖、說明由 LLM 生成 | 無(縮圖若是寫實 AI 圖像,屬定義不明) | 中 | 中 | 官方明列標題、縮圖屬 production assistance,免揭露;但 YPP 審查員會看 metadata,Spam Policy 禁止惡意誤導(官方明說)。LLM 傾向產出浮誇標題(推論);Screen Culture 案顯示 metadata 誤導可以導致終止頻道(媒體報導) |
| (如果使用)AI 生成背景音樂 | 中 | 低 | 低 | 官方例子直接列「AI generated music」需要揭露;條文寫「main focus」,兩者不一致 |

## (c) 查不到官方明確答案的部分

1. **不模仿真人的通用 TTS 旁白是否必須揭露:** 官方沒有直接例子(兩種解讀見 1.4)。
2. **擬真度多高的合成語音會被視為「寫實」:** 官方沒有定義;5 月的自動偵測只提「photorealistic(寫實影像)」,沒有提到聲音。
3. **YPP 的量化界線:** 每週上傳數、人工投入比例、模板相似度門檻,官方都沒有公布。
4. **Spam Policy 九類版本的改版日期與公告:** 查不到(只能確定 2026-10-01 前已生效);舊版「misleading metadata」小節的完整原文,我只取得非官方備份與搜尋摘要。
5. **揭露標籤對推薦的影響:** 只有官方「不影響」的聲明,查不到獨立量化研究。
6. **AI 生成音樂的揭露範圍:** 「作為主體」與「任何 AI 音樂」兩種官方文字並存。
7. **2027 年 YPP 新門檻的逐字數字與 2026-09 品牌置入自動標示:** 2027 年新制的生效日(2027-02-01)已有 YouTube 官方部落格 2026-08-10 原文可證,但 8,000 小時/2,000 萬次的具體門檻我只讀到第三方轉述;品牌置入自動標示也只讀到第三方轉述,沒有直接讀到官方頁面。
8. **AI 人設條款是否涵蓋 AI 技術、AI 政策主題:** 官方列的是健康、法律、財務、政治;談「AI 法規」的影片是否算政治,沒有說明。
9. **自動化上傳的技術限制:** 本次沒有查證 YouTube Data API 上傳(例如未經稽核的 API 專案)是否有可見性限制;建議另外查證。
10. **實際 AI 頻道的揭露比例:** 查不到具分母的系統性統計。

## 建議(推論,附理由)

1. **每支影片都明確回答「AI use」。** 自動標示的觸發前提是「沒有表明」加上「寫實」。明確作答可以避免系統代你決定,也留下你有意識遵循規則的紀錄。選 No 或 Yes 都有依據(見 1.4)。如果想降低未來規則收緊時的爭議,選 Yes 的成本是說明欄裡多一個標籤,官方說不影響推薦與營利。
2. **在頻道「關於」頁和影片說明寫清楚製作方式**(例如「腳本改寫自本人 blog,旁白為合成語音,動畫以程式繪製,內容經本人審閱」)。這不是規則要求,但 YPP 審查員會看「關於」頁和 metadata(官方明說);這段說明能直接回應「看不出是你做的」這類 Reused content 疑慮。
3. **刻意製造影片間的實質差異。** 每支影片的動畫結構、視覺隱喻、配色節奏、開場方式要依主題變化;背景音樂輪替或乾脆不用;避免「同一套版型換文字」。這是針對 Spam Policy 範例和 Generic or Repetitive 條款最直接的防線。
4. **保留你的觀點。** 腳本裡要有「為什麼這篇論文重要、我怎麼看」的段落,不要只轉述論文。這是官方允許範例(original insights)和禁止範例(朗讀非原創材料)之間的分界。
5. **上傳頻率以「你真的審得完」為上限。** 官方沒有數字。但 3 到 15 分鐘的論文講解,如果每天多支、全自動上傳,很難說明人工審查的存在(推論)。建議先維持每週少量,上傳前由你人工確認。
6. **標題、縮圖由 LLM 提案、你定稿。** 禁止使用影片裡沒有兌現的承諾(例如「OpenAI 內部洩漏」「AGI 已經實現」),避開「Malicious clickbait」;縮圖不要用寫實的 AI 人像。
7. **不要給 TTS 旁白設計虛構的人類身分**(姓名、頭像、經歷),以免觸及 AI Personas 條款。若主題涉及醫療 AI、AI 法規,尤其要避免以「專家」口吻給建議。
8. **工具鏈檢查 C2PA。** 如果流程中用到會寫入 C2PA「完全生成」標記的 AI 圖像工具,標籤會永久無法移除;純 Manim 加 TTS 的流程通常不涉及(推論)。
9. **營利時程:** 如果打算申請 YPP,注意 2027-02-01 起門檻加倍(生效日見 YouTube 官方部落格 2026-08-10「New opportunities to earn and changes to the YouTube Partner Program」;具體門檻數字為第三方轉述,請到 YPP 官方說明頁確認)。

## 注意事項

- 本報告的官方頁面內容以 2026-10-19 實際讀取為準。Google Help 頁面多半不顯示最後更新日期,條文可能隨時改動,建議每季重新核對 14328491、1311392、2801973 三個頁面。
- 第三方資料(AIR Media-Tech、Kapwing、各類部落格)可能有商業立場,例如 MCN 推銷稽核服務、工具商推銷產品,文中已標註。網路上大量「三振制」「51% 規則」「2026 年 1 月全面強制揭露」之類說法,**我查不到官方依據,不應採信**。