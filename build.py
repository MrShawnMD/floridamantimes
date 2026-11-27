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
from urllib.parse import quote_plus
import re

from stories import STORIES
from arrests import ARRESTS
from events import EVENTS
from eats import EATS
from giving import LEMONADE
from features import ARTISTS, RENTALS
from places import PLACES
from interviews import INTERVIEWS, WANTED, STANDARD_QS
from cams import CAMS
from counties import county_for, county_of_place
from dispensaries import BRANDS, AREAS, STRAIN_WEEKS

SITE = "https://floridamantimes.com"
NAME = "Florida Man Times"
TAGLINE = "The wildest true stories from the Sunshine State"
ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_EXTS = (".webp", ".jpg", ".jpeg", ".png")
# Page-view counter (GoatCounter). Set the site code to turn on counting, e.g. "floridamantimes".
GOATCOUNTER = ""

SECTIONS = {
    "Florida Man": "florida-man",
    "Florida Woman": "florida-woman",
    "Wild Florida": "wild-florida",
    "Across America": "across-america",
}


def is_fl(s):
    return s.get("state", "Florida") == "Florida"


FL_STORIES = sorted([x for x in STORIES if is_fl(x)], key=lambda x: x["date"], reverse=True)
US_STORIES = sorted([x for x in STORIES if not is_fl(x)], key=lambda x: x["date"], reverse=True)

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


import hashlib as _h
CSS_V = _h.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.css"), "rb").read()).hexdigest()[:8]


def page(title, description, canonical, body, extra_head="", og_type="website", og_image=None):
    og_image = SITE + (og_image or "/og-image.png")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="BV_Wr2EBzm4kA7k0q5h4OoXQKXRjDEyM8KZqTfD7h8s" />
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
<link rel="stylesheet" href="/styles.css?v={CSS_V}">
{counter_tag()}
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


def counter_tag():
    if not GOATCOUNTER:
        return ""
    return (f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" '
            'async src="//gc.zgo.at/count.js"></script>')


def load_views():
    try:
        with open(os.path.join(ROOT, "popularity.json"), encoding="utf-8") as f:
            return json.load(f).get("views", {})
    except (OSError, ValueError):
        return {}


def top_stories(n=10):
    views = load_views()
    newest = sorted(STORIES, key=lambda s: s["date"], reverse=True)
    if not views:
        return newest[:n]
    return sorted(newest, key=lambda s: -int(views.get(s["slug"], 0)))[:n]


def logo(cls="logo"):
    return f'<a class="{cls}" href="/" aria-label="{NAME} home"><span class="logo-mark">FM</span><span class="logo-text">Florida Man <b>Times</b></span></a>'


CONTACT_EMAIL = ""   # set to e.g. "ads@floridamantimes.com" to turn on all contact buttons


COUNTY_URLS = []


HUB = [
    ("/", "🏠", "Home", "Today's weirdest Florida news"),
    ("/best-of/", "🏆", "Top 10", "The most-read Florida Man stories"),
    ("/arrests/", "🚔", "Arrests", "Tonight's weirdest arrests"),
    ("/events/", "🎪", "Events", "Fairs, festivals and python hunts"),
    ("/eats/", "🐊", "Weird Eats", "Gator, frog legs and lion tacos"),
    ("/effd-up/", "🎥", "Eff'd Up With…", "Video interviews with wild Floridians"),
    ("/cams/", "📹", "Florida Cams", "Live cams: manatees, Duval Street, rockets"),
    ("/roach-report/", "🪳", "Roach Report", "Restaurants the state just shut down"),
    ("/restaurant-inspections/", "📍", "My County", "Local news, arrests and eats for your county"),
    ("/clean-plate-club/", "🍽️", "Clean Plate Club", "Restaurants with perfect inspections"),
    ("/dispensaries/", "🌿", "Dispensaries", "Florida's medical marijuana guide"),
    ("/rentals/", "🛸", "Rentals", "Sleep in a UFO or a helicopter"),
    ("/odd-places/", "👻", "Spooky & Odd", "Haunted dolls, gravity hills, skunk apes"),
    ("/artist-of-the-week/", "🎨", "Artist", "Florida's wildest creative minds"),
    ("/gives-back/", "🍋", "Gives Back", "The LEMONADE charity drag race"),
    ("/arrest-lookup/", "🔎", "Arrest Lookup", "Official county booking searches"),
]


def hub_strip():
    chips = "".join(f'<a class="chip" href="{u}"><span aria-hidden="true">{em}</span>{e(n)}</a>' for u, em, n, _ in HUB)
    dupes = "".join(f'<a class="chip dupe" href="{u}" tabindex="-1" aria-hidden="true"><span>{em}</span>{e(n)}</a>' for u, em, n, _ in HUB)
    drift = """<script>(function(){var s=document.querySelector('.hub-inner');if(!s||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var on=true,t,x=0;function half(){return s.scrollWidth/2;}
function go(){if(on&&s.scrollWidth>s.clientWidth+40){x+=0.35;if(x>=half())x-=half();s.scrollLeft=x;}requestAnimationFrame(go);}
function stop(){on=false;clearTimeout(t);}function later(){clearTimeout(t);t=setTimeout(function(){x=s.scrollLeft;on=true;},3500);}
['pointerdown','touchstart','wheel','mouseenter'].forEach(function(ev){s.addEventListener(ev,stop,{passive:true});});
['pointerup','touchend','mouseleave'].forEach(function(ev){s.addEventListener(ev,later,{passive:true});});
s.addEventListener('scroll',function(){if(!on){if(s.scrollLeft>=half())s.scrollLeft-=half();}},{passive:true});
setTimeout(function(){x=s.scrollLeft;requestAnimationFrame(go);},1200);})();</script>"""
    return f"""<nav class="hub" aria-label="Sections"><div class="hub-inner">{chips}{dupes}</div></nav>{drift}
<script>(function(){{var p=location.pathname,best=null;document.querySelectorAll('.hub .chip:not(.dupe)').forEach(function(a){{var h=a.getAttribute('href');if((h==='/'&&p==='/')||(h!=='/'&&p.indexOf(h)===0))best=a;}});if(best){{best.classList.add('on');best.scrollIntoView({{inline:'center',block:'nearest'}});window.scrollTo(0,0);}}}})();</script>"""


def follow_box():
    return """<section class="follow-box"><div class="container follow-inner">
  <div><strong>Follow Florida Man Times</strong><span>Weird, true Florida in your feed every day.</span></div>
  <div class="follow-btns"><a class="fb" href="https://www.facebook.com/floridamantimes" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z"/></svg>Facebook</a><a class="ig" href="https://www.instagram.com/floridaman.times/" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 4.9a4.9 4.9 0 1 0 0 9.8 4.9 4.9 0 0 0 0-9.8zm0 8.1a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zm5.1-8.3a1.15 1.15 0 1 0 0-2.3 1.15 1.15 0 0 0 0 2.3z"/></svg>Instagram</a></div>
</div></section>"""


def explore_grid():
    tiles = "".join(f'<a class="ex-tile" href="{u}"><span class="ex-emoji" aria-hidden="true">{em}</span><strong>{e(n)}</strong><span>{e(d)}</span></a>'
                    for u, em, n, d in HUB[1:])
    return f"""<section class="explore"><div class="container">
  <div class="section-head"><h2 class="label">Explore Florida Man Times</h2></div>
  <div class="ex-grid">{tiles}</div>
</div></section>"""


def header():
    nav = ('<a class="nav-feat" href="/best-of/">Top 10</a><a class="nav-feat" href="/arrests/">Arrests</a><a class="nav-feat" href="/events/">Events</a>'
           '<a class="nav-feat" href="/eats/">Weird Eats</a><a class="nav-feat" href="/effd-up/">Eff\'d Up With…</a><a class="nav-feat" href="/rentals/">Rentals</a><a class="nav-feat" href="/odd-places/">Spooky &amp; Odd</a>'
           '<a class="nav-feat" href="/artist-of-the-week/">Artist of the Week</a><a class="nav-feat" href="/gives-back/">Gives Back</a>')
    sections = "".join(f'<a class="nav-extra" href="/section/{slug}/">{e(n)}</a>' for n, slug in SECTIONS.items())
    latest = FL_STORIES[0]
    return f"""<header class="site-header">
  <div class="bar">
    {logo()}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" onclick="var h=this.closest('.site-header'),o=h.classList.toggle('menu-open');this.setAttribute('aria-expanded',o);document.body.classList.toggle('no-scroll',o)"><span class="burger" aria-hidden="true"></span>Menu</button>
    <nav class="nav" id="site-nav"><a href="/">Home</a>{nav}<a class="nav-feat" href="/arrest-lookup/">Arrest Lookup</a>{sections}<a href="/about/">About</a></nav>
  </div>
  <div class="breaking">
    <div class="breaking-inner">
      <span class="pill live">Latest</span>
      <a href="/stories/{latest['slug']}/">{e(latest['title'])}</a>
    </div>
  </div>
</header>
{hub_strip()}"""


def footer():
    year = dt.date.today().year
    nav = ('<a href="/best-of/">Top 10</a><a href="/arrests/">Weirdest Arrests</a><a href="/arrest-lookup/">Arrest Lookup</a>'
           '<a href="/events/">Events</a><a href="/eats/">Weird Eats</a><a href="/effd-up/">Eff\'d Up With…</a><a href="/rentals/">Crazy Rentals</a><a href="/odd-places/">Spooky &amp; Odd Places</a>'
           '<a href="/artist-of-the-week/">Artist of the Week</a><a href="/gives-back/">Gives Back</a>'
           + "".join(f'<a href="/section/{slug}/">{e(n)}</a>' for n, slug in SECTIONS.items()))
    return f"""{follow_box()}{explore_grid()}<footer class="site-footer">
  <div class="footer-inner">
    <div>
      {logo("logo logo-footer")}
      <p class="footer-tag">{TAGLINE}. Real reports, retold our way, always linked to the source.</p>
    </div>
    <nav class="footer-nav">{nav}<a href="/about/">About</a><a href="/advertise/">Advertise</a><a href="https://www.facebook.com/floridamantimes" target="_blank" rel="noopener">Facebook</a><a href="https://www.instagram.com/floridaman.times/" target="_blank" rel="noopener">Instagram</a><a href="/feed.xml">RSS</a></nav>
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
    ("Hillsborough County", "Tampa · Brandon · Plant City", "HCSO Arrest Inquiry", "https://webapps.hcso.tampa.fl.us/ArrestInquiry/Home/",
     "No name needed: enter today's date in Booking Date, sort by Booking Date. (Brand-new arrests can take up to 24 hours to show.)"),
    ("Polk County", "Lakeland · Winter Haven · Bartow", "Polk Sheriff Jail Inquiry", "https://mugshots.polksheriff.org/detention/jail-inquiry",
     "No name needed: tap the Booking Date tab, pick a day, hit Search."),
    ("Pinellas County", "St. Pete · Clearwater · Largo", "Who's In Jail", "https://pinellassheriff.gov/InmateBooking",
     "No name needed: search by Booking Date."),
    ("Lee County", "Fort Myers · Cape Coral · Bonita Springs", "LCSO Arrest Search", "https://www.sheriffleefl.org/arrest-search/",
     "No name needed: set the Booking Date range and search."),
    ("Sarasota County", "Sarasota · Venice · North Port", "Arrests & Inmate Search", "https://www.sarasotasheriff.org/arrest-reports/",
     "Search by date or name in the sheriff's search box."),
    ("Orange County", "Orlando · Winter Park · Apopka", "Daily Booking List", "https://apps.ocfl.net/Bailbond/",
     "Ready-made list: tap Daily Booking List for everyone booked in the last 24 hours."),
    ("Broward County", "Fort Lauderdale · Hollywood · Pompano", "BSO Booking Blotter", "https://bookingblotter.sheriff.org/",
     "Ready-made list of recent bookings. No search needed."),
    ("Every other Florida county", "Manatee, Charlotte, Pasco, Miami-Dade and more", "Florida Dept. of State jail directory", "https://dos.myflorida.com/library-archives/research/florida-information/government/local-resources/county-jails-and-inmate-searches",
     "Links to every county jail's official search."),
]


def lookup_box(compact=False):
    items = "".join(f"""<li><a class="lookup" href="{u}" target="_blank" rel="noopener">
  <span class="lk-county">{e(c)}</span><span class="lk-towns">{e(t)}</span><span class="lk-tip">{e(tip)}</span><span class="lk-go">{e(label)} ↗</span></a></li>""" for c, t, label, u, tip in LOOKUPS)
    return f"""<section class="lookup-box">
  <div class="lookup-head"><span class="tag">Official records</span>
  <h2>Look Up a Local Arrest</h2>
  <p>See who got booked, with photos, charges and bond, straight from each sheriff's own records. Most let you browse by booking date, so you don't need a name. An arrest or booking does not establish guilt.</p></div>
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
        "Browse recent arrests and booking photos in Hillsborough, Polk, Pinellas, Lee, Sarasota, Orange, Broward and every Florida county using official sheriff's office tools.",
        SITE + "/arrest-lookup/", body))


