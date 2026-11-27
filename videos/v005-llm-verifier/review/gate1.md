# 關卡 1：選題（2026-11-26）

concept-wiki 更新到 `83504b2`（93 張卡，新增 skill-state、is-bash-all-you-need、tasteful-agent、subagent-fold、context-language-models 等）。
成效線索：v001 d7 前 30 秒流失 53 個百分點，下一支的鉤子要在 15 秒內給出看得見的畫面與答案。

## A（建議）SKILL.state：Agent 不留對話歷史，只留一張狀態表

- 卡：`skillstate-state-replaces-history`、`skillstate-results-cost-vs-accuracy`、`discard-history-relevance-at-the-time`（45 條主張，0 pending）
- 類型：機制型＋事實型；預估 8～10 分鐘
- 一句話重點：把歷史丟掉、只留狀態，成本從平方變線性，但賭的是「當下就知道什麼該記」
- 暖身例子：卡上的倉儲例子（item_12 在 shelf_42 → 出貨 → 那一格被刪掉）；10 步算給你看：1+2+…+10=55 對 10 個 1
- 大圖初想：左邊是一卷越拉越長的紙（ReAct 的 prompt），右邊是一塊白板（狀態），每一步擦掉重寫；把每步的紙長疊起來就是三角形（平方），白板是一排等高的長條（線性）。主角：一個倉儲機器人。
- 前置：agent、prompt、token 成本（v004 剛講過 agent loop，可以一句帶過）
- 限制段：軟體版本庫 T=25 的反例、Gemma 只剩 0.42、早期觀察後來才有用就找不回來
- 機制角色：白板（會被擦）與一卷紙。和 v004 的「紙卷 transcript」要刻意區隔（v004 是同一卷紙，這支要讓紙卷變成反派、白板是主角）。

## B LLM-as-a-Verifier：LLM 打分數為什麼老是平手

- 卡：`verifier-expected-value-vs-argmax`、`verifier-three-knobs-g-k-c`（＋可選 PPT 一張）；約 10 分鐘
- 一句話重點：模型心裡其實有 4.16 分，是 argmax 把它壓成 5
- 暖身例子：卡上的 0.02/0.05/0.13/0.35/0.45 機率長條 → 期望值 4.16
- 大圖初想：一條刻度尺＋機率長條，刻度從 5 格變 20 格
- 風險：和 v002 CER（用 token 機率加權投票）很像，觀眾可能覺得重複

## C Is Bash All You Need：只給 agent 一個 shell，反而更準更省

- 卡：`bash-vs-typed-tools-results`、`baseline-who-built-it`、`bash-add-ons-no-detectable-gain`；約 8 分鐘
- 一句話重點：拿掉 60 個專用工具只留 bash，分數高 24 個百分點；但對手工具是誰做的很重要
- 大圖初想：一排 60 個按鈕的控制台 vs 一條管線（pipe）
- 風險：事實型，機制演示較少；和 v004（Claude Code 工具）主題相近

## 頻道定位之外的選項

- FastAPI 的 race condition（5 張卡，常青、很好畫）：頻道訂閱者多是當初的程式教學觀眾，可能留得住人；但不是 AI 論文，偏離頻道一句話。

## 本次標記

無新的 waiting／unsuitable。
