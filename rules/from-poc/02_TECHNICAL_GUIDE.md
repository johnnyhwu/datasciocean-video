<!-- 來源：pre-plan/experiment/opus5_5_effort_xhigh.zip 的 final_xhigh/docs/02_TECHNICAL_GUIDE.md（PoC，使用者滿意），複製日期 2026-11-06。這是 PoC 當時的紀錄；與本 repo 的規則（CLAUDE.md、rules/、skills）衝突時，以本 repo 為準。主要差異：背景改品牌深海色、TTS 改 Gemini、響度 -14 LUFS、軟字幕為主、角色改為鉛錘吉祥物＋機制角色。 -->

# 02 技術手冊：final_xhigh（v4）怎麼做出來的

這份寫給要「照著做出下一支片」的 Claude。所有路徑都相對於 zip 裡的 `source/`，也就是當時的實驗資料夾 `yt-video-lab/`。v4 的程式在 `source/v4/`。

---

## 1. 總覽：一條管線，八個步驟

```
觀念卡（concept-wiki，唯讀）
  │ 人工＋Claude：選卡、寫逐句腳本
  ▼
v4/spec/script.json ── 每句：display（字幕）、say（給 TTS 的念法）、speaker、hold；每場：pad、music、chapter
  │ ① v4/tts/synth.py      Kokoro v1.1-zh 離線 TTS（旁白＋機器人兩個聲音）＋SenseVoice 語音辨識回轉驗證
  ▼
v4/out/audio/<句id>.wav ＋ report.json（每句長度、字錯率、辨識結果、音素）
  │ ② v4/timeline.py       每句長度＝實測音檔長度 → 絕對時間、每場影格數；同時產生 SRT（繁／簡）與有樣式的 ASS
  ▼
v4/spec/timeline.json ＋ out/subs.zh-TW.srt、subs.zh-CN.srt、subs.ass
  │ ③ v4/manim/s1~s4.py    ManimCE，每個場景是一個 Timed 子類別，動畫掛在「第幾句念到幾成」；音效提示點寫成 out/sfx-<場>.json
  │ ④ v4/render.sh         4 個行程平行渲染 11 個場景（每場獨立 media 資料夾）→ ffmpeg concat → out/manim-1080p30.mp4
  │ ⑤ v4/music.py          程式產生背景音樂（每場一種情緒，依小節對齊）→ out/music.wav
  │ ⑥ v4/mix.py            旁白＋音效＋音樂（自動壓低）→ out/mix.wav、out/mix_nomusic.wav
  │ ⑦ v4/package.sh        兩段式響度正規化 −16 LUFS → 燒入字幕版、軟字幕版、無音樂版
  ▼
v4/deliver/*.mp4 ＋ 字幕 ＋ chapters.txt ＋ thumbnail.png
  │ ⑧ 自我檢查：版面紀錄、sheet.py 縮圖、still.py 靜止段落、synccheck.py 同步、ebur128 響度、格數
```

**設計核心：旁白決定時間軸。** 先有聲音，才有時間軸，動畫再掛上去。換聲音或改句子時，只要重跑 ①② 再重渲，動畫會自動對齊。

---

## 2. 框架與版本

