# 關卡 1：選題（2026-11-22）

concept-wiki commit `a5ad44f`（77 張卡）。已做：v001 `rrf-rank-fusion`、v002 cer 三張。
成效線索（只有 2 支，只當參考）：v001 平均看完 10.8%，觀看大多來自訂閱者；搜尋、相關影片很少 → 這次優先選「一般人看標題就想點」的題目。

## 候選 A（建議）：把問題貼兩次，AI 就變準？——Prompt Repetition

- 來源卡：`prompt-repetition-causal-bottleneck-and-fix`、`prompt-repetition-free-lunch-latency`、`prompt-repetition-results-and-boundary`（系列卡，合成一支）
- 類型：機制型（加一段事實型結果）
- 預估長度：7～9 分鐘（45 條主張，和 v002 相當）
- 一句話重點：模型讀前面時還不知道後面；貼第二遍，前面就看得到後面
- 暖身例子：「The bark was rough.」讀到 bark 不知道是狗叫還是樹皮；NameIndex「50 個名字，第 25 個是誰？」21.33% → 97.33%
- 前置知識：只能往前看的注意力（因果注意力）、Prefill 與 Decode 兩階段。都是教科書等級，可以在片中補
- 一張大圖：一條**橫向的 token 長廊**，第一遍 P1、第二遍 P2 接在一起；每個 token 往左拉的注意力光線，P2 的光線能照到整個 P1。鏡頭沿長廊走，最後拉到全景看「快的 Prefill 工廠 vs 慢的 Decode 打字機」
- 機制角色：每個 token 是一個**只能回頭看、不能往前看的小讀者**（戴眼罩的那一側），和 v002 的「票」、v001 的排名不同
- 包裝潛力：反差強（「只是貼兩次」 vs 「47 勝 0 敗」「21% → 97%」），白話好懂
- 限定條件要講到：Claude 極長文本延遲例外；開 CoT 後變中性（5 勝 1 敗 22 平）；NameIndex 是極端查找任務、只列一個模型

## 候選 B：改 context 改在哪，帳單差 7.7 倍——prefix cache 的成本

- 來源卡：`context-edit-cost-by-position`（可再加 `context-chunk-keep-offload-compress-delete`）
- 類型：機制型
- 預估長度：4～6 分鐘
- 一句話重點：快取只能沿用開頭相同的那段，改得越前面越貴
- 暖身例子：[A B C] 把 B 改成 B'，C 沒變也要重算
- 大圖：一排積木（KV cache），改動處之後的積木全部倒下重蓋
- 風險：觀眾面較窄（做 agent 的工程師）；數字是論文為說明而選的例子，不是實測

## 候選 C：一個 1952 年的球隊排名公式，怎麼變成 ChatGPT 的底層——Bradley-Terry

- 來源卡：`bradley-terry-pairwise-preference`（獨立卡）
- 類型：機制型（經典概念）
- 預估長度：約 3 分鐘，剛好在門檻邊緣
- 一句話重點：每個人都有看不見的實力值，比賽結果只是機率
- 暖身例子：實力 8 對 2，贏面八成、兩成爆冷
- 風險：太短；和 v002 的「信心、機率」有點接近

## 建議

選 **A**。理由：一般人一看就懂的反差（貼兩次就變準）、有很強的具體數字、一張大圖清楚，而且主角和前兩支完全不同。
