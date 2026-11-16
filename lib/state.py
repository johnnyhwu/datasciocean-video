"""影片與卡的狀態（規格 §4.3）。狀態寫在檔案裡，中斷後從目前狀態接續，不從頭做。

用法：
  uv run python lib/state.py list                              所有影片的狀態
  uv run python lib/state.py new <影片 ID> --cards a,b,c         建立影片（記下 concept-wiki commit 與來源卡）
  uv run python lib/state.py set <影片 ID> <狀態> [--note "…"]    前進到下一個狀態（只能照順序；退回用 --back）
  uv run python lib/state.py approve <影片 ID> <關卡 1-4> --note "使用者原話摘要"
  uv run python lib/state.py card <卡 ID> waiting|unsuitable|candidate --note "原因"

影片狀態順序：選題 → 規劃 → 腳本 → 查核 → 旁白 → 動畫 → 合成 → 成片 → 發布準備 → 已發布
關卡：1 選題（進入規劃前）、2 規劃（進入腳本前）、3 成片（進入發布準備前）、4 發布（標已發布前）。沒有核准紀錄就不能越過關卡。
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from cards import wiki_commit  # noqa: E402
from paths import ROOT, video_dir  # noqa: E402

ORDER = ["選題", "規劃", "腳本", "查核", "旁白", "動畫", "合成", "成片", "發布準備", "已發布"]
GATE_BEFORE = {"規劃": 1, "腳本": 2, "發布準備": 3, "已發布": 4}
CARDS = ROOT / "state/cards.yaml"


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="minutes")


def load(vid):
    return json.loads((video_dir(vid) / "state.json").read_text())


def save(vid, st):
    (video_dir(vid) / "state.json").write_text(json.dumps(st, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--cards", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--back", action="store_true")
    a = ap.parse_args()
    if a.cmd == "list":
        for d in sorted((ROOT / "videos").iterdir()):
            if (d / "state.json").exists() and not d.name.startswith("_"):
                st = json.loads((d / "state.json").read_text())
                print(f"{d.name:32} {st['status']:6} 卡：{','.join(st['cards'])}  關卡：{sorted(map(int, st['approvals']))}")
        return
    if a.cmd == "card":
        cid, status = a.args
        data = yaml.safe_load(CARDS.read_text()) if CARDS.exists() else {}
        data[cid] = {"status": status, "note": a.note, "wiki_commit": wiki_commit(), "at": now()}
        CARDS.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=True))
        return
    vid = a.args[0]
    if a.cmd == "new":
        video_dir(vid).mkdir(parents=True, exist_ok=True)
        st = {"video": vid, "status": "選題", "cards": a.cards.split(","), "wiki_commit": wiki_commit(),
              "approvals": {}, "history": [{"status": "選題", "at": now(), "note": a.note}], "finished_at": ""}
        save(vid, st)
    elif a.cmd == "set":
        st = load(vid)
        new = a.args[1]
        i, j = ORDER.index(st["status"]), ORDER.index(new)
        if not a.back and j != i + 1:
            sys.exit(f"只能從「{st['status']}」前進到「{ORDER[i + 1]}」；要退回請加 --back")
        g = GATE_BEFORE.get(new)
        if not a.back and g and str(g) not in st["approvals"]:
            sys.exit(f"進入「{new}」前需要關卡 {g} 的核准紀錄（state.py approve）")
        st["status"] = new
        st["history"].append({"status": new, "at": now(), "note": a.note})
        if new == "成片" and not st.get("finished_at"):
            st["finished_at"] = now()
        if new == "已發布" and not st.get("published_at"):
            st["published_at"] = now()          # lib/analytics.py 用它算 d7、d28 的到期日
            up = video_dir(vid) / "upload-result.json"
            if up.exists():
                st["url"] = json.loads(up.read_text()).get("url", "")
        save(vid, st)
    elif a.cmd == "approve":
        st = load(vid)
        st["approvals"][a.args[1]] = {"at": now(), "note": a.note}
        save(vid, st)
    print(json.dumps(load(vid), ensure_ascii=False, indent=1)[:600])


if __name__ == "__main__":
    main()
