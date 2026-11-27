"""Collect every recent Florida headline from many news feeds into scan/feed.json.

The daily story editor reads this file and decides which items are "Florida Man" material.
No keyword filtering happens here on purpose: we grab everything and let the editor judge.
Runs in GitHub Actions (stdlib only). Per-feed results go to scan/status.json.
"""
import email.utils
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

HOURS = 72
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Florida TV stations and newspapers (statewide coverage).
FEEDS = {
    "WFLA (Tampa)": "https://www.wfla.com/feed/",
    "WFLA Florida": "https://www.wfla.com/news/florida/feed/",
    "FOX 13 Tampa": "https://www.fox13news.com/rss/category/news",
    "FOX 13 Local": "https://www.fox13news.com/rss/category/local-news",
    "FOX 35 Orlando": "https://www.fox35orlando.com/rss/category/news",
    "FOX 35 Local": "https://www.fox35orlando.com/rss/category/local-news",
    "WTSP 10 Tampa Bay": "https://www.wtsp.com/feeds/syndication/rss/news",
    "Tampa Bay 28": "https://www.abcactionnews.com/index.rss",
    "WWSB Sarasota": "https://www.mysuncoast.com/arc/outboundfeeds/rss/?outputType=xml",
    "WESH Orlando": "https://www.wesh.com/topstories-rss",
    "ClickOrlando WKMG": "https://www.clickorlando.com/arc/outboundfeeds/rss/?outputType=xml",
    "WPBF West Palm": "https://www.wpbf.com/topstories-rss",
    "WPTV West Palm": "https://www.wptv.com/index.rss",
    "Local 10 Miami": "https://www.local10.com/arc/outboundfeeds/rss/?outputType=xml",
    "CBS Miami": "https://www.cbsnews.com/miami/latest/rss/main",
    "NBC 6 Miami": "https://www.nbcmiami.com/?rss=y",
    "WSVN 7 Miami": "https://wsvn.com/feed/",
    "News4Jax": "https://www.news4jax.com/arc/outboundfeeds/rss/?outputType=xml",
    "First Coast News": "https://www.firstcoastnews.com/feeds/syndication/rss/news",
    "WCJB Gainesville": "https://www.wcjb.com/arc/outboundfeeds/rss/?outputType=xml",
    "WCTV Tallahassee": "https://www.wctv.tv/arc/outboundfeeds/rss/?outputType=xml",
    "WTXL Tallahassee": "https://www.wtxl.com/index.rss",
    "WJHG Panama City": "https://www.wjhg.com/arc/outboundfeeds/rss/?outputType=xml",
    "WKRG Pensacola/Mobile": "https://www.wkrg.com/feed/",
    "WEAR Pensacola": "https://weartv.com/news/local.rss",
    "CBS12 West Palm": "https://cbs12.com/news/local.rss",
    "WFTV Orlando": "https://www.wftv.com/arc/outboundfeeds/rss/?outputType=xml",
    "Keys Weekly": "https://keysweekly.com/feed/",
    "Florida Keys Free Press / KeysInfoNet": "https://www.keysnews.com/search/?f=rss&t=article&l=50",
}

# Broad Google News searches (catch-all for outlets without feeds). Deliberately broad, not "weird" keywords.
GNEWS_QUERIES = [
    "Florida deputies", "Florida police said", "Florida sheriff's office", "Florida arrested",
    "Florida man", "Florida woman", "Florida wildlife", "FWC Florida",
    "Florida county commission", "Florida city council", "Florida lawsuit",
    "Sarasota", "Bradenton", "Tampa", "St. Petersburg Florida", "Fort Myers", "Cape Coral", "Naples Florida",
    "Orlando", "Daytona Beach", "Melbourne Florida", "Ocala", "Gainesville Florida", "Jacksonville",
    "Tallahassee", "Pensacola", "Panama City Beach", "Key West", "Miami", "Fort Lauderdale",
    "West Palm Beach", "Port St. Lucie", "Lakeland Florida", "Polk County Florida",
]
for q in GNEWS_QUERIES:
    FEEDS[f"Google News: {q}"] = ("https://news.google.com/rss/search?q="
                                  + urllib.parse.quote(f"{q} when:3d") + "&hl=en-US&gl=US&ceid=US:en")


STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Georgia",
          "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
          "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
          "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
          "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
          "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
# The other 49 states: their own "<State> man/woman" stories plus broad police-news searches and odd-news desks.
NATIONAL = {"UPI Odd News": "https://rss.upi.com/news/odd_news.rss"}
for q in [f"{st} man" for st in STATES] + [f"{st} woman" for st in STATES[::3]] + [
        "police said man arrested", "deputies said woman", "sheriff's office said", "odd news", "bizarre arrest"]:
    NATIONAL[f"Google News: {q}"] = ("https://news.google.com/rss/search?q="
                                     + urllib.parse.quote(f"{q} when:3d") + "&hl=en-US&gl=US&ceid=US:en")

# Upcoming events: festival / fair / competition announcements (30-day lookback, since events get announced early).
EVENT_QUERIES = ["Florida festival", "Florida festival 2027", "Florida fair 2027", "Florida county fair",
                 "Florida seafood festival", "Florida food festival", "Florida strawberry festival",
                 "Florida renaissance festival", "Florida rodeo", "Florida boat parade", "Florida air show",
                 "Florida chili cook-off", "Florida python challenge", "Florida mullet", "Florida swamp festival",
                 "Florida weird festival", "Florida parade", "Florida holiday lights", "Florida pirate festival",
                 "Sarasota festival", "Tampa festival", "Orlando festival", "Miami festival", "Jacksonville festival",
                 "Key West festival", "Panhandle festival"]
