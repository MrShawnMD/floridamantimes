# Florida Man Times — House Style

Every story is a real news event retold in our own voice. The voice is modeled on the
*spirit* of witty magazine columnists like Troy Johnson (San Diego Magazine): clever,
cheeky, conversational, but still a news story. We never copy anyone's actual lines and
never claim any outside writer wrote for us. Byline is always "Florida Man Times Desk."

## The voice
- **Open with a hook.** A bold one-liner claim or drop the reader into the scene.
  Never open with "A Florida man was arrested..."
- **Mix sentence lengths.** Short punches. Fragments are fine. Then a longer sentence that
  builds and builds before it lands the joke.
- **Absurd, specific comparisons.** Compare the situation to everyday Florida life
  (Publix subs, HOA meetings, I-4 traffic, hurricane prep, flip-flops, golf carts).
- **Mock-serious asides.** Treat the ridiculous with straight-faced gravity
  ("Experts agree: sugar is not worth a felony.").
- **Talk to the reader** ("you") and occasionally to the subject itself
  (the gator, the porta-potty, the Jell-O shot).
- **Close on a zinger** that ties back to the opening.
- 400–700 words, but only real facts. Never pad. If a story only has 3 facts, find more sources or skip it.
- Clean language: no profanity, nothing crude or sexual.

## Story structure (how it shows on the page)
- `quick`: 2–3 plain sentences with the whole story (who, what, where, what happened next). Shown at the top in a "quick take" box.
- `body`: the first 2 paragraphs are the hook and show right away; everything after sits behind a "Keep reading" button.
- After the hook, break the story up with 3–5 subheads: a paragraph that starts with "## " becomes a subhead
  (e.g. "## The heist", "## What happens next"). Keep paragraphs short (1–4 sentences).
- Add real depth: step-by-step timeline, the charges and what they mean under Florida law (penalty range, from an
  official or reliable source), local color, past similar Florida cases, and what happens next (bond, court date).
- `sources`: list of (name, url). Use 2–3 sources when possible; the first is the main one.

## The news part (non-negotiable)
- Every fact comes from the source article. Do not invent quotes, details, ages, charges,
  times or outcomes. Jokes are clearly jokes; facts are clearly facts.
- Attribute: "deputies say," "according to the arrest report," "police said."
- Paraphrase. At most ONE direct quote per story, under 15 words, in quotation marks,
  credited. Never copy the source's sentences or structure.
- Include the 5 W's somewhere in the piece: who (described), what, where (city/county),
  when, and what happens next (charges, etc.).
- Link the original source at the bottom (`source_name`, `source_url`).

## Safety rules (the scanner publishes on its own, so these are strict)
- **Any off-the-wall Florida story is fair game, whatever the topic.** That includes stories
  involving deaths, injuries, crimes of any kind or tragedy. Shawn's test is simply: is it
  bizarre, "only in Florida" news? (Shawn decided this on 2026-11-27.)
- **Don't name private people who were arrested.** Describe them ("a 43-year-old Sanibel
  man"). Officials, agencies and businesses can be named.
- **Never identify victims of sex crimes or anyone under 18** (no names, addresses or other
  identifying details). This is a legal line, not a topic limit: the story itself can still run.
- Always end arrest stories with a light presumed-innocent line.
- Tone: aim the jokes at absurd choices. When someone died or was badly hurt, don't make the
  person who suffered the punchline, and don't joke about race, poverty, illness or addiction.
- Wildlife stories: include the FWC nuisance alligator line (866-392-4286) on gator stories.
- Only use stories from established news outlets (local TV, newspapers, AP, sheriff's or
  police press releases). No forums, no social media posts as the only source.
- Must be in Florida, and recent (ideally the last 14 days).
- Never repeat a story already in `stories.py` (check slugs, titles and source URLs).

## Headlines
- Punchy, specific, SEO-friendly. Start with "Florida Man" / "Florida Woman" when it fits;
  otherwise lead with the funniest concrete detail. Under 90 characters ideally.
- `dek`: one witty line that adds a new detail, not a repeat of the headline.

## Story fields (see stories.py)
slug, title, dek, category ("Florida Man" | "Florida Woman" | "Wild Florida"), location,
date (date of the incident or report, YYYY-MM-DD), emoji, color (hex for the art tile),
quick, body (list of paragraphs, "## " for subheads), sources [(name, url), ...].
Optional: photo_credit (only for an official agency photo, see Images).

