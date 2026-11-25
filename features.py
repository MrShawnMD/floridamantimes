"""Artist of the Week + Crazy Florida Rentals.

ARTISTS: newest first. The first entry is "this week's" artist; the rest become the archive.
RENTALS: weird places to stay in Florida. We link to the source article; we don't copy listing photos.
Images (auto-generated from image_prompt, always captioned as illustrations):
  images/artists/<slug>.jpg   images/rentals/<slug>.jpg
"""

ARTISTS = [
    {
        "slug": "whimzeyland",
        "week_of": "2026-11-24",
        "name": "Todd Ramquist & Kiaralinda",
        "nickname": "The Whimzey Twinz",
        "city": "Safety Harbor",
        "medium": "Folk art, mosaics, recycled sculpture and a LOT of bowling balls",
        "headline": "The Couple Who Turned a Beige Bungalow Into Florida's Bowling Ball Kingdom",
        "body": [
            "Most people redecorate with a new couch. Todd Ramquist and Kiaralinda redecorated with roughly 800 bowling balls.",
            "Their Safety Harbor home, Whimzeyland, started in 1985 as a plain beige house near Tampa. Then came a flea market sign offering free bowling balls, and the two artists called every friend they had to come haul them home. The yard has never been the same.",
            "Today the property is an explosion of mosaic pathways, cobalt bottle trees, wire sculptures and painted bowling balls stacked into pyramids and walls. More than 80 artists have painted a bowling ball for the collection, which now has its own gallery. Neighbors say drivers slow to a crawl just to stare.",
            "It's been featured on HGTV and MTV, and it's still their actual home. So be cool, Florida.",
        ],
        "visit": "1206 Third Street, Safety Harbor. Yard visits and guided tours are offered; check their schedule before you go, and remember it's a private home.",
        "links": [
            ("WUSF", "https://www.wusf.org/post/art-populi-whimzeyland-will-bowl-you-over"),
            ("Atlas Obscura", "https://atlasobscura.com/places/whimzeyland"),
            ("Orlando Weekly", "https://www.orlandoweekly.com/arts/20-wild-and-wonderful-bits-of-folk-art-to-see-at-safety-harbors-whimzeyland-home-30944119/"),
        ],
        "emoji": "🎳",
        "image_prompt": "Ultra-realistic wide photo of a whimsical Florida folk-art yard on a sunny day: hundreds of brightly painted bowling balls stacked into pyramids and walls, rainbow mosaic tile pathways, cobalt-blue bottle trees, colorful wire sculptures and palm trees around a small bungalow covered in art. No people, no readable text, no logos.",
    },
]

