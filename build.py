#!/usr/bin/env python3
"""Builds the Florida Man Times static site from stories.py.

Usage:  python3 build.py

Images: drop a picture named after the story's slug into /images
(e.g. images/florida-man-steals-school-bus-drives-it-all-day.jpg — .jpg, .jpeg, .png or .webp).
The build picks it up automatically. Stories without an image get a clean placeholder.
"""
import datetime as dt
import html
import json
import os
import re

from stories import STORIES
from arrests import ARRESTS
from events import EVENTS
from eats import EATS

SITE = "https://floridamantimes.com"
NAME = "Florida Man Times"
TAGLINE = "The wildest true stories from the Sunshine State"
ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_EXTS = (".webp", ".jpg", ".jpeg", ".png")

SECTIONS = {
    "Florida Man": "florida-man",
    "Florida Woman": "florida-woman",
    "Wild Florida": "wild-florida",
}

e = html.escape


def nice_date(d):
    return dt.date.fromisoformat(d).strftime("%b %-d, %Y")


def read_time(s):
    words = sum(len(p.split()) for p in s["body"])
    return max(1, round(words / 230))


def image_for(s):
    """Return the site path of a story's image, or None."""
    if s.get("image"):
        return s["image"]
    for ext in IMG_EXTS:
        if os.path.exists(os.path.join(ROOT, "images", s["slug"] + ext)):
            return f"/images/{s['slug']}{ext}"
    return None


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def page(title, description, canonical, body, extra_head="", og_type="website", og_image=None):
    og_image = SITE + (og_image or "/og-image.png")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#ffffff">
<meta property="og:site_name" content="{NAME}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
{extra_head}
</head>
<body>
{header()}
<main>
{body}
</main>
{footer()}
</body>
</html>
"""


def logo(cls="logo"):
    return f'<a class="{cls}" href="/" aria-label="{NAME} home"><span class="logo-mark">FM</span><span class="logo-text">Florida Man <b>Times</b></span></a>'


def header():
    nav = '<a href="/arrests/">Weirdest Arrests</a><a href="/events/">Events</a><a href="/eats/">Weird Eats</a>' + "".join(f'<a href="/section/{slug}/">{e(n)}</a>' for n, slug in SECTIONS.items())
    latest = STORIES[0]
    return f"""<header class="site-header">
  <div class="bar">
    {logo()}
    <nav class="nav">{nav}<a href="/about/">About</a></nav>
  </div>
  <div class="breaking">
    <div class="breaking-inner">
      <span class="pill live">Latest</span>
      <a href="/stories/{latest['slug']}/">{e(latest['title'])}</a>
    </div>
  </div>
</header>"""


def footer():
    year = dt.date.today().year
    nav = '<a href="/arrests/">Weirdest Arrests</a><a href="/events/">Events</a><a href="/eats/">Weird Eats</a>' + "".join(f'<a href="/section/{slug}/">{e(n)}</a>' for n, slug in SECTIONS.items())
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div>
      {logo("logo logo-footer")}
      <p class="footer-tag">{TAGLINE}. Real reports, retold our way, always linked to the source.</p>
    </div>
    <nav class="footer-nav">{nav}<a href="/about/">About</a><a href="/feed.xml">RSS</a></nav>
  </div>
  <p class="fine">People in arrest stories are presumed innocent unless proven guilty in court. Story images are illustrations, not photos of the people or events described. © {year} {NAME}.</p>
</footer>"""


def media(s, cls=""):
    img = image_for(s)
    if img:
        return (f'<div class="media {cls}"><img src="{img}" alt="Illustration for: {e(s["title"])}" '
                f'loading="lazy" decoding="async"></div>')
    return (f'<div class="media placeholder {cls}" aria-hidden="true">'
            f'<span class="ph-emoji">{s["emoji"]}</span></div>')


def tag(s):
    return f'<a class="tag" href="/section/{SECTIONS[s["category"]]}/">{e(s["category"])}</a>'