## Images
- **Real photos:** only official government photos (sheriff's office, police, FWC, city/county) of a scene, animal,
  vehicle or object, saved as images/<slug>.jpg with `photo_credit` set (e.g. "Lee County Sheriff's Office").
  NEVER use photos from news sites, AP/Getty, or private people's social posts (they're copyrighted), and NEVER use
  booking photos or photos showing an arrested person's face. If there's no official photo, use an AI illustration.
- Save as `images/<slug>.jpg` (or .png/.webp). The build picks it up automatically; no code changes.
- Wide 16:9, about 1600x900, under ~400 KB (compress before adding).
- Look: photorealistic but over the top. Cinematic lighting, vivid Florida color, the absurd
  moment exaggerated to the max, shot like a movie still. Should stop a scroller cold.
- People in images are invented, fictional characters. Never try to depict the actual person
  involved or any real, identifiable person.
- No brand logos or trademarks (no Target bullseye, no Nissan badge, no mascots), no text in the image.
- Every image is captioned on the site as an illustration automatically.

## Tonight's Weirdest Arrests (arrests.py)
Quick-hit police-blotter items, newest first. Add 3–6 per day when good ones exist.
- **No names. No mugshots. No photos of real people. Ever.** Describe ("a 45-year-old man").
- `headline`: one punchy line in the house voice. `blurb`: 1–3 sentences, facts only from the
  source, attributed ("deputies say"). `charge`: plain-English charge(s) as reported.
- Fields: date (YYYY-MM-DD of the arrest), place (city), county (no "County"), headline, blurb,
  charge, source_name, source_url, optional story (slug, if there is a full story on the site).
- Prefer Southwest Florida / Tampa Bay (Sarasota, Manatee, Charlotte, Lee, Hillsborough, Pinellas,
  Pasco, Polk), then the rest of Florida.
- Same rules as stories: any off-the-wall arrest qualifies, whatever the charge. No names of
  the arrested, never identify victims of sex crimes or minors, facts only from the source.
- Never repeat an item already in arrests.py (check source_url and headline).

