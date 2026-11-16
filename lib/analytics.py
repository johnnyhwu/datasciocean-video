"""發布後的成效追蹤：發布滿 7 天、28 天各抓一次 YouTube Analytics，存成 videos/<id>/d7.json、d28.json，並對照影片段落。

使用者 2026-11-16：成效「要由你自己 track」。Claude 沒辦法自己醒來，所以做法是：
每次開始工作都先跑 `--due`（CLAUDE.md「開始前」），有到期的就抓，抓完把結果講給使用者聽。

用法：
    uv run python lib/analytics.py --due            # 列出每支已發布影片的 d7、d28 狀態（不連線）
    uv run python lib/analytics.py <影片 ID> d7      # 抓發布後第 1～7 天的數據（d28：第 1～28 天）
    uv run python lib/analytics.py <影片 ID> d7 --show   # 只印已經存好的結果

只讀取（範圍 yt-analytics.readonly），授權存在 secrets/youtube_analytics_token.json（不進 git）。設定見 docs/youtube-upload.md。
API 沒有提供的：曝光次數與點閱率（CTR）。需要時請使用者從 Studio 的「觸及率」分頁看那一個數字。
數據大約延遲 2～3 天，所以發布後第 N+3 天才算到期。
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, video_dir  # noqa: E402

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
SECRET = ROOT / "secrets/youtube_client_secret.json"
TOKEN = ROOT / "secrets/youtube_analytics_token.json"
WINDOWS = {"d7": 7, "d28": 28}
LAG = 3   # 數據延遲的天數


def published():
    out = []
    for d in sorted((ROOT / "videos").iterdir()):
        st, up = d / "state.json", d / "upload-result.json"
        if not st.exists() or not up.exists():
            continue
        s = json.loads(st.read_text())
        if s.get("status") != "已發布" or not s.get("published_at"):
            continue
        out.append((d.name, datetime.fromisoformat(s["published_at"]).date(), json.loads(up.read_text())["video_id"]))
    return out


def due(today=None):
    today = today or date.today()
    rows = []
    for vid, pub, _ in published():
        for w, n in WINDOWS.items():
            ready = pub + timedelta(days=n + LAG)
            have = (video_dir(vid) / f"{w}.json").exists()
            rows.append((vid, w, "已抓" if have else ("到期" if today >= ready else f"{ready.isoformat()} 到期")))
    return rows


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    if not SECRET.exists():
        sys.exit(f"找不到 {SECRET.relative_to(ROOT)}。設定步驟見 docs/youtube-upload.md。")
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        print("瀏覽器會開啟 Google 授權頁（只要求「查看 YouTube 數據分析報表」），請選擇頻道所屬的帳號並按同意。")
        creds = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES).run_local_server(port=0)
        TOKEN.write_text(creds.to_json())
        TOKEN.chmod(0o600)
    return build("youtubeAnalytics", "v2", credentials=creds)


def by_scene(curve, timeline):
    """留存曲線（[(影片位置 0～1, 還在看的比例)]）對到場景與句子：每場開頭與結尾的留存、掉最多的幾個位置。"""
    total = timeline["duration"]
    at = lambda sec: next((v for r, v in curve if r * total >= sec), curve[-1][1])
    scenes = []
    for sc in timeline["scenes"]:
        a, b = at(sc["start"]), at(sc["start"] + sc["duration"])
        scenes.append({"id": sc["id"], "name": sc.get("name", ""), "start_s": round(sc["start"], 1), "len_s": round(sc["duration"], 1),
                       "retention_start": round(a, 3), "retention_end": round(b, 3), "lost": round(a - b, 3),
                       "lost_per_min": round((a - b) / max(sc["duration"], 1) * 60, 3)})
    sents = [(sc["start"] + s["start"], sc["id"], s["id"], s["display"]) for sc in timeline["scenes"] for s in sc["sentences"]]
    drops = []
    for (r0, v0), (r1, v1) in zip(curve, curve[1:]):
        sec = r1 * total
        near = max((x for x in sents if x[0] <= sec), default=sents[0], key=lambda x: x[0])
        drops.append({"at_s": round(sec, 1), "drop": round(v0 - v1, 4), "scene": near[1], "sentence": near[2], "text": near[3]})
    # 開頭 30 秒的流失另外看（每支影片開頭都掉最多），之後的才排名
    after = sorted([d for d in drops if d["at_s"] > 30], key=lambda d: -d["drop"])[:8]
    first30 = round(curve[0][1] - at(30), 3)
    return scenes, after, first30


def fetch(vid, window):
    pub, video_id = next((p, v) for n, p, v in published() if n == vid)
    start, end = pub, pub + timedelta(days=WINDOWS[window] - 1)
    if date.today() < end + timedelta(days=LAG):
        print(f"提醒：{window} 的數據要到 {(end + timedelta(days=LAG)).isoformat()} 才完整，現在抓到的是部分數據。")
    ya = service()
    q = lambda **kw: ya.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(),
                                        filters=f"video=={video_id}", **kw).execute()
    tot = q(metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares")
    names = [h["name"] for h in tot["columnHeaders"]]
    totals = dict(zip(names, tot["rows"][0])) if tot.get("rows") else {}
    ret = q(metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio", sort="elapsedVideoTimeRatio")
    curve = [(r[0], r[1]) for r in ret.get("rows", [])]
    rel = [(r[0], r[2]) for r in ret.get("rows", [])]
    src = q(metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views")
    daily = q(metrics="views,estimatedMinutesWatched", dimensions="day", sort="day")
    out = {"video": vid, "video_id": video_id, "window": window, "from": start.isoformat(), "to": end.isoformat(),
           "fetched_at": datetime.now().astimezone().isoformat(timespec="minutes"), "totals": totals,
           "impressions_ctr": None, "_ctr_note": "API 不提供曝光與點閱率；需要時請使用者從 Studio「觸及率」分頁提供",
           "traffic_sources": [dict(zip(["source", "views", "minutes"], r)) for r in src.get("rows", [])],
           "daily": [dict(zip(["day", "views", "minutes"], r)) for r in daily.get("rows", [])],
           "retention": curve, "relative_retention": rel}
    if curve:
        tl = json.loads((video_dir(vid) / "timeline.json").read_text())
        out["scenes"], out["steepest_drops"], out["lost_first_30s"] = by_scene(curve, tl)
    (video_dir(vid) / f"{window}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def show(o):
    t = o["totals"]
    print(f"{o['video']} {o['window']}（{o['from']} ～ {o['to']}，抓取 {o['fetched_at']}）")
    if not t:
        print("  沒有數據（觀看數太少時 YouTube 不提供）")
        return
    print(f"  觀看 {t.get('views')}；觀看時間 {t.get('estimatedMinutesWatched')} 分；平均觀看 {t.get('averageViewDuration')} 秒（{t.get('averageViewPercentage')}%）；"
          f"新訂閱 {t.get('subscribersGained')}；讚 {t.get('likes')}、留言 {t.get('comments')}、分享 {t.get('shares')}")
    print("  流量來源：", "、".join(f"{s['source']} {s['views']}" for s in o["traffic_sources"][:5]))
    if "scenes" not in o:
        print("  沒有留存曲線（觀看數太少時 YouTube 不提供）")
        return
    print(f"  前 30 秒流失 {o['lost_first_30s'] * 100:.0f} 個百分點")
    for s in o["scenes"]:
        print(f"  {s['id']} {s['name']:<10} 留存 {s['retention_start'] * 100:5.1f}% → {s['retention_end'] * 100:5.1f}%（每分鐘掉 {s['lost_per_min'] * 100:.1f}）")
    print("  30 秒之後掉最多的位置：")
    for d in o["steepest_drops"][:5]:
        print(f"    {int(d['at_s'] // 60)}:{int(d['at_s'] % 60):02d}  −{d['drop'] * 100:.1f}  {d['scene']}/{d['sentence']}  {d['text'][:24]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vid", nargs="?")
    ap.add_argument("window", nargs="?", choices=list(WINDOWS))
    ap.add_argument("--due", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    if a.due or not a.vid:
        rows = due()
        if not rows:
            print("沒有已發布的影片")
        for vid, w, st in rows:
            print(f"{'→' if st == '到期' else ' '} {vid}  {w}  {st}")
        if any(st == "到期" for _, _, st in rows):
            print("有到期的：跑 `uv run python lib/analytics.py <id> <d7|d28>`，把結果講給使用者聽（見 retrospective skill）。")
        return
    if not a.window:
        sys.exit("要指定 d7 或 d28")
    p = video_dir(a.vid) / f"{a.window}.json"
    show(json.loads(p.read_text()) if a.show and p.exists() else fetch(a.vid, a.window))


if __name__ == "__main__":
    main()
