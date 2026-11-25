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
WEEKS = 8
WRITEUP_DAYS = 14
WRITEUP_MIN_HP = 3
INSP_URL = "https://www2.myfloridalicense.com/sto/file_download/extracts/{}fdinspi.csv"
WRITEUPS_OUT = os.path.join(ROOT, "roach-report", "writeups.json")
CLEAN_OUT = os.path.join(ROOT, "roach-report", "clean.json")
CLEAN_DAYS = 30
CLEAN_PER_COUNTY = 60
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


def plain_disposition(d):
    d = d.lower()
    if "admin" in d:
        return "Admin complaint recommended"
    if "warning" in d:
        return "Warning issued"
    if "extension" in d or "pending" in d:
        return "Follow-up inspection set"
    if "no further action" in d or "complied" in d:
        return "Fixed on the spot"
    return d.title()


def nice_name(n):
    import string
    n = " ".join(n.split())
    n = re.sub(r"\s+(ZWS|#\s*\d+|\d{3,})$", "", n, flags=re.I).strip()
    return string.capwords(n.lower()) if n.isupper() else n


def writeups():
    """Restaurants with WRITEUP_MIN_HP+ high-priority violations in the last WRITEUP_DAYS days (initial visits,
    not emergency closures), statewide, from DBPR's current-fiscal-year district inspection files."""
    import csv
    cut = dt.date.today() - dt.timedelta(days=WRITEUP_DAYS)
    ccut = dt.date.today() - dt.timedelta(days=CLEAN_DAYS)
    best, latest = {}, {}
    for d in range(1, 8):
        try:
            text = get(INSP_URL.format(d), timeout=180).decode("latin-1")
        except Exception:
            continue
        rows = csv.reader(io.StringIO(text))
        next(rows, None)
        for r in rows:
            if len(r) < 21:
                continue
            try:
                day = dt.datetime.strptime(r[14].strip(), "%m/%d/%Y").date()
                hp = int(r[18] or 0)
            except ValueError:
                continue
            disp = r[13].strip()
            lic0 = re.sub(r"\D", "", r[4]) or r[5]
            if day >= ccut and "routine" in r[12].lower():
                tot = int(r[17] or 0)
                prev = latest.get(lic0)
                if not prev or day > prev[0]:
                    latest[lic0] = (day, tot, r)
            if day < cut or hp < WRITEUP_MIN_HP or "emergency" in disp.lower() or r[10].strip() not in ("1", ""):
                continue
            lic = re.sub(r"\D", "", r[4])
            item = {"name": nice_name(r[5]), "address": " ".join(r[6].split()).title(), "city": r[7].strip().title(),
                    "county": fix_county(r[2].strip().title()), "date": day.isoformat(), "hp": hp,
                    "total": int(r[17] or 0), "result": plain_disposition(disp)}
            k = lic or (item["name"], item["address"])
            if k not in best or (item["date"], item["hp"]) > (best[k]["date"], best[k]["hp"]):
                best[k] = item
    out = sorted(best.values(), key=lambda x: (x["date"], x["hp"]), reverse=True)
    if out:
        os.makedirs(os.path.dirname(WRITEUPS_OUT), exist_ok=True)
        json.dump({"updated": dt.date.today().isoformat(), "days": WRITEUP_DAYS, "min_hp": WRITEUP_MIN_HP, "items": out},
                  open(WRITEUPS_OUT, "w"), separators=(",", ":"))
    print(f"Saved {len(out)} write-ups")
    # Clean Plate Club: latest routine inspection in the last CLEAN_DAYS had zero violations
    by_county = {}
    for day, tot, r in latest.values():
        if tot != 0 or r[11].strip().lower() != "food":
            continue
        name = nice_name(r[5])
        if not name or any(k in name.lower() for k in ("vending", "commissary", "catering truck")):
            continue
        c = fix_county(r[2].strip().title())
        by_county.setdefault(c, []).append({"name": name, "address": " ".join(r[6].split()).title(),
                                            "city": r[7].strip().title(), "county": c, "date": day.isoformat()})
    clean = []
    for c, lst in by_county.items():
        clean += sorted(lst, key=lambda x: x["date"], reverse=True)[:CLEAN_PER_COUNTY]
    if clean:
        json.dump({"updated": dt.date.today().isoformat(), "days": CLEAN_DAYS, "items": clean},
                  open(CLEAN_OUT, "w"), separators=(",", ":"))
    print(f"Saved {len(clean)} clean-plate restaurants")


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
    try:
        writeups()
    except Exception as ex:
        print("Write-ups failed:", ex)
