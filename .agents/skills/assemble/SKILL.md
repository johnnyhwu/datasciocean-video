---
name: assemble
description: 影片第 7、8 步「合成」與「成片自檢」：混音（旁白、音效、品牌音樂）、響度正規化、軟字幕成片，跑完所有程式檢查，整理關卡 3 審查包。
---

# 第 7 步：合成　＋　第 8 步：成片自檢

**Agent 聽不到聲音。** 這一步所有和聲音有關的決定都只能靠量測，交片時要明講哪些沒有經過人耳確認。

## 音樂：只當標點，不鋪底

> **2026-11-27 起品牌音樂停用**：Pixabay 那首被 Content ID 維持認領（`assets/music-library.yaml` 開頭）。新曲子要由使用者從 **YouTube 音效庫**挑好、放進 `assets/music/` 之後才能用；在那之前，交片和上傳都用無音樂版（`package.py --nomusic`，`upload.json` 加 `"video": "out/<id>/deliver/<id>-nomusic.mp4"`）。新曲子進來後，下面的規則照舊。

使用者 2026-11-16 聽了 v001 三版後定的方向，**每支影片都照這個做**：

- 用和 podcast 同一首品牌音樂（`brand_intro`、`brand_sting`、`brand_outro`，授權紀錄在 `assets/music-library.yaml`，檔案在 `assets/music/`，不進 git）。
- **不要鋪底。** 試過兩次都被退：第一次「幾乎聽不到」「好低沉」，第二次換明亮的曲子並調大聲後「干擾人聲」「一直持續存在有點吵」。podcast 專案早就量過原因（`datasciocean-podcast/docs/MUSIC.md`）：音樂的能量集中在 1～4 kHz，和人聲的子音同一個頻段，鋪在旁白下面要嘛聽不見、要嘛蓋話。
- 不自己找音樂，不用 AI 生成的音樂。要換曲子由使用者決定。

在 `script.json` 設定：

```json
"music_punct": {"intro":  {"track": "brand_intro", "after": "<鉤子最後一句的 id>", "lead": 1.25},
                "stings": {"track": "brand_sting", "before": ["<大段落第一句的 id>", "…"]},
                "outro":  {"track": "brand_outro", "pre": 3.0}}
```

| 位置 | 規則 |
|---|---|
| 片頭 | 鉤子最後一句說完的瞬間進來（`lead` 是弱起拍的長度，照抄 1.25）。下一場的 `pad` 前置留約 2.4 秒，這段畫面要在動 |
| 章節轉場 | 全片 3 次左右，放在大段落的開頭。不要每場都放 |
| 片尾 | 最後一句結束前 3 秒壓低進來，旁白結束後升到全音量，鋪滿頻道片尾動畫 |

- 旁白進來時，`mix.py` 會自動把音樂壓到子音頻段比旁白低 22 dB 以上。`mix.json` 的 `music_punct` 列出每一段的時間和實際壓了多少。
- 片頭和轉場的音檔直接來自 podcast，切點是使用者盲測選的，**不要重切**。片尾那一段是影片版另外切的（23 秒，podcast 的只有 7 秒）。
- 動了 `pad` 就是動時間軸，照 `animate` 的「時間軸變了就全部重來」。

## 音效

- 動畫程式的 `sfx=` 只寫種類。實際的聲音由 `assets/sfx-library.yaml` 決定：有列的種類用錄音檔（CC0，放在 `assets/sfx/`，不進 git），同一種類的幾個變化輪流用；沒列的（`whoosh`、`swoosh`）用 `lib/sfx.py` 的合成音。
- 錄音檔的來源、授權、怎麼重新取得，寫在 `assets/sfx-library.yaml` 開頭；逐檔出處在 `assets/sfx/LICENSES-upstream.md`。要加新的音效，先確認是 CC0 或允許營利，再記進去。
- 音量由 `mix.py` 自動對齊合成音的能量，換檔不用重調 `gain`。`mix.py <id> --synth` 可以混一版全合成音來對照。
- 選檔只能靠量測（起音位置、長度、頻率）。新換的音效一律列進審查包的「沒經過人耳確認」。

## 指令

```bash
uv run python lib/mix.py <id>               # → out/<id>/mix.wav、mix_nomusic.wav、mix.json
uv run python lib/package.py <id>           # → out/<id>/deliver/<id>.mp4（−14 LUFS、軟字幕繁簡兩軌）＋ checks.json
uv run python lib/package.py <id> --nomusic # → 無音樂版（對照用）
```

`package.py` 會檢查以下項目，全部通過才算完成：

- 響度在 −14 LUFS ±1 LU 內；
- 真峰值 ≤ −1 dBTP（編碼前有限幅器）；
- 取樣率 48 kHz；
- 影音長度差 ≤ 0.3 秒；
- 格數等於 timeline；
- C2PA 殘留。

響度只在全片做一次，不逐場景正規化；場景音訊保持 WAV，到最後一步才編碼。

## 交片給使用者看

- **附上開啟指令**：`open -a "QuickTime Player" <路徑>`，並請使用者用 QuickTime 或手機看。v001 第一次交片時使用者回報沒有聲音，檔案的音軌經程式檢查是正常的；原因沒有查證。
- **`deliver/` 只留這一版的檔案**。測試用的副本、舊的預覽，先告訴使用者再刪，免得他開到舊檔。
- **每次重交都寫清楚**：這一版和上一版差在哪、片長有沒有變、哪些是新加而沒有經過人耳確認的、要請他特別聽或看的時間點。
- 使用者的回饋是聽感（「低沉」「吵」「沒活力」）時，先量測找出原因再改，並把原因告訴他。不要只調一個音量就重交。

## 成片自檢（第 8 步）

執行 `state.py set <id> 成片`，然後確認下列各項：

| 檢查 | 指令或來源 |
|---|---|
| 字幕（字數、行數、每秒字數、與顯示稿一致） | `timeline.py` 的輸出 |
| 字型（缺字、簡體字） | `lib/checks/fonts.py <id>` |
| 標記與數字 | `lib/checks/claims.py <id>` |
| 版面 | `out/<id>/layout-*.txt` 全部 OK |
| 逐格：跳出、空畫面、靜止段落 | `lib/checks/frames.py <id>` |
| 接縫 | `lib/checks/seams.py <id> -q h` |
| 響度、長度、格數、C2PA | `deliver/checks.json` |
| 結構指紋 | `lib/checks/fingerprint.py <id>`（最近 5 支） |

## 關卡 3 審查包（`videos/<id>/review/gate3.md`）

- 成片路徑：`out/<id>/deliver/<id>.mp4`，請使用者**用手機看完**。另外附無音樂版。
- **被程式標記的項目**：
  - 疑似夾帶事實的包裝句（framing）；
  - 示意例子；
  - 只畫示意的圖；
  - 前置知識段與比例。
- 和規劃不同的地方，以及原因。
- 和最近影片的結構相似度。
- 這次新增或修改的規則。
- **沒經過人耳確認的部分**：旁白、音樂、音效。
- **觀眾體驗自審**：兩輪的分數、修了什麼、沒修什麼和原因（`review/selfreview.md`，做法見 `make-video` 第 4 節）。自審在寫審查包之前做，標題與縮圖草案先照 `publish-prep` 1、2 節做好。

使用者回饋後，只重做受影響的步驟與場景。核准後執行 `state.py approve <id> 3`，再 `set <id> 發布準備`，載入 `publish-prep`。
