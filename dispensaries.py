"""Florida Dispensary Guide data. Florida is MEDICAL-ONLY (recreational failed to make the 2026 ballot).
Keep it factual: no dosing advice, no made-up reviews or ratings. Ratings change daily, so we link out to them.
"""

BRANDS = [
    {"name": "Trulieve", "emoji": "🌴", "tag": "The Florida giant",
     "blurb": "Born in Florida and the biggest name in the state. You're rarely far from one, which makes it the default stop for a lot of new card holders.",
     "url": "https://www.trulieve.com/dispensaries/florida"},
    {"name": "Curaleaf", "emoji": "🍃", "tag": "National chain",
     "blurb": "One of the largest cannabis companies in the country, with stores up and down both Florida coasts. Patients often mention the deals.",
     "url": "https://curaleaf.com/locations/florida"},
    {"name": "Sunnyside", "emoji": "☀️", "tag": "Bright and beachy",
     "blurb": "Clean, friendly stores with a big Florida footprint, from the Panhandle to the Keys area.",
     "url": "https://www.sunnyside.shop/"},
    {"name": "MÜV", "emoji": "💜", "tag": "Everywhere, quietly",
     "blurb": "Lots of small, neighborhood-style locations, including Bradenton, Venice and Pinellas Park. Fan reviews tend to praise the staff.",
     "url": "https://muvfl.com/"},
    {"name": "Fluent", "emoji": "🌊", "tag": "Easygoing",
     "blurb": "A Florida operator with a relaxed vibe and stores across the Gulf Coast and Atlantic side.",
     "url": "https://getfluent.com/"},
    {"name": "Rise", "emoji": "🌅", "tag": "Smaller footprint",
     "blurb": "Fewer Florida locations than the big chains, but a loyal following among patients who've tried around.",
     "url": "https://risecannabis.com/dispensaries/florida/"},
    {"name": "Green Dragon", "emoji": "🐉", "tag": "Best name in the game",
     "blurb": "A Florida-born chain with stores in places like Englewood, Fort Myers, Ocala and St. Petersburg. Points for the name alone.",
     "url": "https://www.greendragon.com/"},
    {"name": "Planet 13", "emoji": "🪐", "tag": "Vegas comes to Florida",
     "blurb": "The company behind the famous Las Vegas cannabis superstore now has Florida locations, starting in the Panhandle.",
     "url": "https://www.planet13.com/"},
]

# Quick "near me" finders by area (Google Maps search + Leafly city lists for live ratings)
AREAS = [
    ("Sarasota & Venice", "Sarasota FL"), ("Bradenton & Lakewood Ranch", "Bradenton FL"),
    ("Tampa", "Tampa FL"), ("St. Pete & Clearwater", "St Petersburg FL"), ("Fort Myers & Cape Coral", "Fort Myers FL"),
    ("Orlando", "Orlando FL"), ("Miami", "Miami FL"), ("Fort Lauderdale", "Fort Lauderdale FL"),
    ("Jacksonville", "Jacksonville FL"), ("Pensacola & the Panhandle", "Pensacola FL"),
]
