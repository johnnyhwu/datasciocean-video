"""發布後的成效追蹤：發布滿 7 天、28 天各抓一次 YouTube Analytics，存成 videos/<id>/d7.json、d28.json，並對照影片段落。

使用者 2026-11-16：成效「要由你自己 track」。Claude 沒辦法自己醒來，所以做法是：
每次開始工作都先跑 `--due`（CLAUDE.md「開始前」），有到期的就抓，抓完把結果講給使用者聽。

用法：
    uv run python lib/analytics.py --due            # 列出每支已發布影片的 d7、d28 狀態（不連線）
    uv run python lib/analytics.py <影片 ID> d7      # 抓發布後第 1～7 天的數據（d28：第 1～28 天）
    uv run python lib/analytics.py <影片 ID> d7 --show   # 只印已經存好的結果
    uv run python lib/analytics.py --overview       # 頻道總覽：最近 28 天哪些影片帶來觀看與訂閱＋我們每支影片的累計

只讀取（範圍 yt-analytics.readonly），授權存在 secrets/youtube_analytics_token.json（不進 git）。設定見 docs/youtube-upload.md。
曝光次數與點閱率：Analytics API 沒有，改用 Reporting API 的 reach 報表（`reach()`，`--overview` 會一起抓）。
GCP 專案要啟用兩個 API：YouTube Analytics API、YouTube Reporting API。
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
        s, r = json.loads(st.read_text()), json.loads(up.read_text())
        if s.get("status") == "已發布" and s.get("published_at"):
            out.append((d.name, datetime.fromisoformat(s["published_at"]).date(), r["video_id"]))
        elif r.get("scheduled_at") and datetime.fromisoformat(r["scheduled_at"]) <= datetime.now().astimezone():
            # 排程時間已過、狀態還沒改：照排程時間算（提醒：跑 state.py set <id> 已發布）
            print(f"提醒：{d.name} 已在 {r['scheduled_at']} 排程公開，請跑 state.py set {d.name} 已發布", file=sys.stderr)
            out.append((d.name, datetime.fromisoformat(r["scheduled_at"]).date(), r["video_id"]))
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


def service(api="youtubeAnalytics", version="v2"):
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
    return build(api, version, credentials=creds)


# ---- 曝光次數與點閱率：YouTube Reporting API 的 reach 報表（2025-09 起提供） ----
# Analytics API（即時查詢）沒有曝光與點閱率；Reporting API 有，但它是「每天產生一份 CSV」的批次報表：
# 第一次要建立一個報表工作（job），之後 YouTube 每天自動產生，約 2 天後開始有檔案。只讀取，範圍同樣是 yt-analytics.readonly。
REACH_TYPE = "channel_reach_basic_a1"
REACH_DIR = ROOT / "out" / "_channel" / "reach"   # 原始 CSV（不進 git）


def reach():
    """建立（如果還沒有）reach 報表工作、下載所有新報表，回傳每支影片的累計曝光與點閱率。"""
    import csv
    import io
    yr = service("youtubereporting", "v1")
    jobs = yr.jobs().list().execute().get("jobs", [])
    job = next((j for j in jobs if j["reportTypeId"] == REACH_TYPE), None)
    if not job:
        job = yr.jobs().create(body={"reportTypeId": REACH_TYPE, "name": "datasciocean reach"}).execute()
        print(f"已建立報表工作 {REACH_TYPE}。YouTube 約 2 天後開始產生每日報表，之後再跑一次。")
    REACH_DIR.mkdir(parents=True, exist_ok=True)
    reps, tok = [], None
    while True:
        r = yr.jobs().reports().list(jobId=job["id"], pageToken=tok).execute()
        reps += r.get("reports", [])
        tok = r.get("nextPageToken")
        if not tok:
            break
    for rep in reps:
        f = REACH_DIR / f"{rep['startTime'][:10]}_{rep['id']}.csv"
        if f.exists():
            continue
        resp, content = yr._http.request(rep["downloadUrl"])
        if int(resp.status) != 200:
            raise RuntimeError(f"下載 reach 報表失敗：HTTP {resp.status}")
        f.write_bytes(content)
    per = {}
    for f in sorted(REACH_DIR.glob("*.csv")):
        for row in csv.DictReader(io.StringIO(f.read_text())):
            v = row.get("video_id")
            imp = float(row.get("video_thumbnail_impressions") or 0)
            ctr = float(row.get("video_thumbnail_impressions_ctr") or 0)
            a = per.setdefault(v, {"impressions": 0, "clicks": 0.0, "days": set()})
            a["impressions"] += imp
            a["clicks"] += imp * ctr
            a["days"].add(row.get("date"))
    out = {v: {"impressions": int(a["impressions"]), "ctr": round(a["clicks"] / a["impressions"], 4) if a["impressions"] else None,
               "days": len(a["days"])} for v, a in per.items()}
    return {"reports": len(reps), "videos": out}


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
           "impressions_ctr": None, "_ctr_note": "來自 Reporting API 的 reach 報表（發布至今累計）；None 表示報表還沒產生",
           "traffic_sources": [dict(zip(["source", "views", "minutes"], r)) for r in src.get("rows", [])],
           "daily": [dict(zip(["day", "views", "minutes"], r)) for r in daily.get("rows", [])],
           "retention": curve, "relative_retention": rel}
    try:
        out["impressions_ctr"] = reach()["videos"].get(video_id)
    except Exception as e:  # noqa: BLE001
        out["_ctr_note"] = f"reach 報表沒抓到：{str(e)[:160]}"
    if curve:
        tl = json.loads((video_dir(vid) / "timeline.json").read_text())
        out["scenes"], out["steepest_drops"], out["lost_first_30s"] = by_scene(curve, tl)
    (video_dir(vid) / f"{window}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def overview(days=28):
    """整個頻道最近 days 天的總覽，加上我們每支已發布影片從發布到現在的累計。存成 state/performance.json，歷史附加在 state/performance.jsonl。
    目的：每支影片做完（使用者按公開後）、選下一個題目之前，看哪支帶來觀看和訂閱，帶進選題和包裝。"""
    end = date.today() - timedelta(days=LAG)
    start = end - timedelta(days=days - 1)
    ya = service()
    q = lambda s, e, **kw: ya.reports().query(ids="channel==MINE", startDate=s.isoformat(), endDate=e.isoformat(), **kw).execute()
    row = lambda r: dict(zip([h["name"] for h in r["columnHeaders"]], r["rows"][0])) if r.get("rows") else {}
    chan = row(q(start, end, metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost"))
    ours = {v: n for n, _, v in published()}
    top = q(start, end, metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained", dimensions="video", sort="-views", maxResults=25)
    by_video = [dict(zip(["video_id", "views", "minutes", "avg_pct", "subs"], r), ours=ours.get(r[0])) for r in top.get("rows", [])]
    src = q(start, end, metrics="views", dimensions="insightTrafficSourceType", sort="-views")
    mine = []
    for vid, pub, video_id in published():
        t = row(q(pub, max(pub, end), metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained", filters=f"video=={video_id}"))
        title = json.loads((video_dir(vid) / "upload.json").read_text()).get("title", "") if (video_dir(vid) / "upload.json").exists() else ""
        mine.append({"video": vid, "title": title, "published": pub.isoformat(), "days": (end - pub).days + 1, **t})
    for m, (_, _, video_id) in zip(mine, published()):
        s = q(date.fromisoformat(m["published"]), max(date.fromisoformat(m["published"]), end), metrics="views",
              dimensions="insightTrafficSourceType", filters=f"video=={video_id}", sort="-views")
        m["traffic_sources"] = dict(s.get("rows", []))
        v = m.get("views") or 0
        m["subs_per_1k_views"] = round(1000 * (m.get("subscribersGained") or 0) / v, 1) if v else None
    try:
        rc = reach()
        for m, (_, _, video_id) in zip(mine, published()):
            m["reach"] = rc["videos"].get(video_id)
        for v in by_video:
            v["reach"] = rc["videos"].get(v["video_id"])
        reach_note = f"reach 報表 {rc['reports']} 份"
    except Exception as e:  # noqa: BLE001 — reach 抓不到不影響其他數字
        reach_note = f"reach 報表沒抓到：{str(e)[:200]}"
    out = {"fetched_at": datetime.now().astimezone().isoformat(timespec="minutes"), "from": start.isoformat(), "to": end.isoformat(),
           "channel": chan, "traffic_sources": [dict(zip(["source", "views"], r)) for r in src.get("rows", [])],
           "top_videos": by_video, "ours_lifetime": mine, "reach_note": reach_note,
           "_note": "top_videos 的 ours 為空的是頻道轉型前的舊影片（程式教學）。曝光與點閱率來自 Reporting API 的 reach 報表（每天一份，累計）。"}
    (ROOT / "state/performance.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    with open(ROOT / "state/performance.jsonl", "a") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")
    return out


def show_overview(o):
    c = o["channel"]
    print(f"頻道 {o['from']} ～ {o['to']}：觀看 {c.get('views')}；觀看時間 {c.get('estimatedMinutesWatched')} 分；"
          f"訂閱 +{c.get('subscribersGained')} −{c.get('subscribersLost')}")
    print("  流量來源：", "、".join(f"{s['source']} {s['views']}" for s in o["traffic_sources"][:6]))
    print("  觀看最多的影片：")
    for v in o["top_videos"][:10]:
        print(f"    {v['views']:>6} 次  {v['subs']:>3} 訂閱  {v['avg_pct']:.0f}%  {v['ours'] or '（舊影片）'}  {v['video_id']}")
    print("  我們的影片（發布至今）：")
    for m in o["ours_lifetime"]:
        r = m.get("reach") or {}
        ctr = f"曝光 {r['impressions']}、點閱率 {r['ctr'] * 100:.1f}%" if r.get("ctr") is not None else "曝光／點閱率：還沒有"
        print(f"    {m['video']}  第 {m['days']} 天  觀看 {m.get('views')}  訂閱 +{m.get('subscribersGained')}（每千次 {m.get('subs_per_1k_views')}）"
              f"  平均看完 {m.get('averageViewPercentage')}%  {ctr}  {m['title']}")
        if m.get("traffic_sources"):
            print("      來源：", "、".join(f"{k} {v}" for k, v in list(m["traffic_sources"].items())[:5]))
    print(f"  {o.get('reach_note', '')}")


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
    ap.add_argument("--overview", action="store_true", help="頻道總覽＋每支已發布影片的累計（每支影片做完、選下一題之前跑）")
    a = ap.parse_args()
    if a.overview:
        p = ROOT / "state/performance.json"
        show_overview(json.loads(p.read_text()) if a.show and p.exists() else overview())
        return
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
