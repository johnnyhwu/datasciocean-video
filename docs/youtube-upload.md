# 用 API 上傳到 YouTube（私人）

`lib/upload.py` 把成片上傳成**私人**，填好標題、三語說明、縮圖、字幕、AI use 欄位。公開由你在 YouTube Studio 自己按。
片尾畫面和自動配音 API 做不到，也在 Studio 手動設定。

## 一次性設定（約 15 分鐘，要登入你的 Google 帳號）

用**擁有 YouTube 頻道的那個 Google 帳號**登入。

### 1. 建專案

1. 開 https://console.cloud.google.com/projectcreate
2. 專案名稱填 `datasciocean-video`（隨意），按「建立」。
3. 建好後，確認頁面左上角的專案選單選的是這個專案。

### 2. 啟用 YouTube Data API v3

1. 開 https://console.cloud.google.com/apis/library/youtube.googleapis.com
2. 按「啟用」。

### 3. 設定 OAuth 同意畫面

1. 開 https://console.cloud.google.com/auth/overview ，按「開始」。
2. 應用程式名稱：`datasciocean-video`；使用者支援電子郵件：選你自己。
3. 目標對象（Audience）：選「外部」（External）。個人 Gmail 帳號只能選這個。
4. 聯絡資訊：填你的 email。同意政策，按「建立」。
5. 左邊選「目標對象」（Audience），在「測試使用者」按「新增使用者」，填你自己的 Gmail（頻道所屬的帳號），儲存。
   - 發布狀態維持「測試中」，不用送審。

### 4. 建立 OAuth 用戶端並下載

1. 左邊選「用戶端」（Clients），按「建立用戶端」。
2. 應用程式類型：**電腦版應用程式**（Desktop app）。名稱隨意。按「建立」。
3. 在跳出的視窗按「下載 JSON」。
4. 把下載的檔案搬到專案的 `secrets/` 資料夾，改名為 `youtube_client_secret.json`：

   ```bash
   mv ~/Downloads/client_secret_*.json secrets/youtube_client_secret.json
   ```

   這個資料夾不進 git。這個檔案是憑證，不要貼到對話裡。

### 5. 第一次授權

第一次執行 `uv run python lib/upload.py <id> --go` 時，瀏覽器會開啟授權頁：

1. 選頻道所屬的帳號。
2. 會出現「Google 尚未驗證這個應用程式」：按「繼續」（這是你自己的應用程式）。
3. 勾選兩個權限（管理 YouTube 影片、查看與管理字幕），按「繼續」。
4. 看到「The authentication flow has completed」就可以關掉分頁。

## 每支影片

```bash
uv run python lib/upload.py <id>        # 預演：只印出會上傳什麼
uv run python lib/upload.py <id> --go   # 上傳成私人
```

上傳完會印出 Studio 的連結。你在 Studio 做三件事：

1. 檢查標題、說明、縮圖、字幕。
2. 設定片尾畫面（最後 20 秒，元件放左右兩側）、自動配音。
3. 把瀏覽權限改成「公開」。

## 成效追蹤（`lib/analytics.py`）

發布滿 7 天、28 天，Claude 會各抓一次這支影片的數據（觀看、平均觀看時間、觀眾在哪裡離開、流量來源），存成 `videos/<id>/d7.json`、`d28.json`。只讀取，不會改任何東西。

多一個一次性設定：開 https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com ，按「啟用」（和上傳用同一個專案、同一個憑證檔）。

第一次抓的時候瀏覽器會再跳一次授權頁，這次只要求「查看 YouTube 數據分析報表」。

曝光次數和點閱率 API 不提供。Claude 需要時會請你從 Studio 的「數據分析 → 觸及率」看那兩個數字。

## 已知的限制

- **授權 7 天過期**：同意畫面在「測試中」時，授權只有 7 天。過期後程式會自動再開一次授權頁，按同意就好。
- **自訂縮圖**要頻道完成電話驗證（https://www.youtube.com/verify）。沒驗證時縮圖那一步會失敗，影片和字幕不受影響。
- 中途失敗可以重跑同一個指令，已經完成的步驟會跳過，不會重複上傳。
