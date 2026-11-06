# 觀念卡格式：影片用的速查

契約全文在 `concept-wiki/docs/card-format.md`，有疑問以它為準。本檔只寫影片流程需要的部分。
探索日期：2026-11-06，concept-wiki commit `14dc852`。

## 位置

| 東西 | 路徑 |
|---|---|
| 卡 | `concept-wiki/wiki/concepts/<id>.md`（檔名＝卡 ID，kebab-case，例如 `verifier-expected-value-vs-argmax`） |
| 索引 | `concept-wiki/wiki/index.md`：每張卡一行，含 id、一句話論點、parent、related、status |
| 參考圖 | `concept-wiki/wiki/figures/<article>/<src>`，由主張的 `figures[].file` 指向（路徑相對於 `wiki/`） |
| 背景詞清單 | `concept-wiki/config/background-terms.md`：讀者預設已知的詞，可當 `prerequisite` 的參考上限 |

## 結構

卡由兩部分組成：YAML frontmatter，加上 `## 主張` 底下一個含 `claims:` 的 ```yaml 區塊。區塊外的文字（例如「名詞補充」）**不是主張**，影片不能當作卡的說法引用。

**frontmatter**：`id`、`title`（一句話論點）、`type_hint`（方法、發現、判斷、可遷移原則…，只供參考）、`context_type`、`sources[]`、`parent`、`related[]`、`status`。

- `context_type` 有三種：`bound_to_source`、`evidence_from_single_source`、`standalone_classic`。
- `sources[]` 每筆含 `article`、`article_title`、`url`、`sections`、`first_appearance`。
- `sources[].url` 就是說明欄要放的 blog 連結。

**claims[]**：`id`（c1、c2b…）、`role`、`text`、`source_quotes`、`anchor_type`、`comparison_target`、`qualifiers[]`、`figures[]`、`importance`、`status`。

- `role` 有七種：`thesis`（恰好一條）、`context`、`mechanism`、`anchor`、`evidence`、`evaluation`、`qualifier`。
- `importance` 越小越重要；`thesis` 一定是 1。
- `qualifiers[]` 每項含 `text` 與 `source_quote`，有時另有 `source: figure_caption`。

## 系列卡與獨立卡

卡上**沒有**「系列」欄位。系列的判斷方式：

- **系列卡**：同一個 `sources[0].article` 的多張卡。同篇文章的卡通常互設 `related`。
- **獨立卡**：所屬文章只有它一張卡，或 `context_type: standalone_classic`。目前的例子是 Bradley-Terry 與 Decision Transformer，它們的出處是 persona-aware-d2s 這篇文章。

## 影片怎麼用卡（硬性規則）

1. **只用 `status: normal` 與 `author_confirmed` 的主張。** `pending_author_confirmation` 一律不用，它附的圖也不能用。`author_confirmed` 的寫法取保守，不能比卡上的句子更強。
2. **用了主張，就要帶出它的 `qualifiers`。** 旁白至少完整說一次。
3. **寫法依 `anchor_type` 決定。** 對照表見 `rules/from-social-media/anchor-writing-rules.md`。重點：
   - 設計參數：主詞是方法名。
   - 官方宣稱：主詞是宣稱方。
   - 原作者解讀：主詞寫「論文指出」。
   - 部落格推論、部落格判斷：以作者口吻寫，但語氣不能比卡強。
4. **數字一定要有 `comparison_target`。** 例外是 `numeric_kind: non_comparative` 的數字。
5. **圖只是參考，不是證據。** 一律重畫；只畫主張文字裡有的數字，範圍不得放大。
6. 查核員的 `card_claim` 判定，以 `claims[].text` 與 `qualifiers` 為準，不以 `source_quotes` 或 blog 為準。影片不讀 blog。

## 圖號與說明

`figures[].caption` 是 blog 的圖說原文，常含出處，例如「來源：原始論文 Figure 5」。它只能用來交代範圍，不能當作主張的內容。

## 卡與 blog 的連結

`sources[].url` 是 blog 文章網址，例如 `https://datasciocean.com/ai-concept/<slug>/`。說明欄的「延伸閱讀」就用它。
