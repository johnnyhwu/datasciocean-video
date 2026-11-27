"""把成片上傳到 YouTube，**一律上傳成私人**；使用者說定版之後，可以排程在上一支影片的 3 天後 09:00（台北）自動公開。

使用者 2026-11-16 同意：Claude 可以用 API 上傳成私人並填好所有欄位；不得上傳成公開、不得事後直接改成公開。
使用者 2026-11-23 加 --schedule（維持 private，只設 publishAt）；2026-11-27 改成上一支的 3 天後 09:00（原本每週六）。
這支程式沒有任何直接設成公開的路徑；privacyStatus 寫死在 PRIVACY。

用法：
    uv run python lib/upload.py <影片 ID>          # 預演：印出會上傳什麼，不連線
    uv run python lib/upload.py <影片 ID> --go     # 真的上傳（第一次會開瀏覽器請使用者授權）
    uv run python lib/upload.py <影片 ID> --update-meta --go   # 已上傳的影片：只更新標題、說明欄、標籤、翻譯（照 upload.json）
                                                          # 不送 status，隱私維持原狀；送完再讀一次隱私狀態確認沒變
    uv run python lib/upload.py <影片 ID> --schedule           # 預演：算出上一支的 3 天後 09:00（台北）
    uv run python lib/upload.py <影片 ID> --schedule --go      # 真的排程（只在使用者說影片定版之後做）
    uv run python lib/upload.py <影片 ID> --schedule --at 2026-12-05T09:00 --go   # 指定時間（台北時間）
    uv run python lib/upload.py <影片 ID> --status             # 讀線上的隱私與排程時間，記進 upload-result.json（使用者自己在 Studio 排程時用）

讀 videos/<id>/upload.json（標題、說明、多語、縮圖、字幕）；結果寫 videos/<id>/upload-result.json。
已經上傳過的步驟（影片、縮圖、各語字幕）會跳過，所以中途失敗可以重跑同一個指令。
憑證在 secrets/（不進 git）：youtube_client_secret.json 由使用者從 Google Cloud 下載；youtube_token.json 是授權後自動產生的。
設定步驟：docs/youtube-upload.md。API 做不到的（片尾畫面、自動配音）仍由使用者在 Studio 手動設定。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, out_dir, video_dir  # noqa: E402

PRIVACY = "private"          # 不要改。公開只能靠排程（publishAt）或使用者自己按
TZ = "Asia/Taipei"
SLOT_HOUR, GAP_DAYS = 9, 3      # 上一支的 3 天後 09:00（使用者 2026-11-27；原本是每週六）
MIN_LEAD_H = 24                   # 排程至少在 24 小時之後，留時間給使用者最後看一眼
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
SECRET = ROOT / "secrets/youtube_client_secret.json"
TOKEN = ROOT / "secrets/youtube_token.json"


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    if not SECRET.exists():
        sys.exit(f"找不到 {SECRET.relative_to(ROOT)}。請照 docs/youtube-upload.md 從 Google Cloud 下載 OAuth 用戶端的 JSON 放到這個位置。")
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None                      # 測試狀態的授權 7 天過期：重新走一次授權
    if not creds or not creds.valid:
        print("瀏覽器會開啟 Google 授權頁，請選擇頻道所屬的帳號並按同意。")
        creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES).run_local_server(port=0)
        TOKEN.write_text(creds.to_json())
        TOKEN.chmod(0o600)
    return build("youtube", "v3", credentials=creds)


def taken_slots(skip):
    """其他影片已經排的或已發布的日期（台北），避免同一天排兩支。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    out = set()
    for d in (ROOT / "videos").iterdir():
        if d.name == skip or not d.is_dir():
            continue
        r = d / "upload-result.json"
        if r.exists() and json.loads(r.read_text()).get("scheduled_at"):
            out.add(datetime.fromisoformat(json.loads(r.read_text())["scheduled_at"]).astimezone(ZoneInfo(TZ)).date())
        s = d / "state.json"
        if s.exists() and json.loads(s.read_text()).get("published_at"):
            out.add(datetime.fromisoformat(json.loads(s.read_text())["published_at"]).date())
    return out


def next_slot(vid):
    """上一支已排程或已發布影片的 GAP_DAYS 天後 09:00（台北）；至少 MIN_LEAD_H 小時後（使用者 2026-11-27：「我們現在 3 天發佈一個新影片」）。"""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo(TZ))
    taken = taken_slots(vid)
    t = now.replace(hour=SLOT_HOUR, minute=0, second=0, microsecond=0)
    if taken:
        t = max(t, datetime.combine(max(taken) + timedelta(days=GAP_DAYS), t.timetz()))
    while t - now < timedelta(hours=MIN_LEAD_H) or t.date() in taken:
        t += timedelta(days=1)
    return t