| 用途 | 工具與版本 | 備註 |
|---|---|---|
| 動畫 | **ManimCE 0.22.1**（Cairo renderer），Python 3.13 | `MovingCameraScene`、`ValueTracker`、`always_redraw`、Text（Pango）。**沒有 LaTeX**，不用 MathTex |
| 數值 | numpy 2.5.4、Pillow 13.0（manim 環境） | |
| TTS | **kokoro-onnx 0.6.1**＋模型 `kokoro-v1.1-zh.onnx`、`voices-v1.1-zh.bin`；onnxruntime 1.31.1 | 離線 CPU，總長 9 分鐘的旁白約 4 分鐘合成完 |
| 中文轉音素 | **misaki 0.9.4**（`misaki[zh]`，`ZHG2P(version="1.1")`），內部用 jieba、cn2an | 輸出注音＋聲調，例如 `ㄉㄚ3ㄈㄣ1`；英文由自訂 `en()` 轉成 IPA |
| 語音辨識（驗證用） | **sherpa-onnx 2.0.1**＋SenseVoice int8（`sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17`） | 只用來檢查念得對不對、時間對不對 |
| 繁簡轉換 | opencc-python-reimplemented 0.1.7（`tw2sp` 產生簡中字幕；`t2s` 算字錯率） | |
| 音訊 | soundfile 0.14、scipy 1.17.1、numpy（TTS 環境，Python 3.11） | 音效、音樂、混音都是 numpy／scipy 自己寫的，不用任何外部音樂資源 |
| 影音 | **ffmpeg 6.1.1**（concat、loudnorm、ebur128、libx264、AAC、mov_text、ass 濾鏡） | |
| 環境管理 | **uv 0.11.32** | 兩個獨立環境：根目錄 `pyproject.toml`（manim）、`v4/tts/pyproject.toml`（TTS 與音訊） |
| 字型 | **Noto Sans CJK TC** Regular／Bold（OFL），在 `source/assets/fonts/` | 要複製到 `~/.fonts/`，Manim（Pango）才找得到；ffmpeg 燒字幕要給 `fontsdir` |
| 硬體 | 4 核 CPU、無 GPU、16 GB RAM | 全片 1080p 渲染約 7 分鐘 |

**為什麼用 ManimCE**：早期實驗比較過 ManimCE、HTML＋GSAP＋Playwright、HyperFrames、Remotion 四種工具，詳見 `docs/background/`。ManimCE 的優勢：

- 最省 token、渲染最快；
- 逐格可重現（每一格像素都一樣）；
- 鏡頭和數學物件的操作最齊全。

---

## 3. 從零重建環境

```bash
cd source                                   # 等於當時的 yt-video-lab/
uv sync                                     # manim 環境（根目錄 pyproject.toml / uv.lock）
mkdir -p ~/.fonts && cp assets/fonts/*.otf ~/.fonts/ && fc-cache -f
cd v4/tts && uv sync                        # TTS／音訊環境（Python 3.11）
mkdir -p models && cd models                # zip 沒附模型（約 600 MB），從 GitHub release 下載：
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.1-zh.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.1-zh.bin
curl -LO https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2
tar xjf sherpa-onnx-sense-voice-*.tar.bz2 && mv sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17 sensevoice   # 需要裡面的 model.int8.onnx、tokens.txt
```

需要系統裝好 ffmpeg 和 Pango（Manim 的 Text 要用）。原本的容器都有。

> 注意：當時 `v4/tts/models` 是指向 `v3/tts/models` 的符號連結；v4 的 TTS 腳本也是用 `uv run --project ../../v3/tts` 執行，兩版共用同一個環境。zip 裡的 `v4/tts` 已經有自己的 `pyproject.toml`、`uv.lock`，照上面的步驟在 `v4/tts` 裡 `uv sync` 就好。

## 4. 重現整支片的指令（依序）

```bash
cd source/v4/tts
uv run python poly.py ..                                      # 列出多音字的讀音，人工逐條看
uv run python synth.py .. --voice zm_050 --speed 1.15 --robot zf_004   # 逐句合成＋驗證，有快取
cd .. && (cd .. && uv run python v4/timeline.py)              # 時間軸、SRT、ASS
Q=l ./render.sh                                               # 低畫質（480p30），用來檢查，約 3～4 分鐘
uv run --project .. python sheet.py sc03 manim/media/Sc03/videos/s1/480p30/Sc03.mp4 out/sheets/sc03.png   # 每場縮圖
Q=h ./render.sh                                               # 1080p30，約 7 分鐘；只重渲某幾場：SCENES="s2:Sc04 s4:Sc10" Q=h ./render.sh
cd tts && uv run python ../music.py && uv run python ../mix.py && cd ..
./package.sh                                                  # 約 7 分鐘（兩次燒字幕需要重新編碼）
uv run --project .. python still.py out/manim-1080p30.mp4     # 靜止段落
ffmpeg -y -i deliver/llm-judge-ties-v4-nomusic.mp4 -ac 1 -ar 16000 out/final16k.wav && (cd tts && uv run python synccheck.py)
ffmpeg -i deliver/llm-judge-ties-v4.mp4 -af ebur128=peak=true -f null -   # 響度
(cd manim && uv run --project ../.. manim -qh -s --disable_caching --media_dir media/Thumb -o thumb thumb.py Thumb)   # YouTube 縮圖
```

