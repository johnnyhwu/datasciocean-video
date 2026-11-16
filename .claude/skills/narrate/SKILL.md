---
name: narrate
description: 影片第 5 步「旁白」：用 Gemini TTS 逐句合成唸法稿、修剪、量時長、回聽檢查，建立以實際音檔為準的時間軸。
---

# 第 5 步：旁白

## 合成前

1. **先估金額，等使用者同意**：句數與預估秒數 × 每秒約 25 tokens × 單價（`rules/external-rules.md`）。一支 10 分鐘的影片約 US$0.14，2027-01-01 起約加倍。已經同意過「每支照常合成」就不用每次問。
2. 確認 `config/voice.json` 的 `narrator` 是定案的聲音。
   - 定案（2026-11-10）：使用者本人的複製聲音 `voice_671rii51x0an`，盲聽勝過 Zubenelgenubi。最後一次使用後保留 1 年，過期就用 `lib/voice_create.py` 重建（錄音稿在 `docs/voice-recording.md`）。
   - 同意錄音只能念一種語言的聲明；中英都念會被拒。
3. 一律直連 Gemini（使用者 2026-11-10：不用 OpenRouter），金鑰是 `.env` 的 `GEMINI_API_KEY`。直連走 REST，`google-genai` 3.0.0 的 SDK 會回 404。
   - **不要讀出或印出 `.env`，連遮罩過的也不行**（2026-11-10 遮罩指令因格式不同把金鑰印了出來）。只用程式確認變數有沒有值。也不要向使用者要金鑰。

## 合成

```bash
uv run python lib/tts_gemini.py <id>               # 逐句合成，有快取（內容沒變就不重做）
uv run python lib/tts_gemini.py <id> --only a3,b7 --force   # 只重骰某幾句
uv run python lib/timeline.py <id>                 # 以實測時長建立時間軸與字幕
```

- 語氣寫在每句的 `style`，或 `voice.json` 的預設。提示詞走獨立的 annotation，不和正文擠在同一段。**語氣提示要短**：podcast 實測，長提示容易失敗。
- seed 無效，重跑就是重骰。已經滿意的版本靠快取鎖定，不要隨便 `--force`。
- 碰到每日上限，程式會存檔停下，重置後跑同一個指令就會接續。同一句連續失敗 3 次就停下來回報。

## 回聽檢查（語音辨識）

```bash
uv run python lib/checks/stt.py <id>               # 每句轉回文字比對；--only 只重查重骰過的句子
```

- 模型預設 **Qwen3-ASR-1.7B**（`mlx-community/Qwen3-ASR-1.7B-bf16`，Apache-2.0，本機共用 Hugging Face 快取，離線載入）。v001 實測比 podcast 的 whisper-large-v3-turbo 準：平均相似度 0.952 → 0.975，無標記 67 → 74 句。熱詞自動取稿子裡的英文專有名詞，不放整句（否則念錯也聽不出來）。`--model whisper` 可換回。
- 比對與正規化照搬 podcast 的 `pipeline/verify.py`。語速和這支影片自己的中位數比（0.6～1.6 倍），不用 podcast 的絕對門檻（短句加使用者的聲音會被大量誤標）；另抓句中超過 1 秒的停頓。
- 標記：相似度 < 0.90、語速離群、句中長停頓、轉錄比稿子長 15% 以上（幽靈音）、語氣提示被念出來。
- 唸法稿漏寫是真的會出錯的：v001 f13 沒有 `say`，TTS 把「1 ÷ (k + 名次)」連括號一起念出來。畫面字有符號或數字的句子一定要寫 `say`。
- 字錯率只是篩選器。同音字（argmax 被聽成「阿瑪」、DataSci 被聽成 DataSide）不算錯，逐條看過再放行。
- 唸錯的句子：改寫唸法稿，記進 `rules/pronunciation.md`，然後重骰。

## 片長

`timeline.py` 會印出總長。超出規劃太多就回去刪句子：重跑 `timeline.py`，改過的句子要重新查核。

## 完成

`state.py set <id> 動畫`，載入 `animate`。

**之後又重新合成任何一句**（動畫已經做好）：時間軸會變，照 `animate` 的「時間軸變了就全部重來」做。

告訴使用者哪些句子沒經過人耳確認。**Claude 聽不到聲音，不要假裝確認過。**
