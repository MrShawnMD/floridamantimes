"""Roach Report data: pull the last few weeks of official Florida DBPR emergency restaurant
closures for Tampa Bay & Southwest Florida (DBPR districts 3 and 7) into closures.json.

Source: https://www2.myfloridalicense.com/hotels-restaurants/public-records/
(weekly "Emergency Closures" spreadsheets, one per week, named by the Sunday it ends)

Run by the GitHub Action every day. Safe to run anywhere with internet; skips quietly on errors.
"""
import datetime as dt
import io
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "closures.json")
URL = "https://www2.myfloridalicense.com/hr/inspections/documents/EOS_Weekly_Extract_{}.xlsx"
DISTRICTS = {"3", "7"}       # 3 = Tampa Bay area, 7 = Sarasota/Manatee/Southwest Florida
WEEKS = 4
SKIP_REASONS = ("unlicensed",)  # paperwork, not grossness


def saturdays(n):
    d = dt.date.today()
    d -= dt.timedelta(days=(d.weekday() - 6) % 7)   # most recent Sunday (or today)
    for i in range(n + 1):
        yield d - dt.timedelta(weeks=i)


def fetch(day):
    try:
        req = urllib.request.Request(URL.format(day.isoformat()), headers={
            "User-Agent": "Mozilla/5.0 (compatible; FloridaManTimesBot/1.0; +https://floridamantimes.com)"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read()
    except Exception:
        return None


def rows(blob):
    import openpyxl
    ws = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    next(it, None)
    for r in it:
        if r and len(r) >= 10 and r[2]:
            yield r


def fmt_time(t):
    try:
        return t.strftime("%-I:%M %p")
    except Exception:
        return ""


def main():
    items, weeks = [], []
    for sat in saturdays(WEEKS):
        blob = fetch(sat)
        if not blob:
            continue
        weeks.append(sat.isoformat())
        for r in rows(blob):
            district, lic, name, addr, city, date, t_close, vacate, t_open, reason = (list(r) + [None] * 11)[:10]
            if str(district).strip() not in DISTRICTS:
                continue
            reason = (reason or "").strip()
            if any(k in reason.lower() for k in SKIP_REASONS):
                continue
            if not isinstance(date, (dt.date, dt.datetime)):
                continue
            items.append({
                "name": str(name).strip(),
                "address": str(addr or "").strip(),
                "city": str(city or "").strip(),
                "date": date.date().isoformat() if isinstance(date, dt.datetime) else date.isoformat(),
                "closed_at": fmt_time(t_close),
                "reason": reason,
                "reopened_at": fmt_time(t_open),
                "license": str(lic or ""),
                "week": sat.isoformat(),
            })
        if len(weeks) >= WEEKS:
            break
    if not items:
        print("No closures fetched; keeping existing closures.json")
        return
    seen, uniq = set(), []
    for x in sorted(items, key=lambda x: (x["date"], x["closed_at"]), reverse=True):
        k = (x["license"], x["date"])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    json.dump({"updated": dt.date.today().isoformat(), "weeks": weeks, "closures": uniq},
              open(OUT, "w"), indent=1)
    print(f"Saved {len(uniq)} closures from {len(weeks)} weekly files")


if __name__ == "__main__":
    main()
