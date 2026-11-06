# 讓 Claude Code 自動讀取自己 YouTube 頻道成效：官方 API、MCP server 與排程方案研究報告（資料查核日：2026-11-02）

**結論先講：自己寫一支本地 Python 腳本，直接呼叫官方 YouTube Analytics API 和 YouTube Reporting API，用作業系統排程（cron/launchd）每天跑，把結果寫進 repo；Claude Code 只負責每 10 支影片做一次分析。另外每月在 YouTube Studio 手動記一次 A/B 測試結果和營利門檻進度。** 原因有三：
- Google 沒有官方的 YouTube MCP server。
- 曝光次數與 CTR 只能從 Reporting API 的批次報表拿，而且要先建 job，只會從建 job 前 30 天開始有資料。
- Test & Compare 的 A/B 結果完全沒有 API。

## TL;DR

- **8 個指標中，有 6 個能用官方 API 完整取得，2 個只能部分取得或拿不到。**
  - **能完整取得：** 留存曲線、平均觀看時長與百分比、每支影片的新增/取消訂閱、流量來源、engaged views（Analytics API），以及曝光與 CTR（Reporting API 的 `channel_reach_basic_a1`，2026-01-15 才上線）。
  - **拿不到：** Test & Compare 的 A/B 結果。
  - **只能部分取得：** 頻道「qualified watch hours」，API 只能近似；訂閱總數 API 會四捨五入。
- **方案選擇：** Google 官方 MCP 目錄裡沒有 YouTube（2026-11 查核）。社群 MCP server 大多是 0–20 star 的個人專案，或者帶有寫入權限、或者要把憑證交給託管服務。**建議用方案 D（自寫腳本）為主，可選擇再包一層極小的唯讀本地 MCP**，讓 Claude Code 對談時能臨時查詢。
- **排程與坑：**
  - 排程交給作業系統的 cron/launchd，不要用 Claude Code 的雲端排程。雲端排程讀不到本機的 token 檔，最小間隔 1 小時，而且還在 research preview。
  - **最大的坑一：** OAuth consent screen 停在「Testing」時，refresh token 7 天就過期。解法是按「Publish app」改成 In production，但不送審。
  - **最大的坑二：** Analytics API 有 48–72 小時延遲，所以「第 7 天」的數據要在第 10 天左右才抓得到完整的。

---

## 一、摘要與結論（一頁版）

**名詞說明（首次出現）**
- **MCP**（Model Context Protocol，模型上下文協定）：讓 AI agent 透過標準介面呼叫外部工具的協定。
- **OAuth**（Open Authorization，開放授權）：讓程式在不拿到你密碼的情況下，取得你授權的存取權杖。
- **scope**（授權範圍）：OAuth 權杖被允許做哪些事的範圍字串。
- **CTR**（Click-Through Rate，點擊率）：曝光後被點擊的比例。
- **YPP**（YouTube Partner Program，YouTube 合作夥伴計畫）：YouTube 的營利資格計畫。
- **PT**（Pacific Time，美國太平洋時間）：YouTube API 計算日期用的時區。

**四個方案的結論**

- **A. 官方 API：三支 API 各司其職，缺一不可。**
  - **YouTube Analytics API（targeted queries，即時查詢型）：** 主力。留存、觀看時長、訂閱增減、流量來源、engagedViews 都在這裡。
  - **YouTube Reporting API（bulk reports，批次報表型）：** 唯一能拿到曝光與 CTR 的官方管道。
  - **YouTube Data API v3：** 用來列影片清單、取影片長度與發布時間、取公開觀看數。
- **B. Google 官方 MCP：查不到 YouTube 的官方 MCP server。** Google Cloud「Supported products」頁列出的是 BigQuery、Cloud Run、Cloud SQL 等 Cloud 產品，以及 Gmail、Drive 等 Workspace 產品，沒有 YouTube（2026-11-02 查核）。
- **C. 社群 MCP：有幾個能讀 Analytics API，甚至能讀 Reporting API 的 reach 報表，但都很新、star 很少。** 其中一部分還帶有上傳、刪除等寫入工具，不符合「只讀」需求。
- **D. 自寫腳本：最可控、最便宜、最好維護。** 你本來就熟 Claude Code 和 MCP，再寫一個約 200 行的 Python 腳本，加一個可選的小型 MCP 包裝，成本很低。

**對這個專案的建議**

- 主幹用方案 D。
- 曝光與 CTR 用 Reporting API 每天下載 reach 報表，存成原始 CSV。
- 第 7/28 天的快照用 Analytics API 抓。
- A/B 測試結果和 YPP 門檻進度每月在 Studio 手動記一次。
- **這是「API 加少量手動匯出」的混合方案，而且這就是目前最好的做法。**

---

## 二、指標對照表

圖例：✅ 能取得　🟡 部分取得或有限制　❌ 不能取得

