# 繁體中文 AI 論文動畫講解頻道：競品、空白與 YouTube 政策研究（資料截至 2026-10-19）

**結論：我找不到已經成形的「繁體中文＋3Blue1Brown 式動畫＋AI 論文機制講解」頻道。這個組合目前是空著的，而且看不出有人做過又失敗；比較像是沒人做。** 簡體中文已經有人做出可行的樣板（漫士沉思錄用 Manim 做動畫，軒轅的編程宇宙用 AI 生成動畫並公開聲明）。繁中市場則由李宏毅的課堂錄影（第三方統計 440,847 訂閱）和泛科學院的 AI 工具教學瓜分。用 Claude Code 自動化生產這件事，YouTube 現行政策沒有禁止，但「看起來像模板量產、沒有創作者原創觀點」的 AI 內容會失去整個頻道的營利資格。所以自動化本身不構成問題，真正的風險在同質化。

## TL;DR
- **空白存在，屬於「沒人做」**：在我能找到的來源裡，沒有任何台灣或香港頻道用 3B1B／Manim（Mathematical Animation Engine，3Blue1Brown 作者 Grant Sanderson 開發的 Python 數學動畫函式庫）的動畫方式講 AI 論文機制。最接近的繁中頻道是「工gin師」，做 LLM（Large Language Model，大型語言模型）與 Diffusion 論文導讀，但形式是簡報和導讀，2024-02 時只有 1,820 訂閱。簡體中文已有三個可參考的樣板。
- **政策可行，但紅線很明確**：YouTube 官方「頻道營利政策」頁面（2026-10-19 擷取）仍列有 2025-07-15 的「inauthentic content（不真實內容）」更新，並明文禁止「以通用或非原創模板製作、給人大量生產印象、且未加入創作者原創見解的 AI 生成內容」，以及「只朗讀非自己創作的資料」的內容。審查以整個頻道為單位。非寫實的動畫不需要做 AI 揭露。
- **需求真實，但缺乏直接數據**：TWNIC（台灣網路資訊中心）2025 年調查顯示 43.19% 的台灣民眾用過生成式 AI，YouTube 觸及台灣 98% 的網路人口、每人每日觀看 115 分鐘。「台灣有多少人想看 AI 原理影片」查不到直接數據。最好的代理指標是李宏毅頻道的訂閱數：從 2024-02 的 18.7 萬成長到 2026-10 的約 44 萬，約為 2.4 倍。

---

## 一頁摘要與給你的建議

**事實（有來源）**
1. 3Blue1Brown 的 YouTube 頻道沒有官方中文配音。官方「About」頁說明字幕靠社群透過 Criblate 網站貢獻；中國方面則由一小組志工把影片附上中文翻譯上傳到 Bilibili（官方帳號）。3B1B 聘人做配音的預算只涵蓋阿拉伯語、法語、德語、西班牙語、印地語五種語言，沒有中文。
2. Two Minute Papers 仍在穩定更新。2026-10-05、10-07、10-11、10-13 都有新片（第三方 ai-tldr.dev 紀錄）。CreatorDB（第三方）在 2026-09-29 記錄為 1,840,000 訂閱、每週約 1.9 支。
3. YouTube 營利政策（2026-10-19 擷取官方頁）目前分成「Generic or Repetitive Content」「Reused content」「Unsatisfying or Off-putting Content」「AI Personas Related to Sensitive Topics」四類。第三方部落格 Peggy K（Google 產品專家）在 2026-07-16 指出，這次是把 inauthentic content 改名，並新增兩個類別；YouTube 官方說法是「不是政策改變，只是說明得更清楚」。

**推論**
- 你的定位有真實的空間。主要原因是供給端門檻高：要懂論文，要會做動畫，還要能寫出好的繁中口語稿。需求不確定反而不是主因。自動化流程正好能降低第二項門檻，但不能省掉第一項和第三項的人工判斷。
- 你最大的風險是「整個頻道被判定為模板量產」，單支影片違規反而不是重點。設計流程時，必須讓每支影片在「概念、比喻、視覺隱喻」上有實質差異。

**三個具體建議**（詳見文末「對你定位的三個啟示」）
1. 定位成「李宏毅課程的 10 分鐘動畫入口」，不要和李宏毅或泛科學院正面競爭。
2. 把「人類 reviewer 的原創觀點」寫進流程，並且讓觀眾看得到，例如你本人出聲、在說明欄寫「我為什麼選這篇」。
3. 從第一天起就準備英文自動配音和簡體字幕，因為台灣頻道超過 40% 的觀看時間來自海外。