def meta(s):
    return f'<p class="meta">{e(s["location"])} <span>·</span> {nice_date(s["date"])} <span>·</span> {read_time(s)} min read</p>'


def card(s, variant=""):
    url = f'/stories/{s["slug"]}/'
    return f"""<article class="card {variant}">
  <a class="card-media" href="{url}">{media(s)}</a>
  <div class="card-body">
    {tag(s)}
    <h3><a href="{url}">{e(s["title"])}</a></h3>
    <p class="dek">{e(s["dek"])}</p>
    {meta(s)}
  </div>
</article>"""


def hero(s):
    url = f'/stories/{s["slug"]}/'
    return f"""<article class="hero">
  <a class="hero-media" href="{url}">{media(s, "wide")}</a>
  <div class="hero-body">
    {tag(s)}
    <h2><a href="{url}">{e(s["title"])}</a></h2>
    <p class="dek">{e(s["dek"])}</p>
    {meta(s)}
    <a class="read-more" href="{url}">Read the story <span aria-hidden="true">→</span></a>
  </div>
</article>"""


def trending(items):
    lis = "".join(
        f'<li><span class="num">{i}</span><div><a href="/stories/{s["slug"]}/">{e(s["title"])}</a>'
        f'<p class="meta">{e(s["category"])}</p></div></li>'
        for i, s in enumerate(items, 1))
    return f'<aside class="trending"><h2 class="label">Trending</h2><ol>{lis}</ol></aside>'


def arrest_id(a):
    return a["date"] + "-" + re.sub(r"[^a-z0-9]+", "-", a["place"].lower()).strip("-")


def arrest_image(a):
    for ext in IMG_EXTS:
        if os.path.exists(os.path.join(ROOT, "images", "arrests", arrest_id(a) + ext)):
            return f"/images/arrests/{arrest_id(a)}{ext}"
    if a.get("story"):
        st = next((x for x in STORIES if x["slug"] == a["story"]), None)
        if st:
            return image_for(st)
    return None


def arrest_thumb(a, cls="thumb"):
    img = arrest_image(a)
    if img:
        return f'<div class="{cls}"><img src="{img}" alt="Illustration" loading="lazy" decoding="async"></div>'
    return f'<div class="{cls} placeholder" aria-hidden="true"><span>{a.get("emoji", "🚨")}</span></div>'


def arrest_feed(items):
    lis = "".join(f"""<li>
  <a class="feed-item" href="/arrests/#{arrest_id(a)}">{arrest_thumb(a)}
  <div><span class="feed-place">{e(a["place"])} · {dt.date.fromisoformat(a["date"]).strftime("%b %-d")}</span>
  <span class="feed-head">{e(a["headline"])}</span></div></a>
</li>""" for a in items)
    return f"""<aside class="rail-box arrests-rail">
  <div class="rail-head"><span class="pill live">Police blotter</span><h2>Tonight's Weirdest Arrests</h2></div>
  <ol class="feed">{lis}</ol>
  <a class="rail-more" href="/arrests/">See all arrests →</a>
  <a class="rail-lookup" href="/arrest-lookup/">🔎 Look up a local arrest (official records)</a>
</aside>"""


def arrest_item(a, compact=False):
    more = f'<a class="arrest-more" href="/stories/{a["story"]}/">Full story →</a>' if a.get("story") else ""
    charge = f'<p class="arrest-charge"><span>Charge</span>{e(a["charge"])}</p>' if a.get("charge") else ""
    blurb = "" if compact else f'<p class="arrest-blurb">{e(a["blurb"])}</p>'
    return f"""<li class="arrest" id="{arrest_id(a)}">
  {arrest_thumb(a, "arrest-img")}
  <div class="arrest-meta"><span class="arrest-place">{e(a["place"])}</span><span>{e(a["county"])} County</span><span>{nice_date(a["date"])}</span></div>
  <h3>{e(a["headline"])}</h3>
  {blurb}{charge}
  <p class="arrest-links">{more}<a href="{a["source_url"]}" rel="nofollow noopener" target="_blank">Source: {e(a["source_name"])} ↗</a></p>
</li>"""