def lemonade_promo():
    L = LEMONADE
    return f"""<section class="container"><a class="lemon-promo" href="/gives-back/{L["slug"]}/">
  <div class="lp-text"><span class="lp-kicker">🍋 Florida Man Times Gives Back</span>
  <h2>LEMONADE: The Lemon Drag Race</h2>
  <p>{e(L["tagline"])} Local businesses sponsor $500 beaters, deck them out and race them at a Florida dragstrip for charity.</p>
  <span class="lp-btn">See how it works →</span></div>
  <div class="lp-img">{'<img src="' + L["hero_image"] + '" alt="Lemon cars racing illustration" loading="lazy">' if os.path.exists(os.path.join(ROOT, L["hero_image"].lstrip("/"))) else '<span>🍋🏁</span>'}</div>
</a></section>"""


def build_best_of():
    views = load_views()
    items = top_stories(10)
    rows = ""
    for i, st in enumerate(items, 1):
        url = f'/stories/{st["slug"]}/'
        v = int(views.get(st["slug"], 0))
        vtxt = f'<span class="views">{v:,} reads</span>' if views else ""
        rows += f"""<li class="best-row"><span class="best-num">{i}</span>
  <a class="best-media" href="{url}">{media(st)}</a>
  <div class="best-body">{tag(st)}<h3><a href="{url}">{e(st["title"])}</a></h3><p class="dek">{e(st["dek"])}</p>
  <p class="meta">{e(st["location"])} <span>·</span> {nice_date(st["date"])} {vtxt}</p></div></li>"""
    note = ("Ranked by reader views over the last 30 days. Updated every day." if views
            else "Rankings start once reader counts come in. Until then, these are the latest stories.")
    body = f"""<section class="container" style="max-width:980px">
  <div class="page-head"><span class="pill live">Most read</span><h1>Best of Florida Man: Top 10</h1>
  <p>The stories Florida can't stop reading. {note}</p></div>
  <ol class="best-list">{rows}</ol>
</section>"""
    write("best-of/index.html", page(
        f"Best of Florida Man: Top 10 Most-Read Stories | {NAME}",
        "The 10 most-read Florida Man stories right now, ranked by readers.",
        SITE + "/best-of/", body))


def lemon_hero_img():
    L = LEMONADE
    if os.path.exists(os.path.join(ROOT, L["hero_image"].lstrip("/"))):
        return f'<img src="{L["hero_image"]}" alt="Illustration: lemon cars drag racing">'
    return '<span class="lemon-emoji">🍋🏁</span>'