---

## 一、YouTube 政策現況（2026-10-19 確認仍有效）

### 1. 營利政策：inauthentic content／Generic or Repetitive Content
- **官方來源**：YouTube Help「YouTube channel monetization policies」（support.google.com/youtube/answer/1311392），擷取日期 2026-10-19。頁首仍保留 2025-07-15 公告：「我們正對『repetitious content』政策做小幅更新，以更清楚說明這包含重複或大量生產的內容，並將名稱改為『inauthentic content』……這類內容一直都不符合營利資格。」
- **與你的流程直接相關的條文（事實，引自官方頁）**：
  - 不得營利：「AI-generated content made with generic or unoriginal templates giving the impression of mass production without adding the creator's original, authentic insights or perspective」。
  - 不得營利：「Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value」。
  - 允許營利：「Same intro and outro for your videos, but the bulk of your content is different」。
  - Reused content 不得營利：「Content that exclusively features readings of other materials you did not originally create」。**這一條對「論文講解」特別敏感：只把論文摘要唸一遍會踩到。**
  - Unsatisfying content 允許營利：「If you use automated tools or templates to help create your content, the final product must still demonstrate your creative vision」，例子包括「using AI to edit your video scripts or generate a unique background visual」。
  - AI Personas：用 AI 生成的「專家」人設談健康、法律、金融、政治，一律不得營利。AI 論文講解不在列舉範圍內，但不要做成擬真 AI 主持人。
  - 審查範圍：審查員會看「主題、最多觀看影片、最新影片、觀看時間占比最大的影片、metadata、About 區」。Reused 政策適用「整個頻道」，違規時「monetization may be removed from your entire channel」。
- **時間軸的矛盾**：官方頁面只標了 2025-07-15 的日期。第三方 Peggy K（2026-07-16）與 creatorblade 都說 2026-07 中旬有一次「改名為 Generic or Repetitive Content，並新增兩類」的澄清。官方頁目前確實使用新的分類名稱，但沒有標出 2026 年的日期。兩種說法我都列出：條文內容以官方頁為準，「何時改的」以第三方說法為參考。
- **未經官方確認的傳言**：第三方 UpTube 宣稱「2027-02-01 起新申請 YPP（YouTube Partner Program，YouTube 合作夥伴計畫，即營利資格）需 8,000 小時觀看」。我在官方頁沒有找到這項規定，標為**查不到官方依據**，請勿當成事實。

### 2. AI 內容揭露要求
- **官方來源**：YouTube Help「Disclosing use of GenAI content」（answer/14328491），擷取日期 2026-10-19。
- **需要揭露**：讓真人看起來說了或做了沒做過的事、修改真實事件或地點的影像、生成實際沒發生過的寫實場景、以 AI 生成音樂為主體。
- **不需要揭露（官方列舉）**：非寫實內容，例如「在全動畫影片中使用 AI 生成的飛彈動畫」；也包括「用生成式 AI 寫或改善大綱、腳本、縮圖、標題、資訊圖表」、字幕生成、「Cloning one's own voice to create voice overs」。
- **自動標記**：YouTube 可能依 C2PA（Coalition for Content Provenance and Authenticity，內容來源認證標準）metadata 或內部偵測自動加上 AI 標籤。長期不揭露的創作者可能被移除內容或「suspension from the YouTube Partner Program」。官方也明說「Disclosing AI content alone won't limit a video's audience or impact its eligibility to earn money」。
- **推論**：Manim 動畫加上 AI 寫的稿屬於「不需揭露」。但如果用的是非你本人聲音的 TTS（Text-to-Speech，文字轉語音）旁白，官方列舉清單沒有明確涵蓋。建議主動勾選「AI use」或在說明欄聲明，因為揭露不影響營利，不揭露卻有被處罰的風險。

### 3. 背景：AI 垃圾內容的規模
- Kapwing 研究（2025-11-28 發布，《衛報》Aisha Down 2025-12-27 報導，公視轉述）：在全球最受歡迎的 15,000 個頻道中，有 278 個是純 AI 生成的「AI 垃圾」頻道，合計約 630 億次觀看、2.21 億訂閱，年營收約 1.17 億美元。Mashable 轉述，新開帳號收到的「first 500 YouTube Shorts」中，「104 were AI-generated, and 165 were "brainrot"」，分別占 21% 和 33%。這 500 支是 Shorts，不是所有類型的影片。
- **推論**：平台正在積極區分「AI 輔助的教育內容」和「AI 量產垃圾」。你的頻道視覺和聲音如果像後者，會被演算法和審查員一起懲罰。

