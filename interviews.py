"""Eff'd Up With... — real VIDEO interviews with Florida's most gloriously unhinged people.

RULES (never break):
- Real interviews only, done by a person from the Florida Man Times team. The daily bot must NEVER write or invent an interview.
- Adults only, sober at the time of the interview, and they agreed in writing to be published.
- Nobody in crisis (addiction, homelessness, mental health) as the subject. Guests are in on the joke.
- Video is hosted on YouTube (free, unlimited, and gets us YouTube viewers too). Thumbnail is a still from the video.

Entry format (newest first):
{
  "slug": "python-pete",
  "guest": "Pete Example",              # name or nickname the guest approved
  "title": "The Python Hunter Who Has Been Bitten 31 Times",
  "dek": "One-line tease.",
  "city": "Everglades City",
  "date": "2026-12-01",
  "emoji": "🐍",
  "video": "https://youtu.be/XXXXXXXXXXX",  # YouTube, Instagram (reel/post), TikTok or Facebook video link, or "/videos/<slug>.mp4"
  "vertical": False,                     # True for phone-style 9:16 (Shorts/Reels)
  "intro": ["Short write-up under the video.", "..."],
  "quotes": [("Question we asked?", "Their best answer."), ...],   # 3-6 best moments
  # thumbnail: images/interviews/<slug>.jpg (a frame from the video)
}
"""

INTERVIEWS = [
    {
        "slug": "quarantine-check-in",
        "guest": "All Gas No Brakes",
        "title": "A Florida Quarantine Check-In",
        "dek": "Remember spring 2020? Florida does. Kind of.",
        "city": "Florida",
        "date": "2026-11-24",
        "emoji": "🎥",
        "video": "https://www.instagram.com/p/CBgTbKbg4TM/",
        "vertical": True,
        "credit": "All Gas No Brakes (Andrew Callaghan)",
        "credit_url": "https://www.instagram.com/allgasnobrakesshow/",
        "intro": [
            "Back in 2020, while the rest of the country was baking sourdough and learning Zoom, Andrew Callaghan's All Gas No Brakes rolled through Florida to see how the Sunshine State was handling lockdown.",
            "The answer, as usual, was: in its own way. Press play.",
        ],
        "quotes": [],
    },
]

# Who we're looking for (shown while there are no interviews yet)
WANTED = [
    ("🐍", "Python hunters", "Anyone who wrestles 15-foot snakes for fun and a paycheck."),
    ("🦍", "Skunk ape hunters", "You've seen it. You have a cast of the footprint. We believe you (mostly)."),
    ("🐊", "Gator wranglers", "Pulled one out of a pool, a car or a Walmart? Talk to us."),
    ("🚗", "Demolition derby & swamp buggy drivers", "Bonus points if your car has a name."),
    ("🐓", "People with way too many animals", "40 roosters, 3 emus and a pig named Steve counts."),
    ("📰", "Actual Florida Men", "Were you in one of our stories? Once your case is closed, tell your side."),
]

# The same questions every guest gets, plus their own
STANDARD_QS = [
    "What's the most Florida thing you've ever done?",
    "Gator or python. Who wins?",
    "Worst idea that seemed great at 2 a.m.?",
    "What did your mom say?",
    "Would you do it again?",
]
