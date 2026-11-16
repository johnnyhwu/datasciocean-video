---
name: assemble
description: 影片第 7、8 步「合成」與「成片自檢」：混音（旁白、音效、曲庫音樂）、兩段式響度正規化、軟字幕成片，跑完所有程式檢查，整理關卡 3 審查包。
---

# 第 7 步：合成　＋　第 8 步：成片自檢

## 音樂

**預設：音樂只當標點，不鋪底**（使用者 2026-11-16 聽了 v001 三版後定的方向）。

- 第一版鋪底太小聲、太低沉；第二版換明亮的曲子並調大聲，使用者說「干擾人聲」「一直持續存在有點吵」，並指定參考 podcast 的開場音。podcast 專案早就量過同一件事（`datasciocean-podcast/docs/MUSIC.md`）：曲子的能量集中在 1～4 kHz 的子音帶，鋪底要嘛聽不見、要嘛蓋話。**不要再試鋪底**，除非使用者要求。
- 用和 podcast 同一首品牌音樂（`brand_intro`、`brand_sting`、`brand_outro`，紀錄在 `assets/music-library.yaml`），在 `script.json` 的 `music_punct` 設定三種位置：
  - **片頭**：鉤子最後一句說完的瞬間進來（`after` 那一句、`lead` 是弱起拍長度）。下一場的 `pad` 前置要留約 2.4 秒給音樂，這段時間畫面必須在動（v001 是鏡頭拉遠），不能停格。
  - **章節轉場**：全片 3 次左右，放在大段落的開頭（`before` 列出該段第一句）。不要每場都放。
  - **片尾**：最後一句結束前 3 秒壓低進來，旁白結束後升回全音量，鋪滿片尾畫面。
- 旁白進來時音樂自動壓低到子音帶比旁白低 22 dB 以上（`mix.py` 的 `punct_track`，`mix.json` 的 `music_punct` 會列出每一段實際壓了多少）。
- 動了 `pad` 就是動時間軸：重跑 `timeline.py`、低畫質重渲清檢查、再渲 1080p。

以下是鋪底模式的規則（場景的 `music` 欄位；沒有 `music_punct` 時才生效）：

- **只能用使用者的曲庫**：`assets/music-library.yaml` 記錄授權資訊（進 git），音樂檔放在 `assets/music/`（不進 git）。不得自己找音樂，AI 生成的音樂預設也不用。
- 場景的 `music` 欄位填曲目代號；連續同代號的場景共用一段，段與段之間交叉淡化。
- 片頭固定用一首識別曲。段落背景從曲庫輪替，記進結構指紋，不要每支都一樣。
- 標 CC 的曲目，說明欄一定要附標示（`mix.json` 的 `music_used` 會列出來）。
- 音量：`music_level_db`（預設 −13，相對旁白，以 200 Hz 以上計）、旁白時再壓低 `music_duck_db`（預設 −6）。`mix.py` 會把音樂 200 Hz 以下減 6 dB。
- **選曲先量頻率，不要只看曲風描述**（v001，使用者 2026-11-16：「幾乎聽不到背景音」「好低沉」「沒什麼活力」）：第一批照「平靜、留白」的描述挑，其中一首 91% 的能量在 250 Hz 以下、2 kHz 以上是 0%，手機和筆電喇叭放不出來。講解段的曲子要：2 kHz 以上有能量（v001 換上的兩首約 6～8%）、有節拍（100～135 BPM）、每 10 秒的音量起伏在 ±2 dB 內（開頭不能是半分鐘的安靜前奏）。使用者要的是有活力，不是低調到聽不見。

曲庫格式：

```yaml
tracks:
  intro_id:   {file: "xxx.mp3", source: "YouTube 音訊庫", license: "不需標示", attribution: "", mood: "片頭識別"}
  curious_1:  {file: "yyy.mp3", source: "YouTube 音訊庫", license: "CC BY 4.0", attribution: "曲名 by 作者", mood: "好奇、輕快"}
```

## 音效

