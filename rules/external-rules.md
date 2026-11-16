# 外部規則現況

查證日期：2026-11-06。建議每季重查一次。標記：**官方**＝官方文件，**第三方**＝非官方來源，**未查**＝這次沒有查。

## YouTube

| 項目 | 現況 | 可信度 |
|---|---|---|
| 章節 | 第一個時間戳是 0:00；至少 3 段，依時間遞增；每段至少 10 秒；寫在說明欄 | 第三方（多個來源一致） |
| 片尾畫面 | 只能放在影片最後 5～20 秒；影片至少 25 秒；16:9 最多 4 個元素；設為「為兒童製作」的影片不能用 | 官方（support.google.com/youtube/answer/6388789） |
| 自動配音 | 官方說明頁列出繁體中文配英文。資格逐支影片判定：超過 120 分鐘、沒有語音、有版權聲明、語速太快的影片都不行。頻道資格各來源說法不一（一說 YPP 優先，一說所有頻道都可以） | 官方加第三方，**到 Studio 實際確認** |
| A/B 測試（Test & Compare）、進階功能的開通條件 | 未查 | 未查，開通時到 Studio 確認 |

**對製作的影響**：最後一個場景留 **20 秒**給頻道片尾動畫（片尾畫面的元件疊在左右兩側）；章節每段至少 10 秒。

### 用 API 上傳（查證日期：2026-11-16；目前硬性限制是不上傳，這裡只記錄現況）

| 項目 | 現況 | 可信度 |
|---|---|---|
| 未驗證的 API 專案 | 2026-11-02 起，`videos.insert` 上傳的影片**不再被鎖成私人**（推翻 2020-07-28 的規定）。沒指定 `status.privacyStatus` 時預設是公開，所以一定要明確指定 | 官方（developers.google.com/youtube/v3/revision_history、docs/videos/insert） |
| 額度 | 上傳有自己的額度：每次 1 單位，每天 100 次。縮圖 `thumbnails.set` 50 單位、字幕 `captions.insert` 400 單位，算在一般的每天 10,000 單位 | 上傳：官方；縮圖與字幕：第三方引用官方計算器 |
| 可以設定 | 標題、說明、多語標題與說明（localizations）、隱私狀態、排程（`publishAt`）、AI 揭露（`status.containsSyntheticMedia`）、為兒童製作、縮圖、字幕、加入播放清單 | 官方 |
| 不能設定 | 片尾畫面、標題縮圖的 A/B 測試、自動配音。這些只能在 Studio 手動做 | 官方文件沒有對應的方法 |
| 授權 | OAuth，範圍 `youtube.upload`（上傳）加 `youtube.force-ssl`（字幕）。同意畫面留在「測試」狀態時，refresh token 7 天過期，每次發片可能要重新登入 | 官方；7 天是 Google OAuth 的一般規定 |

## Gemini 3.8 Flash TTS 聲音複製（官方：aistudio.google.com/docs/voice-replication）

- **建立聲音**：呼叫 `POST /v1beta/voices`，參數是 `voice.type="replicated"`、`voice.model="gemini-3.8-flash-tts"`、`voice.replicated.source_audio` 與 `consent_audio`（`audio/wav`，base64）。
  - `store=true`：取得永久的 `voice_…` ID。每個專案上限 200 個，最後一次使用後保留 1 年。
  - `store=false`：取得 `voicekey_…`，7 天後失效。
- **錄音規格**：參考錄音 10～30 秒，單一成人、乾淨自然。同意錄音由同一人、同一支麥克風、同一個環境錄製。建議格式 24 kHz、單聲道、16-bit WAV。
- **同意聲明的語言**：中文只有 zh-CN（簡體）。聲明原文是「我是此声音的拥有者并授权谷歌使用此声音创建语音合成模型」。英文版是 "I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model."
- **地區與資格**：API 在所有 Gemini API 支援地區都能用（含 EEA、英國、瑞士）。需要付費層（Tier 1 以上），不需要另外申請白名單。AI Studio 的介面另有地區限制（第三方報導）。台灣不在任何限制名單上。
- **輸出**：24 kHz、單聲道、16-bit WAV，附 SynthID 浮水印。文件沒有提到時間戳。
- **輸入限制**：合成語音，或帶 SynthID、C2PA 的錄音會被拒收，所以參考錄音一定要是真人原始錄音。
- **多人對話**：複製聲音不能放進多說話者請求，要每句各自合成再串接。
- **實測（2026-11-10）**：
  - 同意錄音只能念**一種語言**；中英各念一次會回 400 invalid argument，切出英文那段就成功了。
  - `google-genai` 3.0.0 的 `client.voices.create` 和 `client.interactions.create` 都回 404，直接打 REST 才正常（`lib/voice_create.py`、`lib/tts_gemini.py` 已改）。
  - 建立聲音沒有另外顯示費用。
- 價格與 OpenRouter 支援：這次沒有查到。研究 I 寫「音訊輸出 US$9/1M tokens，2027-01-01 起加倍」。**預設直連 Gemini API。**

## OpenRouter（查證 2026-11-07）

- `google/gemini-3.8-flash-tts` 在 OpenRouter 上有兩個端點：Google AI Studio、Google。**兩個的 `supports_voice_cloning` 都是 false**（查 `/api/v1/models/google/gemini-3.8-flash-tts/endpoints`）。
- 結論：**走 OpenRouter 只能用 Gemini 的預設聲音，不能用使用者的複製聲音。** 在 Google 的專案裡建立的 `voice_…` ID 也不能拿到 OpenRouter 用，因為聲音是綁在建立它的 Google Cloud 專案上的。
- 用法：`POST /api/v1/audio/speech`，參數 `model`、`input`、`voice`、`instructions`、`response_format`。
  - `instructions` 會被轉成 Gemini 的 `speech_metadata.style`，語氣不用寫進正文。
  - 文件提醒：Gemini 3.8 會逐字念 `input`。
  - Gemini 只回傳 `pcm`（24 kHz、16-bit、單聲道）。
- 價格和直連一樣：音訊輸出 US$9／百萬 tokens，輸入 US$0.5／百萬 tokens。
- OpenRouter 上**有**聲音複製的模型：`fish-audio/s2.1-pro`、`heygen/heygen-voice-1`、`bytedance-seed/seed-audio-1-0`。複製是無狀態的，每次請求都附上參考音檔（`input_references`）。台灣口音沒有官方保證；podcast repo 的經驗是「複製傳得了音色、傳不了口音」，這三個要實測才知道。

## 動畫工具

- **ManimCE**：PyPI 最新版是 **0.22.1**（2026-10-27），MIT 授權。實驗 v4 用的就是 0.22.1。
- ManimCE 透過 PyAV 內建 libav 輸出影片，**不需要系統的 ffmpeg**。本機沒有安裝 ffmpeg。最後混音與 loudnorm 改用專案內的 Python 套件（例如 `imageio-ffmpeg` 附帶的靜態 ffmpeg，或 PyAV），不做全域安裝。