---

## 二、頻道比較表

說明：「第三方」指 Social Blade、CreatorDB、HypeAuditor、vidIQ、SocialCounts 等非 YouTube 官方統計；「自述」指頻道主或其公司自己公布的數字。我無法直接讀取 YouTube 頻道頁上的即時訂閱數，下表數字全部來自第三方或報導。

| # | 頻道 | 語言 | 訂閱數（日期、來源） | 上傳頻率 | 典型長度 | 風格 | 製作方式／AI 聲明 | 主題 |
|---|---|---|---|---|---|---|---|---|
| 1 | 李宏毅 Hung-yi Lee | 繁中 | 440,847（2026-10-19，SocialCounts.org，第三方）；18.7 萬（2024-02-01，HackMD 盤點） | 隨學期，開課期間每週 2–3 支（ALPHA Camp，日期不詳） | 課堂錄影，精確長度查不到 | 真人＋投影片 | 人工；查不到 AI 聲明 | 機器學習、生成式 AI 課程 |
| 2 | 泛科學院 | 繁中 | 約 27.4 萬（YouTube 頁面 metadata userInteractionCount「274000」，擷取日期不詳）；主辦單位頁（ACCUPASS 泛傳媒）稱曾「突破 10 萬訂閱」（日期不詳）；自述「一年內 YT 突破 500 萬累計觀看」 | 查不到 | 查不到 | 真人主持（原主持人 AJ 莊哲昀已離開，另開「欸那個AJ」頻道） | 人工團隊；查不到 AI 聲明 | AI 工具實測、應用教學 |
| 3 | PanSci 泛科學 | 繁中 | 約 100 萬（政大講座介紹「從 1 到 100 萬訂閱」，講座日期 2025-09-12，自述） | 查不到 | 查不到 | 真人＋圖卡動畫 | 人工團隊 | 綜合科普，含 AI（如可解釋 AI） |
| 4 | 工gin師 | 繁中 | 1,820（2024-02-01，HackMD） | 查不到 | 查不到 | 簡報／論文導讀 | 查不到 | LLM、Diffusion、AI 論文導讀 |
| 5 | 林軒田 | 繁中 | 2.62 萬（2024-02-01，HackMD） | 查不到（以舊課程為主） | 課堂錄影 | 投影片 | 人工 | 機器學習基石、技法 |
| 6 | 陳縕儂 | 繁中 | 4.89 萬（2024-02-01，HackMD） | 查不到 | 課堂錄影 | 投影片 | 人工 | 深度學習應用 |
| 7 | 李沐 Mu Li／跟李沐學AI | 簡中 | YouTube 6.77 萬（2024-02-01，HackMD）；Bilibili 112.3 萬關注（Bilibili 頁面，日期不詳） | 不定期 | 單篇精讀約 40–90 分鐘（CSDN 整理，第三方） | 真人聲音＋論文畫面逐段講 | 人工 | 經典論文逐段精讀（67 篇清單） |
| 8 | 漫士沉思錄（YouTube 名 Meditation Math） | 簡中 | YouTube 查不到；Bilibili 單支 1,147,627 觀看（數學片） | 低頻（推論） | 長，AI 旗艦片 90 分鐘 | **Manim 動畫** | 說明欄聲明「使用 manim 引擎製作」並註明部分素材出自 3b1b；查不到生成式 AI 聲明 | 數學、物理、AI |
| 9 | 王木頭學科學 | 簡中 | YouTube 約 40,300（頁面 metadata，日期不詳）；Bilibili 23.4 萬（日期不詳） | 很低（Bilibili 約 39 支） | 長片，精確長度查不到 | 手繪／圖解旁白 | 查不到 AI 聲明 | Transformer、注意力機制本質 |
| 10 | 軒轅的編程宇宙 | 簡中 | YouTube 查不到（舊第三方 2.13 萬）；自述全網 50 萬+ | 查不到 | 查不到 | **AI 生成的 SVG 動畫** | **明確聲明**：「視頻中的動畫使用 svganimate.ai 製作」 | LLM 原理、程式、資安 |
| 11 | 3Blue1Brown | 英（Bilibili 有中文字幕官方帳號） | 8,525,636（2026-08，HypeAuditor，第三方）；8.43M（2026-06-23，vidIQ，第三方） | 低頻，總共約 239 支（vidIQ） | 常見 15–20 分鐘（今日頭條轉述，第三方） | Manim 動畫＋旁白 | 人工；Manim 是作者自製開源工具 | 數學、神經網路、LLM |
| 12 | Two Minute Papers | 英 | 1,840,000（2026-09-29，CreatorDB，第三方）；1.79M（2026-03-08，Social Blade，第三方） | 約每週 1.9 支（CreatorDB） | 約 5–10 分鐘（第三方轉述） | 論文 demo 畫面＋旁白 | 人工（Károly Zsolnai-Fehér）；查不到 AI 聲明 | 最新 AI 論文速報 |
| 13 | Welch Labs | 英 | 889K（2026-07-04 前後，Social Blade，第三方），147 支 | 低頻 | 查不到 | 動畫（使用 3B1B 版 Manim，GitHub 自述） | 人工 | 機器學習、AI 機制，出版 AI 圖解書 |
| 14 | AI Explained | 英 | 433K（usefulai.com 2026 年版清單，第三方） | 約每月 3 支（usefulai.com） | 15–30 分鐘（usefulai.com） | 旁白＋資料畫面 | 查不到 | 新模型與論文的脈絡分析 |
| 15 | StatQuest | 英 | 114 萬（ALPHA Camp，日期不詳） | 查不到 | 查不到 | 繪本式圖解 | 人工 | ML 概念、Transformer |
| 16 | Andrej Karpathy | 英 | 1.52M（usefulai.com 2026 年版清單，第三方；舊的 42.7 萬已明顯過時） | 不定期（usefulai.com） | 30 分鐘以上（usefulai.com） | 真人寫程式 | 人工 | LLM 從零實作 |