| 指標 | A1 Analytics API | A2 Reporting API | A3 Data API v3 | B 官方 MCP | C 社群 MCP | D 自寫腳本或小型 MCP |
|---|---|---|---|---|---|---|
| 1. 曝光次數與曝光 CTR | ❌ metrics 清單沒有 impressions 或 impressionClickThroughRate（只有 card、annotation 的曝光）[metrics](https://developers.google.com/youtube/analytics/metrics) | ✅ `channel_reach_basic_a1`／`channel_reach_combined_a1`，欄位 `video_thumbnail_impressions`、`video_thumbnail_impressions_ctr`（2026-01-15 起）[channel reports](https://developers.google.com/youtube/reporting/v1/reports/channel_reports) | ❌ | ❌ 不存在 | 🟡 少數支援（如 gomcpgo/youtube_analytics 會自動排 Reporting job），多數不支援 | ✅ 走 Reporting API |
| 2. 開頭 30 秒留存、完整留存曲線 | ✅ `audienceWatchRatio`、`relativeRetentionPerformance`，搭配 `elapsedVideoTimeRatio` 維度；一次只能查一支影片；30 秒點要自己換算 [channel reports](https://developers.google.com/youtube/analytics/channel_reports) | ❌ 影片留存的維度目前沒有任何報表支援 | ❌ | ❌ | 🟡 部分支援（gomcpgo 的 `video_retention` 有 0:30 hook） | ✅ |
| 3. 平均觀看時長、平均觀看百分比 | ✅ `averageViewDuration`、`averageViewPercentage` | ✅（`channel_basic_a3` 報表，推論見細節） | ❌ 只有影片長度 | ❌ | 🟡 視專案而定 | ✅ |
| 4. 每支影片新增與取消訂閱 | ✅ `subscribersGained`、`subscribersLost`（限定影片時只計觀看頁上的訂閱） | ✅ | ❌ | ❌ | 🟡 | ✅ |
| 5. 流量來源 | ✅ `insightTrafficSourceType`；`insightTrafficSourceDetail` 每次最多 25 筆 | ✅ `channel_traffic_source_a3`，每日全量明細 | ❌ | ❌ | 🟡 | ✅ |
| 6. engaged views 與新舊觀看口徑 | ✅ `engagedViews` 與 `views` 並列 | ✅ `engaged_views` 欄位（2025-06-30 起的 a3 版報表） | 🟡 `viewCount` 只有公開數（新口徑），沒有 engaged | ❌ | 🟡 | ✅ |
| 7. 標題與縮圖 A/B（Test & Compare）結果 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ 只能在 Studio 看，要手動記錄 |
| 8. 訂閱總數、365 天有效公開觀看時數 | 🟡 可加總 gained 減 lost 估算訂閱；`estimatedMinutesWatched` 與 qualified watch hours 口徑不同 | 🟡 同左 | 🟡 `subscriberCount` 會被無條件捨去到 3 位有效數字 | ❌ | 🟡 | 🟡 近似值，精確值要看 Studio 的「營利」頁 |

---

## 三、8 個指標逐一查證

### 1. 曝光次數與曝光點擊率（CTR）

**事實**
- **Analytics API 沒有這兩個 metric。**
  - YouTube Analytics API 的 metrics 頁（最後更新 2026-09-14）列出的曝光類只有 `cardImpressions`、`cardTeaserImpressions`、`annotationImpressions`，以及營利用的 `adImpressions`。
  - 沒有 `impressions` 或 `impressionClickThroughRate`。[metrics](https://developers.google.com/youtube/analytics/metrics)
- **Reporting API 在 2026-01-15 新增了 reach 報表。** Revision history 寫明：「The YouTube Reporting API now supports reach reports for channels and content owners. Reach reports provide statistics for video thumbnail impressions and click-through rates.」[revision history](https://developers.google.com/youtube/reporting/revision_history)
  - 頻道可用的兩種報表：
    - `channel_reach_basic_a1`：維度是 date、channel_id、video_id。
    - `channel_reach_combined_a1`：再加上流量來源與裝置維度。
  - 兩者的 metric 都是 `video_thumbnail_impressions` 和 `video_thumbnail_impressions_ctr`。[channel reports](https://developers.google.com/youtube/reporting/v1/reports/channel_reports)
- **口徑定義：**
  - 縮圖顯示超過 1 秒、且至少 50% 可見，才算一次曝光。
  - CTR 是點擊數除以曝光數。[Reporting metrics](https://developers.google.com/youtube/reporting/v1/reports/metrics)

**推論：** 社群專案（如 vitoropereira 的 PR #95）也實測發現 Analytics API 查不到曝光，必須改走 Reporting API。這和官方文件一致。不過那些 PR 多半註明「尚未用真實報表驗證 CTR 單位」。所以 CTR 到底是 0–1 的比例還是 0–100 的百分比，第一次拿到檔案時要自己確認。

### 2. 開頭留存與完整留存曲線

**事實**
- Analytics API 的「Audience retention」報表：
  - 維度必須是 `elapsedVideoTimeRatio`。
  - metric 包括 `audienceWatchRatio`、`relativeRetentionPerformance`、`startedWatching`、`stoppedWatching`、`totalSegmentImpressions`。
  - filter 必須是 `video`，而且「the value must specify a single video ID」，也就是一次只能查一支影片。[channel reports](https://developers.google.com/youtube/analytics/channel_reports)
- 官方範例的寫法是 `filters=video==VIDEO_ID;audienceType==ORGANIC`。[sample requests](https://developers.google.com/youtube/analytics/sample-requests)
- 影片會被切成 100 段。例如 5 分鐘的影片，每段約 3 秒。[metrics](https://developers.google.com/youtube/analytics/metrics)
- **Reporting API 拿不到影片留存。** Revision history 說明 `elapsed_video_time_percentage`、`audience_retention_type` 兩個維度「not currently supported by any reports」。它只有播放清單的留存報表。[revision history](https://developers.google.com/youtube/reporting/revision_history)

**推論：** API 沒有「第 30 秒仍在看的比例」這個現成欄位。做法是用 Data API 取得影片長度 L 秒，再取 `elapsedVideoTimeRatio` 最接近 30/L 那一段的 `audienceWatchRatio` 值。這個值可能大於 1，因為有重看。它和 Studio 的「開頭留存」口徑不一定完全一致，建議同時存整條曲線。

### 3. 平均觀看時長與平均觀看百分比

**事實**
- `averageViewDuration`（秒）和 `averageViewPercentage` 在 Analytics API 的基本報表、時間序列報表都能查，也能用 `video` filter 限定單支影片。[channel reports](https://developers.google.com/youtube/analytics/channel_reports)
- 注意一個限制：`liveOrOnDemand` 維度不能和 `averageViewPercentage` 同時用。

**推論：** Reporting API 的 `channel_basic_a3` 也有對應欄位（平均觀看秒數與百分比）。這次沒有逐欄核對 a3 版的欄位表，使用前請以 `reportTypes.list` 的實際 CSV 表頭為準。

### 4. 每支影片的新增與取消訂閱

**事實：** `subscribersGained` 和 `subscribersLost` 都是 core metric。但官方明說：「in reports that use either the video dimension or the filter parameter to restrict the response to only include data for a particular video, the subscribersGained metric will only include statistics from the specified video's watch page.」[metrics](https://developers.google.com/youtube/analytics/metrics)

**推論：** 單支影片的訂閱數會低估影片的真實貢獻，因為從頻道頁、Shorts 等地方的訂閱不會算進去。做「10 支影片橫向比較」沒問題，但不要拿來和頻道總訂閱數直接相加對帳。

### 5. 流量來源

**事實**
- Analytics API 的 `insightTrafficSourceType` 可以分出 YT_SEARCH（搜尋）、BROWSE（首頁、瀏覽功能）、RELATED_VIDEO（相關影片推薦）、EXT_URL（外部網站）等類別。
- `insightTrafficSourceDetail`（例如搜尋關鍵字、哪支影片推薦過來）的報表限制：
  - 必須 `maxResults` ≤ 25。
  - 必須帶 `insightTrafficSourceType` filter。
  - END_SCREEN、NOTIFICATION 等來源不支援。[channel reports](https://developers.google.com/youtube/analytics/channel_reports)、[dimensions](https://developers.google.com/youtube/analytics/dimensions)
- 自 2024-11-18 起，流量來源報表的「影片數 × 天數」超過 50,000 會回錯誤。[revision history](https://developers.google.com/youtube/reporting/revision_history)
- Reporting API 的 `channel_traffic_source_a3` 報表是每日全量，帶 traffic source detail。

### 6. engaged views 與 2026 年 8 月的觀看數口徑改版

**事實：改版確實存在。** 使用者記憶的「2026 年 8 月改版」是正確的。

- **時間線：**
  - **2025-03-31：** Shorts 先改成從第一格畫面開始算觀看。
  - **2025-04-30：** Analytics API 新增 `engagedViews`，代表舊口徑。
  - **2025-06-30：** Reporting API 的報表升到 a3 版，新增 `engaged_views` 欄位。[revision history](https://developers.google.com/youtube/reporting/revision_history)
  - **2026-08-17：** TeamYouTube 在社群論壇公告，依 Tech Times 報導。
  - **2026-08-19：** YouTube 官方部落格說明：「Starting August 24, 2026, views across YouTube are counted from the first frame going forward — Shorts, Long Form, Podcasts, Live; all the formats.」舊定義改名為 engaged view。[YouTube Blog](https://blog.youtube/inside-youtube/engaged-views-youtube-explained/)
  - **2026-08-27：** API revision history 正式記錄這次變更。
- **2026-08-27 那筆 revision history 的內容：**
  - View 狀態是「Updated」，定義為「Video plays from the first frame」。
  - Engaged View 狀態是「Unchanged」，定義為「Playback continues past the first frame, or the user clicks/taps to play」，用途包括 YPP 營利，以及「majority of core analytics (click-through rate, average view duration)」。
  - 同時把 YPP 門檻用語改為「qualified watch hours」「qualified Shorts views」。
  - API 文件的變動只有「Updated the definition of the engagedViews metric」。[revision history](https://developers.google.com/youtube/reporting/revision_history)
- **API 層面：沒有新增任何 metric 或欄位。** `engagedViews` 和 `engaged_views` 是 2025 年就有的。Analytics API 的 `views` 定義只寫「This metric represents different numbers in different types of reports」，沒有明寫口徑。[metrics](https://developers.google.com/youtube/analytics/metrics)

**推論**
- API 的 `views` 從 2026-08-24 起，在長影片上應該也採用第一格畫面口徑，因為官方說 View 已「Updated」，且是「Standard public view counts」。但 API metrics 頁沒有逐字確認，所以標為推論。
- 對這個專案來說，**跨期比較一律用 `engagedViews`**。`views` 一起存，但 2026-08-24 前後的數字視為斷點，不要直接比較。
- 第三方部落格（Vanpelt Studio）提到一週後 Studio 又加了「views (co-viewed)」指標。**在 API 文件裡查不到這個 metric。**

### 7. 標題與縮圖 A/B 測試（Test & Compare）

**事實：**
- YouTube 說明中心寫明，測試結果在「video's Details page or the Reach tab of your video's Analytics page」查看。
- 勝負依「watch time share」判定，不是 CTR。[YouTube Help](https://support.google.com/youtube/answer/16391400?hl=en-GB)

**查不到：** Analytics、Reporting、Data 三支 API 的 metrics、reports、revision history 裡，都查不到任何 A/B 測試結果的端點或欄位。

**替代做法：**
- 測試結束後，手動在 repo 的 `ab_tests.yaml` 記錄三項資料：各版本、watch time share、結果標籤（Winner、Performed same、Inconclusive）。
- reach 報表是按日的，可以用「換縮圖日期」切段，比較前後 CTR。但同一天內切換的那天要排除。社群專案 Deveadra/katcha 的 issue #70 就這樣設計。這是準實驗，不能等同 A/B 結果。

### 8. 頻道層級：訂閱總數、365 天有效公開觀看時數

**事實**
- **訂閱總數：**
  - Data API 的 `statistics.subscriberCount`「is rounded down to three significant figures」。
  - 官方明說，即使是授權讀自己的頻道也一樣；精確值只能在 Studio 看。[Data API revision history 2019-09-10](https://developers.google.com/youtube/data/revision_history)、[channels](https://developers.google.com/youtube/v3/docs/channels)
- **YPP 門檻現況：** 1,000 訂閱，加上「4,000 qualified watch hours on long-form videos (past 365 days)」，或 1,000 萬 qualified Shorts views（90 天）。[YouTube Creators](https://www.youtube.com/creators/earn/youtube-partner-program/) 依 YouTube 說明中心「Changes to the YouTube Partner Program」頁，500 訂閱這一級（fan funding、Shopping）的門檻不變：「500 subscribers and either 3,000 qualified watch hours in the last year or 3M qualified Shorts views in the last 90 days」。另外從 2027-02-01 起，要從 Shorts Creator Pool 分潤，必須「maintain 10M qualified Shorts views over the last 90 days」。[YouTube Help](https://support.google.com/youtube/answer/12843009)
- **2027 年起的門檻：** YouTube 說明中心「Changes to the YouTube Partner Program」頁原文：「Starting Feb. 1, 2027, YPP entry thresholds for new creators are changing to 8,000 qualified watch hours in the last 365 days, or 20M qualified Shorts views in the last 90 days, in addition to still needing 1k subscribers. If you are already in YPP, your status is not impacted by this update.」[YouTube Help](https://support.google.com/youtube/answer/12843009) YouTube 官方部落格〈New opportunities to earn and changes to the YouTube Partner Program〉也寫明，新條款「will take effect on February 1, 2027」。[YouTube Blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/) 公告日期 2026-08-10 出自第三方報導，部落格頁面上沒有直接看到日期。
- **哪些觀看時數不算數：** 官方說明列出私人影片、不公開影片、已刪除影片、Shorts feed 的觀看時數等，都不計入 qualified watch hours。[YouTube Creators](https://www.youtube.com/creators/earn/youtube-partner-program/)
- **API 的觀看分鐘數定義：** `estimatedMinutesWatched` 是「The number of minutes that users watched videos for the specified channel」，沒有排除上述類型。[metrics](https://developers.google.com/youtube/analytics/metrics)

**推論：口徑不一致，兩者不能直接比。** 近似做法是：
- 用 Analytics API 加總過去 365 天的 `estimatedMinutesWatched`，再除以 60。
- 用 `creatorContentType` 維度排除 SHORTS，只保留目前仍公開的影片。
- 算出來仍只是近似值。申請時以 Studio「營利」頁的進度條為準。

**對你的意義（推論）：** 新頻道幾乎不可能在 2027-02-01 前達到 4,000 小時，所以實際目標應該抓 8,000 小時。

---

## 四、各方案逐項評估

### 方案 A：YouTube 官方三支 API

| 項目 | Analytics API v2 | Reporting API v1 | Data API v3 |
|---|---|---|---|
| 用途 | 即時、客製查詢（單支影片、留存、流量來源） | 每日批次 CSV（全量；曝光與 CTR 只在這裡） | 影片清單、長度、發布時間、公開統計 |
| scope | `yt-analytics.readonly`（營收才需要 `yt-analytics-monetary.readonly`） | `yt-analytics.readonly` 或 monetary 版 | `youtube.readonly` |
| 配額 | 官方只說「Each API request … counts as one unit」，沒有公開預設數字，要到 Cloud Console 的 Quotas 頁看 | 官方說「Quota usage is not an issue」，沒有公開數字 | 預設 10,000 units/天，`videos.list` 每次 1 unit；`search.list`、`videos.insert` 各有獨立的每日 100 次額度；每天 PT 午夜重置 [quota](https://developers.google.com/youtube/data/determine_quota_cost) |
| 費用 | 免費 | 免費 | 免費 |
| 延遲 | 48–72 小時，endDate 會被截到最後一個處理完的日子（2026-09-09 文件新增）[data model](https://developers.google.com/youtube/analytics/data_model) | 建 job 後 24 小時內產生第一份報表；會回補建 job 前 30 天；歷史報表保留 30 天，一般報表保留 60 天 [reports](https://developers.google.com/youtube/reporting/v1/reports) | 近即時（官方建議即時數字用 `videos.list`） |

- **配額的來源：** Analytics 與 Reporting 的配額說明，來自 [data model](https://developers.google.com/youtube/analytics/data_model) 和 [Reporting overview](https://developers.google.com/youtube/reporting)。
- **推論：** 以每週數支影片的規模，三支 API 的配額都用不完。

**認證（三支共用）**
- **不能用 service account。** Google 官方文件〈YouTube Data API: Implementing OAuth 2.0 Authorization〉寫明：「Since there is no way to link a Service Account to a YouTube account, attempts to authorize requests with this flow will generate a NoLinkedYouTubeAccount error.」[OAuth guide](https://developers.google.com/youtube/v3/guides/authentication)
- **不能用 API key。** API key 只能讀公開資料。
- **必須用 OAuth installed-app（桌面應用程式）流程。** 官方另外註明這兩支 API「do not currently support the OAuth 2.0 flow for devices」。[authorization](https://developers.google.com/youtube/analytics/authentication?hl=pt-BR)
- **scope 分級有兩種說法，並列如下：**
  - Phyllo 說所有 YouTube scope 都屬於 sensitive（敏感）。
  - conorbronsdon/yt-analytics-mcp 說 `yt-analytics.readonly`、`youtube.readonly` 是 sensitive 而非 restricted，自用不必走審核，點過「未驗證」警告即可。
  - 兩者並不矛盾。**結論：屬於 sensitive，但個人自用不需要送審。**

### 方案 B：Google 官方或半官方 MCP server

**事實**
- Google Cloud「Supported products」頁（2026-11-02 查核）列出的遠端 MCP server，包括 Agent Registry、AlloyDB、BigQuery、Cloud Run、Cloud SQL、Cloud Storage、Cloud Logging 等。另外 Workspace 列出 Gmail、Drive、Docs、Sheets、Calendar、Chat 等。**沒有 YouTube。** [supported products](https://docs.cloud.google.com/mcp/supported-products)、[Workspace MCP](https://developers.google.com/workspace/guides/configure-mcp-servers)
- github.com/google/mcp 的清單裡也沒有 YouTube。[google/mcp](https://github.com/google/mcp)
- Google 有官方的 Google Analytics（GA4）MCP server，2025-07 發布，標示 Experimental、唯讀、本地執行。**但它是網站分析，不是 YouTube Analytics。** [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)
- 第三方 Scalekit 的文章（2026）也寫「Google ships no official YouTube MCP server」。[Scalekit](https://www.scalekit.com/blog/youtube-mcp-vs-api)

**推論：** 你提到 blog 用的 Search Console MCP，多半也是社群版。Google 同樣沒有官方的 Search Console MCP，這點有第三方整理可佐證。

**結論：方案 B 目前不存在。查不到任何 Google 預告要推出 YouTube MCP 的一手來源。**

### 方案 C：社群或第三方 YouTube MCP server

**查核限制：** star 數和最後 commit 日期，只有在抓到頁面時才記錄。其餘標「未確認」，不猜。

| 專案 | 支援的 API | 寫入權限 | 執行位置與憑證 | 品質訊號（查核時） | 能拿到的指標 |
|---|---|---|---|---|---|
| gomcpgo/youtube_analytics（Go，MIT） | Data、Analytics v2、Reporting（自動排 reach job） | 文件聲稱「never modifies your videos」；要求 `youtube.readonly`、`yt-analytics.readonly`、`yt-analytics-monetary.readonly` | 本地；token 存在 OS config 目錄 | 0 star、1 個 commit | 1、2（含 0:30 hook）、3、4、5、6；7 和 8 不行 |
| conorbronsdon/yt-analytics-mcp（TypeScript） | Analytics `reports.query` | 唯讀（專案定位就是 curated read-only） | 本地；installed-app refresh token；作者明說是搭配 gsc-mcp 使用 | 0 star、2 個 commit | 2–6；沒有 Reporting，所以沒有曝光與 CTR |
| pauling-ai/youtube-studio-mcp（PyPI `youtube-studio-mcp`） | Data、Analytics、Reporting | 有影片管理等寫入工具 | 本地；token 存在 `~/.youtube-mcp/token.json` | 依另一專案 README 引述約 19 star（日期未確認） | 多數指標可取得 |
| oliverhruby/youtube-mcp（`youtube-mcp-full`） | 號稱三支 API 接近 1:1 覆蓋 | 有寫入 | 本地或 Docker | 未確認 | 多數指標可取得 |
| sigvardt/youtube-mcp（`youtube-complete-mcp`） | 三支 API | Data API 可讀寫，但刻意排除 `videos.delete` | 本地 | 未確認 | 多數指標可取得 |
| dogfrogfog/youtube-analytics-mcp | Analytics、Data | 未確認 | 本地；`credentials.json` 放在 `src/auth/` 目錄（有誤 commit 的風險） | 未確認 | 2–6 |
| ZubeidHendricks/youtube-mcp-server 等 | 只有 Data API（API key） | 無 | 本地 | 依 oliverhruby README 引述約 568 star | 只有公開數字，1–5 全部拿不到 |
| PulseMCP 上的託管型（如「Maagpi YouTube」「YouTube Organic Analytics」） | 未確認 | 部分含上傳 | **託管：OAuth 授權會交給第三方** | PulseMCP 頁顯示 2026-04 到 06 有更新 | 未確認 |

- **專案來源：** [gomcpgo](https://github.com/gomcpgo/youtube_analytics)、[conorbronsdon](https://github.com/conorbronsdon/yt-analytics-mcp)、[youtube-studio-mcp](https://pypi.org/project/youtube-studio-mcp/)、[youtube-mcp-full](https://pypi.org/project/youtube-mcp-full/)、[youtube-complete-mcp](https://pypi.org/project/youtube-complete-mcp/)、[PulseMCP](https://www.pulsemcp.com/servers?q=youtube)

**評估（推論）**
- **品質：** 沒有一個專案同時滿足「有一定使用者基數」「唯讀」「支援 Reporting reach」三個條件。gomcpgo 功能最貼近需求，但只有 1 個 commit、0 star。
- **安全性：**
  - 託管型要把 YouTube OAuth 授權交給第三方，不建議。
  - 本地型的風險在於第三方程式碼拿到你的 refresh token。如果要用，請 fork 後鎖定 commit，並審過程式碼。
- **結論：** 社群 MCP 適合拿來參考實作，例如 gomcpgo 的 hook 計算方式、reach job 的排程邏輯。不建議直接當成生產依賴。

### 方案 D：自寫腳本，可選擇再包一層極小的本地 MCP

- **做法：** 用 Python 加 `google-api-python-client`、`google-auth-oauthlib`，建三個 client：`youtubeAnalytics` v2、`youtubereporting` v1、`youtube` v3。
- **設定難度：** 低到中。最麻煩的是 Google Cloud 專案的 OAuth 設定，第一次約 30–60 分鐘（推論）。
- **維護成本：** 低。要做的事只有三件：
  - API 欄位改版時調整，例如 2025 年 Reporting 報表從 a2 升到 a3。
  - 每 60 天內一定要把 Reporting 報表下載下來。
  - 留意 refresh token 失效。
- **小型 MCP 包裝（可選）：** 用官方 MCP Python SDK 包 3–4 個唯讀工具，例如 `get_video_snapshot`、`get_retention`、`query_analytics`。讓 Claude Code 在分析對話中臨時補查。資料抓取仍然交給排程腳本。

**推論：** 排程抓取用確定性的腳本，比讓 LLM 每次自己組 API query 更穩定、更可重現。MCP 只留給互動式探索。

---

## 五、認證設定與 token 不過期的方法

1. **建立 Google Cloud 專案。** 啟用 YouTube Data API v3、YouTube Analytics API、YouTube Reporting API。
2. **設定 OAuth consent screen**（現在叫 Google Auth Platform → Audience）：
   - User type 選 **External**。個人 Gmail 不能選 Internal。
   - 在 Data Access 加入 `.../auth/yt-analytics.readonly` 和 `.../auth/youtube.readonly`。
   - 頻道還沒加入 YPP 前，**不要加** `yt-analytics-monetary.readonly`。非 YPP 頻道查營收會回 403；而且最小權限原則也不需要它。
3. **按「Publish app」把狀態改成 In production，但不送審。**
   - **事實：**
     - Google 文件說，Testing 狀態下「If your OAuth client requests an offline access type and receives a refresh token, that token will also expire」。實務上是 7 天。[Google Cloud Help](https://support.google.com/cloud/answer/15549945?authuser=7)
     - Google Health API 文件則寫 In production 的 refresh token「generally don't expire unless they are revoked or remain unused for a prolonged period (typically six months)」。[Google Health setup](https://developers.google.com/health/setup?authuser=0000)
   - **代價：**
     - 授權時會出現「Google hasn't verified this app」警告，點「進階 → 前往（不安全）」即可。
     - 未驗證的 app 有「100 new users in total」上限，對你自用沒有影響。
   - **事實（第三方實測）：** Testing 狀態下，授權回應的 JSON 會帶 `refresh_token_expires_in` 欄位，可以用它確認自己是否還在 7 天模式。[DEV Community](https://dev.to/ko-hi/googles-oauth-testing-mode-expires-refresh-tokens-in-7-days-publish-the-consent-screen-before-24hm)
   - **注意：** 改成 Production 之後，**要重新跑一次授權**，才會拿到不會 7 天過期的新 token。
4. **建立 OAuth client，類型選 Desktop app。** 用 `InstalledAppFlow.run_local_server()` 跑一次 loopback 授權，記得 `access_type=offline`。
5. **brand account（品牌帳戶）頻道：** 授權畫面會先選 Google 帳號，再選頻道。**一定要選到那個品牌頻道。** 之後查詢用 `ids=channel==MINE`，它會回傳「authenticated user's channel」。[channel reports](https://developers.google.com/youtube/analytics/channel_reports)
   - **事實（社群經驗）：** 有開發者回報，選錯頻道或用了錯的身分，會收到 403。[gist](https://gist.github.com/veuncent/e0b831ab41d598961d2656c7fc5cc0f9?permalink_comment_id=4257646)
   - **推論：** 授權完成後立刻用 Data API 的 `channels.list?mine=true` 核對 channel ID，並寫進設定檔。每次執行時比對一次。
6. **scope 的需求有兩種說法：** 有第三方文章（rapidevelopers）聲稱 `reports.query` 現在「必須」同時有 `youtube.readonly`，這點查不到官方確認。反正你本來就要用 Data API，同時申請這兩個 scope 就不會踩到。

---

## 六、給 Claude Code 的設定步驟概要

**1. 目錄與憑證（安全性）**
- `client_secret.json` 和 `token.json` 放在 repo 外，例如 `~/.config/yt-analytics/`，權限設為 `chmod 600`。
- 或者用 Python `keyring` 存進 macOS Keychain 或 Windows Credential Manager。
- repo 的 `.gitignore` 預先加入 `*client_secret*.json`、`token*.json`、`.env`，並加上 pre-commit 的 secret 掃描。
- **權限限制：** scope 只給 `yt-analytics.readonly` 和 `youtube.readonly`，這兩個 scope 本身就無法上傳或修改。這是 API 層級的唯讀保證。

**2. 一次性初始化（現在就做）**
- 跑 `auth.py`，完成授權並核對頻道 ID。
- 跑 `setup_reach_job.py`：呼叫 `jobs.create` 建立 `channel_reach_basic_a1` job。建議同時建 `channel_reach_combined_a1`、`channel_basic_a3`、`channel_traffic_source_a3` 三個 job。
- **一定要在發布第一支影片前建好。** Reporting API 只從建 job 起算，最多回補前 30 天。[reports](https://developers.google.com/youtube/reporting/v1/reports)

**3. 每日排程（作業系統 cron 或 launchd，建議每天台灣時間 18:00，約為 PT 凌晨）**

`fetch_daily.py` 依序做四件事：
1. 用 `jobs.reports.list` 下載所有新報表（含回補的 backfill 版本），原樣存成 `data/raw/reporting/<report_type>/<date>_<createTime>.csv`。
   - backfill 會取代舊資料，所以要用「同一天取最新 createTime」做冪等合併。
2. 讀 `videos.yaml`，也就是發布日清單，可以用 Data API 的 uploads playlist 自動同步。
   - 找出「發布後滿 10 天、還沒有 d7 快照」和「發布後滿 31 天、還沒有 d28 快照」的影片。
3. 對這些影片用 Analytics API 抓三類資料：
   - 窗口為 [發布日, 發布日+6] 或 [發布日, 發布日+27]（PT 日期）的基本 metrics。
   - 流量來源。
   - 留存曲線（每支一次查詢）。
   - 再從 reach CSV 加總同一窗口的曝光數，並算出加權 CTR。
4. 寫入快照後 `git commit`。

**為什麼是第 10 天和第 31 天（推論）：** 官方說延遲 48–72 小時，而且 endDate 會被截斷。晚 3 天抓，才能保證窗口完整。腳本要檢查回傳資料的最後日期是否等於窗口終點，不等於就延後重試。

**4. Claude Code 的角色**
- 每累積 10 支有 d28 快照的影片，由 Claude Code（手動下指令，或用 hook 偵測）讀 `data/videos/*/d28.json`，產出 `reports/analysis_NN.md`。
- **Claude Code 的排程功能比較（事實，code.claude.com 文件，2026-11-02 查核）：**
  - **雲端排程任務（原名 routines，`/schedule`）：** 在 Anthropic 雲端執行，每次是全新 clone，「Access to local files: No」，最小間隔 1 小時，仍是 research preview。**它讀不到本機的 token 檔。** 要用的話，得把 refresh token 放進雲端環境變數，而官方警告「Anyone who uses the environment can read the values」，不建議這樣做。
  - **Desktop 本地排程任務：** 能讀本機檔案，但電腦睡眠時會跳過；醒來後只補跑 7 天內最近的一次。
  - **`/loop`：** 綁定在 session 上，7 天後過期。
  - [scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks.md)、[routines](https://code.claude.com/docs/en/routines)、[desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks)
  - **推論：** 抓資料用作業系統 cron；如果你的機器會關機，改放到家用常開的機器或小 VM。Claude Code 只在分析時使用。另一個選項是 GitHub Actions 的 schedule，但要把 refresh token 放進 GitHub Secrets，憑證就離開本機了，安全性取捨請自行評估。

**5. repo 格式建議**
```
data/
  channel.json                  # channel_id、建 job 時間、各 report job id
  videos.yaml                   # video_id、publish_at(UTC)、duration_s、title、thumbnail_version
  raw/reporting/channel_reach_basic_a1/2026-11-01_<createTime>.csv
  videos/<video_id>/
    d7.json  d28.json           # 每個 JSON 含 schema_version、fetched_at、window_pt、data_through_pt、metrics{views, engagedViews, estimatedMinutesWatched, averageViewDuration, averageViewPercentage, subscribersGained, subscribersLost, impressions, impressions_ctr}
    retention_d28.csv           # elapsedVideoTimeRatio, audienceWatchRatio, relativeRetentionPerformance
    traffic_d28.csv             # insightTrafficSourceType, views, engagedViews, estimatedMinutesWatched
  manual/ab_tests.yaml          # 手動：Test & Compare 結果
  manual/ypp_progress.yaml      # 手動：每月 Studio「營利」頁的訂閱數與 qualified watch hours
```
- JSON 適合 git diff 和 Claude 閱讀；曲線、明細用 CSV。
- 每份快照都記下 `view_definition: "first_frame_since_2026-08-24"`，避免日後誤比。

**6. 手動部分（每月約 5 分鐘）**
- A/B 測試結果。
- Studio「營利」頁的精確訂閱數與 qualified watch hours。
- 必要時用 Studio 進階模式匯出 CSV 對帳。說明中心提到匯出上限是 500 列。[YouTube Help](https://support.google.com/youtube/answer/9717005?hl=en)

---

## 七、已知的坑

1. **7 天 token 過期。** Testing 狀態下 refresh token 7 天過期。要改 In production，並**重新授權**。In production 的 token 若約 6 個月沒用也會失效；每日排程自然就避開了。
2. **曝光與 CTR 不在 Analytics API。** 只在 Reporting API 的 reach 報表（2026-01-15 起），而且只從建 job 起算、回補 30 天。更早的資料只能在 Studio 看。
3. **Reporting 報表會過期。** 一般報表 60 天後刪除，歷史回補報表 30 天後刪除。job 長期沒人下載時，也可能被設定 `expireTime` 而停止產生。[jobs](https://developers.google.com/youtube/reporting/v1/reference/rest/v1/jobs)
4. **延遲 48–72 小時，endDate 會被截斷。** 回傳的資料可能比你要的窗口短，而且不會報錯。
5. **日期以太平洋時間計。** Data API 配額在 PT 午夜重置。社群實作指出 Reporting 檔案是固定的 PST（UTC-8）日。台灣時間的「第 7 天」和 PT 會差一天，要統一用 PT。
6. **留存曲線一次只能查一支影片。** filter 不能用逗號列多支。
7. **流量來源明細最多 25 筆**，而且「影片數 × 天數」不能超過 50,000。
8. **單支影片的訂閱數只計觀看頁上的訂閱。**
9. **觀看數口徑在 2026-08-24 斷點。** 一律用 `engagedViews` 做跨期比較。
10. **訂閱總數在 API 會被捨去**到 3 位有效數字；qualified watch hours 和 `estimatedMinutesWatched` 口徑不同。
11. **brand account 授權要選對頻道。** 用 `channels.list?mine=true` 核對。
12. **非 YPP 頻道請求營收 metrics 會回 403。** 先不要加 monetary scope。
13. **Analytics API 的配額沒有公開數字。** 要在自己專案的 Cloud Console 查看；以這個規模不會用完（推論）。
14. **API 回傳的欄位順序以 header 為準。** 透過 Data API 存下的影片中繼資料，依開發者政策要在 30 天內刷新或刪除。[data model](https://developers.google.com/youtube/analytics/data_model)
    - **推論：** 你自己頻道的 Analytics 數字不是 Data API 的資源中繼資料，但 title 這類欄位屬於中繼資料，建議每次跑排程時一併刷新。

---

## 八、注意事項

- **報告日期：** 本報告依 2026-11-02 能取得的官方文件撰寫。Reporting API 的 revision history 最新一筆是 2026-10-30；Analytics API 的 metrics 頁最後更新是 2026-09-14。
- **其他未逐一核實的項目：**
  - 社群 MCP 專案的 star 數與 commit 日期，只有部分抓到頁面，其餘標「未確認」。ZubeidHendricks/youtube-mcp-server 的 star 數各來源不一致，查不到確定數字。
  - Reporting API 的 `channel_basic_a3` 欄位，以及 CTR 的數值單位（0–1 或 0–100），請在第一次拿到 CSV 時確認。