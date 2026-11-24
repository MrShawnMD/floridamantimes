"""Florida Man Times Gives Back — charity events.

Edit freely. Anything marked TBA shows as "Announcing soon" on the site.
"""

LEMONADE = {
    "slug": "lemonade",
    "name": "LEMONADE",
    "kicker": "Florida Man Times Gives Back presents",
    "tagline": "When life hands you a lemon, race it for charity.",
    "date": "TBA",
    "venue": "A Florida dragstrip (announcing soon)",
    "beneficiary": "Local Florida charities (announcing soon)",
    "contact_email": "",  # set this to turn on the "Become a sponsor" button
    "hero_image": "/images/lemonade-hero.jpg",
    "image_prompt": "Ultra-realistic wide action photo at a Florida drag strip at golden hour: two hilariously beat-up cheap old sedans painted bright lemon yellow and covered in sponsor-style decorations race side by side off the starting line, one trailing a puff of smoke, a bumper held on with zip ties, a giant cartoon lemon mascot cheering in the stands, families waving, palm trees behind the grandstand. Fun, over the top, charity-event energy.",
    "intro": [
        "Every Florida driver has owned one. The car that rattles at 40 mph, leaks something mysterious and has a check-engine light that's basically decoration. A lemon.",
        "LEMONADE puts those cars to work. Local businesses sponsor a $500–$1,500 beater, turn it into a rolling billboard, put a driver behind the wheel and line it up at a real Florida dragstrip. Nobody is setting records. Everybody is raising money for local charities.",
    ],
    "how": [
        ("Buy a lemon", "Each team gets a car that costs $500 to $1,500. That's the whole engine budget, forever. Receipts required. No secret turbos."),
        ("Make it ridiculous", "Decorate it yourself or hire a local wrap shop, artist or school art club. Wraps, paint, costumes, giant fake lemons on the roof. The weirder, the better."),
        ("Pass tech", "Every car must pass the track's safety inspection: working brakes, seat belt, no leaks, a helmeted driver. Lemons are welcome; danger isn't."),
        ("Race for good", "Teams run head-to-head down the strip in a bracket-style format, so the slowest car can still win. Every dollar raised goes to the event's charities."),
    ],
    "tiers": [
        {
            "name": "The Squeeze",
            "price": "$2,500",
            "perks": ["One team entry with a $500–$1,500 lemon", "Your logo on your car and the event page",
                      "Team intro on the track PA", "Social media shout-out"],
        },
        {
            "name": "The Zest",
            "price": "$5,000",
            "perks": ["Everything in The Squeeze", "Featured story about your team on Florida Man Times",
                      "Logo on the event banner and T-shirts", "10 pit passes for your crew and customers"],
        },
        {
            "name": "Fresh-Squeezed",
            "price": "$10,000",
            "featured": True,
            "perks": ["Everything in The Zest", "Named award (e.g. \"Most Likely to Fall Apart, presented by You\")",
                      "On-site booth or display", "Video spotlight of your car build"],
        },
        {
            "name": "Grand Lemonade",
            "price": "$25,000",
            "perks": ["Title sponsor: \"LEMONADE presented by You\"", "Two team entries",
                      "Top logo placement everywhere: car, banner, shirts, site", "Hands the winning trophy at the finish line"],
        },
    ],
    "awards": [
        ("🏆", "The Golden Lemon", "Bracket race champion."),
        ("🐢", "The Sour Puss", "Slowest run of the day. Proudly."),
        ("🎨", "Best in Squeeze", "Best decorated car, judged by the crowd."),
        ("🔧", "Most Likely to Fall Apart", "Held together by hope and zip ties."),
        ("🍋", "People's Choice", "Fans vote with Lemon Bucks: $1 = 1 vote, all to charity."),
        ("💨", "The Smoke Show", "Most dramatic launch that goes almost nowhere."),
    ],
    "extras": [
        ("Lemon Parade", "Every car does a slow parade lap before racing so fans can see the builds up close."),
        ("Pit Crew Squeeze", "Teams race to change a tire on their lemon. Fastest crew wins bragging rights."),
        ("Kids' Lemonade Stand Challenge", "Local school and youth teams run lemonade stands at the track; the stand that raises the most wins a trophy for their school."),
        ("Lemon Bucks", "Fans buy Lemon Bucks to vote for People's Choice and cheer on their favorite car. Every dollar goes to charity."),
        ("The Lemon Auction", "At the end of the day, the most famous lemons can be auctioned off as legendary local relics."),
    ],
}
