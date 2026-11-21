# v002 上傳清單：CER 信心加權投票

還沒上傳。你看完成片、定好標題之後，說一聲我才會用 `lib/upload.py` 上傳成**私人**；公開由你自己按。

## 檔案

- [ ] 影片：`out/v002-cer-confidence-voting/deliver/v002-cer-confidence-voting.mp4`
- [ ] 字幕：`out/v002-cer-confidence-voting/deliver/subs.zh-TW.srt`、`subs.zh-CN.srt`
- [ ] 縮圖：`videos/v002-cer-confidence-voting/thumbs/A.png`（1280×720，使用者 2026-11-21 選定）。上傳時用的是第一版 `thumb-v1.png`，要在 Studio 換成 A

## 標題（暫定，等你選）

**同一題問 AI 五次，答案不一樣，該信哪個？｜CER**（候選與理由在 `review/gate4.md`）

## 縮圖

2026-11-21 第四版 `thumbs/D.png`（待使用者確認）：只留兩個超大數字，375 打叉、400 發光打勾，大字「AI 多數決 竟然錯了」（使用者要求補上「AI 多數決」）。使用者：「站在一個笨笨的人類的角度…除非真的 catch his eyes」。出處 h2、s5（400＝100×5×0.8）、e6、b4；數字是片中假設的例子。

先前：第三版，**使用者選 A**：「AI 多數決 選錯了」。三顆冒汗的票 375 ✗、兩顆笑臉 400 ✓（h1～h3、e6「又被騙過去了」；400＝100×5×0.8，s5；數字都是片中假設的例子）。
沒選的 B（「AI 很猶豫 也算一票？」）、C（「AI 投票 看信心」）留在 `thumbs/`；第二版在 `thumbs/v2/`。原始檔 `thumb.py`。
標題 2026-11-21 改成「同一題問 AI 五次，答案不一樣，該信哪個？｜CER」。使用者：舊標題「實在太不吸引人了」、第二輪「太深奧，把一般滑手機的人類想的笨一點」，選定這個。

## 說明欄

2026-11-21 加上原始論文連結（使用者要求）。查證：ACL Anthology 2025.acl-long.390 與 arXiv 2502.14634 的標題都是「CER: Confidence Enhanced Reasoning in LLMs」，ACL 2025 Main 和卡上的文章標題一致；只查網址與標題，沒讀內容。影片已上傳，這段要由使用者在 Studio 的說明欄貼上（三種語言）。

### 繁體中文

```
同一道題讓 AI 算好幾次，再用多數決選答案，這是 Self-Consistency（SC）的做法。但它把每一條推理路徑都算成一票，聽不到模型的猶豫。
CER 讓猶豫的票變輕：替每一條路徑算一個信心分數，再把支持同一個答案的分數加起來。分數怎麼算，要回答兩個問題：看哪幾步？每一步都算，越後面的步驟越重。每一步怎麼量？只看中間答案那幾個 token 的機率。它不需要訓練任何模型。
這集也會講它的極限：模型原本沒有的知識，信心怎麼算都補不了。

延伸閱讀
完整文章：https://datasciocean.com/paper-intro/cer/
原始論文（ACL 2025）：CER: Confidence Enhanced Reasoning in LLMs
https://aclanthology.org/2025.acl-long.390/
arXiv：https://arxiv.org/abs/2502.14634

章節
0:00 五票的難題
0:30 多數決怎麼做
1:15 每一票都一樣重
1:45 讓票有輕重
2:37 看哪幾步
3:39 每一步怎麼量
5:01 合成一張票
5:52 它的極限
6:45 三點回顧
```

### English（只翻譯）

標題：Ask an AI the Same Question Five Times, Get Different Answers: Which One Do You Trust? | CER

```
Ask an AI the same question several times and pick the answer by majority vote: that is Self-Consistency (SC). But it counts every reasoning path as one vote, so it cannot hear the model's hesitation.
CER makes hesitant votes lighter: it gives each path a confidence score, then sums the scores of the paths that support the same answer. Computing the score means answering two questions. Which steps? Every step counts, and later steps weigh more. How is each step measured? Only by the probability of the tokens of the intermediate answer. It needs no model training.
This episode also covers its limit: no way of computing confidence can make up for knowledge the model never had.

Further reading
Full article (in Chinese): https://datasciocean.com/paper-intro/cer/
Paper (ACL 2025): CER: Confidence Enhanced Reasoning in LLMs
https://aclanthology.org/2025.acl-long.390/
arXiv: https://arxiv.org/abs/2502.14634

Chapters
0:00 A five-vote dilemma
0:30 How majority voting works
1:15 Every vote weighs the same
1:45 Giving votes weight
2:37 Which steps to look at
3:39 How to measure each step
5:01 Combining into one vote
5:52 Its limits
6:45 Three-point recap
```

### 简体中文（只翻譯）

標題：同一题问 AI 五次，答案不一样，该信哪个？｜CER

```
同一道题让 AI 算好几次，再用多数决选答案，这是 Self-Consistency（SC）的做法。但它把每一条推理路径都算成一票，听不到模型的犹豫。
CER 让犹豫的票变轻：替每一条路径算一个信心分数，再把支持同一个答案的分数加起来。分数怎么算，要回答两个问题：看哪几步？每一步都算，越后面的步骤越重。每一步怎么量？只看中间答案那几个 token 的概率。它不需要训练任何模型。
这集也会讲它的极限：模型原本没有的知识，信心怎么算都补不了。

延伸阅读
完整文章：https://datasciocean.com/paper-intro/cer/
原始论文（ACL 2025）：CER: Confidence Enhanced Reasoning in LLMs
https://aclanthology.org/2025.acl-long.390/
arXiv：https://arxiv.org/abs/2502.14634

章节
0:00 五票的难题
0:30 多数决怎么做
1:15 每一票都一样重
1:45 让票有轻重
2:37 看哪几步
3:39 每一步怎么量
5:01 合成一张票
5:52 它的极限
6:45 三点回顾
```

## 上傳時的設定

- 瀏覽權限：私人（程式固定）；語言：中文（台灣）；分類：科學與科技
- 「經過變造的內容」（AI use）：建議 **No**。旁白是你本人的複製聲音，畫面是非寫實動畫。
- 音樂是品牌音樂（Pixabay 授權）、音效是 CC0，都不需要標示。
- 標籤：CER、Confidence Enhanced Reasoning、信心加權投票、Self-Consistency、多數決、LLM、推理、Chain of Thought、logits

## 發布後要手動做的（API 做不到）

- 片尾畫面（最後 5～20 秒；錘錘和字標在正中間，元件放左右兩側）
- 自動配音
- 說明欄可以加上 v001 的連結，v001 的說明欄也可以回連這支