---

## 5. 資料格式

### 5.1 `spec/script.json`（唯一要手寫的內容檔）

```jsonc
{
 "title": "LLM 評審為什麼老是平手？",
 "gap": 0.22,                       // 句與句之間的固定間隔（秒）
 "scene_pad": [0.4, 0.5],           // 預設的場景前後留白
 "voices": {"narrator": {"voice": "zm_050", "speed": 1.15}, "robot": {"voice": "ROBOT", "speed": 1.0}},  // ROBOT 由 --robot 參數指定
 "scenes": [
  {"id": "sc03", "name": "期望值：找平衡點", "music": "bright",          // music：背景音樂情緒
   "chapter": [2, "期望值：找平衡點"],                                  // 有 chapter 的場景，開頭會有章節卡
   "pad": [1.7, 1.3],                                                   // 章節場景要 1.7 秒讓章節卡掀開
   "sentences": [
     {"id": "c5", "display": "算算看：1 乘 2%，加 2 乘 5%，一路加到 5 乘 45%。",   // 字幕（最多 2 行 × 20 個全形字）
      "say": "算算看：一乘百分之二，加二乘百分之五，一路加到，五乘百分之四十五。",   // 給 TTS 的念法（可省略，省略就念 display）
      "hold": 0.4},                                                     // 這句念完後多停幾秒，給動畫時間
     {"id": "c8", "speaker": "robot", "display": "4.16 比 4.3，B 比較好！", "say": "四點一六，比四點三。B 比較好！"}
   ]}
 ]
}
```

v4 共 120 句，其中機器人台詞 7 句，分成 11 個場景、6 章。

### 5.2 `spec/timeline.json`（由 timeline.py 產生）

- 每個場景：`start`（全片絕對秒數）、`duration`、`start_frame`、`frames`（影格數）、`chapter`、`music`。
- 每句：`start`、`end`（場景內秒數）、`abs`（全片絕對秒數），以及 script 的所有欄位。
- `duration`＝634.99 秒，`frames`＝19050（30 fps）。**成片的格數必須等於這個值。**

### 5.3 其他

| 檔案 | 內容 |
|---|---|
| `out/audio/report.json` | 每句 `{key, dur, cer, stt, ph}`。`key` 是 text、聲音、語速的雜湊，相同就跳過不重合成 |
| `out/sfx-<場>.json` | `[{"t": 場景內秒數, "kind": "thud", "gain": 0.8}, …]`，由動畫程式的 `at(..., sfx=)` 記錄 |
| `out/manim-layout-<場>.txt` | 版面檢查結果。`OK`，或者「誰在幾秒超出哪個區域」「哪個動畫晚了幾秒開始」 |

---

## 6. ① TTS：`v4/tts/synth.py`

- **兩個說話者**：旁白 `zm_050`（男聲，語速 1.15）、機器人 `zf_004`（女聲，語速 1.0）。
  - 旁白聲音是 v3 時從 19 個聲音裡挑的，依據是語音辨識錯字率和音高起伏，而且 argmax 兩次都被正確認出。
  - 機器人聲音是 v4 從 12 個女聲裡挑的：加上機器音效後辨識錯字率是 0，音高起伏夠。