EVENTS = {f"Google News: {q}": ("https://news.google.com/rss/search?q=" + urllib.parse.quote(f"{q} when:30d")
                                + "&hl=en-US&gl=US&ceid=US:en") for q in EVENT_QUERIES}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def text(el, *names):
    for n in names:
        x = el.find(n)
        if x is not None:
            if x.text and x.text.strip():
                return x.text.strip()
            if x.get("href"):
                return x.get("href")
    return ""


def clean(s, n=320):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s[:n]


def parse_date(s):
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def parse(data, source):
    root = ET.fromstring(data)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//a:entry", ns)
    out = []
    for it in items:
        title = clean(text(it, "title", "{http://www.w3.org/2005/Atom}title"), 220)
        link = text(it, "link", "{http://www.w3.org/2005/Atom}link")
        desc = text(it, "description", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content")
        date = parse_date(text(it, "pubDate", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated",
                               "{http://purl.org/dc/elements/1.1/}date"))
        src = source
        s_el = it.find("source")
        if source.startswith("Google News") and s_el is not None and s_el.text:
            src = s_el.text.strip()
            title = re.sub(r"\s+-\s+" + re.escape(src) + r"$", "", title)
        if title and link:
            out.append({"title": title, "summary": clean(desc), "link": link.strip(), "source": src,
                        "via": source, "published": date.isoformat() if date else ""})
    return out


def collect(feeds, cutoff, seen, status):
    items = []
    for name, url in feeds.items():
        try:
            try:
                raw = fetch(url)
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise
                time.sleep(12)
                raw = fetch(url)
            got = parse(raw, name)
            fresh = 0
            for x in got:
                d = parse_date(x["published"]) if x["published"] else None
                if d and d < cutoff:
                    continue
                key = re.sub(r"[^a-z0-9]+", " ", x["title"].lower()).strip()[:90]
                if key in seen:
                    continue
                seen.add(key)
                items.append(x)
                fresh += 1
            status[name] = {"ok": True, "items": len(got), "kept": fresh}
        except Exception as e:  # keep going; report broken feeds
            status[name] = {"ok": False, "error": str(e)[:160]}
        time.sleep(2.0 if "news.google.com" in url or "keysnews" in url else 0.4)
    items.sort(key=lambda x: x["published"], reverse=True)
    return items


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS)
    seen, status = set(), {}
    items = collect(FEEDS, cutoff, seen, status)
    national = [x for x in collect(NATIONAL, cutoff, seen, status) if "florida" not in x["title"].lower()]
    os.makedirs("scan", exist_ok=True)
    meta = {"generated": datetime.now(timezone.utc).isoformat(), "hours": HOURS, "count": len(items),
            "feeds_ok": sum(1 for s in status.values() if s["ok"]), "feeds_total": len(status)}
    with open("scan/feed.json", "w") as f:
        json.dump({"meta": meta, "items": items}, f, indent=0, ensure_ascii=False)
    # Compact, numbered list for the editor to read in full (numbers match feed.json items).
    with open("scan/headlines.txt", "w") as f:
        f.write(f"# {meta['count']} Florida headlines, newest first, collected {meta['generated'][:16]} UTC. "
                "Format: number | published (UTC) | source | headline. Full link + summary: scan/feed.json items[number].\n")
        for i, x in enumerate(items):
            f.write(f"{i} | {x['published'][:16].replace('T', ' ')} | {x['source']} | {x['title']}\n")
    with open("scan/national.json", "w") as f:
        json.dump({"meta": {"generated": meta["generated"], "count": len(national)}, "items": national}, f, indent=0, ensure_ascii=False)
    with open("scan/national.txt", "w") as f:
        f.write(f"# {len(national)} headlines from the other 49 states, newest first. Format: number | published (UTC) | source | headline. "
                "Full link + summary: scan/national.json items[number].\n")
        for i, x in enumerate(national):
            f.write(f"{i} | {x['published'][:16].replace('T', ' ')} | {x['source']} | {x['title']}\n")
    events = collect(EVENTS, datetime.now(timezone.utc) - timedelta(days=30), set(), status)
    with open("scan/events.json", "w") as f:
        json.dump({"meta": {"generated": meta["generated"], "count": len(events)}, "items": events}, f, indent=0, ensure_ascii=False)
    with open("scan/events.txt", "w") as f:
        f.write(f"# {len(events)} Florida event headlines (last 30 days). Format: number | published | source | headline. "
                "Full link + summary: scan/events.json items[number]. Always confirm dates on the official event site.\n")
        for i, x in enumerate(events):
            f.write(f"{i} | {x['published'][:10]} | {x['source']} | {x['title']}\n")
    with open("scan/status.json", "w") as f:
        json.dump({"meta": meta, "feeds": status}, f, indent=1)
    print(f"{meta['count']} Florida + {len(national)} national + {len(events)} event headlines; {meta['feeds_ok']}/{meta['feeds_total']} feeds ok")


if __name__ == "__main__":
    main()
