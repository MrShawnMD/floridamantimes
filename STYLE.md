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
- 250–450 words. Clean language: no profanity, nothing crude or sexual.

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
- **Don't name private people who were arrested.** Describe them ("a 43-year-old Sanibel
  man"). Officials, agencies and businesses can be named.
- Always end arrest stories with a light presumed-innocent line.
- **Skip** any story involving: a death or serious injury, sexual crimes or nudity-as-the-joke,
  children as victims, abuse, mental health crises, suicide, hate crimes, or anyone under 18.
  We mock absurd choices, never suffering, race, poverty, illness or addiction.
- Wildlife stories: no animal cruelty as a punchline. Include the FWC nuisance alligator
  line (866-392-4286) on gator stories.
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
body (list of paragraphs), source_name, source_url.

## Images
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
- Same safety rules as stories, strictly: skip violence with injuries, weapons fired, sex crimes,
  anything involving kids, abuse, DUI crashes with injuries, addiction/overdoses, mental-health
  crises, homelessness, and deaths. Weird and harmless only: absurd choices, odd thefts, silly
  getaways, bizarre excuses, animals behaving badly.
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
