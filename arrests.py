"""Tonight's Weirdest Arrests — quick-hit arrest blurbs.

Newest first. Rules (see STYLE.md "Weirdest Arrests"): no names, no mugshots, no photos of
real people; one or two punchy sentences in the house voice; every fact from the source;
skip anything involving violence with injuries, sex crimes, kids, abuse, addiction,
mental-health crises or homelessness. Optional "story" = slug of a full story on the site (its image is reused).
Images: images/arrests/<date>-<place-slug>.jpg (illustration, invented people only). "emoji" is the fallback.
"""

ARRESTS = [
    {
        "date": "2026-11-19",
        "place": "Tampa",
        "county": "Hillsborough",
        "emoji": "💳",
        "headline": "Man returns to scene of the crime. Specifically, to pick up his card skimmer.",
        "blurb": "Deputies say a 45-year-old man and a buddy went back to a Lowe's self-checkout to collect a credit card skimmer that had been planted on the card machine. Store loss-prevention staff spotted them first. One man was arrested; deputies are still looking for the other.",
        "charge": "Several fraud-related charges",
        "source_name": "Tampa Bay 28",
        "source_url": "https://www.tampabay28.com/news/region-hillsborough/man-arrested-in-tampa-credit-card-skimming-case-deputies-seek-second-suspect",
    },
    {
        "date": "2026-11-15",
        "place": "North Fort Myers",
        "county": "Lee",
        "emoji": "☕",
        "headline": "Roommate allegedly answers a sugar complaint with a sword.",
        "blurb": "Deputies say an argument over borrowed coffee sugar ended with one roommate threatening the other with a martial arts weapon.",
        "charge": "Aggravated assault with a deadly weapon",
        "source_name": "Tampa Free Press",
        "source_url": "https://www.tampafp.com/sword-pulled-over-stolen-coffee-sugar-lands-florida-man-in-jail/",
        "story": "florida-man-sword-over-roommates-coffee-sugar",
    },
    {
        "date": "2026-11-06",
        "place": "Miami Gardens",
        "county": "Miami-Dade",
        "emoji": "🚌",
        "headline": "Man takes a school bus for a full-day joyride. His reason: he thought he'd get away with it.",
        "blurb": "Deputies say a 23-year-old took a bus from a private company's gated lot and drove it around for a whole day. The company already knew him.",
        "charge": "Three felony charges",
        "source_name": "Local 10 News",
        "source_url": "https://www.local10.com/news/local/2026/11/06/south-florida-man-stole-school-bus-drove-it-around-for-a-day-deputies-say/",
        "story": "florida-man-steals-school-bus-drives-it-all-day",
    },
    {
        "date": "2026-10-27",
        "place": "Sanibel",
        "county": "Lee",
        "emoji": "🚽",
        "headline": "Stolen SUV, smashed gate, porta-potty hideout. Pants not included.",
        "blurb": "Police say a 43-year-old man took a construction worker's SUV, drove through a gate and ended up holed up in a portable toilet, minus his pants.",
        "charge": "Multiple charges",
        "source_name": "Tampa Free Press via AOL",
        "source_url": "https://www.aol.com/news/pants-optional-porta-potty-pursuit-201945746.html",
        "story": "sanibel-man-stolen-suv-porta-potty-pants",
    },
    {
        "date": "2026-06-24",
        "place": "Thonotosassa",
        "county": "Hillsborough",
        "emoji": "🚨",
        "headline": "Fake cop tries to pull over a real cop's car.",
        "blurb": "Deputies say a man in a black Suburban flipped on emergency lights behind a vehicle on U.S. 301 to make a traffic stop. The vehicle was an undercover sheriff's car. Detectives say they found two illegal light setups and a gun.",
        "charge": "False personation, unlawful use of blue lights, firearm during a felony",
        "source_name": "WWSB / ABC7 Sarasota",
        "source_url": "https://www.mysuncoast.com/2026/06/25/man-arrested-impersonating-law-enforcement",
    },
    {
        "date": "2026-06-02",
        "place": "Ocala",
        "county": "Marion",
        "emoji": "🍸",
        "headline": "Woman calls 911 three times over a denied Jell-O shot.",
        "blurb": "Police say the bar cut her off, so she reported it to 911. Repeatedly.",
        "charge": "Charges including misuse of 911",
        "source_name": "Fox News",
        "source_url": "https://www.foxnews.com/category/us/us-regions/southeast/florida?page=13",
        "story": "florida-woman-calls-911-over-jello-shot",
    },
]