def arrests_band():
    items = "".join(arrest_item(a) for a in ARRESTS[:4])
    return f"""<section class="arrests-band">
  <div class="container">
    <div class="band-head">
      <div><span class="pill live">Police blotter</span><h2>Tonight's Weirdest Arrests</h2>
      <p>The strangest calls from Florida sheriff's reports, in two sentences or less. No names, no mugshots.</p></div>
      <a class="button" href="/arrests/">See all arrests</a>
    </div>
    <ol class="arrest-grid">{items}</ol>
  </div>
</section>"""


def build_arrests():
    groups = {}
    for a in ARRESTS:
        groups.setdefault(a["date"], []).append(a)
    days = "".join(
        f'<section class="arrest-day"><h2 class="label">{dt.date.fromisoformat(d).strftime("%A, %B %-d, %Y")}</h2>'
        f'<ol class="arrest-list">{"".join(arrest_item(a) for a in items)}</ol></section>'
        for d, items in groups.items())
    body = f"""<section class="container">
  <div class="page-head"><span class="pill live">Police blotter</span><h1>Tonight's Weirdest Arrests</h1>
  <p>The strangest arrests from across Florida, straight from sheriff's reports and local news. We never post names or mugshots, and everyone is presumed innocent unless proven guilty in court.</p></div>
  <div class="arrests-layout"><div>{days}</div><aside>{lookup_box()}</aside></div>
</section>"""
    write("arrests/index.html", page(
        f"Tonight's Weirdest Arrests in Florida | {NAME}",
        "The weirdest arrests in Florida, updated daily: strange charges and bizarre police reports from Sarasota, Tampa Bay and across the Sunshine State.",
        SITE + "/arrests/", body))


def upcoming_events():
    today = dt.date.today().isoformat()
    return sorted([ev for ev in EVENTS if ev["end"] >= today], key=lambda ev: ev["start"])


def event_when(ev):
    a, b = dt.date.fromisoformat(ev["start"]), dt.date.fromisoformat(ev["end"])
    if not ev.get("confirmed", True) and (b - a).days >= 27:
        return a.strftime("%B %Y")
    if a == b:
        return a.strftime("%b %-d, %Y")
    if a.month == b.month:
        return f"{a.strftime('%b %-d')}–{b.day}, {b.year}"
    return f"{a.strftime('%b %-d')} – {b.strftime('%b %-d, %Y')}"


def event_card(ev):
    a = dt.date.fromisoformat(ev["start"])
    tags = "".join(f'<span class="mini-tag">{e(t)}</span>' for t in ev.get("tags", []))
    badge = '<span class="tba">Confirm dates</span>' if not ev.get("confirmed", True) else ""
    note = f'<p class="ev-note">{e(ev["date_note"])}</p>' if ev.get("date_note") else ""
    return f"""<article class="event">
  <div class="ev-date"><span class="ev-mon">{a.strftime("%b")}</span><span class="ev-day">{a.day if ev.get("confirmed", True) or (dt.date.fromisoformat(ev["end"]) - a).days < 27 else "TBA"}</span></div>
  <div class="ev-body">
    <div class="ev-tags">{tags}{badge}</div>
    <h3><span class="ev-emoji">{ev["emoji"]}</span>{e(ev["name"])}</h3>
    <p class="meta">{e(ev["city"])} <span>·</span> {event_when(ev)}</p>
    <p class="ev-blurb">{e(ev["blurb"])}</p>{note}
    <a class="ev-link" href="{ev["link"]}" rel="noopener" target="_blank">Details ↗</a>
  </div>
</article>"""


def events_band():
    evs = upcoming_events()[:4]
    if not evs:
        return ""
    return f"""<section class="container">
  <div class="section-head split"><h2 class="label">Coming Up in Weird Florida</h2><a class="see-all" href="/events/">All events →</a></div>
  <div class="event-grid">{"".join(event_card(ev) for ev in evs)}</div>
</section>"""