## Weird Florida Events (events.py)
Oddball Florida festivals, fairs, livestock shows and competitions (frog legs, mullet toss,
swamp cabbage, skunk ape, python challenge, worm gruntin', county fairs, rodeos...).
- Only add events with a real official or reputable source link. Never guess a date: if exact
  dates aren't announced, set confirmed=False with a date_note (e.g. "Held every July; dates
  announced in May") and use the month range.
- Past events drop off automatically. When a TBA event's dates get announced, update it and set
  confirmed=True.
- Blurb: 1–3 lines in the house voice, facts from the source.

## Weird Eats (eats.py)
Places to eat strange Florida food (gator, frog legs, wild game, swamp cabbage, python...).
- status "menu" only when a recent (last ~12 months) source shows it's served now; otherwise
  "legend". Never claim a place serves something you can't source.
- Blurb: 1–3 lines in the house voice. Link the source.
- Arrest images: illustrations only, saved as images/arrests/<date>-<place-slug>.jpg
  (e.g. images/arrests/2026-06-24-thonotosassa.jpg). Same image rules as stories: invented
  people, never a mugshot or the real person. Arrests linked to a full story reuse its image.
  In the daily report, include an image prompt + file name for each new arrest.

## Automatic images (generate_images.py + GitHub Action)
Every new story, arrest and eats item gets an `image_prompt` field (one paragraph, following the
Images rules above). When it is pushed, the "Generate missing images" GitHub Action asks OpenAI
for the picture, crops it to 16:9 and publishes it. Items that already have an image file are
skipped, so a hand-made image always wins: drop a file at the right path to override.

## Artist of the Week & Crazy Rentals (features.py)
- ARTISTS: newest first; the first entry is "this week". Real, public Florida artists or art places only, with real sources. Upbeat, celebratory — never mocking. Don't publish a private home address unless the artists publish it themselves.
- RENTALS: real, bookable weird Florida stays. Link to an article or the listing; never copy listing photos.
- Images: AI illustrations only (images/artists/<slug>.jpg, images/rentals/<slug>.jpg), made automatically from image_prompt. No real faces of the artists, no logos or text.
- Mondays: the scanner may add one new artist (put it at the top) and 1–2 new rentals.

## Eff'd Up With… (interviews.py) — VIDEO interviews
- Only Shawn's team adds these. The daily bot must NEVER write, invent, or edit an interview or its quotes.
- Each episode: a YouTube link (or a small /videos/<slug>.mp4), a short write-up, and 3–6 real quotes taken from the video.
- Guests: adults, sober on camera, signed release, in on the joke. No one in crisis (addiction, homelessness, mental health) as the subject.

## The Roach Report (closures.json) — automatic, hands off
- Built every day by the GitHub Action from Florida DBPR's official weekly emergency-closure files (fetch_closures.py).
- Never edit closures.json by hand and never add jokes to the list itself. The page shows only what the state published:
  name, address, date, reason, and reopen status. A closure is not a conviction or a fine; most reopen within a day.
- A Roach Report *story* is fine (e.g. "Most roach-filled week of the year"), but stick to the state record and say they reopened.

## Spooky & Odd Places (places.py → /odd-places/)
Creepy, haunted and just-plain-strange real places you can visit in Florida (haunted dolls, gravity hills,
psychic towns, cryptid HQs, folk-art castles, weird cemeteries, odd ruins).
- **Spooky and odd only.** Never feature a real tragedy as the attraction: no sites built around deaths,
  massacres, prisons or reform schools, crashes, shipwrecks or disasters with victims, and no ghost legends
  about real children who died. Legends are fine when they're the place's own well-known lore.
- Real, visitable places only, each with a reputable source (official site, state/national park, local
  news, Atlas Obscura, Visit Florida). Never invent hours, prices, addresses or legends. If a place has
  closed or was destroyed, don't add it.
- Fields: slug, name, city, kind ("Haunted" | "Mystery" | "Cryptid" | "Strange"), emoji, blurb (2–3 lines,
  house voice, facts from the source), visit (one practical line, no made-up hours), source_name,
  source_url, image_prompt. New places go at the TOP.
- Images: AI illustrations at images/places/<slug>.jpg, made automatically from image_prompt. No real
  people's faces, no logos, no readable text.
- Never repeat a place already in places.py.
- Mondays: the scanner may add 1–2 new places.

## Where to Eat This Week (weekly story, Fridays)
A weekly statewide story built from the state's own inspection data: who got shut down, and a couple of
spotless places worth a visit. Title format (keep the brand name every week): "Roaches' Choice: Where Florida's Bugs Ate This Week (and Where You Should Instead)" — you may swap the part after the colon for a fresh pun that week, but always start with "Roaches' Choice:". It's a normal story in stories.py (category "Wild Florida", slug
where-to-eat-florida-week-of-<YYYY-MM-DD of the DBPR week>).
- "Don't eat" half: use only closures.json (DBPR emergency closures) for the latest week. Name the
  restaurant, city and the state's stated reason, nothing more. Jokes go at the bugs, never at the owners
  or workers. Always say a closure is a one-day snapshot, not a conviction, and say whether they reopened.
  Never add details the state record doesn't show.
- "Do eat" half: 2–3 places from the Clean Plate Club data (roach-report/clean.json, zero violations),
  favoring independent local spots over chains, spread around the state. Name 1–2 real dishes only if
  the restaurant's own site, menu or a reputable outlet lists them, and link that source.
- Photos: NEVER copy food photos from restaurant websites, menus, Google, Yelp or delivery apps (they're
  copyrighted). Use the AI image_prompt only. A restaurant's real photo can be used only if Shawn says
  the restaurant gave written permission; then save it as images/<slug>.jpg with photo_credit set.
- Point readers to the Roach Report and Clean Plate Club at the end.

## Across America (the other 49 states)

Florida is the core of the site. The homepage lead story is ALWAYS a Florida story (the build enforces this). National stories live in their own "🇺🇸 Meanwhile, Not in Florida" row and the /section/across-america/ page.

- Source: scan/national.txt (numbered; links + summaries in scan/national.json). Same safety rules as Florida stories: real, reputable sources, funny because of an absurd choice, nobody badly hurt, no sexual crimes, no crimes against kids, presumed-innocent line on arrests, no names of private people who were arrested.
- Headline style mirrors ours, with the state: "Minnesota Man …", "New York Woman …", "Ohio Couple …". Keep the house voice; a light running joke that Florida finally has competition is fine, but don't overdo it.
- Fields: same as any story, plus "state": "<Full state name>" (e.g. "Minnesota"), "category": "Across America", "location": "<City>, <State>". Never set state to "Florida" for these.
- Volume: morning run 2 national stories, afternoon run 1 (only if genuinely good). Florida stories always come first in effort and count.
