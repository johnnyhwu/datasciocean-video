---
name: narrate
description: 影片第 5 步「旁白」：用 Gemini TTS 逐句合成唸法稿、修剪、量時長、回聽檢查，建立以實際音檔為準的時間軸。
---

# 第 5 步：旁白

## 合成前

1. **先估金額，等使用者同意**：句數與預估秒數 × 每秒約 25 tokens × 單價（`rules/external-rules.md`）。一支 10 分鐘的影片約 US$0.14，2027-01-01 起約加倍。已經同意過「每支照常合成」就不用每次問。
2. 確認 `config/voice.json` 的 `narrator` 是定案的聲音。
   - 複製聲音的 voice ID 由 `lib/voice_create.py` 建立。
   - 盲聽定案前，用 podcast 的預設聲音 Zubenelgenubi 當備案。
3. 金鑰放在 `.env` 的 `GEMINI_API_KEY`。**不要讀出或印出 `.env`**，也不要向使用者要金鑰。

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

規格要求把每句音檔轉回文字，和唸法稿比對字錯率。這道檢查**在旁白實驗證實可靠之後才保留**；在那之前，用人耳抽查。

- 候選工具：podcast 用的 whisper-large-v3-turbo（mlx_audio），參數要設 `temperature=0`、`condition_on_previous_text=False`、`hallucination_silence_threshold=2.0`，否則會幻聽。
- 字錯率只是篩選器。同音字（argmax 被聽成「阿瑪」）不算錯，逐條看過再放行。
- 唸錯的句子：改寫唸法稿，記進 `rules/pronunciation.md`，然後重骰。

## 片長

`timeline.py` 會印出總長。超出規劃太多就回去刪句子：重跑 `timeline.py`，改過的句子要重新查核。

## 完成

`state.py set <id> 動畫`，載入 `animate`。

告訴使用者哪些句子沒經過人耳確認。**Claude 聽不到聲音，不要假裝確認過。**