def build_giving():
    L = LEMONADE
    # hub page
    hub = f"""<section class="container" style="max-width:1000px">
  <div class="page-head"><span class="tag">Community</span><h1>Florida Man Times Gives Back</h1>
  <p>Florida gives us a lot of headlines. This is where we give back: weird, fun, community events that raise real money for local Florida charities.</p></div>
  <a class="give-card" href="/gives-back/{L["slug"]}/">
    <div class="give-img">{lemon_hero_img()}</div>
    <div class="give-body"><span class="lp-kicker">Event #1 · {e(L["date"] if L["date"] != "TBA" else "Date announcing soon")}</span>
    <h2>LEMONADE: The Lemon Drag Race</h2><p>{e(L["tagline"])}</p><span class="lp-btn">Learn more & sponsor a car →</span></div>
  </a>
</section>"""
    write("gives-back/index.html", page(f"Florida Man Times Gives Back | {NAME}",
          "Charity events from Florida Man Times, starting with LEMONADE, the lemon car drag race for local charities.",
          SITE + "/gives-back/", hub))
    # event page
    how = "".join(f'<li><span class="how-n">{i}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (t, d) in enumerate(L["how"], 1))
    tiers = "".join(f"""<div class="tier{' featured' if t.get('featured') else ''}">{'<span class="tier-flag">Most popular</span>' if t.get('featured') else ''}
  <h3>{e(t["name"])}</h3><p class="tier-price">{e(t["price"])}</p>
  <ul>{''.join(f'<li>{e(x)}</li>' for x in t["perks"])}</ul></div>""" for t in L["tiers"])
    awards = "".join(f'<div class="award"><span>{em}</span><h3>{e(n)}</h3><p>{e(d)}</p></div>' for em, n, d in L["awards"])
    extras = "".join(f'<li><strong>{e(n)}.</strong> {e(d)}</li>' for n, d in L["extras"])
    cta = (f'<a class="button big" href="mailto:{L["contact_email"]}?subject=LEMONADE%20sponsorship">Become a sponsor</a>'
           if L["contact_email"] else '<span class="button big disabled">Sponsor sign-ups open soon</span>')
    facts = f"""<div class="lemon-facts">
  <div><span>When</span><strong>{e(L["date"] if L["date"] != "TBA" else "Announcing soon")}</strong></div>
  <div><span>Where</span><strong>{e(L["venue"])}</strong></div>
  <div><span>Benefiting</span><strong>{e(L["beneficiary"])}</strong></div>
</div>"""
    body = f"""<section class="lemon-hero"><div class="container lemon-hero-in">
  <div class="lh-text"><span class="lp-kicker">{e(L["kicker"])}</span>
  <h1>LEMONADE</h1><p class="lh-sub">The Lemon Drag Race</p>
  <p class="lh-tag">{e(L["tagline"])}</p>{cta}</div>
  <div class="lh-img">{lemon_hero_img()}</div>
</div></section>
<section class="container" style="max-width:1000px">
  {facts}
  <div class="story-body lemon-intro">{''.join(f'<p>{e(p)}</p>' for p in L["intro"])}</div>
  <div class="section-head"><h2 class="label">How it works</h2></div>
  <ol class="how-list">{how}</ol>
  <div class="section-head"><h2 class="label">Sponsor a lemon</h2></div>
  <div class="tiers">{tiers}</div>
  <div class="section-head"><h2 class="label">Trophies nobody wants (but everybody wants)</h2></div>
  <div class="awards">{awards}</div>
  <div class="section-head"><h2 class="label">More at the track</h2></div>
  <ul class="extras">{extras}</ul>
  <div class="cta lemon-cta"><div><h2>Want your business behind the wheel?</h2>
  <p>Grab a sponsorship, build the ugliest car in Florida, and raise money for a good cause.</p></div>{cta}</div>
  <p class="section-sub" style="margin-top:20px">All cars must pass the host track's safety inspection, and all drivers must meet the track's requirements. Event details are subject to change.</p>
</section>"""
    write(f"gives-back/{L['slug']}/index.html", page(
        f"LEMONADE: The Lemon Car Drag Race for Charity | {NAME}",
        "Local businesses sponsor $500 lemon cars, decorate them and drag race them at a Florida dragstrip to raise money for local charities.",
        f"{SITE}/gives-back/{L['slug']}/", body, og_image=L["hero_image"] if os.path.exists(os.path.join(ROOT, L["hero_image"].lstrip("/"))) else None))


def feat_image(folder, slug):
    for ext in IMG_EXTS:
        if os.path.exists(os.path.join(ROOT, "images", folder, slug + ext)):
            return f"/images/{folder}/{slug}{ext}"
    return None


def feat_pic(folder, item, cls="feat-photo"):
    img = feat_image(folder, item["slug"])
    if img:
        return f'<div class="{cls}"><img src="{img}" alt="Illustration" loading="lazy" decoding="async"></div>'
    return f'<div class="{cls} placeholder" aria-hidden="true"><span>{item["emoji"]}</span></div>'


def rental_card(r):
    return f"""<article class="rental">
  {feat_pic("rentals", r)}
  <div class="rental-body"><span class="tag">{e(r["city"])}</span><h3>{e(r["name"])}</h3>
  <p class="ev-blurb">{e(r["blurb"])}</p>
  <a class="ev-link" href="{r["source_url"]}" rel="noopener" target="_blank">See it on {e(r["source_name"])} ↗</a></div>
</article>"""


def place_card(p):
    return f"""<article class="rental" id="{p["slug"]}">
  {feat_pic("places", p)}
  <div class="rental-body"><span class="tag">{e(p["kind"])} · {e(p["city"])}</span><h3>{e(p["name"])}</h3>
  <p class="ev-blurb">{e(p["blurb"])}</p>
  <p class="meta">{e(p["visit"])}</p>
  <a class="ev-link" href="{p["source_url"]}" rel="noopener" target="_blank">Read more on {e(p["source_name"])} ↗</a></div>
</article>"""


def build_places():
    body = f"""<section class="container">
  <div class="page-head"><span class="tag">Road trip, if you dare</span><h1>Spooky &amp; Odd Florida</h1>
  <p>Haunted dolls, gravity hills, psychic towns, skunk apes and a castle in a swamp. The creepiest and strangest real places you can visit in Florida. Pictures are illustrations; follow each link for real details, and check hours before you drive.</p></div>
  <div class="rental-grid">{"".join(place_card(p) for p in PLACES)}</div>
</section>"""
    write("odd-places/index.html", page(
        f"Spooky & Odd Florida: Haunted, Creepy and Strange Places to Visit | {NAME}",
        "Robert the Doll, Coral Castle, Spook Hill, Cassadaga and more: the spookiest, strangest real places to visit in Florida.",
        SITE + "/odd-places/", body))


def build_rentals():
    body = f"""<section class="container">
  <div class="page-head"><span class="tag">Stay weird</span><h1>Crazy Florida Rentals</h1>
  <p>UFOs, military helicopters, school buses and bowling-ball art houses. The strangest places you can actually book a night in Florida. Pictures are illustrations; follow each link for the real listing details and photos.</p></div>
  <div class="rental-grid">{"".join(rental_card(r) for r in RENTALS)}</div>
</section>"""
    write("rentals/index.html", page(
        f"Crazy Florida Rentals: The Weirdest Airbnbs in Florida | {NAME}",
        "Sleep in a UFO, a Chinook helicopter, a school bus or an art house: the weirdest vacation rentals in Florida.",
        SITE + "/rentals/", body))


def build_artist():
    cur, past = ARTISTS[0], ARTISTS[1:]
    links = " · ".join(f'<a href="{u}" rel="noopener" target="_blank">{e(n)} ↗</a>' for n, u in cur["links"])
    paras = "".join(f"<p>{e(p)}</p>" for p in cur["body"])
    archive = ""
    if past:
        archive = '<div class="section-head"><h2 class="label">Past artists</h2></div><div class="rental-grid">' + "".join(
            f"""<article class="rental">{feat_pic("artists", a)}<div class="rental-body"><span class="tag">{e(a["city"])}</span>
<h3>{e(a["name"])}</h3><p class="ev-blurb">{e(a["headline"])}</p></div></article>""" for a in past) + "</div>"
    body = f"""<article class="story">
  <header class="story-head"><span class="pill live">Artist of the Week</span>
  <h1>{e(cur["headline"])}</h1>
  <p class="story-dek">{e(cur["name"])}, aka “{e(cur["nickname"])}” · {e(cur["city"])} · {e(cur["medium"])}</p></header>
  <figure class="story-media">{feat_pic("artists", cur, "media wide")}<p class="caption">Illustration inspired by the artists' work. See the links below for real photos.</p></figure>
  <div class="story-body">{paras}</div>
  <div class="source-box"><span class="label">Visit</span><p>{e(cur["visit"])}</p><p>Read more: {links}</p></div>
  <div class="source-box" style="margin-top:14px"><span class="label">Know a wild Florida artist?</span>
  <p>Artist nominations open soon. We're looking for the strangest, most wonderful creative minds in the state.</p></div>
</article>
<section class="container">{archive}</section>"""
    write("artist-of-the-week/index.html", page(
        f"Florida Man Artist of the Week: {cur['name']} | {NAME}",
        f"This week: {cur['name']} of {cur['city']}. {cur['headline']}",
        SITE + "/artist-of-the-week/", body))


def features_row():
    a = ARTISTS[0]
    rentals = "".join(f"""<li><a href="/rentals/"><span class="eat-mini">{r["emoji"]}</span><div><strong>{e(r["name"])}</strong>
<p class="meta">{e(r["city"])}</p></div></a></li>""" for r in RENTALS[:4])
    return f"""<section class="container feat-row">
  <a class="artist-feature" href="/artist-of-the-week/">
    {feat_pic("artists", a)}
    <div class="af-body"><span class="pill live">Artist of the Week</span><h2>{e(a["headline"])}</h2>
    <p class="meta">{e(a["name"])} · {e(a["city"])}</p></div>
  </a>
  <aside class="rail-box"><div class="rail-head"><span class="tag">Crazy Rentals</span><h2>Sleep in a UFO. Or a helicopter.</h2></div>
  <ul class="eat-list rental-mini">{rentals}</ul><a class="rail-more" href="/rentals/">See all crazy rentals →</a></aside>
</section>"""


def interview_pic(iv, cls="feat-photo"):
    img = feat_image("interviews", iv["slug"])
    if img:
        return f'<div class="{cls}"><img src="{img}" alt="{e(iv["guest"])}" loading="lazy" decoding="async"></div>'
    return f'<div class="{cls} placeholder" aria-hidden="true"><span>{iv["emoji"]}</span></div>'


def video_player(iv):
    v = iv.get("video", "")
    vert = " vertical" if iv.get("vertical") else ""
    yt = re.search(r"(?:youtu\.be/|v=|shorts/|embed/)([\w-]{11})", v)
    if yt:
        return (f'<div class="video{vert}"><iframe src="https://www.youtube-nocookie.com/embed/{yt.group(1)}?rel=0&modestbranding=1" '
                f'title="{e(iv["title"])}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
    ig = re.search(r"instagram\.com/(?:[\w.]+/)?(reel|reels|p|tv)/([\w-]+)", v)
    if ig:
        kind = "reel" if ig.group(1) in ("reel", "reels") else ig.group(1)
        return (f'<div class="video vertical social"><iframe src="https://www.instagram.com/{kind}/{ig.group(2)}/embed/captioned/" '
                f'title="{e(iv["title"])}" loading="lazy" scrolling="no" allowtransparency="true" allowfullscreen></iframe></div>')
    tt = re.search(r"tiktok\.com/.*?/video/(\d+)", v)
    if tt:
        return (f'<div class="video vertical social"><iframe src="https://www.tiktok.com/embed/v2/{tt.group(1)}" '
                f'title="{e(iv["title"])}" loading="lazy" allow="encrypted-media; fullscreen" allowfullscreen></iframe></div>')
    if "facebook.com" in v or "fb.watch" in v:
        from urllib.parse import quote
        return (f'<div class="video{vert}"><iframe src="https://www.facebook.com/plugins/video.php?href={quote(v, safe="")}&show_text=false" '
                f'title="{e(iv["title"])}" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>')
    if v:
        poster = feat_image("interviews", iv["slug"]) or ""
        return f'<div class="video{vert}"><video controls playsinline preload="metadata" poster="{poster}" src="{e(v)}"></video></div>'
    return interview_pic(iv, "media wide")


def credit_line(iv):
    if not iv.get("credit"):
        return ""
    who = e(iv["credit"])
    if iv.get("credit_url"):
        who = f'<a href="{iv["credit_url"]}" rel="noopener" target="_blank">{who} ↗</a>'
    return f'<p class="caption">Video by {who}. Originally posted on Instagram; embedded with credit.</p>'


def effd_logo(size=""):
    return f'<span class="effd-logo {size}">Eff\'d Up <em>With…</em></span>'


def build_interviews():
    if INTERVIEWS:
        cards = "".join(f"""<a class="rental ep" href="/effd-up/{iv["slug"]}/"><div class="ep-thumb">{interview_pic(iv)}<span class="play" aria-hidden="true">▶</span></div>
<div class="rental-body"><span class="tag">{e(iv["city"])}</span><h3>{e(iv["title"])}</h3><p class="ev-blurb">{e(iv["dek"])}</p>
<span class="meta">{e(iv["guest"])} · {nice_date(iv["date"])}</span></div></a>""" for iv in INTERVIEWS)
        main = f'<div class="section-head"><h2 class="label">Latest episodes</h2></div><div class="rental-grid">{cards}</div>'
    else:
        main = '<div class="effd-soon"><span class="pill live">Episode 1</span><h2>Episode 1 drops soon.</h2><p>We\'re lining up our first guest and getting the cameras rolling.</p></div>'
    wanted = "".join(f'<div class="award"><span>{em}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for em, t, d in WANTED)
    qs = "".join(f"<li>{e(q)}</li>" for q in STANDARD_QS)
    body = f"""<section class="effd-hero"><div class="container">
  {effd_logo("big")}
  <p class="effd-tag">On-camera interviews with Florida's most gloriously unhinged people. In their own words. Unfiltered (mostly).</p>
</div></section>
<section class="container" style="margin-top:36px">{main}
  <div class="section-head" style="margin-top:44px"><h2 class="label">Who we want to talk to</h2></div>
  <div class="awards">{wanted}</div>
  <div class="two-up" style="margin-top:44px">
    <div class="rail-box"><div class="rail-head"><span class="tag">The Five</span><h2>Every guest gets these</h2></div><ol class="effd-qs">{qs}</ol></div>
    <div class="rail-box"><div class="rail-head"><span class="tag">House rules</span><h2>How we do it</h2></div>
    <ul class="effd-rules"><li>Real people, on camera. Nothing staged or made up.</li><li>Adults only, sober when we talk, and they signed off on it.</li>
    <li>You're in on the joke, not the butt of it.</li><li>Think you belong here? Guest sign-ups open soon.</li></ul></div>
  </div>
</section>"""
    write("effd-up/index.html", page(f"Eff'd Up With…: Interviews With Florida's Wildest People | {NAME}",
        "Video interviews with Florida's python hunters, skunk ape believers, gator wranglers and actual Florida Men.",
        SITE + "/effd-up/", body))
    for iv in INTERVIEWS:
        qa = "".join(f'<div class="qa"><p class="q">{e(q)}</p><p class="a">“{e(a)}”</p></div>' for q, a in iv.get("quotes", []))
        intro = "".join(f"<p>{e(p)}</p>" for p in iv["intro"])
        b = f"""<article class="story"><header class="story-head">{effd_logo()}<h1>{e(iv["title"])}</h1>
<p class="story-dek">{e(iv["dek"])}</p><p class="meta">{e(iv["guest"])} · {e(iv["city"])} · {nice_date(iv["date"])}</p></header>
<figure class="story-media">{video_player(iv)}{credit_line(iv)}</figure>
<div class="story-body">{intro}{('<h2>Best moments</h2>' + qa) if qa else ''}</div>{share_links(iv, SITE + "/effd-up/" + iv["slug"] + "/")}</article>"""
        write(f"effd-up/{iv['slug']}/index.html", page(f"Eff'd Up With {iv['guest']}: {iv['title']} | {NAME}", iv["dek"],
            SITE + f"/effd-up/{iv['slug']}/", b, og_type="article"))


def effd_promo():
    if INTERVIEWS:
        iv = INTERVIEWS[0]; line, link, cta = iv["title"], f"/effd-up/{iv['slug']}/", "Watch the episode →"
    else:
        line, link, cta = "Video interviews with Florida's python hunters, skunk ape believers and gator wranglers. Episode 1 coming soon.", "/effd-up/", "See who we're looking for →"
    return f"""<section class="container"><a class="effd-promo" href="{link}">{effd_logo()}<p>{e(line)}</p><span class="effd-cta">{cta}</span></a></section>"""


def cam_card(c):
    return f"""<article class="rental cam">
  <div class="ep-thumb">{feat_pic("cams", c)}<span class="live-dot">● LIVE</span></div>
  <div class="rental-body"><span class="tag">{e(c["tag"])} · {e(c["city"])}</span><h3>{c["emoji"]} {e(c["name"])}</h3>
  <p class="ev-blurb">{e(c["blurb"])}</p>
  <p class="meta"><strong>Best time:</strong> {e(c["best"])}</p>
  <a class="cam-btn" href="{c["link"]}" rel="noopener" target="_blank">Watch live on {e(c["link_name"])} ↗</a></div>
</article>"""


def build_cams():
    body = f"""<section class="effd-hero"><div class="container">
  <span class="effd-logo big">Florida <em>Cams</em></span>
  <p class="effd-tag">Live, right now, somewhere in Florida: manatees piling into a power plant, a party on Duval Street, a rocket about to leave the planet. Pull up a chair.</p>
</div></section>
<section class="container" style="margin-top:32px">
  <div class="rental-grid">{"".join(cam_card(c) for c in CAMS)}</div>
  <p class="section-sub" style="margin-top:22px">Cams are run by the organizations linked on each card, so they may go offline for weather, maintenance or the off-season. Pictures here are illustrations; tap through for the real live view.</p>
</section>"""
    write("cams/index.html", page(f"Florida Cams: Live Florida Webcams | {NAME}",
        "Live Florida webcams: manatee cams at Blue Spring and a power plant, Sloppy Joe's and Mallory Square in Key West, Space Coast rocket launches and more.",
        SITE + "/cams/", body))


REGIONS = ["Tampa Bay", "Sarasota & Manatee", "Southwest Florida", "Orlando & Central", "South Florida", "North Florida & Panhandle"]
_REG = {
    "Tampa Bay": "Hillsborough Pinellas Pasco Hernando Citrus Polk",
    "Sarasota & Manatee": "Sarasota Manatee Charlotte",
    "Southwest Florida": "Lee Collier Hendry Glades DeSoto Hardee Highlands",
    "Orlando & Central": "Orange Osceola Seminole Lake Volusia Brevard Sumter Marion Flagler",
    "South Florida": "Miami-Dade Broward Palm_Beach Monroe Martin St._Lucie Indian_River Okeechobee",
}
REGION_OF = {c.replace("_", " "): r for r, cs in _REG.items() for c in cs.split()}
ALL_COUNTIES = sorted(["Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Calhoun", "Charlotte", "Citrus", "Clay",
    "Collier", "Columbia", "DeSoto", "Dixie", "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", "Glades", "Gulf",
    "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough", "Holmes", "Indian River", "Jackson", "Jefferson",
    "Lafayette", "Lake", "Lee", "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", "Martin", "Miami-Dade", "Monroe", "Nassau",
    "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach", "Pasco", "Pinellas", "Polk", "Putnam", "St. Johns", "St. Lucie",
    "Santa Rosa", "Sarasota", "Seminole", "Sumter", "Suwannee", "Taylor", "Union", "Volusia", "Wakulla", "Walton", "Washington"])


def load_closures():
    try:
        return json.load(open(os.path.join(ROOT, "closures.json")))
    except Exception:
        return {"updated": "", "weeks": [], "closures": []}


def reason_emoji(r):
    r = r.lower()
    out = ""
    if "roach" in r: out += "🪳"
    if "rodent" in r: out += "🐀"
    if "fly" in r: out += "🪰"
    if "sewage" in r: out += "🚽"
    if "water" in r: out += "🚱"
    return out or "⚠️"


def closure_card(c):
    d = dt.date.fromisoformat(c["date"])
    status = (f'<span class="rr-ok">✓ Passed follow-up, cleared to reopen</span>' if c.get("reopened_at")
              else '<span class="rr-pending">Reopen time not listed yet</span>')
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f'{c["name"]} {c["address"]} {c["city"]} FL')
    cty = c.get("county") or county_for(c["city"])
    return f"""<article class="rr-card closed" data-county="{e(cty)}" data-region="{e(REGION_OF.get(cty, "North Florida & Panhandle"))}">
  <div class="rr-emoji" aria-hidden="true">{reason_emoji(c["reason"])}</div>
  <div class="rr-body"><h3>{e(c["name"].title() if c["name"].isupper() else c["name"])}</h3>
  <p class="meta"><a href="{maps}" rel="noopener" target="_blank">{e(c["address"])}, {e(c["city"])}</a> · {e(cty)} County</p>
  <p class="rr-why"><strong>{e(c["reason"])}</strong> · Closed {d.strftime("%a, %b %-d")}{(" at " + e(c["closed_at"])) if c.get("closed_at") else ""}</p>
  {status}</div>
</article>"""


def load_writeups():
    try:
        return json.load(open(os.path.join(ROOT, "roach-report", "writeups.json")))
    except Exception:
        return {"items": [], "days": 14, "min_hp": 3}


RR_JS = r"""
(function(){
var WU=[],CLN=[],shownR='all',shownC='all',kind='both',page=0,PER=30;
var bs=document.querySelectorAll('.rr-chip'),ks=document.querySelectorAll('.rr-kind'),sel=document.getElementById('rr-county'),
cs=document.querySelectorAll('.rr-card'),out=document.getElementById('rr-showing'),wl=document.getElementById('wu-list'),
more=document.getElementById('wu-more'),secC=document.getElementById('sec-closed'),secW=document.getElementById('sec-written'),
emC=document.getElementById('empty-closed'),emW=document.getElementById('empty-written');
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function match(county,region){return (shownC!=='all')?county===shownC:(shownR==='all'||region===shownR);}
function fmt(d){var x=new Date(d+'T12:00:00');return x.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});}
function cls(r){return r.indexOf('Admin')>=0?'rr-bad':(r.indexOf('Warning')>=0?'rr-warn':(r.indexOf('Fixed')>=0?'rr-ok':'rr-pending'));}
function wcard(w){var q=encodeURIComponent(w.name+' '+w.address+' '+w.city+' FL');
return '<article class="rr-card wu"><div class="rr-emoji" aria-hidden="true">⚠️</div><div class="rr-body"><h3>'+esc(w.name)+'</h3>'+
'<p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(w.address)+', '+esc(w.city)+'</a> · '+esc(w.county)+' County</p>'+
'<p class="rr-why"><strong>'+w.hp+' high-priority violation'+(w.hp===1?'':'s')+'</strong> ('+w.total+' total) · Inspected '+fmt(w.date)+'</p>'+
'<span class="'+cls(w.result)+'">'+esc(w.result)+'</span></div></article>';}
function render(push){
 var nc=0;cs.forEach(function(x){var s=match(x.dataset.county,x.dataset.region);x.style.display=s?'':'none';if(s)nc++;});
 var f=WU.filter(function(w){return match(w.county,w.region);});
 wl.innerHTML=f.slice(0,(page+1)*PER).map(wcard).join('');
 more.hidden=f.length<=(page+1)*PER; more.textContent='Show more ('+(f.length-(page+1)*PER)+' left)';
 secC.hidden=kind==='written'; secW.hidden=kind==='closed';
 emC.hidden=nc>0; emW.hidden=f.length>0;
 var where=shownC!=='all'?shownC+' County':(shownR==='all'?'Florida':shownR);
 out.textContent=where+': '+nc+' shut down · '+f.length+' written up';
 bs.forEach(function(b){b.classList.toggle('on',shownC==='all'&&b.dataset.r===shownR);});
 ks.forEach(function(b){b.classList.toggle('on',b.dataset.k===kind);});
 var el=document.getElementById('ei-list'),et=document.getElementById('ei-title');
 if(el){var cf=CLN.filter(function(c){return match(c.county,c.region);}),hh2=shownC!=='all'?shownC+' County':(shownR!=='all'?shownR:'Florida');
  et.textContent='✨ Where to eat instead in '+hh2;
  el.innerHTML=cf.slice(0,8).map(function(c){var q=encodeURIComponent(c.name+' '+c.address+' '+c.city+' FL');
   return '<article class="cp-card"><span class="cp-badge" aria-hidden="true">✨</span><div><h3>'+esc(c.name)+'</h3><p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(c.address)+', '+esc(c.city)+'</a> · Perfect inspection</p></div></article>';}).join('')+
   (cf.length>8?'<a class="cp-countylink" style="display:block;margin-top:8px;font-weight:800;color:var(--accent-ink)" href="/clean-plate-club/'+(shownC!=='all'?'#'+encodeURIComponent(shownC):(shownR!=='all'?'#'+encodeURIComponent(shownR):''))+'">See all '+cf.length+' →</a>':'');}
 var cl=document.getElementById('rr-countylink'),cx=document.getElementById('rr-cleanlink');
 if(cl)cl.innerHTML=shownC!=='all'?'<a href="/restaurant-inspections/'+shownC.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'-county/">Open the full '+esc(shownC)+' County page →</a>':'';
 if(cx){var hh=shownC!=='all'?shownC:(shownR!=='all'?shownR:'');cx.href='/clean-plate-club/'+(hh?'#'+encodeURIComponent(hh):'');cx.textContent='✨ Want somewhere clean instead? See the cleanest restaurants in '+(hh?(shownC!=='all'?hh+' County':hh):'Florida')+' →';}
 if(push){var h=shownC!=='all'?shownC:(shownR!=='all'?shownR:'');history.replaceState(null,'',h?'#'+encodeURIComponent(h):location.pathname);}
}
bs.forEach(function(b){b.addEventListener('click',function(){shownR=b.dataset.r;shownC='all';sel.value='all';page=0;render(true);});});
sel.addEventListener('change',function(){shownC=sel.value;shownR='all';page=0;render(true);});
ks.forEach(function(b){b.addEventListener('click',function(){kind=b.dataset.k;render(false);});});
more.addEventListener('click',function(){page++;render(false);});
var h=decodeURIComponent(location.hash.slice(1));
if(h){if([].some.call(bs,function(b){return b.dataset.r===h;}))shownR=h;else if([].some.call(sel.options,function(o){return o.value===h;})){shownC=h;sel.value=h;}}
render(false);
fetch('/roach-report/clean.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
 CLN=(d.items||[]).map(function(w){w.region=(window.RR_REGION||{})[w.county]||'North Florida & Panhandle';return w;});render(false);});
fetch('/roach-report/writeups.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
 WU=(d.items||[]).map(function(w){w.region=(window.RR_REGION||{})[w.county]||'North Florida & Panhandle';return w;});render(false);});
})();
"""


def build_roach():
    data = load_closures()
    cl = data["closures"]
    wu = load_writeups()
    items = wu.get("items", [])
    n, nw = len(cl), len(items)
    roach = sum("roach" in c["reason"].lower() for c in cl)
    rodent = sum("rodent" in c["reason"].lower() for c in cl)
    from collections import Counter
    counts = Counter((c.get("county") or county_for(c["city"])) for c in cl)
    counts.update(w["county"] for w in items)
    rcounts = Counter()
    for k, v in counts.items():
        rcounts[REGION_OF.get(k, "North Florida & Panhandle")] += v
    chips = (f'<button class="rr-chip on" data-r="all">All Florida <b>{n + nw}</b></button>'
             + "".join(f'<button class="rr-chip" data-r="{e(r)}">{e(r)} <b>{rcounts.get(r, 0)}</b></button>' for r in REGIONS))
    opts = '<option value="all">All 67 counties</option>' + "".join(
        f'<option value="{e(k)}">{e(k)} ({counts.get(k, 0)})</option>' for k in ALL_COUNTIES)
    cards = "".join(closure_card(c) for c in cl)
    weeks = len(data.get("weeks", [])) or 8
    region_js = json.dumps(REGION_OF)
    write("roach-report/rr.js", RR_JS)
    body = f"""<section class="effd-hero"><div class="container">
  <span class="effd-logo big">The Roach <em>Report</em></span>
  <p class="effd-tag">Every Florida restaurant the state shut down, plus the ones inspectors wrote up for serious violations, straight from official inspection records. Pick your county. Updated daily.</p>
  <div class="rr-stats"><div><b>{n}</b><span>🚫 shut down</span></div><div><b>{nw}</b><span>⚠️ written up</span></div><div><b>{roach}</b><span>🪳 roach closures</span></div><div><b>{rodent}</b><span>🐀 rodent closures</span></div></div>
</div></section>
<section class="container" style="margin-top:28px;max-width:900px">
  <div class="rr-filter" role="toolbar" aria-label="Filter by region">{chips}</div>
  <label class="rr-select"><span>County</span><select id="rr-county">{opts}</select></label>
  <div class="rr-kinds"><button class="rr-kind on" data-k="both">Both</button><button class="rr-kind" data-k="closed">🚫 Shut down</button><button class="rr-kind" data-k="written">⚠️ Written up</button></div>
  <p class="rr-showing" id="rr-showing"></p>
  <p class="cp-countylink" id="rr-countylink"></p>
  <a class="cp-cross" href="/clean-plate-club/" id="rr-cleanlink">✨ Want somewhere clean instead? See the Clean Plate Club →</a>

  <div id="sec-closed">
    <div class="section-head"><h2 class="label">🚫 Shut down by the state · last {weeks} weeks</h2></div>
    <p class="rr-empty" id="empty-closed" hidden>🎉 No emergency closures here in the last {weeks} weeks.</p>
    <div class="rr-list">{cards}</div>
  </div>

  <div id="sec-written" style="margin-top:34px">
    <div class="section-head"><h2 class="label">⚠️ Written up: {wu.get("min_hp", 3)}+ high-priority violations · last {wu.get("days", 14)} days</h2></div>
    <p class="section-sub">These restaurants stayed open. An inspector found serious problems and either had them fixed on the spot, issued a warning, or recommended a formal complaint.</p>
    <p class="rr-empty" id="empty-written" hidden>🎉 No serious write-ups here in the last {wu.get("days", 14)} days.</p>
    <div class="rr-list" id="wu-list"><p class="section-sub">Loading inspections…</p></div>
    <button class="rr-kind" id="wu-more" hidden style="margin-top:14px">Show more</button>
  </div>

  <div class="eat-instead" style="margin-top:38px"><span class="ei-kicker">Okay, now you're hungry and nervous</span>
  <h2 id="ei-title">✨ Where to eat instead</h2>
  <p>Restaurants that aced their most recent state inspection with zero violations this month.</p></div>
  <div class="sponsor-slot"><span class="sponsor-tag">Sponsored · Featured clean restaurant</span>
  <h3>Your restaurant here</h3><p>Passed your inspection with flying colors? Get the featured spot on this list.</p>
  <a class="cam-btn" href="/advertise/#clean">Feature my restaurant →</a></div>
  <div class="cp-list" id="ei-list" style="margin-top:14px"></div>

  <div class="source-box" style="margin-top:28px"><span class="label">How this works</span>
  <p><strong>Shut down</strong> means a state inspector found an immediate health risk, most often roaches or rodents, and ordered the restaurant closed until it passed a follow-up. Most reopen within a day.</p>
  <p><strong>High-priority violations</strong> are the most serious category on a Florida inspection (things like food held at unsafe temperatures, no handwashing, or pests). <strong>Fixed on the spot</strong> means the problem was corrected during the visit. A warning or recommended complaint is not a final judgment.</p>
  <p>Source: <a href="https://www2.myfloridalicense.com/hotels-restaurants/public-records/" rel="noopener" target="_blank">Florida DBPR inspection and emergency closure records ↗</a>{(" · Last updated " + nice_date(data["updated"])) if data.get("updated") else ""}. Conditions may have changed since. Owners: to check or correct a record, contact DBPR.</p></div>
</section>
<script>window.RR_REGION={region_js};window.RR_V="{data.get("updated", "")}";</script>
<script src="/roach-report/rr.js?v={data.get("updated", "")}" defer></script>"""
    write("roach-report/index.html", page(f"The Roach Report: Florida Restaurant Closures & Health Violations by County | {NAME}",
        "Florida restaurants state inspectors shut down or wrote up for serious violations, by county, from official DBPR records. Updated daily.",
        SITE + "/roach-report/", body))


def county_slug(c):
    return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-") + "-county"


def load_clean():
    try:
        return json.load(open(os.path.join(ROOT, "roach-report", "clean.json")))
    except Exception:
        return {"items": [], "days": 30}


def wu_card_html(w):
    cls = "rr-bad" if "Admin" in w["result"] else ("rr-warn" if "Warning" in w["result"] else ("rr-ok" if "Fixed" in w["result"] else "rr-pending"))
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f'{w["name"]} {w["address"]} {w["city"]} FL')
    d = dt.date.fromisoformat(w["date"]).strftime("%a, %b %-d")
    return f"""<article class="rr-card wu"><div class="rr-emoji" aria-hidden="true">⚠️</div><div class="rr-body"><h3>{e(w["name"])}</h3>
<p class="meta"><a href="{maps}" rel="noopener" target="_blank">{e(w["address"])}, {e(w["city"])}</a></p>
<p class="rr-why"><strong>{w["hp"]} high-priority violation{"s" if w["hp"] != 1 else ""}</strong> ({w["total"]} total) · Inspected {d}</p>
<span class="{cls}">{e(w["result"])}</span></div></article>"""


def clean_card_html(c):
    maps = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f'{c["name"]} {c["address"]} {c["city"]} FL')
    d = dt.date.fromisoformat(c["date"]).strftime("%b %-d")
    return f"""<article class="cp-card"><span class="cp-badge" aria-hidden="true">✨</span><div><h3>{e(c["name"])}</h3>
<p class="meta"><a href="{maps}" rel="noopener" target="_blank">{e(c["address"])}, {e(c["city"])}</a> · Perfect inspection {d}</p></div></article>"""