- 動畫程式的 `sfx=` 只寫種類（`tick`、`pop`、`slide`…）。實際的聲音由 `assets/sfx-library.yaml` 決定：有列的種類用錄音檔（CC0，放在 `assets/sfx/`，不進 git），同一種類的幾個變化輪流用；沒列的用 `lib/sfx.py` 的合成音。
- 錄音檔來源、授權、怎麼重新取得都寫在 `assets/sfx-library.yaml` 開頭；逐檔出處在 `assets/sfx/LICENSES-upstream.md`。要加新的音效，先確認是 CC0 或允許營利，再記進去。
- 音量由 `mix.py` 的 `calibrate` 自動對齊合成音的能量，換檔不用重調 `gain`。`mix.py <id> --synth` 可以混一版全合成音來對照。
- Claude 聽不到：選檔只能靠量測（起音位置、長度、頻率）。新換的音效一律列進審查包的「沒經過人耳確認」。

## 指令

```bash
uv run python lib/mix.py <id>            # → out/<id>/mix.wav、mix_nomusic.wav、mix.json
uv run python lib/package.py <id>        # → out/<id>/deliver/<id>.mp4（−14 LUFS、軟字幕繁簡兩軌）＋ checks.json
```

`package.py` 會檢查以下項目，全部通過才算完成：

- 響度在 ±1 LU 內；
- 真峰值 ≤ −1 dBTP；
- 取樣率 48 kHz；
- 影音長度差 ≤ 0.3 秒；
- 格數等於 timeline；
- C2PA 殘留。

響度只在全片做一次，不逐場景正規化；場景音訊保持 WAV，到最後一步才編碼。

交給使用者看之前（v001 的經驗）：

- **曲庫是空的就早點說**：進到這一步才發現 `assets/music-library.yaml` 不存在，只能交無音樂版。開始做動畫時就先確認曲庫，沒有就當下問使用者。
- **`deliver/` 只留這一版的檔案**：測試用的副本（無字幕版、舊的預覽）刪掉，免得使用者開到舊檔。
- **請使用者用 QuickTime 或手機開**，並附上指令 `open -a "QuickTime Player" <路徑>`。v001 第一次交片時使用者回報沒有聲音，檔案本身的音軌經程式檢查是正常的；原因沒有查證（推測是編輯器內建預覽不支援這個音訊格式）。
- 每次重交都要寫清楚這一版和上一版差在哪、哪些是新加而沒有經過人耳確認的。

## 成片自檢（第 8 步）

執行 `state.py set <id> 成片`，然後確認下列各項：

| 檢查 | 指令或來源 |
|---|---|
| 字幕（字數、行數、每秒字數、與顯示稿一致） | `timeline.py` 的輸出 |
| 字型（缺字、簡體字） | `lib/checks/fonts.py <id>` |
| 標記與數字 | `lib/checks/claims.py <id>` |
| 版面 | `out/<id>/layout-*.txt` 全部 OK |
| 逐格：跳出、空畫面、靜止段落 | `lib/checks/frames.py <id>`（✗ 一定要修；靜止段落補有目的的小動作） |
| 接縫 | `lib/checks/seams.py <id> -q h`（畫面一格不差＋接縫空檔 0.8～1.6 秒） |
| 響度、長度、格數、C2PA | `deliver/checks.json` |
| 結構指紋 | `lib/checks/fingerprint.py <id>`（最近 5 支） |

## 關卡 3 審查包（`videos/<id>/review/gate3.md`）

- 成片路徑：`out/<id>/deliver/<id>.mp4`，請使用者**用手機看完**。另外附一版無音樂的，因為 Claude 聽不到聲音。
- **被程式標記的項目**：
  - 疑似夾帶事實的包裝句（framing）；
  - 示意例子；
  - 只畫示意的圖；
  - 前置知識段與比例。
- 和規劃不同的地方，以及原因。
- 和最近影片的結構相似度。
- 這次新增或修改的規則。
- **沒經過人耳確認的部分**：旁白、音樂、音效。

使用者回饋後，只重做受影響的步驟與場景。核准後執行 `state.py approve <id> 3`，再 `set <id> 發布準備`，載入 `publish-prep`。
