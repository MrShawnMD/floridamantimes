"""Roach Report data: pull the last few weeks of official Florida DBPR emergency restaurant
closures for ALL of Florida into closures.json, with each restaurant's county from DBPR's license files.

Source: https://www2.myfloridalicense.com/hotels-restaurants/public-records/
(weekly "Emergency Closures" spreadsheets, one per week, named by the Sunday it ends)

Run by the GitHub Action every day. Safe to run anywhere with internet; skips quietly on errors.
"""
import datetime as dt
import io
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "closures.json")
URL = "https://www2.myfloridalicense.com/hr/inspections/documents/EOS_Weekly_Extract_{}.xlsx"
DISTRICTS = None            # None = every district (all of Florida)
LICENSE_URL = "https://www2.myfloridalicense.com/sto/file_download/extracts/hrfood{}.csv"
WEEKS = 4
SKIP_REASONS = ("unlicensed",)  # paperwork, not grossness


def saturdays(n):
    d = dt.date.today()
    d -= dt.timedelta(days=(d.weekday() - 6) % 7)   # most recent Sunday (or today)
    for i in range(n + 1):
        yield d - dt.timedelta(weeks=i)


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; FloridaManTimesBot/1.0; +https://floridamantimes.com)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def license_counties():
    """License number -> county, from DBPR's 7 district license files."""
    import csv
    out = {}
    for d in range(1, 8):
        try:
            text = get(LICENSE_URL.format(d), timeout=120).decode("latin-1")
        except Exception:
            continue
        rows = csv.reader(io.StringIO(text))
        hdr = next(rows, [])
        try:
            li, ci = hdr.index("License Number"), hdr.index("Location County")
        except ValueError:
            continue
        for r in rows:
            if len(r) > max(li, ci) and r[li].strip():
                out[re.sub(r"\D", "", r[li])] = r[ci].strip().title()
    return out


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


# DBPR county codes: first 2 digits of a license number, counties in alphabetical order from 11
_ALPHA = ("Alachua Baker Bay Bradford Brevard Broward Calhoun Charlotte Citrus Clay Collier Columbia Dade DeSoto Dixie Duval "
          "Escambia Flagler Franklin Gadsden Gilchrist Glades Gulf Hamilton Hardee Hendry Hernando Highlands Hillsborough Holmes "
          "Indian_River Jackson Jefferson Lafayette Lake Lee Leon Levy Liberty Madison Manatee Marion Martin Monroe Nassau Okaloosa "
          "Okeechobee Orange Osceola Palm_Beach Pasco Pinellas Polk Putnam St._Johns St._Lucie Santa_Rosa Sarasota Seminole Sumter "
          "Suwannee Taylor Union Volusia Wakulla Walton Washington").split()
CODE_TO_COUNTY = {str(11 + i): n.replace("_", " ") for i, n in enumerate(_ALPHA)}


def fix_county(c):
    c = c.replace("Dade", "Miami-Dade") if c.lower() in ("dade", "miami dade", "miami-dade") else c
    return {"Desoto": "DeSoto", "St. Johns": "St. Johns", "St Johns": "St. Johns", "St Lucie": "St. Lucie", "St. Lucie": "St. Lucie"}.get(c, c)


def main():
    items, weeks = [], []
    for sat in saturdays(WEEKS):
        blob = fetch(sat)
        if not blob:
            continue
        weeks.append(sat.isoformat())
        for r in rows(blob):
            district, lic, name, addr, city, date, t_close, vacate, t_open, reason = (list(r) + [None] * 11)[:10]
            if DISTRICTS and str(district).strip() not in DISTRICTS:
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
    counties = license_counties()
    sys.path.insert(0, ROOT)
    from counties import county_for
    for x in items:
        num = re.sub(r"\D", "", x["license"])
        c = counties.get(num, "") or CODE_TO_COUNTY.get(num[:2], "")
        x["county"] = fix_county(c) if c else county_for(x["city"])
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