def clean_sponsor(where):
    return f"""<div class="sponsor-slot"><span class="sponsor-tag">Sponsored · Featured clean restaurant</span>
<h3>Your restaurant here</h3><p>Passed your inspection with flying colors? Get the featured spot for {e(where)} on the Clean Plate Club.</p>
<a class="cam-btn" href="/advertise/#clean">Feature my restaurant →</a></div>"""


CP_JS = r"""
(function(){
var CL=[],R='all',C='all',page=0,PER=40,bs=document.querySelectorAll('.rr-chip'),sel=document.getElementById('cp-county'),
list=document.getElementById('cp-list'),more=document.getElementById('cp-more'),out=document.getElementById('cp-showing'),cty=document.getElementById('cp-countylink');
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function slug(c){return c.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'-county';}
function card(c){var q=encodeURIComponent(c.name+' '+c.address+' '+c.city+' FL'),d=new Date(c.date+'T12:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'});
return '<article class="cp-card"><span class="cp-badge" aria-hidden="true">✨</span><div><h3>'+esc(c.name)+'</h3><p class="meta"><a href="https://www.google.com/maps/search/?api=1&query='+q+'" rel="noopener" target="_blank">'+esc(c.address)+', '+esc(c.city)+'</a> · '+esc(c.county)+' County · Perfect inspection '+d+'</p></div></article>';}
function render(push){var f=CL.filter(function(c){return C!=='all'?c.county===C:(R==='all'||c.region===R);});
list.innerHTML=f.slice(0,(page+1)*PER).map(card).join('')||'<p class="rr-empty">No perfect inspections listed here in the last 30 days yet. Check back soon.</p>';
more.hidden=f.length<=(page+1)*PER;more.textContent='Show more ('+(f.length-(page+1)*PER)+' left)';
var where=C!=='all'?C+' County':(R==='all'?'Florida':R);out.textContent=f.length+' restaurants with a perfect inspection in '+where;
cty.innerHTML=C!=='all'?'<a href="/restaurant-inspections/'+slug(C)+'/">See everything for '+esc(C)+' County: closures, write-ups and clean spots →</a>':'';
bs.forEach(function(b){b.classList.toggle('on',C==='all'&&b.dataset.r===R);});
if(push){var h=C!=='all'?C:(R!=='all'?R:'');history.replaceState(null,'',h?'#'+encodeURIComponent(h):location.pathname);}}
bs.forEach(function(b){b.addEventListener('click',function(){R=b.dataset.r;C='all';sel.value='all';page=0;render(true);});});
sel.addEventListener('change',function(){C=sel.value;R='all';page=0;render(true);});
more.addEventListener('click',function(){page++;render(false);});
var h=decodeURIComponent(location.hash.slice(1));
if(h){if([].some.call(bs,function(b){return b.dataset.r===h;}))R=h;else if([].some.call(sel.options,function(o){return o.value===h;})){C=h;sel.value=h;}}
fetch('/roach-report/clean.json?v='+(window.RR_V||'')).then(function(r){return r.json();}).then(function(d){
CL=(d.items||[]).map(function(c){c.region=(window.RR_REGION||{})[c.county]||'North Florida & Panhandle';return c;});render(false);});
})();
"""


