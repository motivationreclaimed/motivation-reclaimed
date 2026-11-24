# Motivation Reclaimed — content engine & posting playbook

Faceless motivation channel. Instagram / TikTok / YouTube Shorts, all posted through Publer via the Zapier connector.
Business email: mr@pixevon.com. Handles: @motivationreclaimed (IG, TikTok), @motivation_reclaimed (YouTube).

## THE ONLY STYLE: SKETCH + THE BEAR CUB (owner, 23–24 Nov 2026 — "only make videos like this")
Every video, from now on, is made in the SKETCH style with `make_sketch.py` + `engine_sketch/`. The old styles
(TOON3D, GOLD3D, STICK2D, make.py, make3d.py) are RETIRED — never use them again. Approved examples: `specs/031`–`040`.
- **Look (copy exactly):** pure black background. Everything is drawn in scratchy, hand-drawn white lines (several jittered
  passes per line, 10 fps "line boil" — built into `Sk`). Bodies are filled solid black with a white sketched outline.
  A hand-drawn ground line. NO scenery, NO gradients, NO colour, NO glow — minimal like the owner's reference video.
- **The character = THE BEAR CUB** (owner, 24 Nov 2026 — replaced the wolf, whose face "looked like the devil"; never
  draw the wolf again). Black bear cub, round ears, round head, big friendly white eyes, white muzzle with a small
  black nose and a small mouth, simple long body. Soft and kind — no spikes, no sharp angles, no angry brows.
  Drawn only via `bear_front(...)` (close-ups and medium shots, expressions `"sad" "tired" "neutral" "hopeful" "happy"`,
  `look=(x,y)` eye direction, `blink`) and `bear_side(...)` (rigged side view: `walk(phase,amp)`, `run(phase)`, `STAND`,
  `KNEEL`, `FLOOR_SIT`, `ARMS_UP`, blend with `mix(a,b,k)`, `facing=-1` to turn round, lift him with a smaller `gy` to
  jump). (`wolf_front`/`wolf_side` in older specs are aliases that now draw the bear.) Never invent another hero.
  Other figures are optional and rare (simple sketched outlines). If a story needs a pose that doesn't exist, change the story.
- **Filmmaking (like the reference):** hard CUTS between WIDE (tiny wolf on a long line), MEDIUM (wolf ~520 px tall) and
  CLOSE-UP (`bear_front(S, W/2, 2500, 1900, expr, look)` — face fills the frame, text above his ears). Something
  happens every 1–2 s. Use small sketched props from `engine_sketch.sketch`: `cloud` (rain), `sun`, `moon`, `star`,
  `plant` (sprout → tree with flowers), `flower`, `stairs`, `block`, `wall`, `sign` (signpost with a word), `counter`.
- **Text:** ONLY Amatic SC Bold (`assets/fonts/`, OFL) via `S.text(y, [lines], size)`, ALL CAPS, white, big
  (120–190 px), placed in the top band (y ≈ 220–520). One to four short words per card ("A BAD DAY", "NOT YET?",
  "TRY 2", "DAY 17"). Final card = the message, 2 short lines max ("BUILD IT" / "AGAIN."). Never put text over his face.
  Avoid characters the font lacks (no arrows/emoji).
- **Watermark:** "MOTIVATION RECLAIMED" is added automatically by `S.out()` (y≈1415, black edge) — never remove it.
  No on-screen CTA band in this style (the CTA goes in the caption).
- **Music (owner, 22–23 Nov): MUSIC ON.** Every short uses the owner's track `assets/music/owner/main_track.mp3`
  FROM 0:00 (never a random slice), mixed by `make_sketch.py` (volume 0.55, 0.5 s fade-out). No other music, never
  vidIQ or any generator. Don't promote music on screen (content rule below).
