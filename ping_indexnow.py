"""Tell Bing / Yahoo / DuckDuckGo (via IndexNow) about every page in the sitemap. Free, no account.
Key file lives at the site root: https://floridamantimes.com/4d124515cdf24ea2477bc11e2317a52e.txt"""
import json, re, urllib.request, os
ROOT = os.path.dirname(os.path.abspath(__file__))
KEY = "4d124515cdf24ea2477bc11e2317a52e"
HOST = "floridamantimes.com"
urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "FloridaManTimesBot/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, len(urls), "URLs")
except Exception as ex:
    print("IndexNow failed:", ex)