def events_band_inner():
    evs = upcoming_events()[:4]
    if not evs:
        return ""
    return f"""<div class="section-head split"><h2 class="label">Coming Up in Weird Florida</h2><a class="see-all" href="/events/">All events →</a></div>
  <div class="event-list">{"".join(event_card(ev) for ev in evs)}</div>"""


LOOKUPS = [
    ("Hillsborough County", "Tampa · Brandon · Plant City", "Arrest Inquiry", "https://webapps.hcso.tampa.fl.us/ArrestInquiry/Home/"),
    ("Polk County", "Lakeland · Winter Haven · Bartow", "Jail Inquiry", "https://mugshots.polksheriff.org/detention/jail-inquiry"),
    ("Sarasota County", "Sarasota · Venice · North Port", "Arrests & Inmate Search", "https://www.sarasotasheriff.org/arrest-reports/"),
    ("Pinellas County", "St. Pete · Clearwater · Largo", "Inmate Booking Search", "https://pinellassheriff.gov/InmateBooking"),
    ("Every other Florida county", "Manatee, Charlotte, Lee, Pasco and more", "Florida Dept. of State county jail directory", "https://dos.myflorida.com/library-archives/research/florida-information/government/local-resources/county-jails-and-inmate-searches"),
]


def lookup_box(compact=False):
    items = "".join(f"""<li><a class="lookup" href="{u}" target="_blank" rel="noopener">
  <span class="lk-county">{e(c)}</span><span class="lk-towns">{e(t)}</span><span class="lk-go">{e(label)} ↗</span></a></li>""" for c, t, label, u in LOOKUPS)
    return f"""<section class="lookup-box">
  <div class="lookup-head"><span class="tag">Official records</span>
  <h2>Look Up a Local Arrest</h2>
  <p>Search the sheriff's own booking records, with charges, bond and booking photos, straight from the official source. An arrest or booking does not establish guilt.</p></div>
  <ul class="lookup-list">{items}</ul>
</section>"""


def build_lookup():
    body = f"""<section class="container" style="max-width:900px">
  <div class="page-head"><span class="pill live">Public records</span><h1>Florida Arrest Lookup</h1>
  <p>Who got booked last night? Every link below goes to an official sheriff's office or state government search, so the information comes straight from the source and stays up to date. Florida Man Times doesn't host or copy booking records.</p></div>
  {lookup_box()}
  <p class="section-sub" style="margin-top:20px">Booking information is an arrest record, not a conviction. For the final outcome of a case, check the county Clerk of Court.</p>
</section>"""
    write("arrest-lookup/index.html", page(
        f"Florida Arrest Lookup: Official County Booking Searches | {NAME}",
        "Look up recent arrests and jail bookings in Hillsborough, Polk, Sarasota, Pinellas and every Florida county using official sheriff's office search tools.",
        SITE + "/arrest-lookup/", body))


def build_events():
    evs = upcoming_events()
    body = f"""<section class="container">
  <div class="page-head"><span class="tag">Calendar</span><h1>Weird Florida Events</h1>
  <p>Frog legs, flying mullet, swamp cabbage, skunk apes and livestock. The oddball festivals, fairs and competitions coming up around Florida. Dates change, so check the official link before you go.</p></div>
  <div class="event-list">{"".join(event_card(ev) for ev in evs) or '<p class="empty">New events coming soon.</p>'}</div>
</section>"""
    write("events/index.html", page(
        f"Weird Florida Events & Festivals Calendar | {NAME}",
        "Upcoming weird Florida festivals and events: Frog Leg Festival, Swamp Cabbage Festival, Mullet Toss, Skunk Ape Festival, Python Challenge, county fairs and livestock shows.",
        SITE + "/events/", body))