RENTALS = [
    {
        "slug": "area-1609-ufo",
        "name": "Area 1609: Sleep Inside a UFO",
        "city": "Lake Placid",
        "emoji": "🛸",
        "blurb": "A flying saucer parked among the palms and Spanish moss. Round porthole windows, spaceship vibes, zero abductions (reportedly). Tell your neighbors you spent the weekend in orbit.",
        "source_name": "Family Destinations Guide",
        "source_url": "https://familydestinationsguide.com/wonderfully-weird-airbnb-florida/",
        "image_prompt": "Ultra-realistic photo of a shiny silver flying-saucer-shaped tiny vacation rental with round porthole windows, sitting among palm trees and Spanish moss in rural Florida at dusk, warm light glowing from the portholes. No people, no readable text, no logos.",
    },
    {
        "slug": "chinook-helicopter",
        "name": "The Converted Chinook Helicopter",
        "city": "Brooksville",
        "emoji": "🚁",
        "blurb": "A real CH-47D Chinook military helicopter turned into a tiny home, complete with a full kitchen and air conditioning. Aviation nerds, this is your Ritz-Carlton.",
        "source_name": "TravelAwaits",
        "source_url": "https://www.travelawaits.com/3017808/cool-airbnbs-in-florida-for-all-types-of-travelers/",
        "image_prompt": "Ultra-realistic photo of a retired twin-rotor military transport helicopter converted into a cozy tiny-home vacation rental, parked on a grassy Florida lot under oak trees, string lights, a small porch with chairs at the rear ramp, golden hour. No people, no readable text, no logos.",
    },
    {
        "slug": "skoolie-vero-beach",
        "name": "Skoolie in the Trees",
        "city": "Vero Beach",
        "emoji": "🚌",
        "blurb": "An old-school school bus converted into a getaway, parked under thick tree cover. It has a stove and a private bedroom. The shower is outside, because of course it is.",
        "source_name": "TravelAwaits",
        "source_url": "https://www.travelawaits.com/3017808/cool-airbnbs-in-florida-for-all-types-of-travelers/",
        "image_prompt": "Ultra-realistic photo of a converted vintage school bus tiny-home rental painted in soft colors, parked under a lush green Florida tree canopy, string lights and an outdoor shower enclosure beside it, dappled sunlight. No people, no readable text, no logos.",
    },
    {
        "slug": "casa-loco",
        "name": "Casa Loco",
        "city": "Safety Harbor",
        "emoji": "🌀",
        "blurb": "A two-bedroom kaleidoscope of novelty art from the same artists behind Whimzeyland, our Artist of the Week. It sits right across the street from the bowling ball house.",
        "source_name": "Only In Your State",
        "source_url": "https://www.onlyinyourstate.com/florida/exceptional-airbnbs-fl",
        "image_prompt": "Ultra-realistic photo of a small Florida cottage vacation rental painted in wild psychedelic colors, covered in mosaics, folk art and quirky sculptures, tropical garden in front, bright sunny day. No people, no readable text, no logos.",
    },
    {
        "slug": "star-wars-winter-haven",
        "name": "The Galaxy-Far-Far-Away Apartment",
        "city": "Winter Haven",
        "emoji": "🌌",
        "blurb": "A space-saga-themed rental covered wall to wall in posters, artwork and memorabilia, listed at about $114 a night. May the deposit be returned to you.",
        "source_name": "FinanceBuzz",
        "source_url": "https://financebuzz.com/affordable-florida-airbnbs",
        "image_prompt": "Ultra-realistic interior photo of a small apartment themed like a retro sci-fi spaceship: starfield wallpaper, glowing control-panel style decor, model rockets and generic space memorabilia on the walls, blue and red accent lighting. No real characters, no logos, no readable text.",
    },
    {
        "slug": "caja-verde-container",
        "name": "Caja Verde: The Shipping Container",
        "city": "Gainesville",
        "emoji": "📦",
        "blurb": "A shipping container tucked into a two-acre garden about a mile from UF and downtown. Your stay, delivered in one standard freight unit.",
        "source_name": "Time Out",
        "source_url": "https://www.timeout.com/florida/hotels/the-best-airbnbs-in-florida",
        "image_prompt": "Ultra-realistic photo of a green shipping container converted into a stylish tiny-home rental with large windows and a wooden deck, surrounded by a lush two-acre tropical garden in North Florida, morning light. No people, no readable text, no logos.",
    },
    {
        "slug": "st-cloud-treehouse",
        "name": "The Treehouse",
        "city": "Saint Cloud",
        "emoji": "🌳",
        "blurb": "A tiny treehouse with a wraparound porch, floor-to-ceiling windows and big branches crossing right outside. Your inner 10-year-old just packed a bag.",
        "source_name": "TravelAwaits",
        "source_url": "https://www.travelawaits.com/3017808/cool-airbnbs-in-florida-for-all-types-of-travelers/",
        "image_prompt": "Ultra-realistic photo of a charming tiny treehouse with a wraparound porch and floor-to-ceiling windows built among the thick branches of a giant Florida oak draped in Spanish moss, warm evening light. No people, no readable text, no logos.",
    },
]
