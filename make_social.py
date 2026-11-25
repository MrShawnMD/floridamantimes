"""Daily social kit: for each new story, make
  social/<slug>/video.mp4   - 1080x1920 vertical video (story image, headline, slow zoom, AI voiceover)
  social/<slug>/cover.jpg   - the first frame (for thumbnails)
  social/<slug>/caption.json- ready-to-paste captions for Facebook/Instagram and TikTok
Voiceover uses OpenAI text-to-speech when OPENAI_API_KEY is set; otherwise the video is silent.
Runs in the GitHub Action. Only makes kits for the newest stories that don't have one yet.
"""
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from stories import STORIES  # noqa: E402
import build  # noqa: E402

OUT = os.path.join(ROOT, "social")
FONT_BLACK = os.path.join(ROOT, "assets", "fonts", "Inter-Black.otf")
FONT_BOLD = os.path.join(ROOT, "assets", "fonts", "Inter-Bold.otf")
W, H = 1080, 1920
LIME, INK, WHITE = (163, 230, 53), (16, 20, 16), (255, 255, 255)
MAX_PER_RUN = int(os.environ.get("SOCIAL_MAX", "3"))
SITE = "floridamantimes.com"


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def frame(s, img_path):
    """Build the still 1080x1920 frame that the video slowly zooms into."""
    base = Image.open(img_path).convert("RGB")
    # blurred background fill
    bg = base.resize((int(H * base.width / base.height), H)).crop((0, 0, W, H)) if base.width / base.height > W / H else base.resize((W, int(W * base.height / base.width)))
    bg = bg.crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    # main image: tall crop centered
    pw, ph = W, 980
    r = max(pw / base.width, ph / base.height)
    im = base.resize((int(base.width * r) + 1, int(base.height * r) + 1))
    x0 = (im.width - pw) // 2
    im = im.crop((x0, 0, x0 + pw, ph))
    bg.paste(im, (0, 470))
    d = ImageDraw.Draw(bg)
    # top brand bar
    d.rectangle((0, 0, W, 130), fill=INK)
    f_brand = ImageFont.truetype(FONT_BLACK, 52)
    d.rounded_rectangle((48, 33, 112, 97), 14, fill=INK, outline=LIME, width=3)
    d.text((80, 65), "FM", font=ImageFont.truetype(FONT_BLACK, 30), fill=LIME, anchor="mm")
    d.text((132, 65), "Florida Man", font=f_brand, fill=WHITE, anchor="lm")
    tw = d.textlength("Florida Man ", font=f_brand)
    d.text((132 + tw, 65), "Times", font=f_brand, fill=LIME, anchor="lm")
    # category pill
    f_pill = ImageFont.truetype(FONT_BOLD, 34)
    label = s["category"].upper()
    lw = d.textlength(label, font=f_pill)
    d.rounded_rectangle((48, 168, 48 + lw + 48, 222), 27, fill=LIME)
    d.text((72, 195), label, font=f_pill, fill=INK, anchor="lm")
    # headline (top area)
    size = 68
    while size > 44:
        f_h = ImageFont.truetype(FONT_BLACK, size)
        lines = wrap(d, s["title"], f_h, W - 96)
        if len(lines) * size * 1.12 <= 220:
            break
        size -= 4
    y = 246
    for ln in lines[:4]:
        d.text((48, y), ln, font=f_h, fill=WHITE)
        y += int(size * 1.12)
    # bottom: dek + CTA
    f_dek = ImageFont.truetype(FONT_BOLD, 44)
    dek_lines = wrap(d, s["dek"], f_dek, W - 96)[:3]
    yb = 1500
    for ln in dek_lines:
        d.text((48, yb), ln, font=f_dek, fill=WHITE)
        yb += 56
    d.rounded_rectangle((48, 1730, W - 48, 1840), 55, fill=LIME)
    d.text((W // 2, 1785), "Full story: " + SITE, font=ImageFont.truetype(FONT_BLACK, 46), fill=INK, anchor="mm")
    return bg


def script_for(s):
    quick = s.get("quick") or s["dek"]
    return f"{s['title']}. {quick} The full story is at Florida Man Times dot com."


def tts(text, path):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return False
    body = json.dumps({
        "model": os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        "voice": os.environ.get("OPENAI_TTS_VOICE", "ash"),
        "input": text,
        "instructions": "Upbeat, witty local TV news anchor with a playful Florida twang. Brisk pace, deadpan delivery on the punchlines.",
        "response_format": "mp3",
    }).encode()
    req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            open(path, "wb").write(r.read())
        return True
    except Exception as ex:
        print("TTS failed:", ex)
        return False


def duration(path):
    out = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 20.0


def captions(s):
    url = f"https://{SITE}/stories/{s['slug']}/"
    place = re.sub(r"[^A-Za-z]", "", s["location"].split(",")[0]) or "Florida"
    tags = f"#FloridaMan #Florida #{place} #FloridaManTimes #OnlyInFlorida #WeirdNews"
    return {
        "facebook": f"{s['title']}\n\n{s['dek']}\n\n{s.get('quick', '')}\n\n👇 Full story in the comments",
        "facebook_comment": f"Full story: {url}",
        "instagram": f"{s['title']} 🐊\n\n{s.get('quick') or s['dek']}\n\nFull story: link in bio → {SITE}\n\n{tags}",
        "tiktok": f"{s['title']} 🐊 Full story at {SITE} {tags}",
        "link": url,
    }


def make(s):
    img = build.image_for(s)
    if not img:
        return False
    img_path = os.path.join(ROOT, img.lstrip("/"))
    folder = os.path.join(OUT, s["slug"])
    os.makedirs(folder, exist_ok=True)
    still = frame(s, img_path)
    cover = os.path.join(folder, "cover.jpg")
    still.save(cover, quality=88)
    still_png = os.path.join(folder, "_still.png")
    still.save(still_png)
    audio = os.path.join(folder, "_voice.mp3")
    has_audio = tts(script_for(s), audio)
    secs = (duration(audio) + 1.2) if has_audio else 12.0
    frames = int(secs * 30)
    vf = (f"scale=1188:2112,zoompan=z='min(zoom+0.0002,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={frames}:s={W}x{H}:fps=30,format=yuv420p")
    cmd = [ffmpeg(), "-y", "-loop", "1", "-i", still_png]
    if has_audio:
        cmd += ["-i", audio]
    cmd += ["-vf", vf, "-t", f"{secs:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-r", "30"]
    cmd += (["-c:a", "aac", "-b:a", "128k", "-shortest"] if has_audio else ["-an"])
    cmd += ["-movflags", "+faststart", os.path.join(folder, "video.mp4")]
    r = subprocess.run(cmd, capture_output=True, text=True)
    for f in (still_png, audio):
        if os.path.exists(f):
            os.remove(f)
    if r.returncode != 0:
        print("ffmpeg failed:", r.stderr[-800:])
        return False
    cap = captions(s)
    cap["voiceover"] = script_for(s) if has_audio else ""
    json.dump(cap, open(os.path.join(folder, "caption.json"), "w"), indent=1, ensure_ascii=False)
    print("Made social kit:", s["slug"], f"({secs:.1f}s, audio={has_audio})")
    return True


def main():
    done = 0
    for s in STORIES:
        if done >= MAX_PER_RUN:
            break
        if os.path.exists(os.path.join(OUT, s["slug"], "video.mp4")):
            continue
        if make(s):
            done += 1
    print(f"Social kits made: {done}")


if __name__ == "__main__":
    main()
