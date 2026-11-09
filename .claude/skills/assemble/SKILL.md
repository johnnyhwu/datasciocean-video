---
name: assemble
description: 影片第 7、8 步「合成」與「成片自檢」：混音（旁白、音效、曲庫音樂）、兩段式響度正規化、軟字幕成片，跑完所有程式檢查，整理關卡 3 審查包。
---

# 第 7 步：合成　＋　第 8 步：成片自檢

## 音樂

- **只能用使用者的曲庫**：`assets/music-library.yaml` 記錄授權資訊（進 git），音樂檔放在 `assets/music/`（不進 git）。不得自己找音樂，AI 生成的音樂預設也不用。
- 場景的 `music` 欄位填曲目代號；連續同代號的場景共用一段，段與段之間交叉淡化。
- 片頭固定用一首識別曲。段落背景從曲庫輪替，記進結構指紋，不要每支都一樣。
- 標 CC 的曲目，說明欄一定要附標示（`mix.json` 的 `music_used` 會列出來）。
- 旁白時音樂壓低的幅度（`music_duck_db`），在旁白實驗中用耳朵決定。

曲庫格式：

```yaml
tracks:
  intro_id:   {file: "xxx.mp3", source: "YouTube 音訊庫", license: "不需標示", attribution: "", mood: "片頭識別"}
  curious_1:  {file: "yyy.mp3", source: "YouTube 音訊庫", license: "CC BY 4.0", attribution: "曲名 by 作者", mood: "好奇、輕快"}
```

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
