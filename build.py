#!/usr/bin/env python3
"""Builds the Florida Man Times static site from stories.py.

Usage:  python3 build.py
Writes index.html, /stories/<slug>/, /section/<name>/, sitemap.xml, robots.txt, feed.xml.
"""
import datetime as dt
import html
import json
import os
import re

from stories import STORIES

SITE = "https://floridamantimes.com"
NAME = "Florida Man Times"
TAGLINE = "The wildest true stories from the Sunshine State"
ROOT = os.path.dirname(os.path.abspath(__file__))

SECTIONS = {
    "Florida Man": "florida-man",
    "Florida Woman": "florida-woman",
    "Wild Florida": "wild-florida",
}

e = html.escape


def nice_date(d):
    return dt.date.fromisoformat(d).strftime("%B %-d, %Y")


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def page(title, description, canonical, body, extra_head="", og_type="website"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Oswald:wght@500;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
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


def header():
    today = dt.date.today().strftime("%A, %B %-d, %Y")
    nav = "".join(f'<a href="/section/{slug}/">{e(n)}</a>' for n, slug in SECTIONS.items())
    ticker = " &nbsp;★&nbsp; ".join(e(s["title"]) for s in STORIES[:5])
    return f"""<header class="masthead">
  <div class="topbar"><span>{today}</span><span>Sarasota, Florida</span><span>Est. 2026 · Always Unbelievable, Always True</span></div>
  <a class="logo" href="/"><span class="logo-small">The</span>Florida Man Times</a>
  <p class="tagline">{TAGLINE}</p>
  <nav class="nav"><a href="/">Front Page</a>{nav}<a href="/about/">About</a></nav>
  <div class="ticker"><span class="ticker-label">Breaking</span><div class="ticker-track"><span>{ticker}</span></div></div>
</header>"""


def footer():
    year = dt.date.today().year
    return f"""<footer class="footer">
  <a class="logo logo-footer" href="/">Florida Man Times</a>
  <p>{TAGLINE}. Every story is based on real, published news reports, rewritten by us and linked to the original source.</p>
  <p class="fine">People named or described in arrest stories are presumed innocent unless proven guilty in court. © {year} Florida Man Times.</p>
</footer>"""


def art(s, size=""):
    return f'<div class="art {size}" style="--c:{s["color"]}" aria-hidden="true"><span>{s["emoji"]}</span></div>'


def card(s, lead=False):
    url = f'/stories/{s["slug"]}/'
    cls = "card lead" if lead else "card"
    return f"""<article class="{cls}">
  <a href="{url}">{art(s, "big" if lead else "")}</a>
  <div class="card-text">
    <a class="kicker" href="/section/{SECTIONS[s["category"]]}/">{e(s["category"])}</a>
    <h2><a href="{url}">{e(s["title"])}</a></h2>
    <p class="dek">{e(s["dek"])}</p>
    <p class="meta">{e(s["location"])} · {nice_date(s["date"])}</p>
  </div>
</article>"""


def build_home():
    lead, rest = STORIES[0], STORIES[1:]
    side = rest[:2]
    grid = rest[2:]
    body = f"""<section class="front">
  {card(lead, lead=True)}
  <div class="side">{''.join(card(s) for s in side)}</div>
</section>
<h3 class="rule"><span>More Unbelievable Headlines</span></h3>
<section class="grid">{''.join(card(s) for s in grid)}</section>
<section class="tipbox">
  <h3>Seen something only Florida could produce?</h3>
  <p>Our tip line opens soon. If it's real, wild, and from the Sunshine State, it might be our next headline.</p>
</section>"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": NAME,
        "url": SITE + "/",
        "description": TAGLINE,
    }
    write("index.html", page(
        f"{NAME} | Florida Man News, Weird Florida Stories & Headlines",
        "Florida Man Times covers the latest Florida Man and Florida Woman news: bizarre arrests, wild gator encounters and the weirdest true stories from the Sunshine State.",
        SITE + "/",
        body,
        f'<script type="application/ld+json">{json.dumps(jsonld)}</script>',
    ))


def build_story(s, i):
    url = f'{SITE}/stories/{s["slug"]}/'
    paras = "".join(f"<p>{e(p)}</p>" for p in s["body"])
    related = [x for x in STORIES if x is not s][:3]
    jsonld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": s["title"],
        "description": s["dek"],
        "datePublished": s["date"],
        "dateModified": s["date"],
        "mainEntityOfPage": url,
        "image": [SITE + "/og-image.png"],
        "author": {"@type": "Organization", "name": NAME},
        "publisher": {"@type": "Organization", "name": NAME,
                      "logo": {"@type": "ImageObject", "url": SITE + "/favicon.svg"}},
        "articleSection": s["category"],
    }
    body = f"""<article class="story">
  <a class="kicker" href="/section/{SECTIONS[s["category"]]}/">{e(s["category"])}</a>
  <h1>{e(s["title"])}</h1>
  <p class="dek big-dek">{e(s["dek"])}</p>
  <p class="meta">By the Florida Man Times Desk · {e(s["location"])} · {nice_date(s["date"])}</p>
  {art(s, "hero")}
  <div class="story-body">{paras}</div>
  <p class="source">Source: <a href="{s["source_url"]}" rel="nofollow noopener" target="_blank">{e(s["source_name"])}</a></p>
</article>
<h3 class="rule"><span>Keep Reading</span></h3>
<section class="grid">{''.join(card(x) for x in related)}</section>"""
    write(f'stories/{s["slug"]}/index.html', page(
        f'{s["title"]} | {NAME}',
        s["dek"],
        url,
        body,
        f'<script type="application/ld+json">{json.dumps(jsonld)}</script>',
        og_type="article",
    ))


def build_sections():
    for name, slug in SECTIONS.items():
        items = [s for s in STORIES if s["category"] == name]
        cards = "".join(card(s) for s in items) or "<p>New stories coming soon.</p>"
        body = f"""<h1 class="section-title">{e(name)}</h1>
<p class="section-dek">The latest {e(name)} stories, straight from real Florida headlines.</p>
<section class="grid">{cards}</section>"""
        write(f"section/{slug}/index.html", page(
            f"{name} News & Stories | {NAME}",
            f"The latest {name} news and weird stories from across Florida.",
            f"{SITE}/section/{slug}/",
            body,
        ))


def build_about():
    body = """<article class="story">
  <h1>About Florida Man Times</h1>
  <div class="story-body">
  <p>Florida is the only place where the news reads like fiction. Florida Man Times collects the strangest, funniest and most unbelievable true stories from across the Sunshine State and serves them up in one place.</p>
  <p>Every story we publish starts with a real, published news report. We rewrite it in our own words and always link back to the original source so you can see it for yourself.</p>
  <p>Some of our stories involve arrests. An arrest is only an accusation, and everyone is presumed innocent unless proven guilty in court. We cover the absurd, not the tragic.</p>
  <p>Based in Sarasota, Florida. Of course.</p>
  </div>
</article>"""
    write("about/index.html", page(
        f"About | {NAME}",
        "About Florida Man Times, the home of Florida Man news and the weirdest true stories from the Sunshine State.",
        SITE + "/about/",
        body,
    ))


def build_404():
    body = """<article class="story center">
  <h1>This page wandered off.</h1>
  <p class="dek big-dek">Probably chasing a gator. Head back to the front page for today's headlines.</p>
  <p><a class="button" href="/">Back to the Front Page</a></p>
</article>"""
    write("404.html", page(f"Page Not Found | {NAME}", "Page not found.", SITE + "/404.html", body))


def build_feeds():
    today = dt.date.today().isoformat()
    urls = [(SITE + "/", today), (SITE + "/about/", today)]
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
    build_home()
    for i, s in enumerate(STORIES):
        build_story(s, i)
    build_sections()
    build_about()
    build_404()
    build_feeds()
    print(f"Built {len(STORIES)} stories.")
