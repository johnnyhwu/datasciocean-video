---
name: select-topic
description: 影片第 1 步「選題」：從 concept-wiki 找出下一支影片的候選（卡的組合、類型、預估長度、一句話重點、暖身例子想法），交關卡 1。
---

# 第 1 步：選題

## 做法

1. 確認 submodule 是最新的：`git submodule update --remote concept-wiki`。記下 commit；如果有新卡，更新 `state/inventory.md`。
2. 讀 `concept-wiki/wiki/index.md` 和 `state/inventory.md`，排除已做成影片的卡（`state.py list`）和 `state/cards.yaml` 標成 `unsuitable` 的卡（這個檔在第一次執行 `state.py card` 時才會出現）。
3. 對每個候選，用 `uv run python lib/cards.py <卡 ID>…` 讀**可用的主張**。pending 的不算；卡外的「名詞補充」不是主張。
4. 依下面的標準判斷，挑 2～4 個候選寫進審查包。

## 組成規則

- **系列卡**（同一篇文章的多張卡）合成一支。
- **獨立卡**一張做一支。不足 3 分鐘就標 `waiting`，可以和其他相關的獨立卡合併（可以跨文章），把候選組合交給使用者決定。跨文章合併時，只講各卡上有的內容，不加卡上沒有的比較。
- **超過 15 分鐘**：預設依觀念邊界拆成系列，同時列出「只選主軸卡做一支」的方案。拆出的每一支都要 3～15 分鐘、有自己的一句話重點，而且開場獨立就看得懂。

## 選題標準

| 項目 | 規則 |
|---|---|
| 類型 | 分成**機制型**（講一個做法怎麼運作）或**事實型**（講數據、比較、發現）。兩種都做 |
| 前置知識成本 | 前置知識能不能在影片裡合理補完？補完會超過 15 分鐘，就標 `unsuitable` |
| 內容量 | 估算可用主張講完要多久：可用主張的單位數 ÷ 200 × 1.3（講解會比卡長），至少 3 分鐘，不足標 `waiting`。門檻見 `rules/speech-rate.md` |
| 證據 | 卡上的主張要有足夠的證據支撐 |
| 機制型 | 一定要有能承載核心機制的小例子（3B1B：「能讓觀眾自己重新發現的具體例子」）。卡上的機制描述不夠細，就標 `unsuitable` |
| 事實型 | 一定要有具體案例，或能逐項揭露的比較；沒有就標 `unsuitable` 或 `waiting` |
| 常青 | 優先選常青的觀念與機制，不做「最新論文快報」 |
| 不重複 | 和最近幾支的主題、開場、機制角色不要太像（反模板） |
| 成效 | 有 `videos/*/d7.json`、`d28.json` 時先看一眼：哪種題目、哪種開場留得住人。樣本很少，只當線索 |

標成 `waiting` 或 `unsuitable` 時要寫原因：`uv run python lib/state.py card <卡 ID> waiting --note "原因"`。

## 審查包（`videos/_gate1-<日期>.md`，使用者選定後搬進該影片的 `review/gate1.md`）

每個候選寫：

- 來源卡與 ID；
- 類型；
- 預估長度；
- **一句話重點**（≤30 字，就是之後的承諾句草稿）；
- **暖身例子的初步想法**（一兩句：用什麼小東西演出核心機制）；
- 前置知識有哪些；
- **「一張大圖」的初步想法**：這個機制能畫成什麼形狀的圖（管線、時間軸、座標系），主角是什麼。想不出來的題目要註明，這會是最大的風險。
- 可能的機制角色。每支都要不同。

另外列出這次新標的 `waiting`、`unsuitable` 與原因。

## 使用者選定之後

```bash
uv run python lib/state.py new v<三位數>-<slug> --cards 卡1,卡2 --note "關卡 1：使用者選的與原話"
uv run python lib/state.py approve v…-… 1 --note "…"
uv run python lib/state.py set v…-… 規劃
```