**表格解讀（推論）**：繁中頻道分成兩類。一類是「長課堂錄影」（李宏毅、林軒田、陳縕儂），另一類是「AI 工具實用」（泛科學院）。「10 分鐘內、動畫、講單一機制」這一格是空的。簡中已有人填補，但他們的作品不是太長（漫士 90 分鐘），就是更新太少（王木頭）。

---

## 三、3Blue1Brown 的中文狀況與 Two Minute Papers 現況

- **3B1B 有沒有中文字幕**（事實，3blue1brown.com/about）：YouTube 字幕由社群透過 Ben Eater 建立的 Criblate 網站翻譯，經核准後成為官方字幕；由於 YouTube 在中國無法使用，「有一小群志工把影片附中文翻譯上傳到 Bilibili」。3B1B 的 Substack 寫到，他們傾向用真人配音而不是 AI 配音，首批預算給了五種語言，不含中文。
- **推論**：繁中觀眾要看 3B1B 的 LLM 系列，在 YouTube 上要靠社群字幕，原生的繁中配音或動畫版不存在。這不代表你可以搬運 3B1B（違反 reused content 政策），而是說「繁中觀眾習慣 3B1B 視覺語言，卻沒有母語版本」這個缺口確實存在。
- **3B1B 本身在 AI 主題上的動向**：2025 年夏天 3B1B 委託 Welch Labs 製作擴散模型（diffusion model）客座影片，Grant Sanderson 提供編輯意見（3B1B Substack）。這說明高品質的 AI 機制動畫是 3B1B 生態系主動擴張的方向。
- **Two Minute Papers**：仍活躍。最近影片包括 2026-10-13〈OpenAI Just Changed What It Means To Do Math〉、2026-09-24〈Claude Opus 5.5 AI: An Incredible Leap Forward〉（ai-tldr.dev，第三方）。訂閱數成長趨緩：Social Blade 2026-03-08 為 1.79M，CreatorDB 2026-09-29 為 1.84M，約 7 個月成長 5 萬。

---

## 四、觀眾反應（坦白說明：樣本嚴重不足）

**我沒有完成系統性的留言抽樣。** 研究期間無法讀取 YouTube 影片頁（被機器人防護擋下），所以抽樣數是「0 支影片、0 則留言」。以下只是代理證據，不能當成留言分析：