def build_clean_plate():
    cd = load_clean()
    items = cd.get("items", [])
    from collections import Counter
    counts = Counter(c["county"] for c in items)
    rc = Counter()
    for k, v in counts.items():
        rc[REGION_OF.get(k, "North Florida & Panhandle")] += v
    chips = (f'<button class="rr-chip on" data-r="all">All Florida <b>{len(items)}</b></button>'
             + "".join(f'<button class="rr-chip" data-r="{e(r)}">{e(r)} <b>{rc.get(r, 0)}</b></button>' for r in REGIONS))
    opts = '<option value="all">All 67 counties</option>' + "".join(
        f'<option value="{e(k)}">{e(k)} ({counts.get(k, 0)})</option>' for k in ALL_COUNTIES)
    write("clean-plate-club/cp.js", CP_JS)
    upd = load_closures().get("updated", "")
    body = f"""<section class="effd-hero cp-hero"><div class="container">
  <span class="effd-logo big">The Clean Plate <em>Club</em></span>
  <p class="effd-tag">The good news side of the Roach Report: Florida restaurants that just aced their state health inspection with zero violations. Pick your county and eat with confidence.</p>
</div></section>
<section class="container" style="margin-top:28px;max-width:900px">
  <div class="rr-filter" role="toolbar" aria-label="Filter by region">{chips}</div>
  <label class="rr-select"><span>County</span><select id="cp-county">{opts}</select></label>
  <p class="rr-showing" id="cp-showing"></p>
  <p class="cp-countylink" id="cp-countylink"></p>
  {clean_sponsor("your county")}
  <div class="cp-list" id="cp-list" style="margin-top:18px"><p class="section-sub">Loading inspections…</p></div>
  <button class="rr-kind" id="cp-more" hidden style="margin-top:14px">Show more</button>
  <a class="cp-cross" href="/roach-report/">🪳 Morbidly curious? See who got shut down in the Roach Report →</a>
  <div class="source-box" style="margin-top:24px"><span class="label">How this works</span>
  <p>A restaurant makes the Clean Plate Club when its most recent routine state inspection in the last {cd.get("days", 30)} days found zero violations. It's a snapshot of one visit, not a guarantee, and plenty of great restaurants with a minor write-up won't appear. Featured spots are paid and always labeled.</p>
  <p>Source: <a href="https://www2.myfloridalicense.com/hotels-restaurants/public-records/" rel="noopener" target="_blank">Florida DBPR inspection records ↗</a>. Updated daily.</p></div>
</section>
<script>window.RR_REGION={json.dumps(REGION_OF)};window.RR_V="{upd}";</script>
<script src="/clean-plate-club/cp.js?v={upd}" defer></script>"""
    write("clean-plate-club/index.html", page(f"Clean Plate Club: Florida Restaurants With Perfect Health Inspections | {NAME}",
        "Florida restaurants that just passed their state health inspection with zero violations, by county. Updated daily from official DBPR records.",
        SITE + "/clean-plate-club/", body))