- **流程**：`prep(text)`（同音字替換）→ `ZHG2P(...)(text)` 轉成音素 → `Kokoro.create(phonemes, is_phonemes=True)` → 去頭尾靜音 → 機器人另外套 `robot_fx` → 存 24 kHz 的 wav → SenseVoice 辨識 → 算字錯率。
- **字錯率計算**：OpenCC 轉成簡體 → cn2an 把阿拉伯數字轉成中文 → 只留漢字，再算編輯距離。超過 0.12 列為可疑，逐條人工看。
- **英文**：
  - 全大寫的縮寫照字母念（`LET` 表），其他英文要寫進 `WORDS` 音標表：`argmax ˈɑɹɡmˌæks`、`pivot pˈɪvət`、`token tˈOkən`、`terminal tˈɜɹmənəl`、`bench bˈɛnʧ`、`ensemble ɑnsˈɑmbəl`、`p pˈi`。
  - 不認識的字會讓程式停下來，這是刻意的。
- **多音字**：先跑 `tts/poly.py ..`，列出含多音字的詞和注音，人工看，錯的在 `prep()` 換成同音字。完整清單見 `04_LESSONS_LEARNED.md`。
- **機器音效 `robot_fx`**：
  - 原音 62%；
  - 加 30% 回授梳狀濾波（延遲 4.5 ms、回授係數 0.42，聽起來有金屬感）；
  - 加 22% 的 55 Hz 環形調變；
  - 再做 160～7000 Hz 帶通。
  - 處理後辨識錯字率仍是 0。

## 7. ② 時間軸與字幕：`v4/timeline.py`

- 每場：`t += pad[0]`。每句：`start = t`、`end = t + 音檔長度`，接著 `t += 長度 + gap + hold`。場景結尾：`t += pad[1] − gap`。
- **SRT**：每條字幕顯示到句尾後 0.15 秒，避免一閃而過。斷行用 `lib/timeline.py` 的 `split_lines()`：
  - 最多 2 行、每行 20 個全形字（ASCII 算半格）；
  - 優先在標點斷行，不切開英數，也不切開 jieba 切出的詞；
  - 句尾的句號拿掉。
- **機器人台詞**：SRT 前面加「評審：」。ASS 裡用 `R` 樣式（橘色、粗體），前面加小字灰色的「評審 ▸」。旁白用 `N` 樣式（白色）。
  - 兩種樣式都是 Noto Sans CJK TC 58 px、外框 3.2、`MarginV` 62，`PlayResY` 1080。
- `deliver/chapters.txt` 由各場景的 `start` 產生（YouTube 章節格式 `mm:ss 標題`）。

## 8. ③ 動畫：`v4/manim/common.py` ＋ `s1.py`～`s4.py`

### 8.1 座標與版面

- Manim 畫面寬 14.22、高 8 單位，原點在中心。
- 版面規格在 `source/spec/style.json`（`lib/layout.py` 讀取），以畫面比例表示：
  - 主畫面區 `main` 是 y 0.05～0.74（上方 74%）；
  - 註解區 `annotation` 是 0.74～0.80；
  - **字幕區 `subtitle` 是 0.80～0.95，動畫不能進去**；
  - 左右各留 5% 的安全邊界。
- `common.py` 換算好的常數：`TOP`＝3.6、`BOTTOM`＝−1.92、`MIDY`＝0.84（主畫面中線）、`XL`＝−6.4、`XR`＝6.4、`ANN_Y`。
- 字級：`fs(frac)` 把「字高佔畫面高的比例」換成 Manim 的 font_size。`T(s, frac, color)` 是一般字，`B(...)` 是粗體。
  - 一般標籤 0.03～0.045，重點數字 0.06～0.14，最小不要低於 0.024。
- 配色：`BG #0D1017`、`ARG #FF8C42`（argmax 橘）、`EXP #2EC4B6`（期望值青）、`GOOD`、`BAD`、`TIE`、`GOLD`、`PURPLE`、`BLUE`、`PINK`、`SCREEN`、`PANEL`。
- 背景用 `bgplate(name)`：`manim/assets/bg_*.png` 是 7 張預先產生的 1920×1080 背景（深藍底、各色光暈、暗角、淡點陣、抖動防色階），每場選一張。

