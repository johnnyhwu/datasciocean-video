# v001 上傳清單：RRF 排名融合

Claude 不上傳。以下素材由你定稿後自己發布。

## 檔案

- [ ] 影片：`out/v001-rrf-rank-fusion/deliver/v001-rrf-rank-fusion.mp4`（1080p30，7 分 59 秒）
- [ ] 字幕：`out/v001-rrf-rank-fusion/deliver/subs.zh-TW.srt`、`subs.zh-CN.srt`（影片裡也內嵌了這兩軌軟字幕；上傳 SRT 才能在 YouTube 上切換與搜尋）
- [ ] 縮圖：`videos/v001-rrf-rank-fusion/thumbs/thumb.png`（1280×720）

## 標題＋縮圖（使用者 2026-11-16 定案）

**標題：RRF 排名融合：一個公式、一個旋鈕、一個盲點**

**縮圖：`videos/v001-rrf-rank-fusion/thumbs/thumb.png`**（1280×720）：大字「不看分數」、公式 Σ 1 ÷ (k + 名次)、發光的錘錘、底部是片尾的海。

- 專用構圖，原始檔是 `thumb.py`。元素都是成片裡出現的：公式（2:11 起）、錘錘、片尾動畫的海。
- 縮圖的字補充標題沒說的那一半：標題說「一個公式」，縮圖說這個公式的重點是不看分數、只看名次。
- 開場模式／寫法：明確目標／並列式。標題的三個詞對應影片的三大段：公式（2:11）、旋鈕（3:53）、盲點（4:32）。
- 過程：原本提的三組標題你覺得不夠有趣，以 C 為底改寫後選定；第一版縮圖（成片截圖加字）你覺得醜，重做成這一張。

## 說明欄

### 繁體中文

```
同一個問題同時問向量搜尋和全文搜尋，兩邊給的分數尺度不同，不能直接相加。
RRF（Reciprocal Rank Fusion）的做法是不看分數、只看名次：每一路給 1 ÷ (k + 名次)，再全部加起來。
但它有一個盲點：正確答案如果在其中一路完全沒被撈到，可能被排到後面。這集也會講怎麼補救。

延伸閱讀
完整文章：https://datasciocean.com/paper-intro/cerebras-rag/

章節
0:00 分數能不能相加
0:30 為什麼要合併
1:13 分數為什麼不能加
2:11 只看名次
3:53 k 是一個旋鈕
4:32 共識的盲點
6:03 怎麼補救
```

### English（只翻譯）

標題：Reciprocal Rank Fusion (RRF): One Formula, One Dial, One Blind Spot

```
Ask vector search and full-text search the same question, and their scores come on different scales, so you can't simply add them.
RRF (Reciprocal Rank Fusion) ignores the scores and looks only at ranks: each retriever contributes 1 ÷ (k + rank), and the contributions are summed.
But it has a blind spot: if the correct answer is completely missed by one of the retrievers, it can end up ranked lower. This episode also covers how to fix that.

Further reading
Full article (in Chinese): https://datasciocean.com/paper-intro/cerebras-rag/

Chapters
0:00 Can scores be added?
0:30 Why merge at all
1:13 Why scores can't be added
2:11 Looking only at ranks
3:53 k is a dial
4:32 The blind spot of consensus
6:03 How to fix it
```

### 简体中文（只翻譯）

標題：RRF 排名融合：一个公式、一个旋钮、一个盲点

```
同一个问题同时问向量搜索和全文搜索，两边给的分数尺度不同，不能直接相加。
RRF（Reciprocal Rank Fusion）的做法是不看分数、只看名次：每一路给 1 ÷ (k + 名次)，再全部加起来。
但它有一个盲点：正确答案如果在其中一路完全没被捞到，可能被排到后面。这集也会讲怎么补救。

延伸阅读
完整文章：https://datasciocean.com/paper-intro/cerebras-rag/

章节
0:00 分数能不能相加
0:30 为什么要合并
1:13 分数为什么不能加
2:11 只看名次
3:53 k 是一个旋钮
4:32 共识的盲点
6:03 怎么补救
```

## 上傳時的設定

- [ ] **AI use（Altered or synthetic content）建議答案：No。** 理由：旁白是你本人的複製聲音，畫面是非寫實的動畫。YouTube 官方把「複製自己的聲音做旁白」、非寫實動畫、AI 協助腳本與標題縮圖都列為不需揭露。
- [ ] **C2PA**：最終檔沒有殘留（`deliver/checks.json`）。
- [ ] **音樂標示**：不需要。品牌音樂是 Jonas Blakewood / Presentation（Pixabay Content License，可營利、不需標示）。Pixabay 的曲子偶爾會收到 Content ID 聲明；收到的話，用 `assets/music-library.yaml` 記的來源頁提出異議。
- [ ] **音效**：CC0，不需標示。
- [ ] **英文**：開啟 YouTube 自動配音（繁中配英文）；還不能用的話，告訴我，我再做英文翻譯字幕。
- [ ] **片尾畫面**：只能放在最後 5～20 秒（7:39 之後）。錘錘和字標在畫面正中間，推薦影片和訂閱鈕放左右兩側。這是第一支，還沒有下一支可以放，先放訂閱鈕。
- [ ] **播放清單**：這支屬於 Cerebras RAG 系列，系列名稱還沒定；之後有第二集時再建。

## 發布後

告訴我影片網址和發布時間，我記進狀態，之後可以做這支的回顧。