- **李宏毅**：《天下》報導說他的課「融入動漫梗與生活化例子，讓艱深的 AI 知識變得易懂有趣」；Threads 使用者（2025-10-19）推薦理由是「課程淺顯易懂，老師講話也蠻風趣」。這是 2 則社群貼文，不是留言抽樣。
- **3B1B × Welch Labs 擴散模型影片**：X 上一則轉發評語是「visual, intuitive, elegant」，ResetEra 論壇一則貼文稱讚內容。共 2 則，屬於讚賞面，沒有抱怨樣本。
- **軒轅的編程宇宙 Transformer 影片**（Bilibili）：播放 121,207、點讚 4,970、收藏 7,705。**推論**：收藏數高於點讚數，代表觀眾把它當成「之後要學的教材」來存，這是教育型動畫內容的典型訊號。
- **Bilibili 標題生態**：搜尋結果裡充斥「最強動畫講解」「草履蟲都學的會」這類標題（推論：內容農場化，同質性很高）。這正好是你要避開的「generic」樣貌。

**建議補做**：挑 6 支影片（李宏毅生成式 AI 第 1 講、3B1B〈But what is a GPT?〉、Two Minute Papers 近期一支、漫士 90 分鐘 AI 片、軒轅 Transformer 片、泛科學院一支），每支取「熱門排序前 100 則」，人工分類成「讚賞點／抱怨點／提問」。

---

## 五、空白分析：繁中＋3B1B 動畫＋AI 論文機制

- **事實**：研究子代理和我自己的搜尋都沒有找到已成形的台灣或香港 Manim 式 AI 講解頻道。2024-02 的台灣 AI YouTuber 盤點（HackMD，16 個頻道或課程）全部是課堂、課程或論文導讀形式。唯一相關的痕跡是個人 Manim 教學文和 Threads 上「用 Codex＋Manim＋Remotion 做研究影片」的貼文，都不是頻道。
- **簡中已有人做**：漫士沉思錄（Manim，Bilibili 單支百萬觀看）、軒轅的編程宇宙（AI 生成動畫，自述 YouTube 播放 12 萬+，未經驗證）、王木頭學科學（Bilibili 單支 37 萬）。
- **是「沒人做」還是「做了失敗」**：查不到任何「做過後停更或失敗」的繁中案例。**推論**：比較像沒人做。原因可能是（1）同時要具備論文理解、動畫程式、中文腳本三種能力；（2）台灣市場小，人工製作一支 Manim 影片的成本難以回收；（3）李宏毅的免費課程已經滿足「想真正學」的那群人，壓縮了中間層。第 1 和第 2 點正是 Claude Code 自動化能改變的部分。
- **潛在風險（推論）**：簡中動畫頻道的觀眾多在 Bilibili。繁中觀眾則是「知道 LLM、但不讀論文」，對 90 分鐘長片的耐受度可能較低。你的 3–15 分鐘設定比較合適。

---

## 六、成長路徑（公開談過的部分）

- **李宏毅**（《天下》未來城市）：2017 年起把台大機器學習課上傳 YouTube，「學期末，頻道訂閱數就來到 8,000 人；2021 年訂閱數破十萬人，近兩年再因生成式 AI 翻倍，訂閱突破 24 萬大關」。非凡新聞 2025-07-28 報導「YT 訂閱破 32 萬」，SocialCounts 2026-10-19 為 440,847。**推論**：突破點是「生成式 AI 熱潮＋開放文組修課的《生成式 AI 導論》」，而不是單一爆紅影片。
- **3Blue1Brown**（3blue1brown.com/about、Wikipedia）：Manim 是作者在史丹佛快畢業時的副專案，2015-03-04 上傳第一支影片，2015–2016 在 Khan Academy 做影片，2016 年底起全職投入。**推論**：先有工具，後有頻道。你的 Claude Code 流程等於在複製「工具先行」這條路。
- **PanSci 泛科學**：總經理馮瑞麒在政大講座（2025-09-12，綜合院館三樓演講廳）談「從 1 到 100 萬訂閱」，重點是「並非靠偶然的爆紅影片，而是一套完整、以數據為基礎的頻道經營策略」。講座細節查不到。
- **Two Minute Papers、Welch Labs、漫士沉思錄**：本次研究查不到它們公開談論起步或突破影片的一手資料。

---

## 七、台灣觀眾對 AI 內容的需求規模