### 8.2 `Timed` 場景基底類別（最重要）

每個場景都是 `class ScXX(Timed): SID = "scXX"; BG = "exp"`，在 `construct()` 裡寫動畫，最後呼叫 `self.finish()`。

| 方法 | 作用 |
|---|---|
| `setup()` | 讀 timeline 裡這一場的資料；加背景、頂部進度條（HUD）；如果這場有 `chapter`，先蓋上章節卡 |
| `A(句id, frac, off)` | 這句念到第 `frac` 比例的時間（場景內秒數），例如 `A("c5", 0.5)` 是 c5 念到一半 |
| `E(句id, off)` | 這句念完的時間 |
| `at(t, *anims, run_time, sfx, gain)` | **時間排程器**：等到第 t 秒（精確到影格），播放動畫，並在這個時間點記一個音效提示。如果 t 已經過了，記一筆「starts late」。**動畫依序播放，同一時間要同時發生的放在同一個 `at()` 裡** |
| `sfx(kind, t, gain)` | 只記音效、不播放動畫 |
| `card_out(t=0.75)` | 章節卡往左滑出 |
| `whip_in(*mobs, t, run)` | 甩鏡進場：物件從右邊一個畫面寬的位置滑進來 |
| `finish(mode)` | 場景收尾。`card` 是下一場有章節時，最後 1.15 秒蓋上章節卡；`whip` 是全部往左甩出；`fade` 是淡出（最後一場）；`none` 是什麼都不做（第 1 場鑽進腦袋）。預設依 timeline 自動判斷 |
| `chapter_tag(n, 文字)` | 左上角的章節小標 |
| `lipsync(robot)` | 讀這一場機器人台詞的 wav，以每 1/30 秒的 RMS 驅動嘴巴：說話時顯示張開的橢圓，高度隨音量變化，不說話時恢復原本的嘴型 |
| `check()` | 每個 `at()` 之後檢查所有物件的外框是否進入字幕區或超出安全邊界。完全在畫面外的不算（甩鏡）。物件設 `nocheck = True` 可以略過（裝飾、油壓機的桿子） |
| `tear_down()` | 寫出 `out/manim-layout-<場>.txt` 和 `out/sfx-<場>.json` |
| `zone_check = False` | 鏡頭推近的時候暫時關掉版面檢查 |

**一個場景的寫法範例**（節錄自 `s1.py` 的 Sc03）：

```python
class Sc03(Timed):
    SID = "sc03"; BG = "exp"
    def construct(self):
        robot = Robot(scale=0.62).move_to([XL + 0.95, TOP - 1.75, 0]); self.lipsync(robot)
        self.add(self.chapter_tag(2, "期望值：找平衡點"), robot)
        self.card_out()                                                    # 章節卡滑走
        big = B("期望值", 0.11, EXP).move_to([1.2, TOP - 1.0, 0])
        self.at(self.A("c1", 0.6), *robot.to_mode("exp"), run_time=0.4, sfx="click")   # 念到 60% 時扳開關
        self.at(self.A("c1", 0.7), pop_in(big), robot.mouth_shape("happy"), run_time=0.4, sfx="chime", gain=0.4)
        ...
        self.finish()
```

### 8.3 元件庫（`common.py`）