def eat_card(x):
    eats = "".join(f'<span class="mini-tag">{e(t)}</span>' for t in x["eats"])
    status = ('<span class="status on">On the menu</span>' if x["status"] == "menu"
              else '<span class="status legend">Florida food legend</span>')
    return f"""<article class="eat">
  <div class="eat-emoji" aria-hidden="true">{x["emoji"]}</div>
  <div class="eat-body">
    {status}
    <h3>{e(x["name"])}</h3>
    <p class="meta">{e(x["place"])} <span>·</span> {e(x["city"])}</p>
    <div class="ev-tags">{eats}</div>
    <p class="ev-blurb">{e(x["blurb"])}</p>
    <a class="ev-link" href="{x["source_url"]}" rel="nofollow noopener" target="_blank">Source: {e(x["source_name"])} ↗</a>
  </div>
</article>"""


def build_eats():
    on = [x for x in EATS if x["status"] == "menu"]
    legends = [x for x in EATS if x["status"] != "menu"]
    body = f"""<section class="container">
  <div class="page-head"><span class="tag">Food</span><h1>Weird Eats in Florida</h1>
  <p>Gator tail, frog legs, elk, swamp cabbage, and the time a Tampa taco shop sold lion. Where to eat the strangest things in the Sunshine State. Menus change, so call ahead.</p></div>
  <div class="section-head"><h2 class="label">On the menu now</h2></div>
  <div class="eat-grid">{"".join(eat_card(x) for x in on)}</div>
  <div class="section-head"><h2 class="label">Florida food legends</h2></div>
  <p class="section-sub">No longer served, but never forgotten.</p>
  <div class="eat-grid">{"".join(eat_card(x) for x in legends)}</div>
</section>"""
    write("eats/index.html", page(
        f"Weird Eats in Florida: Gator, Frog Legs, Python & More | {NAME}",
        "Where to eat gator tail, frog legs, elk, swamp cabbage and other strange foods in Florida, plus legendary lion tacos and python pizza.",
        SITE + "/eats/", body))


def mini(s):
    url = f'/stories/{s["slug"]}/'
    return f"""<article class="mini">
  <a class="mini-media" href="{url}">{media(s)}</a>
  <div>{tag(s)}<h3><a href="{url}">{e(s["title"])}</a></h3><p class="meta">{e(s["location"])}</p></div>
</article>"""


def headline_list(items, title):
    lis = "".join(
        f'<li><span class="num">{i}</span><div><a href="/stories/{s["slug"]}/">{e(s["title"])}</a>'
        f'<p class="meta">{e(s["category"])}</p></div></li>' for i, s in enumerate(items, 1))
    return f'<aside class="trending"><h2 class="label">{title}</h2><ol>{lis}</ol></aside>'


def section_row(name, slug):
    items = [s for s in STORIES if s["category"] == name][:4]
    if not items:
        return ""
    return f"""<section class="container">
  <div class="section-head split"><h2 class="label">{e(name)}</h2><a class="see-all" href="/section/{slug}/">More {e(name)} →</a></div>
  <div class="grid4 rowscroll">{"".join(card(s) for s in items)}</div>
</section>"""


def eats_teaser():
    on = [x for x in EATS if x["status"] == "menu"][:3]
    leg = [x for x in EATS if x["status"] != "menu"][:1]
    lis = "".join(f"""<li><span class="eat-mini">{x["emoji"]}</span><div><strong>{e(x["name"])}</strong>
<p class="meta">{e(x["city"])} · {e(", ".join(x["eats"][:3]))}</p></div></li>""" for x in on + leg)
    return f"""<aside class="rail-box">
  <div class="rail-head"><span class="tag">Weird Eats</span><h2>Gator, frog legs &amp; the lion taco</h2></div>
  <ul class="eat-list">{lis}</ul>
  <a class="rail-more" href="/eats/">See the full guide →</a>
</aside>"""


