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


# ---- Strains of the Week ------------------------------------------------------------------------------
# One Sativa, one Indica, one Hybrid each week, each a real product on a real Florida dispensary menu.
# Rules: facts only from the dispensary/brand page or a live-menu tracker (link it in "source").
# No health or medical claims, no dosing advice, no invented reviews or effects. Flavor/lineage as the seller
# describes it. Stock and prices change, so say "check your local menu". Paid picks: "sponsored": True (labeled).
# Newest week first. Never post these to Facebook/Instagram/TikTok (Meta and TikTok ban cannabis promotion).
STRAIN_WEEKS = [
    {"week": "2026-11-27",
     "title": "Strains of the Week: A Safari, a Watermelon and a Cherry Walk Into a Dispensary",
     "intro": "Three picks off real Florida menus this week, one from each team. We don't smoke-test anything and we don't make medical promises; we just read the labels so you have something to ask about at the counter. Card holders only, 21+ unless your doctor says otherwise.",
     "picks": [
        {"type": "Sativa", "name": "Soul Safari", "brand": "Trulieve", "dispensary": "Trulieve",
         "form": "3.5g whole flower (TruFlower)", "thc": "27% THC on the listed batch",
         "lineage": "(Malawi Gold × Northern Lights × Haze) × Face Off OG BX1",
         "notes": "Trulieve describes it as a sativa with a bright, globally inspired aroma. Translation: it smells like it has a passport. Listed at $35, sometimes on sale for less.",
         "link": "https://www.trulieve.com/product/trulieve-soul-safari-whole-flower-90045",
         "source": "Trulieve product page"},
        {"type": "Indica", "name": "Watermelon Burst", "brand": "MÜV", "dispensary": "MÜV",
         "form": "Flower (Reserve and Essence lines)", "thc": "Varies by batch, check the label",
         "lineage": "Florida Cake × TK BX1",
         "notes": "MÜV lists it as an indica with sweet, citrus and hops flavors, and limonene, caryophyllene, linalool and humulene as the top terpenes. A Florida-bred cross that sounds like a summer cookout.",
         "link": "https://muvfl.com/post/watermelon-burst",
         "source": "MÜV strain spotlight"},
        {"type": "Hybrid", "name": "Cherry Lime", "brand": "High Supply and others", "dispensary": "Sunnyside, Goldflower and more",
         "form": "Eighths (3.5g flower)", "thc": "Around 18–20% THC on most labels",
         "lineage": "Sold as a hybrid",
         "notes": "On about a dozen Florida menus as of mid-November, including Sunnyside in Port St. Lucie and Goldflower in Cape Coral, with eighths listed around $50 before sales. Sounds like a cocktail, legally isn't one.",
         "link": "https://www.jointcommerce.com/strains/cherry-lime/florida",
         "source": "JointCommerce live-menu tracker (menus checked Nov 19, 2026)"},
     ]},
]