| 元件 | 說明 |
|---|---|
| `Robot(color, scale, switch)` | 機器人評審：頭（可掀開的蓋子 `open_lid()`）、螢幕眼睛（`blink()`、`look(v)`）、嘴型（`mouth_shape("happy"/"flat"/"sad"/"o")`）、說話用的嘴 `talk`、胸前開關 `to_mode("exp"/"arg")`（滑動並整隻變色）。`sweat(robot)` 是汗滴 |
| `Contestant(字母, 顏色)` | 有臉的參賽者（文件形狀），`mood()` 換表情 |
| `paddle(數字)`、`stamp(文字)`＋`stamp_in()`、`pop_in`、`shake`、`jolt` | 評分牌、印章砸下、彈出、搖晃、跳一下 |
| `ProbMenu(probs, color, title)` | 自動完成選單式的機率表（token 方塊＋橫條＋百分比），可以逐列長出 |
| `press(label)` | 油壓機（`nocheck`，桿子會伸出畫面） |
| `Seesaw(counts, …)` | 積木蹺蹺板：`counts` 是每個分數的積木數（1 塊＝1%）。支點位置 `fx`、傾角 `angle` 都是 ValueTracker；`settle(target)` 讓支點滑過去、傾角跟著力矩變；`set_counts()` 換一組分佈。用 `always_redraw` 畫 |
| `Balance(w, at)` | 天平，`ang` 是傾角，`pan(±1)` 取得秤盤位置 |
| `waffle(counts, colors)` | 10×10 百格圖，依直行填色 |
| `Chart(xs, y0, y1, …)`＋`.p(i, v)`＋`.series(idx, vals, color)` | 不用 LaTeX 的折線圖 |
| `num(值, 小數位, …)` | Text 做的計數器，用 `m.tr.animate.set_value(v)` 讓它滾動 |
| `db_icon`、`bubble`、`think`、`knob`＋`turn`、`coin`、`gear`、`check_mark`、`cross_mark`、`tag`、`pill` | 資料庫圖示、對話泡泡、想法泡泡、旋鈕、硬幣、齒輪、勾、叉、示意標籤、膠囊標籤 |
| `shatter(m)`、`confetti(center)` | 碎裂掉落、紙屑噴出 |
| `chapter_card(n, title)` | 斜切的章節卡（陰影＋色塊＋大號數字＋章名＋片名） |

### 8.4 常用 Manim 技巧

- **物理系統用 ValueTracker 加 `always_redraw`**：蹺蹺板、天平、會被拉伸的 S 曲線（`st` 從 0 到 1，同時改橫軸範圍和點的位置）、體重計平均值的晃動範圍。
- **兩個量連動用 `UpdateFromAlphaFunc`**：支點移動時傾角跟著算（`Seesaw.settle`）。
- **鏡頭**：`self.camera.frame.animate.scale(0.8).move_to(...)`，用在推近評審和鑽進螢幕。推近時要 `zone_check = False`。
- **在一個 `at()` 裡用 `LaggedStart` 依序出現**：積木雨、百格圖逐格填色、出票機吐票。
- **加上 updater 之後，等待的格子也會逐格渲染**：進度條和嘴型同步都是 updater，所以會比較慢，但時間精確。

### 8.5 場景清單（v4）

| 檔案 | 場景 | 主要動畫 |
|---|---|---|
| s1.py | Sc01 老是平手 | 舞台、評審舉牌、印章疊起來、27% 百格圖、沒有冠軍的頒獎台、推近、標題卡、開蓋鑽進螢幕 |
| | Sc02 腦袋裡的機率 | 輸出串流＋分數格、自動完成選單、魚鉤、油壓機壓碎、倒帶、≠、警示帶 |
| | Sc03 期望值 | 扳開關、積木雨、蹺蹺板、3-2-1 倒數、支點滑動、算式、B 的分佈、放大的尺、出票機 |
| s2.py | Sc04 案例 | 任務卡、兩個代理人、終端機、/tmp 複製品、兩條路徑、檢查通過、想法泡泡被壓扁、三組百格圖 |
| | Sc05 證據 | 機器手臂、扳開關長條賽跑、+16.6、兩個限定條件、理想挑選者量尺 |
| s3.py | Sc06 三個旋鈕＋G | 控制面板、3×8 呼叫工廠＋計數器、看法線與 5 格、20 格尺、準確率曲線、兩種說法相撞 |
| | Sc07 K | 體重計點圖、晃動範圍縮小、+2 公斤、K 曲線、argmax 跑點、對角線、16 倍印章、粗尺與細尺 |
| | Sc08 C | 問題卡裂開、三張子準則卡、評審視線光束、準確率長條、ensemble 示意格子、C＝1、3 與「？」、換領域 |
| s4.py | Sc09 勝率與循環賽 | 20 個參賽者、S 曲線、1–20 壓成 0–1、曲線拉伸、190 條線 |
| | Sc10 PPT | 環狀賽 20 場、A／B 位置與天平、勝分硬幣、前 5 名、弱基準與強基準、pivot 輪、105 對 190、÷ 場次、落榜、5 人小圈 |
| | Sc11 代價與收尾 | 紅色格子回來、0 次排錯、半分計分、人審分流、帳單、三張重點卡、機器人說出答案、紙屑 |
| thumb.py | Thumb | YouTube 縮圖 |

