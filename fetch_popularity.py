#!/usr/bin/env python3
"""Pull page views for the last 30 days from GoatCounter into popularity.json.

Needs GOATCOUNTER_CODE (e.g. "floridamantimes") and GOATCOUNTER_TOKEN (API token, read-only is fine).
Without them, does nothing and the Top 10 falls back to newest stories.
"""
import datetime as dt
import json
import os
import re
import urllib.request

CODE = os.environ.get("GOATCOUNTER_CODE", "").strip()
TOKEN = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    if not (CODE and TOKEN):
        print("GoatCounter not configured; skipping.")
        return
    start = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    url = f"https://{CODE}.goatcounter.com/api/v0/stats/hits?start={start}&limit=200"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}",
                                               "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    views = {}
    for h in data.get("hits", []):
        m = re.match(r"^/stories/([a-z0-9-]+)/?$", h.get("path", ""))
        if m:
            views[m.group(1)] = views.get(m.group(1), 0) + int(h.get("count", 0))
    with open(os.path.join(ROOT, "popularity.json"), "w", encoding="utf-8") as f:
        json.dump({"updated": dt.date.today().isoformat(), "views": views}, f, indent=1)
    print(f"Saved views for {len(views)} stories.")


if __name__ == "__main__":
    main()
