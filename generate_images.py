#!/usr/bin/env python3
"""Auto-generate missing images with the OpenAI Images API.

For every story / arrest / eats item that has an "image_prompt" but no image file yet,
request an image, crop it to 16:9, resize to 1600x900 and save it where build.py looks.

Needs env OPENAI_API_KEY (stored as a GitHub Actions secret). Without it, does nothing.
Optional env OPENAI_IMAGE_MODEL (default gpt-image-2.5-flare), IMAGE_QUALITY (default medium),
MAX_IMAGES (default 12 per run).
"""
import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from stories import STORIES  # noqa: E402
from arrests import ARRESTS  # noqa: E402
from eats import EATS  # noqa: E402
import build  # noqa: E402

KEY = os.environ.get("OPENAI_API_KEY", "").strip()
MODELS = [m for m in [os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2.5-flare"), "gpt-image-1.5"] if m]
QUALITY = os.environ.get("IMAGE_QUALITY", "medium")
MAX = int(os.environ.get("MAX_IMAGES", "12"))

SAFETY = (" Photorealistic but over the top, news-photo look, vivid Florida color, wide landscape. "
          "All people are invented fictional characters, not real or identifiable people. "
          "No brand logos, no readable text, no gore.")


def jobs():
    for s in STORIES:
        if s.get("image_prompt") and not build.image_for(s):
            yield os.path.join("images", s["slug"] + ".jpg"), s["image_prompt"]
    for a in ARRESTS:
        if a.get("image_prompt") and not build.arrest_image(a):
            yield os.path.join("images", "arrests", build.arrest_id(a) + ".jpg"), a["image_prompt"]
    for x in EATS:
        if x.get("image_prompt") and not build.eat_image(x):
            yield os.path.join("images", "eats", x["slug"] + ".jpg"), x["image_prompt"]


def generate(prompt):
    last = None
    for model in MODELS:
        body = json.dumps({"model": model, "prompt": prompt + SAFETY, "size": "1536x1024",
                           "quality": QUALITY, "n": 1}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body,
                                     headers={"Authorization": f"Bearer {KEY}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r)["data"][0]
            if data.get("b64_json"):
                return base64.b64decode(data["b64_json"]), model
            with urllib.request.urlopen(data["url"], timeout=120) as r:
                return r.read(), model
        except urllib.error.HTTPError as err:
            last = f"{model}: HTTP {err.code} {err.read()[:300]!r}"
            print("  ", last)
    raise RuntimeError(last or "no model worked")


def save(raw, path):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = im.size
    th = round(w * 9 / 16)
    if th < h:  # crop to 16:9 from the center
        top = (h - th) // 2
        im = im.crop((0, top, w, top + th))
    im = im.resize((1600, 900), Image.LANCZOS)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    im.save(full, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    todo = list(jobs())
    print(f"{len(todo)} image(s) missing.")
    if not KEY:
        print("OPENAI_API_KEY not set; skipping image generation.")
        return
    made = 0
    for path, prompt in todo[:MAX]:
        print("Generating", path)
        try:
            raw, model = generate(prompt)
            save(raw, path)
            made += 1
            print("   saved with", model)
        except Exception as err:  # keep going; one failure shouldn't stop the rest
            print("   FAILED:", err)
    print(f"Generated {made} image(s).")


if __name__ == "__main__":
    main()