| 指標 | 數字（分母、日期、來源） |
|---|---|
| 生成式 AI 使用率 | 43.19%；付費訂閱率 8.54%（TWNIC《2025 台灣網路報告》，有效樣本 2,142 份，調查期間 2025-07-28 至 09-01，2025-12-17 發布） |
| AI 使用素養 | 66.23% 認為能用 AI 完成想做的事（同報告，樣本 1,405） |
| YouTube 觸及 | 98% 網路人口、超過 1,800 萬成人、人均每日 115 分鐘（YouTube Brandcast 2026，Google 台灣官方部落格） |
| YouTube 廣告觸及 | 1,840 萬人、總人口的 79.4%（DataReportal《Digital 2025 Taiwan》，2025 年初） |
| YouTube 作為新聞主要來源 | 14.67%（TWNIC 2025） |
| 台灣頻道的海外觀看 | 台灣頻道內容的觀看時間超過 40% 來自台灣以外（YouTube 內部資料，截至 2025-12，Brandcast 2026） |
| 「AI 原理講解」的直接需求數據 | **查不到** |

**推論**：大約 43% 的使用者已經在用生成式 AI，但只有 8.54% 願意付費，這表示「會用」的人很多，「想懂原理」的人是其中的少數。李宏毅頻道從 2024-02 到 2026-10 約成長 25 萬訂閱，是目前最接近「繁中觀眾想懂 AI 原理」的可觀察數字。合理的天花板假設是數萬到十多萬訂閱，不是百萬。

---

## 八、對你定位的三個啟示

1. **定位成「李宏毅課的 10 分鐘動畫入口」，而不是「台灣版 Two Minute Papers」。** 理由：Two Minute Papers 型的速報需要高頻更新，容易被判為「每支只差幾句話」的模板內容；繁中也已有泛科學院佔住「新工具」這個位置。機制講解（例如「注意力機制為什麼有效」「這篇論文改了 Transformer 的哪一步」）每支影片的概念天生不同，最容易通過 Generic or Repetitive Content 審查。可以在說明欄連結李宏毅的對應課程，借用他的信任度。（推論）
2. **讓「人類原創觀點」在影片裡看得見，把它當成流程的硬性關卡。** 官方條文判斷的是「是否加入創作者原創見解」與「是否只朗讀非自己創作的資料」。建議：（a）每支影片由你錄一段 30 秒的開場或結論，說明「為什麼這篇重要、我不同意哪裡」；（b）Claude Code 產出的比喻和視覺隱喻要有一份「本片獨有」清單，經你審核；（c）片頭片尾可以固定，但主體的動畫結構不能共用同一套模板；（d）旁白若是非本人的 TTS，主動勾選 AI 揭露；（e）不做擬真 AI 主持人。（依據官方政策的推論）
3. **一開始就設計成「繁中母片＋多語分發」。** 台灣頻道超過 40% 的觀看時間來自海外，3B1B 也沒有中文配音。YouTube 官方說明頁「Use automatic dubbing」（support.google.com/youtube/answer/15569972）的支援語言表列有「Chinese (Traditional) · English」，確認可以把繁中影片自動配音成英文（只支援配成英文），再加上簡體字幕，可以觸及簡中與英語觀眾。動畫用 Manim，畫面裡的文字盡量少，以降低多語化的成本。（推論）

---

## 研究方法與可能的遺漏

- **方法**：18 次網路搜尋（中英文混合，涵蓋政策、個別頻道、台灣數據、3B1B 中文化），抓取 4 個頁面全文（YouTube 營利政策頁、AI 揭露頁、Peggy K 部落格、HackMD 台灣 AI YouTuber 盤點），另外派 1 個子代理專查繁中／簡中 Manim 式 AI 頻道及最新訂閱數。
- **主要遺漏**：
  1. 無法直接讀取 YouTube 頻道頁和影片頁，所以**所有訂閱數都是第三方或報導數字**，留言分析樣本為 0。
  2. 搜尋預算有限，沒有查到 Bilibili 上其他繁中創作者、Threads 和 Podcast 上的潛在競品，也沒有查 Shorts 型 AI 講解帳號。
  3. 泛科學院的訂閱數只有頁面 metadata 的約 27.4 萬（擷取日期不詳），PanSci 只有講座自述的約 100 萬，兩者都沒有經過第三方統計核對。
  4. 2026-07 政策「再次改名」只有第三方說法，官方頁沒有標日期。
  5. 「2027 年 YPP 門檻提高」是單一第三方說法，未經查證。
  6. StatQuest 的數字來自日期不詳的 ALPHA Camp 文章，可能已經過時；AI Explained 和 Karpathy 已改用 usefulai.com 2026 年版清單（第三方）的數字。