def build_home():
    lead = STORIES[0]
    left = STORIES[1:3]
    latest = STORIES[3:11]
    body = f"""<section class="front3 container">
  <div class="col-left">{"".join(mini(s) for s in left)}</div>
  <div class="col-lead">{hero(lead)}</div>
  <div class="col-right">{arrest_feed(ARRESTS[:6])}</div>
</section>
<section class="container">
  <div class="section-head split"><h2 class="label">Latest Headlines</h2><a class="see-all" href="/section/florida-man/">All stories →</a></div>
  <div class="latest-wrap">
    <div class="grid4">{"".join(card(s) for s in (latest or STORIES[1:]))}</div>
  </div>
</section>

<section class="container two-up">
  <div>{events_band_inner()}</div>
  <div>{eats_teaser()}{headline_list(STORIES[:5], "Most Read")}</div>
</section>
{"".join(section_row(n, sl) for n, sl in SECTIONS.items())}
<section class="container">
  <div class="cta">
    <div>
      <h2>Seen something only Florida could pull off?</h2>
      <p>Our tip line opens soon. If it's real, wild and from the Sunshine State, it could be our next headline.</p>
    </div>
    <span class="cta-badge">🌴 Tips coming soon</span>
  </div>
</section>"""
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME,
              "url": SITE + "/", "description": TAGLINE}
    write("index.html", page(
        f"{NAME} | Florida Man News, Weird Florida Stories & Headlines",
        "Florida Man Times covers the latest Florida Man and Florida Woman news: bizarre arrests, wild gator encounters and the weirdest true stories from the Sunshine State.",
        SITE + "/", body,
        f'<script type="application/ld+json">{json.dumps(jsonld)}</script>',
        og_image=image_for(lead)))


def share_links(s):
    url = f'{SITE}/stories/{s["slug"]}/'
    from urllib.parse import quote
    u, t = quote(url, safe=""), quote(s["title"], safe="")
    return f"""<div class="share">
  <span>Share</span>
  <a href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener">Facebook</a>
  <a href="https://twitter.com/intent/tweet?url={u}&text={t}" target="_blank" rel="noopener">X</a>
  <a href="sms:?&body={t}%20{u}">Text</a>
  <button type="button" onclick="navigator.clipboard.writeText('{url}');this.textContent='Copied!'">Copy link</button>
</div>"""


def build_story(s):
    url = f'{SITE}/stories/{s["slug"]}/'
    paras = "".join(f"<p>{e(p)}</p>" for p in s["body"])
    related = [x for x in STORIES if x is not s][:3]
    img = image_for(s)
    jsonld = {
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": s["title"], "description": s["dek"],
        "datePublished": s["date"], "dateModified": s["date"],
        "mainEntityOfPage": url,
        "image": [SITE + (img or "/og-image.png")],
        "author": {"@type": "Organization", "name": NAME},
        "publisher": {"@type": "Organization", "name": NAME,
                      "logo": {"@type": "ImageObject", "url": SITE + "/favicon.svg"}},
        "articleSection": s["category"],
    }
    caption = '<p class="caption">Illustration. Not a photo of the people or events described.</p>' if img else ""
    body = f"""<article class="story">
  <header class="story-head">
    {tag(s)}
    <h1>{e(s["title"])}</h1>
    <p class="story-dek">{e(s["dek"])}</p>
    <div class="byline">
      <span class="avatar">FM</span>
      <div><strong>Florida Man Times Desk</strong>{meta(s)}</div>
    </div>
  </header>
  <figure class="story-media">{media(s, "wide")}{caption}</figure>
  <div class="story-body">{paras}</div>
  <div class="source-box">
    <span class="label">Source</span>
    <a href="{s["source_url"]}" rel="nofollow noopener" target="_blank">{e(s["source_name"])} ↗</a>
    <p>This story is based on reporting by {e(s["source_name"])}, retold in our own words.</p>
  </div>
  {share_links(s)}
</article>
<section class="container">
  <div class="section-head"><h2 class="label">Keep Reading</h2></div>
  <div class="grid">{''.join(card(x) for x in related)}</div>
</section>"""
    write(f'stories/{s["slug"]}/index.html', page(
        f'{s["title"]} | {NAME}', s["dek"], url, body,
        f'<script type="application/ld+json">{json.dumps(jsonld)}</script>',
        og_type="article", og_image=img))