def schedule(a):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    res_path = video_dir(a.vid) / "upload-result.json"
    res = json.loads(res_path.read_text()) if res_path.exists() else {}
    if "video_id" not in res:
        sys.exit("還沒上傳過，沒有影片可以排程。")
    if a.status:
        live = service().videos().list(part="status", id=res["video_id"]).execute()["items"][0]["status"]
        res["privacy"] = live["privacyStatus"]
        if live.get("publishAt"):
            res["scheduled_at"] = datetime.fromisoformat(live["publishAt"].replace("Z", "+00:00")).astimezone(ZoneInfo(TZ)).isoformat(timespec="minutes")
        res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(f"隱私：{live['privacyStatus']}；排程：{res.get('scheduled_at', '無')}")
        return
    t = datetime.fromisoformat(a.at).replace(tzinfo=ZoneInfo(TZ)) if a.at else next_slot(a.vid)
    if t <= datetime.now(ZoneInfo(TZ)):
        sys.exit(f"{t} 已經過了")
    print(f"排程公開：{t.isoformat(timespec='minutes')}（台北，週{'一二三四五六日'[t.weekday()]}）；在那之前維持 private")
    if not a.go:
        print("這是預演，沒有連線。確認無誤後加 --go。")
        return
    yt = service()
    live = yt.videos().list(part="status", id=res["video_id"]).execute()["items"][0]["status"]
    if live["privacyStatus"] != PRIVACY:
        sys.exit(f"線上隱私是 {live['privacyStatus']}，不是 private；不動。請使用者到 Studio 確認：{res['studio']}")
    keep = {k: live[k] for k in ("embeddable", "license", "publicStatsViewable", "selfDeclaredMadeForKids", "containsSyntheticMedia") if k in live}
    utc = t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    yt.videos().update(part="status", body={"id": res["video_id"], "status": {**keep, "privacyStatus": PRIVACY, "publishAt": utc}}).execute()
    import time
    for _ in range(5):   # 剛寫入時回讀可能還沒同步（v005：第一次讀到 publishAt=None，幾秒後就有了）
        after = yt.videos().list(part="status", id=res["video_id"]).execute()["items"][0]["status"]
        if after.get("publishAt"):
            break
        time.sleep(4)
    if after["privacyStatus"] != PRIVACY or not after.get("publishAt"):
        sys.exit(f"排程後狀態不對：{after.get('privacyStatus')}、publishAt={after.get('publishAt')}。請立刻到 Studio 檢查：{res['studio']}")
    res["scheduled_at"] = t.isoformat(timespec="minutes")
    res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print("已排程（目前仍是 private）：", res["scheduled_at"], res["studio"])