## 9. ④ 渲染：`v4/render.sh`

```bash
printf "%s\n" $SCENES | xargs -P 4 -I{} sh -c 'f=${1%%:*}; n=${1##*:};
  uv run --project ../.. manim -q'$Q' --fps 30 --disable_caching --media_dir media/$n -o $n $f.py $n > ../out/log-$n.txt 2>&1' _ {}
```

- `Q=l` 輸出 480p30（檢查用），`Q=h` 輸出 1080p30。
- 每場用 `--media_dir media/<場景>`，避免平行渲染互搶文字快取。
- 渲完後依序把各場 mp4 寫進清單，用 `ffmpeg -f concat -c copy` 接起來，最後印出每場的版面檢查結果。
- 實測：全片 1080p 約 441 秒；重渲 4 場約 170 秒。

## 10. ⑤ 背景音樂：`v4/music.py`

- 完全用 numpy／scipy 合成，C 大調、A 小調系，**依每場的 `music` 情緒產生**：

| 情緒 | BPM | 和弦進行 | 特色 |
|---|---|---|---|
| playful | 104 | C–Am–F–G | 撥弦 8 分音琶音、輕鼓 |
| mystery | 84 | Am–F–Dm–E | 墊音＋鐘聲，無鼓 |
| bright | 100 | C–G–Am–F | 琶音＋鐘聲＋輕鼓 |
| groove | 96 | Am–G–F–G | 搖擺 hi-hat、低音切分 |
| machine | 100 | Dm–G–C–Am | 16 分音的機械滴答 |
| sport | 112 | C–F–G–C | 四拍大鼓＋2、4 拍拍手 |
| warm | 88 | F–G–Em–Am–F–G–C–C | 慢琶音、收在 C |

- **音色**：
  - 墊音是 3 個微失諧的加法合成（4 個泛音、0.35 秒起音）；
  - 撥弦用 Karplus-Strong，用 `scipy.signal.lfilter` 做延遲回授，速度快；
  - 貝斯是正弦波加二倍頻；
  - 鼓是正弦掃頻的大鼓、高通雜訊的 hi-hat、帶通雜訊的拍手；
  - 鐘聲是非整數倍泛音。
  - 最後過 9 kHz 低通。
- 每段先正規化到相同 RMS，場景交界做 1.2 秒交叉淡化，最後一場淡出 3 秒。

## 11. ⑥ 混音：`v4/mix.py`（48 kHz 立體聲）

- **基準是旁白**：每句先正規化到「有聲部分 RMS」−20 dBFS，峰值上限 0.95。
- **講話偵測**：10 ms 一格算 RMS，高於 −40 dB 算講話。起音 30 ms、釋放 350 ms，平滑成 0～1 的包絡 `vact`。
- **音效**：
  - 每種音效先正規化到有聲 RMS −30 dBFS，再加上各自的修正值 `TRIM`（例如 tick −6、thud 0）；
  - 乘上每個提示點的 `gain`；
  - 講話時壓低約 4 dB。
- **音樂**：
  - 整體 RMS 設在人聲 −17 dB；
  - 講話時再壓低 7 dB；
  - 第一場的刮唱片提示點之後，音樂靜音 1.6 秒，再用 0.8 秒淡回。