def build_sections():
    for name, slug in SECTIONS.items():
        items = [s for s in STORIES if s["category"] == name]
        cards = "".join(card(s) for s in items) or '<p class="empty">New stories coming soon.</p>'
        body = f"""<section class="container">
  <div class="page-head"><span class="tag">Section</span><h1>{e(name)}</h1>
  <p>The latest {e(name)} stories, straight from real Florida headlines.</p></div>
  <div class="grid">{cards}</div>
</section>"""
        write(f"section/{slug}/index.html", page(
            f"{name} News & Stories | {NAME}",
            f"The latest {name} news and weird stories from across Florida.",
            f"{SITE}/section/{slug}/", body))


def build_about():
    body = """<article class="story">
  <header class="story-head"><span class="tag">About</span><h1>About Florida Man Times</h1></header>
  <div class="story-body">
  <p>Other states have news. Florida has <em>stories</em>. The kind where you read the headline, read it again, and then call someone just to say it out loud.</p>
  <p>Florida Man Times is where those stories live. The stolen school buses. The gators who won't leave the driveway. The 911 calls that probably should have been texts to a friend.</p>
  <p>Here's our deal. Every story starts with a real report from a real news outlet or police agency. We retell it in our own words, with jokes clearly labeled as jokes and facts kept straight. Every story links back to the original source so you can check our homework.</p>
  <p>We laugh at bad decisions, never at people's suffering. And because an arrest is only an accusation, everyone in our arrest stories is presumed innocent unless a court says otherwise. Our story images are illustrations, not photos of the real people involved.</p>
  <p>Based in Sarasota, Florida. Of course.</p>
  </div>
</article>"""
    write("about/index.html", page(
        f"About | {NAME}",
        "About Florida Man Times, the home of Florida Man news and the weirdest true stories from the Sunshine State.",
        SITE + "/about/", body))


def build_404():
    body = """<article class="story center">
  <h1>This page wandered off.</h1>
  <p class="story-dek">Probably chasing a gator. Head back to the front page for today's headlines.</p>
  <p><a class="button" href="/">Back to the front page</a></p>
</article>"""
    write("404.html", page(f"Page Not Found | {NAME}", "Page not found.", SITE + "/404.html", body))


def build_feeds():
    today = dt.date.today().isoformat()
    urls = [(SITE + "/", today), (SITE + "/about/", today), (SITE + "/arrests/", today), (SITE + "/events/", today), (SITE + "/eats/", today), (SITE + "/arrest-lookup/", today)]
    urls += [(f"{SITE}/section/{slug}/", today) for slug in SECTIONS.values()]
    urls += [(f'{SITE}/stories/{s["slug"]}/', s["date"]) for s in STORIES]
    sm = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    items = ""
    for s in STORIES:
        d = dt.datetime.fromisoformat(s["date"]).strftime("%a, %d %b %Y 12:00:00 -0500")
        items += (f"<item><title>{e(s['title'])}</title><link>{SITE}/stories/{s['slug']}/</link>"
                  f"<guid>{SITE}/stories/{s['slug']}/</guid><pubDate>{d}</pubDate>"
                  f"<description>{e(s['dek'])}</description></item>")
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{NAME}</title>'
          f"<link>{SITE}/</link><description>{TAGLINE}</description>{items}</channel></rss>\n")


if __name__ == "__main__":
    for s in STORIES:
        assert s["category"] in SECTIONS, s["category"]
        assert re.fullmatch(r"[a-z0-9-]+", s["slug"]), s["slug"]
    os.makedirs(os.path.join(ROOT, "images"), exist_ok=True)
    build_home()
    for s in STORIES:
        build_story(s)
    build_sections()
    build_arrests()
    build_events()
    build_lookup()
    build_eats()
    build_about()
    build_404()
    build_feeds()
    with_img = sum(1 for s in STORIES if image_for(s))
    print(f"Built {len(STORIES)} stories ({with_img} with images).")