def plan(vid):
    vd = video_dir(vid)
    spec = json.loads((vd / "upload.json").read_text())
    video = ROOT / spec["video"] if spec.get("video") else out_dir(vid) / "deliver" / f"{vid}.mp4"   # v005：可指定無音樂版
    thumb = ROOT / spec["thumbnail"]
    caps = [(c["language"], c.get("name", ""), ROOT / c["file"]) for c in spec.get("captions", [])]
    problems = []
    for p in [video, thumb] + [c[2] for c in caps]:
        if not p.exists():
            problems.append(f"找不到檔案：{p.relative_to(ROOT)}")
    if len(spec["title"]) > 100:
        problems.append("標題超過 100 字元")
    if len(spec["description"].encode()) > 5000:
        problems.append("說明欄超過 5000 bytes")
    if thumb.exists() and thumb.stat().st_size > 2 * 1024 * 1024:
        problems.append("縮圖超過 2MB")
    checks = out_dir(vid) / "deliver/checks.json"
    if checks.exists() and json.loads(checks.read_text()).get("c2pa", {}).get("found"):
        problems.append("成片有 C2PA 殘留")
    state = json.loads((vd / "state.json").read_text())
    if "3" not in state.get("approvals", {}):
        problems.append("關卡 3 還沒核准")
    body = {"snippet": {"title": spec["title"], "description": spec["description"], "categoryId": str(spec.get("category_id", 28)),
                        "defaultLanguage": spec.get("language", "zh-TW"), "defaultAudioLanguage": spec.get("language", "zh-TW"),
                        "tags": spec.get("tags", [])},
            "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": bool(spec.get("contains_synthetic_media", False)), "embeddable": True},
            "localizations": spec.get("localizations", {})}
    return spec, video, thumb, caps, body, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid")
    ap.add_argument("--go", action="store_true", help="真的上傳（沒加就只預演）")
    ap.add_argument("--update-meta", action="store_true", help="只更新已上傳影片的標題、說明欄、標籤、翻譯；不動隱私")
    ap.add_argument("--schedule", action="store_true", help="排程公開：上一支已排程影片的 3 天後 09:00（台北），影片維持 private 直到那時")
    ap.add_argument("--at", help="和 --schedule 一起用：指定台北時間，例如 2026-12-05T09:00")
    ap.add_argument("--status", action="store_true", help="讀線上的隱私與排程時間並記錄")
    a = ap.parse_args()
    if a.schedule or a.status:
        return schedule(a)
    spec, video, thumb, caps, body, problems = plan(a.vid)
    res_path = video_dir(a.vid) / "upload-result.json"
    res = json.loads(res_path.read_text()) if res_path.exists() else {}

    print(f"影片：{video.relative_to(ROOT)}（{video.stat().st_size / 1e6:.1f} MB）" if video.exists() else "影片：缺")
    print(f"隱私：{PRIVACY}（寫死；公開由使用者在 Studio 按）")
    print(f"標題：{body['snippet']['title']}")
    for lang, loc in body["localizations"].items():
        print(f"  [{lang}] {loc['title']}")
    print(f"說明欄：{len(body['snippet']['description'])} 字；分類 {body['snippet']['categoryId']}；AI 揭露 containsSyntheticMedia={body['status']['containsSyntheticMedia']}")
    print(f"縮圖：{thumb.relative_to(ROOT)}")
    for lang, name, p in caps:
        print(f"字幕 [{lang}]：{p.relative_to(ROOT)}")
    print("已完成的步驟：", {k: v for k, v in res.items() if k != "at"} or "無")
    if problems:
        print("問題：")
        for p in problems:
            print("  ✗", p)
        sys.exit(1)
    if not a.go:
        print("\n這是預演，沒有連線。確認無誤後加 --go。")
        return

    from googleapiclient.http import MediaFileUpload
    yt = service()

    if a.update_meta:
        if "video_id" not in res:
            sys.exit("還沒上傳過，沒有影片可以更新。")
        live = yt.videos().list(part="status,localizations", id=res["video_id"]).execute()["items"][0]
        before = live["status"]["privacyStatus"]
        # 線上已有的語言版本保留（例如 YouTube 自動建立的預設語言版本），再蓋上 upload.json 的；預設語言用 snippet 的標題與說明
        locs = {**live.get("localizations", {}), **body["localizations"]}
        dl = body["snippet"]["defaultLanguage"]
        if dl in locs:
            locs[dl] = {"title": body["snippet"]["title"], "description": body["snippet"]["description"]}
        # 只送 snippet 與 localizations；status 完全不送，所以隱私不會被改
        yt.videos().update(part="snippet,localizations",
                           body={"id": res["video_id"], "snippet": body["snippet"], "localizations": locs}).execute()
        after = yt.videos().list(part="status,snippet", id=res["video_id"]).execute()["items"][0]
        if after["status"]["privacyStatus"] != before:
            sys.exit(f"隱私狀態從 {before} 變成 {after['status']['privacyStatus']}！請立刻到 Studio 檢查：{res['studio']}")
        res["meta_updated_at"] = __import__("datetime").datetime.now().isoformat(timespec="minutes")
        res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(f"已更新標題與說明欄（隱私維持 {before}）：{after['snippet']['title']}")
        print(" ", res["studio"])
        return

    def save():
        res_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))

    if "video_id" not in res:
        req = yt.videos().insert(part="snippet,status,localizations", body=body, notifySubscribers=False,
                                 media_body=MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4"))
        out = None
        while out is None:
            st, out = req.next_chunk()
            if st:
                print(f"  上傳 {st.progress() * 100:.0f}%")
        if out["status"]["privacyStatus"] != PRIVACY:
            sys.exit(f"上傳後的隱私狀態是 {out['status']['privacyStatus']}，不是 {PRIVACY}。影片 ID {out['id']}，請立刻到 Studio 檢查。")
        res.update(video_id=out["id"], url=f"https://youtu.be/{out['id']}", studio=f"https://studio.youtube.com/video/{out['id']}/edit", privacy=PRIVACY)
        save()
        print("影片已上傳（私人）：", res["studio"])
    if not res.get("thumbnail"):
        try:
            yt.thumbnails().set(videoId=res["video_id"], media_body=MediaFileUpload(str(thumb))).execute()
            res["thumbnail"] = True
            save()
            print("縮圖已設定")
        except Exception as e:
            print("縮圖失敗（頻道要先完成電話驗證才能用自訂縮圖；可以在 Studio 手動上傳）：", str(e)[:200])
    done = res.setdefault("captions", [])
    for lang, name, p in caps:
        if lang in done:
            continue
        try:
            yt.captions().insert(part="snippet", body={"snippet": {"videoId": res["video_id"], "language": lang, "name": name}},
                                 media_body=MediaFileUpload(str(p), mimetype="application/octet-stream")).execute()
            done.append(lang)
            save()
            print(f"字幕 [{lang}] 已上傳")
        except Exception as e:
            print(f"字幕 [{lang}] 失敗（可以在 Studio 手動上傳）：", str(e)[:200])
    print("\n完成。影片是私人狀態。請使用者到 Studio 檢查、設定片尾畫面，然後自己按公開：")
    print(" ", res["studio"])


if __name__ == "__main__":
    main()