- 輸出 `mix.wav`（含音樂）和 `mix_nomusic.wav`。
- 實測：旁白期間音樂比人聲低 19.7 dB，1～4 kHz 語音頻段低 24 dB。

音效產生器 `v4/sfx.py`：14 種音效，全部用 numpy 合成，包括 pop、tick、click、thud、ding、chime、boing、crunch、whoosh、swoosh、rise、slide、scratch、buzz。

## 12. ⑦ 打包：`v4/package.sh`

1. **兩段式 loudnorm**：先用 `print_format=json` 量測，再帶入 `measured_I/TP/LRA/thresh` 和 `linear=true`，目標 I＝−16、TP＝−1.5、LRA＝11。AAC 192k、48 kHz。
2. **軟字幕版**：`mov_text`，繁中、簡中兩軌。
3. **燒入版**：`-vf "ass=out/subs.ass:fontsdir=…"`，libx264 crf 20、veryfast、yuv420p。
4. **無音樂版**：同樣流程，換用 `mix_nomusic.wav`。

> 可攜性注意：`package.sh` 的 `F=/root/.fonts` 是當時容器的路徑。換環境要改成放 Noto 字型的資料夾，例如 `../assets/fonts`。

## 13. ⑧ 自我檢查工具與 v4 的結果

| 工具 | 做什麼 | 門檻 | v4 結果 |
|---|---|---|---|
| `out/manim-layout-*.txt` | 每個 `at()` 之後的版面檢查 | 全部 OK；只容許晚 0.1～0.4 秒 | 只剩輕微延遲，加上一個刻意的魚鉤 |
| `sheet.py sid clip out.png [full]` | 每句結束後 0.25 秒的畫面拼成 4 欄縮圖，洋紅框標出字幕區。加 `full` 表示 clip 是整支片 | 人（Claude）逐張看 | 低畫質看 3 輪，最後看成片 |
| `still.py video` | 每秒 4 格、160×90 灰階，平均像素差小於 0.35 且持續 4 秒以上，就算靜止段落 | 越少越好 | 53 秒降到 14 秒（2.2%） |
| `tts/synccheck.py` | 依每條字幕的時間切出成片音訊，辨識後算字錯率 | 平均約 0.05；超過 0.2 的要確認只是同音字 | 120 條，平均 0.045 |
| `ffmpeg … ebur128=peak=true` | 整體響度和峰值 | −16 LUFS 左右，峰值低於 −1 | −16.4 LUFS，−1.0 dBFS |
| `ffprobe -count_packets` | 影片格數 | 必須等於 timeline 的 `frames` | 19050＝19050 |

---

## 14. 做下一支片的建議步驟（含時間預估）

1. **選卡**：讀 concept-wiki 的卡，挑同一篇的 3～4 張。只用 normal 主張，列出 qualifiers 和要標「示意」的數字。
2. **分鏡＋腳本**：
   - 每場先想「物理比喻」和「怎麼把數字畫出來」，再寫句子；
   - 標出角色台詞；
   - 估算總長：中文約每秒 4.3～4.5 字。
3. **TTS**：`poly.py` → 修 `prep()` → `synth.py` → 看總長，太長就回到第 2 步刪句子。約 4 分鐘加上人工檢查。
4. **時間軸**：`timeline.py`。
5. **寫動畫**：
   - 先寫 2～3 場，用 `Q=l` 渲染，看縮圖、修，再寫下一批；
   - 程式碼量參考：v4 的 4 個場景檔加 common.py，約 2,060 行（v3 是約 1,540 行）。
6. **1080p 渲染 → 音樂 → 混音 → 打包。**
7. **自我檢查**：補靜止段落、核對忠實度、補示意標籤，然後只重渲有改的場景。
8. **交付**：成片、無音樂版、字幕、章節、縮圖、報告。
   - 明講哪些沒經人耳確認。
   - 不要覆蓋舊的快照。