- **Length:** DUR 9.6 s (8–10 s allowed). Frame 0 must already show something + a text card (it's the thumbnail; no fade-in).

## CONTENT DIRECTION — UPLIFTING, NOT COMPARISON (owner, 22 Nov 2026)
The channel now makes people feel better. Each video = one warm, true message for someone having a hard time, told as
a tiny story of the bear: a setback / doubt → a small turn → hope. Examples already made: a bad day is not a bad life;
everything happens at the right time; small steps still count; rest is not quitting; build it again; you're not behind;
find one good thing; keep going even when nobody sees it; fall, get up, try again; look how far you've come.
More ideas live in `ideas.md` (use top first, remove once used, add new ones in the same spirit).
- NO "X vs Y" comparisons, lanes, races against others, "which one are you". NO money videos for now.
- Calm, kind, hopeful. Every story ends on the bear feeling better (smile, arms up, walking on).
- Never repeat a message, hook card or final line already in specs/ (check the last ~20).
- **NEVER promote or favour gambling, drinking or music (owner — absolute rule).** No betting, alcohol, pubs, music apps,
  headphones, instruments, playlists — in any frame, caption or hashtag.
- **Off-limits:** "alpha/sigma", manosphere, dating advice, anything that puts down any group. UK + US English.

## Making a video
1. Read `posted.md` and the last ~10 specs; pick the next idea from `ideas.md`.
2. Copy the closest spec from `specs/031`–`040` to `specs/NNN_slug.py`; write a NEW little story (3–5 shots, cuts
   wide/medium/close). A spec defines `DUR`, `CAPTION`, `frame(t)` → `S.out()`.
3. Preview once: `python3 make_sketch.py specs/NNN_slug.py --stills 1 3 5 6.8 8.8` → LOOK at
   `previews/NNN_slug_stills.png`: text readable and not over his face/ears, bear fully in frame, feet on the ground
   line / steps, nothing floating or passing through props, story readable without sound. Fix once if needed.
4. Render: `python3 make_sketch.py specs/NNN_slug.py` → `videos/NNN_slug.mp4` (~20 s). Then the QUALITY GATE.
5. Variety self-check every run: different message, props, shot order, hook card and ending from the last ~10.
   Put one line "Variety check: …" in the run report.

## QUALITY GATE — no bugged video is ever posted (owner requirement)
After rendering, run `python3 tools/qa.py videos/NNN_slug.mp4` and LOOK at every frame of `previews/NNN_slug_qa.png`.
(In this style blackdetect warnings on WIDE shots are expected — the frame is mostly black with thin lines; only fail
if a frame is truly empty.) Post only if: 1080×1920, 8–10 s; bear visible and readable in every shot; no text over
his face; all text fully on screen and readable; no limb through props/walls, feet on the ground; poses change smoothly
(no sudden wrong pose); props behave logically; content rule respected. Max 2 fix rounds; otherwise drop the concept and
make a simpler one by copying a proven spec (031–040). One line per video in the report: "QA: passed (checked N frames)".

## Captions (SEO, VARIED, human — avoids "inauthentic/repetitive content" flags)
There is NO fixed template. Every caption must read differently from the last ~10 in posted.md captions (see specs/).
- **First line = the title.** Unique, under 90 characters, contains a keyword (motivation, discipline, mindset, habits, self improvement, consistency…). YouTube uses it as the Short's title. Never reuse a title pattern twice in a row (e.g. not "Same X. Three people." again). Work the keyword into the sentence naturally — never tack it on in brackets like "... (discipline)" (21 Nov run did this on all 7; looks templated).
- **Body:** 1–3 short lines. Vary the structure: sometimes a reflection, sometimes one blunt sentence, sometimes a question, sometimes a tiny story. Sometimes no body at all.
- **Voice:** roughly half the captions in a quiet first-person voice — a man rebuilding himself, speaking plainly, like a note to himself. Examples of the RIGHT tone:
  - "Didn't feel like it today. Did it anyway. That's the whole secret."
  - "I used to wait for motivation. Now I just start and let it catch up."
  - "Nobody claps for the boring days. They're the ones that count."
  The rest: direct second person ("You don't need a new year. You need a Tuesday.").
  BANNED (cringe/hype): "grindset", "alpha", "king", "sigma", "hustle harder", "no days off", "rise and grind", ALL-CAPS shouting, emoji spam, "Day X of my journey" on every post, fake life details (jobs, family, money, illnesses), invented quotes from real people.
- **Sign-off:** optional and rotating — "Follow for more.", "Save this for tomorrow.", "Send this to someone who needs it.", or none. Never the same sign-off twice in a row.
- **Emojis:** 0–2, varied. 🏺 occasionally, not every time.
- **Hashtags:** 3–5, rotated. Always 1–2 core (#motivation #discipline #mindset) + 2–3 from the pool, matched to the concept:
  #selfimprovement #motivationalvideo #consistency #habits #selfdiscipline #growthmindset #nevergiveup #mentalstrength #personalgrowth #dailymotivation #success #comeback #healing #patience #progress #animation #mentalhealth #positivity #hope #youvegotthis
- Save the caption as `CAPTION` in the spec (so future runs can check for repetition).

## Posting (Zapier → Publer)
1. `git add` the spec + video, commit, `git -c push.negotiate=true push`. Public URL (use the jsDelivr CDN — Publer often fails to fetch raw.githubusercontent.com, 21 Nov 2026). PIN THE COMMIT (`git rev-parse HEAD`), because `@main` is cached for hours and can serve an OLD file with the same name:
   `https://cdn.jsdelivr.net/gh/motivationreclaimed/motivation-reclaimed@<commit-sha>/videos/<file>.mp4`
2. Publer `upload_media` (selected_api `App232404CLIAPI`, workspace_id, upload_type `url`, `file_urls` = [ALL of this run's CDN URLs in one call]) → one media id per file. If the result says "not a publicly accessible media", wait ~1 minute and retry ONCE with the same CDN URL, then once with `https://raw.githubusercontent.com/motivationreclaimed/motivation-reclaimed/main/videos/<file>.mp4`. Only if all fail, log it PENDING (the catch-up task retries).
3. Publer `create_post` with `state: "scheduled"`, `scheduled_at` (ISO, UTC), `media_ids`, `text` = CAPTION.
   - Workspace: `6af6583ee39d7f4bffa1aa3e` (Motivation Reclaimed). Zapier connection: mr@pixevon.com.
   - Accounts (ALL THREE every time): `6af658d73a8f484368c1cf7e` (Instagram), `6af65b2b1fc93c847bca0e16` (TikTok), `6af65afdd185a8df145dea8a` (YouTube).
   - NEVER use the abyanhammad@gmail.com / Unbreachd Studios connection — that is a different brand.
   - If a call times out, do NOT retry blindly (it may have gone through) — note it in the report instead.
   - **Auto first comment (engagement):** in create_post also set `auto_comment_enabled: true` and `auto_comment_text: ["<one short, genuine question tied to the video that's easy to answer, e.g. 'What's the one habit you're rebuilding this month?'>"]`. Vary it every time. If create_post fails because of this option (plan limit / parameter error), immediately retry the SAME call once without the auto-comment fields (failed calls cost no Zapier tasks) and note it in posted.md so future runs skip it.
4. Append a line to `posted.md`: `NNN | slug | FORMAT | scheduled_at | concept one-liner`. Commit + push.

## Schedule (date-based — check today's date first) — POST EVERY DAY, NEVER SKIP A DAY (owner, 24 Nov 2026)
Zapier trial ends ~27 Nov 2026, then Zapier FREE (100 tasks/month; every successful call = 2 tasks).
- **Until 26 Nov 2026 (trial):** 2 posts/day at 12:00 and 21:00 UK.
- **From 27 Nov 2026:** ONE post EVERY day at 21:00 UK (Mon–Sun, no gaps), all three platforms.
  - Monday run: 4 videos → Mon, Tue, Wed, Thu 21:00.  Thursday run: 3 videos → Fri, Sat, Sun 21:00.
  - Always fill the next empty days after the last scheduled post (posted.md); never leave a day empty, never double a day.
- **Budget trick (keeps daily posting on the free plan):** upload ALL of a run's videos in ONE `upload_media` call
  (`file_urls` = list of every CDN URL; it returns one media id per file, in order), then one `create_post` per video.
  ≈ 9 uploads + 30 posts = 39 calls ≈ 78 tasks/month + 4 for analytics ≈ 82 < 100.
- Never schedule into the past. Publer free allows max 10 pending posts per account.

## Compilations — **PAUSED by owner: do NOT make, schedule or post any compilation (tall or wide) until this line says ACTIVE.** Owner found the format boring; it is being redesigned. Ignore the rules below until then. `compile.py`
Track progress in `compilations.md` (create if missing): lines `TALL | up to NNN | date` and `WIDE | up to NNN | date`.
- **TALL (~3 min, 9:16, all three platforms)** — when ≥ 18 shorts have been posted since the last TALL (≈3 min of video), make ONE of this run's slots a tall compilation of those shorts (it counts as one of the run's posts). Long enough for TikTok Creator Rewards (>1 min).
- **WIDE (~10 min, 16:9, YouTube ONLY — account `6af65afdd185a8df145dea8a`)** — when ≥ 60 shorts have been posted since the last WIDE, make ONE slot a wide compilation of those shorts.
- How: old video files may already be deleted, so re-render the needed shorts from their specs into a temp folder (`python3 make.py specs/NNN_x.py` then move the file out of videos/ — do NOT commit these re-renders), then
  `python3 compile.py tall "<N> Lessons on <theme>" videos/cNNN_tall.mp4 <clips…>` or `python3 compile.py wide "<N> Lessons on <theme>" videos/cNNN_wide.mp4 <clips…>`.
  Wide also writes `<name>_chapters.txt` — put those chapter lines in the YouTube caption (description) after the first line.
- File must be under 95 MB (GitHub raw limit). If larger, re-encode with a lower `-maxrate` before pushing.
- Caption: first line is the title (e.g. "10 Minutes of Discipline Lessons | Motivation Reclaimed"), a short description, chapters (wide), and ALWAYS the service line: "Want animations like these for your brand or channel? Email mr@pixevon.com". Then 3–5 hashtags.
- Log in posted.md with FORMAT `COMPILATION TALL` / `COMPILATION WIDE`, then update compilations.md. Commit + push.

## Animation service mention (owner rule — the owner sells custom animations)
- About **1 in 5** captions end with one low-key line before the hashtags, varied, e.g. "Animation by Pixevon — mr@pixevon.com" / "We animate for brands too: mr@pixevon.com". Subtle, never an advert, never two in a row; log `SERVICE` in the posted.md concept line. (Nothing extra on screen.)

## Monthly analytics check (separate scheduled task, 1st of each month)
Uses exactly 2 Zapier calls (4 tasks) — nothing else:
1. Publer `generate_top_posts` (selected_api `App232404CLIAPI`, workspace `6af6583ee39d7f4bffa1aa3e`, date_from/date_to = last month, sort_by `engagement_rate`).
2. Publer `find_analytics` (tool `publer_find_analytics_by_date_range`, same workspace, from/to = last month, chart_ids `["followers","video_views","engagement_rate"]`).
Then write `insights.md` (overwrite): followers and views trend, top 5 and bottom 5 posts matched to their FORMAT/series/topic via posted.md, and 3–5 plain rules for next month ("more STORY comebacks", "fewer TRIO", "phone/screen-time topics win"). Commit + push.
**Video runs: read `insights.md` first (if present) and lean towards what it says works**, while still obeying the VARIETY rules.

## Zapier budget rules (important on the free plan)
- Do NOT call inspect / discover / list / read actions on Zapier during normal runs — every successful call burns 2 tasks. All IDs needed are in this file.
- Only call `upload_media` (ONE batched call per run) and `create_post` (one per video). Use inspect only if one of those calls fails with a parameter error.
- If Zapier reports the task limit is reached: stop posting, keep the rendered videos committed in the repo, log them in posted.md as `NOT SCHEDULED (zapier limit)`, and say so clearly in the final report so the owner can post them manually or upgrade.

## If Zapier / Publer is unavailable (connector down, outage, 5xx errors)
- Still make and render all the videos, commit + push them, and log each in posted.md as
  `NNN | slug | FORMAT | PENDING (zapier unavailable) | planned_slot | concept` (planned_slot = the ISO time it should have gone out).
- Say so clearly in the run report. Do not burn retries in a loop — the separate **catch-up / retry task** (Mon & Thu 15:17 and 20:17 UK, 5 h after the main run; it also does the full run if the main run failed) will post them.
- Retry task behaviour: if posted.md has NO `PENDING` lines → stop immediately, do nothing else. Otherwise, for each PENDING video:
  upload_media + create_post as normal; if its planned slot is already in the past, schedule it at the next free 12:00/21:00 slot (21:00 only on the free plan)
  after the last scheduled post (never in the past); replace PENDING with the real scheduled_at; commit + push.
  If Zapier is still down, leave them PENDING for the next retry.

## Housekeeping (keeps the free GitHub repo small)
- Publer copies each video when `upload_media` runs, so old video files are no longer needed.
- At the start of every run, `git rm` any `videos/*.mp4` whose post is scheduled more than 7 days in the past (per posted.md). Keep specs and logs.

## Keeping credits low
- One preview sheet per video (plus at most one re-check after a fix), one render. No extra re-renders unless something is visibly broken.
- Reuse/extend engine helpers instead of writing new drawing code per video.