def build_county_pages():
    cl = load_closures()
    wu = load_writeups()
    cd = load_clean()
    ups = upcoming_events()
    urls = []
    for county in ALL_COUNTIES:
        slug = county_slug(county)
        region = REGION_OF.get(county, "North Florida & Panhandle")
        closed = [c for c in cl["closures"] if (c.get("county") or county_for(c["city"])) == county]
        written = [w for w in wu.get("items", []) if w["county"] == county]
        clean = [c for c in cd.get("items", []) if c["county"] == county]
        loc_stories = [st for st in FL_STORIES if county_of_place(st.get("location", "")) == county]
        loc_arrests = [a for a in ARRESTS if (a.get("county") or county_of_place(a.get("place", ""))) == county]
        loc_events = [ev for ev in ups if county_of_place(ev.get("city", "")) == county]
        loc_eats = [x for x in EATS if county_of_place(x.get("city", "") or x.get("address", "")) == county]
        loc_fun = ([("rental", r) for r in RENTALS if county_of_place(r["city"]) == county]
                   + [("cam", c) for c in CAMS if county_of_place(c["city"]) == county]
                   + [("place", p) for p in PLACES if county_of_place(p["city"]) == county])
        cities = sorted({x["city"] for x in closed + written + clean if x.get("city")})[:6]
        sections, nav = [], []

        def sec(anchor, label, html, extra=""):
            nav.append(f'<a href="#{anchor}">{label}</a>')
            sections.append(f'<section id="{anchor}" class="cty-sec">{extra}<div class="section-head"><h2 class="label">{label}</h2></div>{html}</section>')

        if loc_stories:
            sec("news", "📰 Local Florida Man news", f'<div class="grid">{"".join(card(st) for st in loc_stories[:6])}</div>')
        else:
            sec("news", "📰 Florida Man news", f'<p class="section-sub">No {e(county)} County stories yet (behave yourselves). Here\'s the latest from around the state:</p><div class="grid">{"".join(card(st) for st in FL_STORIES[:3])}</div>')
        if loc_arrests:
            sec("arrests", "🚔 Weirdest local arrests", f'<div class="arrest-list">{"".join(arrest_item(a) for a in loc_arrests[:6])}</div>')
        closed_html = "".join(closure_card(c) for c in closed) or f'<p class="rr-empty">🎉 No emergency closures in {e(county)} County in the last 8 weeks.</p>'
        written_html = "".join(wu_card_html(w) for w in written) or f'<p class="rr-empty">🎉 No serious write-ups in {e(county)} County in the last 2 weeks.</p>'
        sec("roach", "🪳 Local Roach Report", f"""<h3 class="cty-h3">🚫 Shut down by the state · last 8 weeks</h3><div class="rr-list">{closed_html}</div>
<h3 class="cty-h3">⚠️ Written up: 3+ high-priority violations · last 2 weeks</h3><div class="rr-list">{written_html}</div>""")
        clean_html = "".join(clean_card_html(c) for c in clean[:40]) or '<p class="section-sub">No perfect inspections listed in the last 30 days yet.</p>'
        nav.append('<a href="#eat">✨ Where to eat</a>')
        sections.append(f"""<section id="eat" class="cty-sec"><div class="eat-instead"><span class="ei-kicker">Okay, now you're hungry and nervous</span>
  <h2>✨ Where to eat instead in {e(county)} County</h2><p>Restaurants that aced their most recent state inspection with zero violations this month.</p></div>
  {clean_sponsor(county + " County")}<div class="cp-list" style="margin-top:16px">{clean_html}</div></section>""")
        loc_artists = [a for a in ARTISTS if county_of_place(a.get("city", "")) == county]
        if loc_artists:
            sec("artist", "🎨 Local artist", "".join(
                f"""<a class="artist-feature" href="/artist-of-the-week/">{feat_pic("artists", a)}<div class="af-body"><span class="pill live">Artist of the Week</span><h2>{e(a["headline"])}</h2><p class="meta">{e(a["name"])} · {e(a["city"])}</p></div></a>""" for a in loc_artists[:2]))
        if loc_eats:
            sec("weird-eats", "🐊 Weird local eats", f'<div class="eats-grid">{"".join(eat_card(x) for x in loc_eats)}</div>')
        if loc_events:
            sec("events", "🎪 Things to do", f'<div class="ev-grid">{"".join(event_card(ev) for ev in loc_events[:6])}</div>')
        if loc_fun:
            html = "".join(rental_card(x) if k == "rental" else cam_card(x) if k == "cam" else place_card(x) for k, x in loc_fun)
            sec("odd", "🛸 Strange stays, cams & odd spots", f'<div class="rental-grid">{html}</div>')
        sibs = [c for c in ALL_COUNTIES if REGION_OF.get(c, "North Florida & Panhandle") == region and c != county]
        sib_html = "".join(f'<a class="rr-chip" href="/restaurant-inspections/{county_slug(c)}/">{e(c)}</a>' for c in sibs)
        def nm(x):
            n = x.get("name", "")
            return n.title() if n.isupper() else n
        q_closed = (f"In the last 8 weeks the state ordered {len(closed)} {county} County restaurant{'s' if len(closed) != 1 else ''} to close temporarily: "
                    + "; ".join(f"{nm(c)} in {c.get('city','').title()}" for c in closed[:6]) + ". Most reopen within a day once they pass a follow-up inspection."
                    ) if closed else f"No {county} County restaurants were ordered closed by the state in the last 8 weeks."
        q_clean = (f"{len(clean)} {county} County restaurants passed their latest routine state inspection with zero violations in the last 30 days, including "
                   + ", ".join(f"{nm(c)} ({c.get('city','').title()})" for c in clean[:6]) + ".") if clean else f"We haven't seen a perfect-score inspection in {county} County in the last 30 days yet."
        faqs = [
            (f"Which {county} County restaurants were shut down recently?", q_closed),
            (f"Where can I eat in {county} County with a clean inspection?", q_clean),
            (f"How do I check a {county} County restaurant's health inspection?",
             f"Florida's Division of Hotels and Restaurants (DBPR) inspects restaurants and posts every result online. This page pulls the state's records for {county} County every day, or you can search any restaurant on the DBPR website."),
        ]
        faq_html = "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)
        sections.append(f'<section id="faq" class="cty-sec"><div class="section-head"><h2 class="label">❓ {e(county)} County restaurant inspection questions</h2></div>{faq_html}</section>')
        ld = [{"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Florida counties", "item": SITE + "/restaurant-inspections/"},
                  {"@type": "ListItem", "position": 3, "name": f"{county} County", "item": SITE + f"/restaurant-inspections/{slug}/"}]}]
        intro = (f"{len(closed)} restaurant{'s' if len(closed) != 1 else ''} shut down in the last 8 weeks, "
                 f"{len(written)} written up for serious violations, and {len(clean)} with a perfect inspection this month.")
        body = f"""<section class="effd-hero"><div class="container">
  <span class="tag" style="background:rgba(255,255,255,.1);color:#d4d4d4">📍 Your local Florida Man Times</span>
  <h1 class="effd-logo big" style="margin-top:10px">{e(county)} <em>County</em></h1>
  <p class="effd-tag">{e(county)} County restaurant inspections, closures and clean-plate winners, plus weird local news, arrests and things to do in {e(county)} County{(", including " + ", ".join(cities)) if cities else ""}. Updated daily.</p>
  <div class="rr-stats"><div><b>{len(loc_stories)}</b><span>📰 local stories</span></div><div><b>{len(closed)}</b><span>🚫 shut down</span></div><div><b>{len(written)}</b><span>⚠️ written up</span></div><div><b>{len(clean)}</b><span>✨ perfect scores</span></div></div>
</div></section>
<nav class="cty-nav" aria-label="On this page"><div class="hub-inner">{"".join(nav)}</div></nav>
<div class="container" style="max-width:1000px">
{"".join(sections)}
<section class="cty-sec"><div class="section-head"><h2 class="label">📍 More of {e(region)}</h2></div><div class="county-grid">{sib_html}</div>
<p style="margin-top:14px"><a class="cp-countylink" href="/restaurant-inspections/" style="font-weight:800;color:var(--accent-ink)">All 67 counties →</a></p></section>
<div class="source-box" style="margin-top:24px"><span class="label">About these records</span>
<p>Inspection data comes from <a href="https://www2.myfloridalicense.com/hotels-restaurants/public-records/" rel="noopener" target="_blank">Florida DBPR ↗</a>. Shut down means an emergency closure until a follow-up passed; most reopen within a day. A write-up or warning is not a final judgment. Perfect scores reflect one routine visit. Everyone arrested is presumed innocent.</p></div>
</div>"""
        write(f"restaurant-inspections/{slug}/index.html", page(
            f"{county} County Restaurant Inspections, Closures & Local News | {NAME}",
            f"{county} County, FL restaurant inspections updated daily: {intro} Plus local weird news, arrests and things to do.",
            SITE + f"/restaurant-inspections/{slug}/", body,
            "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)))
        urls.append(SITE + f"/restaurant-inspections/{slug}/")
    by_region = "".join(
        f'<div class="section-head" style="margin-top:22px"><h2 class="label">{e(r)}</h2></div><div class="county-grid">'
        + "".join(f'<a class="rr-chip" href="/restaurant-inspections/{county_slug(c)}/">{e(c)}</a>' for c in ALL_COUNTIES if REGION_OF.get(c, "North Florida & Panhandle") == r)
        + "</div>" for r in REGIONS)
    write("restaurant-inspections/index.html", page(f"Florida by County: Local Weird News, Arrests & Restaurant Inspections | {NAME}",
        "Pick any of Florida's 67 counties for local weird news, arrests, restaurant closures and the cleanest places to eat.",
        SITE + "/restaurant-inspections/", f"""<section class="container" style="max-width:900px"><div class="page-head"><span class="tag">All 67 counties</span>
<h1>📍 Pick your county</h1><p>Your local Florida Man news, arrests, Roach Report and where to eat.</p></div>{by_region}</section>"""))
    return urls


POPULAR_COUNTIES = ["Sarasota", "Manatee", "Hillsborough", "Pinellas", "Pasco", "Polk", "Lee", "Charlotte",
                    "Orange", "Miami-Dade", "Broward", "Palm Beach"]


def county_block():
    cl = load_closures()["closures"]
    cd = load_clean().get("items", [])
    chips = ""
    for c in POPULAR_COUNTIES:
        shut = sum(1 for x in cl if (x.get("county") or county_for(x["city"])) == c)
        good = sum(1 for x in cd if x["county"] == c)
        chips += (f'<a class="cb-chip" href="/restaurant-inspections/{county_slug(c)}/"><strong>{e(c)}</strong>'
                  f'<span>🚫 {shut} · ✨ {good}{"+" if good >= 60 else ""}</span></a>')
    opts = "".join(f'<option value="/restaurant-inspections/{county_slug(c)}/">{e(c)} County</option>' for c in ALL_COUNTIES)
    return f"""<section class="county-block"><div class="cb-head"><span class="tag">📍 Your county</span>
<h2>Florida Man, but local</h2><p>Pick your county for local weird news, arrests, restaurant inspections and where to eat.</p></div>
<div class="cb-grid">{chips}</div>
<div class="cb-foot"><select onchange="if(this.value)location.href=this.value" aria-label="Pick your county"><option value="">All 67 counties…</option>{opts}</select>
<span class="cb-key">🚫 shut down (8 wks) · ✨ perfect inspections (30 days)</span></div></section>"""


def county_picker():
    opts = "".join(f'<option value="/restaurant-inspections/{county_slug(c)}/">{e(c)} County</option>' for c in ALL_COUNTIES)
    return f"""<section class="container"><div class="county-picker"><span>📍 Get your local news:</span>
<select onchange="if(this.value)location.href=this.value" aria-label="Pick your county"><option value="">Pick your county…</option>{opts}</select></div></section>"""


def roach_teaser():
    cl = load_closures()["closures"][:4]
    if not cl:
        return ""
    lis = "".join(f"""<li><a href="/roach-report/"><span class="eat-mini">{reason_emoji(c["reason"])}</span><div><strong>{e(c["name"].title() if c["name"].isupper() else c["name"])}</strong>
<p class="meta">{e(c["city"])} · {e(c["reason"])}</p></div></a></li>""" for c in cl)
    return f"""<aside class="rail-box"><div class="rail-head"><span class="tag">The Roach Report</span><h2>Shut down by the state this week</h2></div>
<ul class="eat-list rental-mini">{lis}</ul><a class="rail-more" href="/roach-report/">See the full Roach Report →</a></aside>"""


def build_social():
    kits = []
    for st in STORIES:
        folder = os.path.join(ROOT, "social", st["slug"])
        if os.path.exists(os.path.join(folder, "video.mp4")):
            try:
                cap = json.load(open(os.path.join(folder, "caption.json")))
            except Exception:
                cap = {}
            kits.append((st, cap))
    def copy_btn(label, text):
        return (f'<button class="sk-copy" type="button" data-t="{e(text)}">{label}</button>' if text else "")
    cards = "".join(f"""<article class="sk-card">
  <video controls playsinline preload="none" poster="/social/{st["slug"]}/cover.jpg" src="/social/{st["slug"]}/video.mp4"></video>
  <div class="sk-body"><span class="tag">{e(st["category"])} · {nice_date(st["date"])}</span><h3>{e(st["title"])}</h3>
  <a class="cam-btn" href="/social/{st["slug"]}/video.mp4" download="{st["slug"]}.mp4">⬇ Download video</a>
  <div class="sk-btns">{copy_btn("📘 Facebook post", cap.get("facebook"))}{copy_btn("💬 FB comment (link)", cap.get("facebook_comment"))}
  {copy_btn("📸 Instagram", cap.get("instagram"))}{copy_btn("🎵 TikTok", cap.get("tiktok"))}{copy_btn("🔗 Link", cap.get("link"))}</div></div>
</article>""" for st, cap in kits) or '<p class="empty">No videos yet. The morning robot makes them for each new story.</p>'
    body = f"""<section class="container" style="max-width:900px">
  <div class="page-head"><span class="tag">Team only · not listed on the site</span><h1>Social Kit</h1>
  <p>Every new story comes with a ready-to-post vertical video and captions. On your phone: tap Download, then post it to TikTok, Reels or Facebook, and tap a Copy button to paste the caption. For Facebook, post the caption with the video, then paste the link as the first comment.</p></div>
  <div class="sk-list">{cards}</div>
</section>
<script>document.addEventListener('click',function(ev){{var b=ev.target.closest('.sk-copy');if(!b)return;
navigator.clipboard.writeText(b.dataset.t).then(function(){{var o=b.textContent;b.textContent='✓ Copied';setTimeout(function(){{b.textContent=o;}},1400);}});}});</script>"""
    write("social/index.html", page(f"Social Kit | {NAME}", "Team social kit.", SITE + "/social/", body,
          extra_head='<meta name="robots" content="noindex,nofollow">'))


TYPE_EMOJI = {"Sativa": "☀️", "Indica": "🌙", "Hybrid": "🌗"}


def strain_card(p):
    spon = '<span class="spon">Sponsored</span>' if p.get("sponsored") else ""
    return f"""<article class="strain {p["type"].lower()}">
  <div class="strain-type">{TYPE_EMOJI.get(p["type"], "🌿")} {e(p["type"])} of the Week {spon}</div>
  <h3>{e(p["name"])}</h3>
  <p class="meta">{e(p["brand"])} · at {e(p["dispensary"])}</p>
  <ul class="strain-facts"><li><b>Form:</b> {e(p["form"])}</li><li><b>Potency:</b> {e(p["thc"])}</li><li><b>Lineage:</b> {e(p["lineage"])}</li></ul>
  <p>{e(p["notes"])}</p>
  <a class="cam-btn" href="{e(p["link"])}" rel="noopener sponsored" target="_blank">See it ({e(p["source"])}) ↗</a>
</article>"""


STRAIN_FINE = ("Florida is medical-only: you need an active Medical Marijuana Use Registry card to buy. "
               "We don't give medical or dosing advice, and effects differ person to person; talk to your qualified physician. "
               "Menus, potency and prices change batch to batch, so check your local store. Paid picks are always labeled Sponsored.")


def build_strains():
    if not STRAIN_WEEKS:
        return
    weeks = sorted(STRAIN_WEEKS, key=lambda w: w["week"], reverse=True)
    for i, w in enumerate(weeks):
        others = "".join(f'<li><a href="/dispensaries/strains-of-the-week/{o["week"]}/">{e(o["title"])}</a> <span class="meta">{o["week"]}</span></li>'
                         for o in weeks if o is not w)[:6000]
        body = f"""<section class="container" style="padding-top:36px">
  <p class="meta"><a href="/dispensaries/">Weed Guide</a> › Strains of the Week</p>
  <span class="tag">Strains of the Week · {w["week"]}</span>
  <h1>{e(w["title"])}</h1>
  <p class="story-dek" style="max-width:820px">{e(w["intro"])}</p>
  <div class="strain-grid">{"".join(strain_card(p) for p in w["picks"])}</div>
  <div class="source-box"><span class="label">The fine print</span><p>{STRAIN_FINE}</p></div>
  {f'<h2 class="label" style="margin-top:28px">Past picks</h2><ul class="past-weeks">{others}</ul>' if others else ""}
  <p style="margin-top:20px"><a href="/advertise/">Dispensaries: want your strain featured? →</a></p>
</section>"""
        desc = "This week's Florida Sativa, Indica and Hybrid picks: " + ", ".join(p["name"] for p in w["picks"]) + ". Real products on Florida dispensary menus."
        title = f"{e(w['title'])} | {NAME}"
        write(f"dispensaries/strains-of-the-week/{w['week']}/index.html",
              page(title, desc, SITE + f"/dispensaries/strains-of-the-week/{w['week']}/", body))
        if i == 0:
            write("dispensaries/strains-of-the-week/index.html",
                  page(f"Florida Strains of the Week: Sativa, Indica & Hybrid Picks | {NAME}", desc,
                       SITE + f"/dispensaries/strains-of-the-week/{w['week']}/", body))


def strains_teaser():
    if not STRAIN_WEEKS:
        return ""
    w = max(STRAIN_WEEKS, key=lambda w: w["week"])
    picks = "".join(f'<li><span>{TYPE_EMOJI.get(p["type"], "🌿")} <b>{e(p["type"])}:</b></span> {e(p["name"])} <span class="meta">({e(p["dispensary"])})</span></li>' for p in w["picks"])
    return f"""<div class="source-box strains-box" style="margin-top:28px"><span class="label">🌿 Strains of the Week</span>
  <h3 style="margin:6px 0"><a href="/dispensaries/strains-of-the-week/">{e(w["title"])}</a></h3>
  <ul class="strain-mini">{picks}</ul><a class="rail-more" href="/dispensaries/strains-of-the-week/">Read this week's picks →</a></div>"""


def build_dispensaries():
    mq = lambda q: "https://www.google.com/maps/search/" + quote_plus(q)
    brands = "".join(f"""<article class="rental"><div class="rental-body">
  <span class="tag">{e(b["tag"])}</span><h3>{b["emoji"]} {e(b["name"])}</h3><p class="ev-blurb">{e(b["blurb"])}</p>
  <a class="cam-btn" href="{mq(b["name"] + " dispensary Florida")}" rel="noopener" target="_blank">Find a {e(b["name"])} near you ↗</a></div></article>""" for b in BRANDS)
    areas = "".join(f"""<a class="ex-tile" href="{mq("medical marijuana dispensary " + q)}" rel="noopener" target="_blank">
<span class="ex-emoji" aria-hidden="true">📍</span><strong>{e(n)}</strong><span>Dispensaries on the map, with ratings ↗</span></a>""" for n, q in AREAS)
    body = f"""<section class="effd-hero"><div class="container">
  <span class="effd-logo big">The Florida <em>Weed Guide</em></span>
  <p class="effd-tag">Where Florida's medical marijuana patients shop, how to get your card, and the rules that keep you out of our Weirdest Arrests page.</p>
</div></section>
<section class="container" style="margin-top:32px">
  <div class="source-box" style="border-left:5px solid var(--accent)"><span class="label">First things first</span>
  <p><strong>Florida is medical-only.</strong> Recreational marijuana fell short of the 60% it needed in 2024, and the 2026 version didn't make the ballot. To buy at a dispensary you need a state Medical Marijuana Use Registry card.</p></div>
  {strains_teaser()}

  <div class="section-head" style="margin-top:36px"><h2 class="label">How to get a card</h2></div>
  <ol class="how-list" style="list-style:none;padding:0">
    <li><span class="how-n" style="background:var(--accent)">1</span><div><h3>See a qualified doctor</h3><p>Only doctors registered with the state can certify you. Your first visit has to be an in-person exam; renewals can often be done by video. Visits usually run about $150 to $250.</p></div></li>
    <li><span class="how-n" style="background:var(--accent)">2</span><div><h3>Doctor adds you to the registry</h3><p>If you qualify, the doctor enters you into Florida's Medical Marijuana Use Registry.</p></div></li>
    <li><span class="how-n" style="background:var(--accent)">3</span><div><h3>Apply and pay the state fee</h3><p>You finish the application online and pay the state's $75 card fee. You'll get an email you can use while the plastic card is in the mail.</p></div></li>
    <li><span class="how-n" style="background:var(--accent)">4</span><div><h3>Renew on time</h3><p>Doctor certifications and the card both have to be renewed, and the state fee applies each time. Set a reminder.</p></div></li>
  </ol>
  <p class="section-sub" style="margin-top:16px"><a href="https://knowthefactsmmj.com/" rel="noopener" target="_blank">Official Florida Office of Medical Marijuana Use site ↗</a></p>
  <div class="sponsor-slot">
    <span class="sponsor-tag">Sponsored · Featured card doctors</span>
    <h3>Need your card? Featured doctors coming soon.</h3>
    <p>Are you a Florida-qualified medical marijuana physician or clinic? Get in front of Floridians looking for a card, right on this page.</p>
    <a class="cam-btn" href="/advertise/#weed-guide">Get your practice listed →</a>
  </div>

  <div class="section-head" style="margin-top:40px"><h2 class="label">Find one near you</h2></div>
  <div class="ex-grid">{areas}</div>

  <div class="section-head" style="margin-top:40px"><h2 class="label">The big names</h2></div>
  <div class="rental-grid">{brands}</div>

  <div class="section-head" style="margin-top:40px"><h2 class="label">Picking the good stuff</h2></div>
  <div class="awards">
    <div class="award"><span>🧑‍🔬</span><h3>Ask the budtender</h3><p>Staff know what just came in and what patients keep coming back for. Tell them what you're after.</p></div>
    <div class="award"><span>🏷️</span><h3>Read the label</h3><p>Florida products list THC and CBD content and a harvest or packaging date. Fresher flower is usually better.</p></div>
    <div class="award"><span>💸</span><h3>Watch the deals</h3><p>Chains run daily and first-time patient discounts. Sign up for texts at the ones you like.</p></div>
    <div class="award"><span>⭐</span><h3>Check live ratings</h3><p>Ratings change constantly, so use the map links above to see what local patients say this week.</p></div>
  </div>

  <div class="section-head" style="margin-top:40px"><h2 class="label">Rules that keep you off our front page</h2></div>
  <div class="awards">
    <div class="award"><span>🚗</span><h3>Don't drive high</h3><p>A medical card is not a DUI pass. Florida's DUI law covers drugs too, and yes, that includes golf carts and lawn mowers.</p></div>
    <div class="award"><span>🏖️</span><h3>Not in public</h3><p>Smoking medical marijuana in public places is not allowed. Keep it at home.</p></div>
    <div class="award"><span>🧾</span><h3>Keep it in the package</h3><p>Carry your card and keep products in their original dispensary packaging.</p></div>
    <div class="award"><span>🗺️</span><h3>Don't cross state lines</h3><p>Marijuana is still illegal under federal law, so it can't leave Florida with you, even to a legal state.</p></div>
  </div>
  <p class="section-sub" style="margin-top:20px">For patients 18+ with a valid Florida card (minors need a caregiver). This guide is general information, not medical or legal advice. Paid placements are always labeled Sponsored; everything else on this page is unpaid.</p>
</section>"""
    write("dispensaries/index.html", page(f"Florida Dispensary Guide: Medical Marijuana Card & Best-Known Dispensaries | {NAME}",
        "How to get a Florida medical marijuana card, where to find dispensaries near you, the big Florida chains and the rules to know.",
        SITE + "/dispensaries/", body))


SPONSOR_SLOTS = [
    ("weed-guide", "🌿", "The Florida Weed Guide", "Featured card doctors and clinics, plus a dispensary partner spot. Readers here are actively looking for a card or a store.",
     "/dispensaries/"),
    ("roach-report", "🪳", "The Roach Report", "\"Presented by\" sponsorship, a natural fit for pest control, cleaning and restaurant-supply companies. Updated daily, built to be shared.",
     "/roach-report/"),
    ("clean", "🍽️", "Clean Plate Club", "Featured spot for your county on our list of restaurants with perfect state inspections. Readers come here right after the Roach Report.", "/clean-plate-club/"),
    ("eats", "🐊", "Weird Eats", "Feature your restaurant, food truck or bar next to Florida's strangest menus.", "/eats/"),
    ("events", "🎪", "Weird Florida Events", "Promote your festival, fair or event on our upcoming-events calendar.", "/events/"),
    ("cams", "📹", "Florida Cams", "Sponsor the live cams page, or get your own business cam featured.", "/cams/"),
    ("lemonade", "🍋", "LEMONADE Charity Drag Race", "Sponsor a lemon car: tiers from $2,500 to $25,000, all for local charities.", "/gives-back/lemonade/"),
    ("site", "📰", "Sitewide & social", "Banner spots on stories, plus sponsored mentions in our daily videos on TikTok, Reels and Facebook.", "/"),
]


def build_advertise():
    tiles = "".join(f"""<article class="rental" id="{sid}"><div class="rental-body"><h3>{em} {e(n)}</h3><p class="ev-blurb">{e(d)}</p>
<a class="ev-link" href="{u}">See the page →</a></div></article>""" for sid, em, n, d, u in SPONSOR_SLOTS)
    contact = (f'<a class="cam-btn" href="mailto:{CONTACT_EMAIL}?subject=Advertising%20on%20Florida%20Man%20Times">Email {CONTACT_EMAIL}</a>'
               if CONTACT_EMAIL else '<span class="cam-btn" style="opacity:.6">Advertising inquiries open soon</span>')
    body = f"""<section class="effd-hero"><div class="container">
  <span class="effd-logo big">Advertise with <em>Florida Man</em></span>
  <p class="effd-tag">Put your business in front of people who love Florida at its weirdest. Every sponsored spot is clearly labeled, and we only take sponsors we'd send our own friends to.</p>
  <div style="margin-top:20px">{contact}</div>
</div></section>
<section class="container" style="margin-top:32px">
  <div class="section-head"><h2 class="label">Sponsor spots</h2></div>
  <div class="rental-grid">{tiles}</div>
  <div class="source-box" style="margin-top:28px"><span class="label">The fine print</span>
  <p>Sponsored placements are labeled. Sponsors never get a say in our news stories, arrests or the Roach Report, which come straight from public records. Medical marijuana physicians are responsible for following Florida's advertising rules for qualified physicians, and doctor and dispensary listings are kept separate.</p></div>
</section>"""
    write("advertise/index.html", page(f"Advertise on Florida Man Times | {NAME}",
        "Sponsor the Florida Weed Guide, Roach Report, Weird Eats, events, live cams or the LEMONADE charity drag race.",
        SITE + "/advertise/", body))


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


def eat_image(x):
    for ext in IMG_EXTS:
        if os.path.exists(os.path.join(ROOT, "images", "eats", x["slug"] + ext)):
            return f"/images/eats/{x['slug']}{ext}"
    return None


def eat_card(x):
    from urllib.parse import quote
    eats = "".join(f'<span class="mini-tag">{e(t)}</span>' for t in x["eats"])
    status = ('<span class="status on">On the menu</span>' if x["status"] == "menu"
              else '<span class="status legend">Florida food legend</span>')
    img = eat_image(x)
    pic = (f'<div class="eat-photo"><img src="{img}" alt="{e(x["eats"][0])} illustration" loading="lazy" decoding="async"></div>'
           if img else f'<div class="eat-photo placeholder" aria-hidden="true"><span>{x["emoji"]}</span></div>')
    addr = ""
    if x.get("address"):
        maps = "https://www.google.com/maps/search/?api=1&query=" + quote(x["name"] + ", " + x["address"])
        addr = (f'<p class="eat-addr">📍 {e(x["address"])}</p>'
                f'<a class="dir-btn" href="{maps}" target="_blank" rel="noopener">Get directions</a>')
    return f"""<article class="eat">
  {pic}
  <div class="eat-body">
    {status}
    <h3>{e(x["name"])}</h3>
    <p class="meta">{e(x["place"])} <span>·</span> {e(x["city"])}</p>
    <div class="ev-tags">{eats}</div>
    <p class="ev-blurb">{e(x["blurb"])}</p>
    {addr}
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


US_ABBR = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC"}


def across_america_row():
    """Compact headline strip: lots of national weirdness, very little space."""
    if not US_STORIES:
        return ""
    lis = "".join(
        f'<li><span class="st">{US_ABBR.get(s.get("state",""), "US")}</span>'
        f'<a href="/stories/{s["slug"]}/">{e(s["title"])}</a></li>' for s in US_STORIES[:8])
    return f"""<section class="container">
  <div class="across-strip">
    <div class="as-head"><h2>🇺🇸 Meanwhile, Not in Florida</h2><a href="/section/across-america/">All {len(US_STORIES)} →</a></div>
    <ul class="as-list">{lis}</ul>
  </div>
</section>"""


def build_home():
    lead = FL_STORIES[0]
    left = FL_STORIES[1:4]
    latest = FL_STORIES[4:12]
    body = f"""<section class="front3 container">
  <div class="col-left"><h2 class="label left-label">Earlier this week</h2>{"".join(mini(s) for s in left)}</div>
  <div class="col-lead">{hero(lead)}{county_block()}</div>
  <div class="col-right">{arrest_feed(ARRESTS[:6])}</div>
</section>
<section class="container">
  <div class="section-head split"><h2 class="label">Latest Headlines</h2><a class="see-all" href="/section/florida-man/">All stories →</a></div>
  <div class="latest-wrap">
    <div class="grid4">{"".join(card(s) for s in (latest or FL_STORIES[1:]))}</div>
  </div>
</section>

<section class="container two-up">
  <div>{events_band_inner()}<div style="margin-top:22px">{roach_teaser()}</div></div>
  <div>{eats_teaser()}{headline_list(top_stories(5), "Best of Florida Man")}<a class="rail-more" href="/best-of/">See the Top 10 →</a></div>
</section>
{across_america_row()}
{lemonade_promo()}
{features_row()}
{effd_promo()}
{"".join(section_row(n, sl) for n, sl in SECTIONS.items() if n != "Across America")}
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


def share_links(s, url=None):
    url = url or f'{SITE}/stories/{s["slug"]}/'
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
    def para(p):
        return f"<h2>{e(p[3:])}</h2>" if p.startswith("## ") else f"<p>{e(p)}</p>"
    lead, rest = s["body"][:2], s["body"][2:]
    paras = "".join(para(p) for p in lead)
    if rest:
        paras += (f'<div class="story-rest" id="rest">{"".join(para(p) for p in rest)}</div>'
                  '<button class="keep-reading" type="button" onclick="document.getElementById(\'rest\').classList.add(\'open\');this.remove()">'
                  'Keep reading <span aria-hidden="true">↓</span></button>')
    quick = f'<aside class="quick-take"><span class="label">The quick take</span><p>{e(s["quick"])}</p></aside>' if s.get("quick") else ""
    srcs = s.get("sources") or [(s["source_name"], s["source_url"])]
    src_links = "".join(f'<li><a href="{u}" rel="nofollow noopener" target="_blank">{e(n)} ↗</a></li>' for n, u in srcs)
    src_names = ", ".join(e(n) for n, _ in srcs[:2])
    cty = county_of_place(s.get("location", "")) if is_fl(s) else None
    same = [x for x in STORIES if x is not s and ((cty and is_fl(x) and county_of_place(x.get("location", "")) == cty) or (not is_fl(s) and not is_fl(x)))]
    related = (same + [x for x in STORIES if x is not s and x not in same])[:3]
    cty_link = (f'<a class="cty-link" href="/restaurant-inspections/{county_slug(cty)}/"><span>📍 More from {e(cty)} County</span>'
                f'<strong>Local news, arrests, restaurant inspections &amp; where to eat →</strong></a>') if cty else ""
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
    if img and s.get("photo_credit"):
        caption = f'<p class="caption">Photo: {e(s["photo_credit"])}</p>'
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
  {quick}
  <div class="story-body">{paras}</div>
  <div class="source-box">
    <span class="label">{"Sources" if len(srcs) > 1 else "Source"}</span>
    <ul class="src-list">{src_links}</ul>
    <p>Based on reporting by {src_names}, retold in our own words.</p>
  </div>
  {share_links(s)}
  {cty_link}
</article>
<section class="container">
  <div class="section-head"><h2 class="label">More Stories</h2></div>
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
    urls = [(SITE + "/", today), (SITE + "/about/", today), (SITE + "/arrests/", today), (SITE + "/events/", today), (SITE + "/eats/", today), (SITE + "/arrest-lookup/", today), (SITE + "/best-of/", today), (SITE + "/gives-back/", today), (SITE + "/gives-back/lemonade/", today), (SITE + "/rentals/", today), (SITE + "/odd-places/", today), (SITE + "/artist-of-the-week/", today), (SITE + "/effd-up/", today), (SITE + "/cams/", today), (SITE + "/roach-report/", today), (SITE + "/dispensaries/", today), (SITE + "/dispensaries/strains-of-the-week/", today), (SITE + "/advertise/", today), (SITE + "/clean-plate-club/", today), (SITE + "/restaurant-inspections/", today)] + [(u, today) for u in COUNTY_URLS] + [(SITE + f"/effd-up/{iv['slug']}/", today) for iv in INTERVIEWS] + [(SITE + f"/dispensaries/strains-of-the-week/{w['week']}/", today) for w in STRAIN_WEEKS]
    urls += [(f"{SITE}/section/{slug}/", today) for slug in SECTIONS.values()]
    urls += [(f'{SITE}/stories/{s["slug"]}/', s["date"]) for s in STORIES]
    sm = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /social/\nDisallow: /scan/\n\nSitemap: {SITE}/sitemap.xml\n")
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
    build_best_of()
    build_giving()
    build_rentals()
    build_places()
    build_artist()
    build_interviews()
    build_cams()
    build_roach()
    build_social()
    build_dispensaries()
    build_strains()
    build_advertise()
    build_clean_plate()
    COUNTY_URLS[:] = build_county_pages()
    build_eats()
    build_about()
    build_404()
    build_feeds()
    with_img = sum(1 for s in STORIES if image_for(s))
    print(f"Built {len(STORIES)} stories ({with_img} with images).")
