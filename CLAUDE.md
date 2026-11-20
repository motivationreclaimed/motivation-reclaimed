# Motivation Reclaimed — content engine & posting playbook

Faceless motivation channel. Instagram / TikTok / YouTube Shorts, all posted through Publer via the Zapier connector.
Business email: mr@pixevon.com. Handles: @motivationreclaimed (IG, TikTok), @motivation_reclaimed (YouTube).

## STYLES — RANDOMISE between three (owner, 15 Nov 2026)
Every new video uses ONE of these three styles, picked at random (roughly a third each); never the same style 3 times in a row. Record it in posted.md as the first word of FORMAT (e.g. `TOON3D · CLIMB`, `GOLD3D · RACE`, `STICK2D · SPLIT 2`).
- **TOON3D — the dark 3D gold world with the cartoon cast** (owner: "perfect"). Black background, black/dark sets, moving camera, reflections, gold glow — but the people are cartoon characters drawn with `draw_toon()` (engine3d/r3d.py): hero look `"hero"` (charcoal hoodie, gold crack, gold light behind him), others `"grey"`, `"teal"`, `"coral"`, `"mustard"` (with `prop="phone"` for scrollers, `bright=0.85`). Templates: `templates/toon3d_stairs.py` (cleanest) and `templates/toon3d_race.py`. Cartoon poses available (engine3d/toon.py): `STAND, walk(phase, amp), run(phase), PHONE, SIT, SIT_SAD, ARMS_UP, HOLD, WAVE`. If a story needs anything else (squats, lifting, pull-ups, climbing a ladder, lying down…) use GOLD3D or STICK2D for that video instead — never force a pose that doesn't exist.
- **GOLD3D — the dark 3D gold world with the ivory mannequin figures** (the section below). Ready examples: specs/010–012.
- **STICK2D — the original white stick-figure panels** (`python3 make.py specs/NNN_slug.py`, see "STICK2D details" below; examples specs/002–009).
Rotate topics (money/discipline), formats and CTAs as before, independently of the style.

## 3D "GOLD LIGHT" world (used by TOON3D and GOLD3D)
- A dark matte 3D world (reflective floor, fog, distant light strips), a camera that MOVES (push-in, follow, fly-through, slow orbit at the end).
- The HERO is the ivory figure with glowing gold kintsugi cracks — the only warm light source; he lights the floor and the people near him. Everyone else = matte grey 3D figures (often on their phones: blue screen glow).
- Each video is a small story with stakes, like the reference channels the owner loves: a race, a climb, a gym that empties, a wall, a split timeline… Something must happen every 1–2 s.
- Tools of the style (use most of them every video): one short HOOK line in the first second (≤ 5 words, e.g. "SAME 24 HOURS.", "EVERYONE WANTS THE TOP."), floating labels over figures, little speech TAGS ("let's go.", "maybe monday."), counters (DAY / REPS / STEPS), a SPEED-UP section (×4, motion blur, counter racing) to show time passing, and the gold PAYOFF (burst, sparks, orbit, one short closing line like "ONE STEP A DAY.").
- Text is Liberation Serif, letter-spaced caps (built into the helpers). Calm tone, no shouting.
- (STICK2D keeps its own original rules — see "STICK2D details".)
- **Ready to post (rendered, committed):** `specs/010_which_lane.py`, `011_one_step_a_day.py`, `012_still_here.py` (all GOLD3D) with their videos. The next run includes these three as 3 of its videos but **spreads them out, randomised with the new TOON3D and STICK2D videos it makes** (never two GOLD3D in a row; e.g. TOON3D, GOLD3D, STICK2D, GOLD3D, TOON3D, STICK2D, GOLD3D). Run them through the QUALITY GATE too.

## Brand rules (never break)
- Times New Roman–style serif (Liberation Serif) for all text — never mono/sans.
- The HERO always carries the glowing gold kintsugi cracks.
- Only ONE short hook line (≤ 5 words) at the start + labels/tags/counters. No long titles or paragraphs on screen.
- **Every video has an on-screen CTA** (owner's rule): set `CTA = "..."` in the spec. `chrome(d, t, CTA, PAYOFF)` draws it for the WHOLE video in ALL CAPS letter-spaced serif at y≈335 (top band, under the app's top UI) plus the watermark at y≈1440. Keep all important action and text between y 300 and 1400 (TikTok/Reels/Shorts UI covers the rest) — hook/counter text sits at y≈520. Keep it ≤ 8 words, calm tone.
  Rotate CTA types and never repeat the exact wording of the last ~10 videos: comment a word ("Comment 'reclaim' if this is you."), comment an answer ("Which one are you? Comment below."), save ("Save this for the hard days."), share ("Send this to someone who needs it."), small commitment ("Comment 'day 1' and start today."). Match it to the concept.
- **Retention (owner, 16 Nov — beats "view jail"):** (1) **NO FADE-IN of any kind (owner, 16 Nov)** — the first frame is the thumbnail, so frame 0 is the full scene with the HOOK line at full opacity (no fade from black, no text fade-in, no black/empty first frame). A short fade-OUT (last 0.3 s) is built into the engines and is fine; (2) never signal the end — the video ENDS 1.0–1.4 s after `PAYOFF` (e.g. PAYOFF 8.2, DUR 9.4), closing line visible on the last frame, no long hold/outro; (3) aim for a loop — the last frame should flow naturally back into the first (same place/pose/light where possible) so rewatches count.
- Every video ends with the PAYOFF at `PAYOFF` (~8.0–8.6 s): gold flash (automatic), hero raises arms (`ARMS_V`), aura/floor light grow, `sparks`, camera orbits or pulls back, one short gold closing line; the sound logo plays automatically.
- Watermark "MOTIVATION RECLAIMED" is automatic.
- **Sound (owner, 20 Nov 2026):** sound effects + PROPER original background music that the engines add automatically: a library of real composed instrumental pieces (sampled piano, strings, cello, harp, e-piano, celesta; no drums, no vocals) in `assets/music/<mood>_N.ogg`, made by `tools/compose_music.py` with the MIT-licensed FluidR3 soundfont. Each track lands its warm "gold" chord exactly on the video's PAYOFF (engine3d/music.py aligns it); a random variant is picked per video. Set `MOOD` in every spec: `"warm"` (calm everyday, default), `"hopeful"` (progress, climbs, payday), `"tense"` (struggle, setbacks, quitting), `"night"` (late night, phone, sleep). Never a trending/copyrighted track, and never vidIQ or any paid music generator (owner). Don't add any other music. (Background score only — the content rule below still bans PROMOTING music on screen.)
- **Quality (all styles):** 1080×1920, 30 fps, CRF 16, up to 16 Mbps (≈8–15 MB per 10 s short), preset medium, tune film, near-lossless intermediates — built into the engines; never lower it to save time. The engine keeps grain LIGHT and adds gentle sharpening so videos survive Instagram/TikTok/YouTube re-compression (heavy grain turns into blotches there) — don't add extra grain/noise or blur effects.
- **Length: 8–10 s.** (EPISODES are 60–90 s but PAUSED — see below.) Do not change unless the owner updates this line.
- Tone: calm, motivating, no hype, no shouting. Never repeat a concept already in `posted.md`.

## POSITIONING — built to earn from brand deals (owner's core goal)
The channel is NOT a generic quote page. It is **"the calm discipline channel": habits, focus, routines and rebuilding yourself** — an audience of adults (roughly 18–35) who buy apps, books, journals, fitness and productivity tools.
- **Every concept must carry one specific, practical idea** viewers can use today (a habit, a routine, a focus trick, a mindset shift with an action) — never a vague quote. Favour adult-life topics that sponsors care about: phone/screen time, morning routine, gym consistency, reading, focus/deep work, sleep, money discipline, starting a business, comebacks after failure. Avoid kid/school-meme topics.
- **The Reclaimed man is a character, not a mascot:** same gold-cracked figure, an ongoing story of someone rebuilding his life. Some videos can continue his arc (his mornings, his setbacks, his small wins) so viewers follow HIM — this is what makes a faceless channel trustworthy to brands.
- **Recurring series** (rotate; name the series as the caption's first words about 1 in 3 videos, e.g. "Rebuild Series:", "Day 1 vs Day 365:", "One Habit:", "Quiet Wins:"). Series make people follow and come back.
- **Save-worthy over pretty:** each video should be something a viewer wants to save or send to a friend.
- Engagement > followers: CTAs (see brand rules), comment-bait questions people can genuinely answer, and the auto first comment below.
- **MONEY DISCIPLINE (owner, 15 Nov 2026; reduced 20 Nov: money videos get slightly fewer views) — about 1 in 4 videos** (never two money videos in a row). Make them land like the discipline ones: hook on a relatable moment (payday, the 3pm coffee, the online basket at midnight) and a human story with a rival/setback, not numbers first; is a money-habit video (higher-paying niche, attracts budgeting/saving/banking app sponsors). Same gold hero, same 3D style, same calm discipline message, applied to money: no-spend weekend, save before you spend, the small daily spend that adds up, cancelling unused subscriptions, an emergency fund jar filling up, building a side project after work, delayed gratification (buy it now vs in 30 days). Counters in money suit it well (SAVED £0 → £1,200 / "$" alternate between videos for UK+US). **Habits only — never financial advice:** no specific stocks, crypto, trading, get-rich-quick, income claims or "how I made £X". Extra hashtags for these: #moneyhabits #personalfinance #saving #budgeting #financialfreedom (still 3–5 total). Log them with `MONEY` in the posted.md concept line; never two in a row. The monthly analytics decides whether to raise or lower this.
- **NEVER promote or favour gambling, drinking or music (owner, 20 Nov 2026 — absolute rule).** Not even indirectly or as a background prop: no betting, casinos, scratch cards, odds or "bet"; no alcohol, pubs, bars, beer/wine, "drinks", "home brew" or anything that could read as alcohol (say "coffee at home"); no music — no music subscriptions or apps, headphones/earbuds, playlists, songs, concerts, instruments, dancing to music. In money videos, the thing he KEEPS or rewards himself with must never be one of these (e.g. never "keeps the MUSIC subscription" — 015 did this; don't repeat). Prefer neutral items: gym, books, savings, cloud storage, phone plan, food, travel. Check every label, prop, tag, caption and hashtag against this before posting.
- **Off-limits topics (owner rule):** no "alpha male", "sigma", manosphere, dating/relationship-advice, "leave/ignore girls", "women are a distraction", or anything that puts down any group. The channel is about rebuilding yourself — keep it inclusive.
- **Audience: UK + US** (account is UK-based). Write in natural English that reads well to both (everyday words, no regional slang from elsewhere); use relatable UK/US-life moments (alarm before work, the commute, the gym after work, Sunday reset, scrolling in bed). Keep hashtags English.

## VARIETY (owner's explicit rule)
Never the same scene type twice in a row. Record the FORMAT in posted.md. 3D formats:
- **RACE** — lanes, two or more runners (`specs/010_which_lane.py` / `engine3d/race.py`).
- **CLIMB** — stairs/steps/ladder up, others stop below (`specs/011_one_step_a_day.py`).
- **QUIT** — a group starts together, they drop out one by one, he's still there (`specs/012_still_here.py`).
- **WALL** — boxes as bricks: build a wall / break through one (use `box()`).
- **DOOR / ROOM** — a doorway of light, bed + alarm, desk… built from `box()` (keep sets minimal).
- **CROWD** — many grey figures walking one way, he turns / walks the other way.
- **REVERSE** — open on the gold success, then a REWIND (◀◀ icon, reverse motion, whoosh) back to the start ("ATTEMPT 01" / "ONE YEAR AGO"), a fast speed-up montage of the failures with an attempt counter + small FAIL stamps, then the final attempt → PASS → gold PAYOFF.
Also vary camera moves, which counter (DAY / REPS / STEPS / HOURS), the speed-up moment, tags and sounds. The gold hero + gold PAYOFF ending stay constant.
**Avoid the "mass-produced / repetitive content" flag (YouTube, Meta, TikTok demonetise templated channels):** every video must be a genuinely different little story, not the same template with new labels. Vary the STRUCTURE too, not just the props: the payoff time (7.4–8.6 s, always ending 1.0–1.4 s later), whether there is a speed-up at all (skip it in ~1 in 3), where the hook sits, the camera path, the number of figures, the length (8–10 s), the closing line. Never reuse a hook line, tag line or closing line from the last ~15 videos (check specs/). No reused footage between videos.

## EPISODES — **OFF (owner, 15 Nov 2026): no long videos for now — maybe in 2–3 months. Do NOT make, schedule or post any EPISODE until this line says ACTIVE.** Normal shorts only, exactly as before. Rules below apply only once ACTIVE.
- **Ratio (when ACTIVE): 1 in every 6 posted videos is an EPISODE** (60–90 s original story). Never two episodes in a row. Count in posted.md (FORMAT `EPISODE`). The owner will later raise this to 2 in 6 — only change it when this line says so.
- Posted to all three platforms like any short (same upload_media + create_post, same slots). It counts as one of the run's videos.
- What an episode is: ONE continuous story of the Reclaimed man rebuilding one part of his life (phone at night, gym after work, reading instead of scrolling, Sunday reset, money, a comeback after a setback), carrying ONE practical idea viewers can use tonight.
- **Hook + re-hook (non-negotiable — people must not scroll):**
  - First second: a striking subtitle line + something already moving/counting (e.g. "He checked his phone 96 times yesterday." with a counter racing up).
  - Every 6–10 s a new beat: label changes (THE RULE / NIGHT 1 / DAY 4 / DAY 30…), a new subtitle that makes viewers want the next one ("On day four he nearly gave in."), a sound cue (whoosh/hit) and something visibly new (prop, light, counter, bar).
  - Include a setback in the middle (nearly quits) before the turn — that's the tension that holds viewers.
  - End on the gold PAYOFF with the practical rule spelled out in the last subtitle + CTA.
- Build it by copying `templates/episode_template.py` (working 70 s example: BEATS list, `beat()`, `ctx.subtitle()`, label per beat). Write a NEW story each time — never re-post the template's phone story.
- Subtitles: short plain sentences (≤ 9 words), third person ("he"), calm. Labels stay UPPERCASE one or two words.
- Caption: first line "Rebuild Series, Episode N: <title with keyword>" (N = next episode number from posted.md), then 1–2 lines + a question. Hashtags as normal.
- Render takes ~5–6 min (normal). Check one preview sheet with 6–8 stills across the beats before rendering.

## Making a video (3D)
1. Pick the next unused concept from `ideas.md` (adapt it to a 3D scene type above; invent freely in the same spirit). Check `posted.md` first.
2. Copy the closest example spec (`specs/011_one_step_a_day.py` or `specs/012_still_here.py` are the cleanest templates) to `specs/NNN_slug.py` and rewrite the scene.
   A 3D spec defines `DUR` (10.0), `PAYOFF` (~7.6), `BLUR=(t0,t1)` (the speed-up window), `SOUNDS`, `CTA`, `CAPTION` and `frame(t, sub)` → `(image, overlay)`.
   Building blocks (`engine3d/r3d.py`, `engine3d/race.py`): `Cam(pos, target)`, `room(img, cam)`, `box(...)` (steps, walls, beds, desks, doors), `barbell(...)`,
   figures `joints(x, z, pose, facing)` + `draw_figure(img, emis, cam, J, hero=True/False, warm=, alpha=)`, poses `STAND, SIT, PHONE_STAND, ARMS_V`,
   `pose_run(phase)`, `pose_phone_walk(phase)`, `mix(a, b, k)`; light `aura`, `floor_light`, `blob` (phone glow), `sparks`; `compose(img, emis)` (bloom);
   text `spaced(...)`, `tag(d, x, y, text, gold)`, `chrome(d, t, CTA, PAYOFF)`. Speed-up = a scene-time function like `st(t)` (×4 inside BLUR).
3. Check ONE preview sheet: `python3 make3d.py specs/NNN_slug.py --stills <6–7 times across the video>` and LOOK at it: figures visible and readable, nothing off-screen, tags fully on screen, text not overlapping, camera never empty for long. Fix and re-check once if needed.
4. Render: `python3 make3d.py specs/NNN_slug.py` → `videos/NNN_slug.mp4` (~1.5 min). Then the QUALITY GATE (below) — mandatory.
5. **Variety self-check before posting (every run):** compare this run's videos with the last ~10 in specs/ — scene type, hook, tags, closing line, camera path, payoff time, speed-up yes/no, topic (MONEY vs discipline). If any two look like the same template, rewrite one before posting. Put a one-line "Variety check: …" in the run report so the owner can see it.

## STICK2D details (original white stick figures)
- Spec structure like `specs/004_the_alarm.py` / `specs/008_the_crowd.py`: `DURATION`, `PAYOFF`, `HERO`, `CTA`, `CAPTION`, `SOUNDS`, `PANELS` (1–4 stacked panels, one-word UPPERCASE labels). Formats: SPLIT 2, STORY, PROGRESSION 4, TRIO 3 (max 1 in 4 of the STICK2D videos), COUNTER, REVERSE.
- Helpers in `engine/core.py`: `ctx.figure(x, pose, facing, crack, gy, glow=ctx.payoff_glow)`, poses (stand, proud, push, sit, slump, kneel, arms_up, reach, phone, lift, squat, lie), `walk`, `climb`, `pose_track`, `track`, props (`slope`, `stairs`, `boulder`, `wall`, `barbell`, `phone`, `bed`, `flag`, `text`), effects (`spot`, `light`, `sparks`, `dust`, `impact`).
- The engine draws the CTA band, safe-zone layout, watermark and payoff automatically. No hook text in STICK2D — labels only. Never set `CHARACTER`/`FACES`.
- Preview: `python3 make.py specs/NNN_slug.py --stills 1.5 4 PAYOFF+1`; render: `python3 make.py specs/NNN_slug.py`.

## QUALITY GATE — no bugged video is ever posted (owner requirement)
After rendering EVERY video (any style), run `python3 tools/qa.py videos/NNN_slug.mp4` and LOOK at every frame of `previews/NNN_slug_qa.png` (a frame every 0.25 s). The video may only be posted if ALL of these hold:
- No automatic warnings (frozen spans, black frames); 1080×1920; 8–10 s.
- The hero is visible and readable in every beat; the camera is never empty / pointing at nothing (cut instead of flying through emptiness).
- No figure clipped by the frame edge at an important moment, no figures overlapping each other's faces, no limb through a face, no figure floating or sinking into the floor/props, no hands missing the object they hold (bar, jar, bag, phone).
- No pose glitches between frames (sudden wrong pose, flicker, sideways jumps), walking/running looks like a cycle.
- All text fully on screen, readable, not overlapping other text or speech tags; speech tags point at the right person; the CTA is correct.
- Glow never washes a character out to a white/beige blob; the payoff reads clearly.
- Logic: props move with whatever holds them, nothing appears before its cause, one consistent look per shot; nothing moving crosses the hook/counter text or the CTA by accident.
- Content: nothing in any frame promotes or favours gambling, drinking or music (see POSITIONING).
If something fails: fix it and re-render, then run the gate again (max 2 fix rounds). If it still isn't clean, DO NOT post it — drop that concept and make a simpler video from a proven template instead (specs/010–012, templates/toon3d_*.py, specs/002–009). Write one line per video in the run report: "QA: passed (checked N frames)" or what was fixed.

## Captions (SEO, VARIED, human — avoids "inauthentic/repetitive content" flags)
There is NO fixed template. Every caption must read differently from the last ~10 in posted.md captions (see specs/).
- **First line = the title.** Unique, under 90 characters, contains a keyword (motivation, discipline, mindset, habits, self improvement, consistency…). YouTube uses it as the Short's title. Never reuse a title pattern twice in a row (e.g. not "Same X. Three people." again).
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
  #selfimprovement #motivationalvideo #consistency #habits #selfdiscipline #growthmindset #nevergiveup #mentalstrength #personalgrowth #dailymotivation #success #focus #morningroutine #gymmotivation #comeback #healing #patience #progress #animation #stickfigure
- Save the caption as `CAPTION` in the spec (so future runs can check for repetition).

## Posting (Zapier → Publer)
1. `git add` the spec + video, commit, `git -c push.negotiate=true push`. Public URL:
   `https://raw.githubusercontent.com/motivationreclaimed/motivation-reclaimed/main/videos/<file>.mp4`
2. Publer `upload_media` (selected_api `App232404CLIAPI`, upload_type `url`, `file_urls` = [raw URL]) → media id.
3. Publer `create_post` with `state: "scheduled"`, `scheduled_at` (ISO, UTC), `media_ids`, `text` = CAPTION.
   - Workspace: `6af6583ee39d7f4bffa1aa3e` (Motivation Reclaimed). Zapier connection: mr@pixevon.com.
   - Accounts (ALL THREE every time): `6af658d73a8f484368c1cf7e` (Instagram), `6af65b2b1fc93c847bca0e16` (TikTok), `6af65afdd185a8df145dea8a` (YouTube).
   - NEVER use the abyanhammad@gmail.com / Unbreachd Studios connection — that is a different brand.
   - If a call times out, do NOT retry blindly (it may have gone through) — note it in the report instead.
   - **Auto first comment (engagement):** in create_post also set `auto_comment_enabled: true` and `auto_comment_text: ["<one short, genuine question tied to the video that's easy to answer, e.g. 'What's the one habit you're rebuilding this month?'>"]`. Vary it every time. If create_post fails because of this option (plan limit / parameter error), immediately retry the SAME call once without the auto-comment fields (failed calls cost no Zapier tasks) and note it in posted.md so future runs skip it.
4. Append a line to `posted.md`: `NNN | slug | FORMAT | scheduled_at | concept one-liner`. Commit + push.

## Schedule (date-based — check today's date first)
Zapier trial started 13 Nov 2026 and ends ~27 Nov 2026, then the account is on Zapier FREE (100 tasks/month).
Every successful Zapier tool call costs 2 tasks, and each video needs 2 calls (upload_media + create_post) = 4 tasks.

- **Until 26 Nov 2026 (trial):** 2 posts/day at 12:00 and 21:00 UK (UK lunch + UK evening/US afternoon), all three platforms. Each run schedules 7 videos. (Posts already scheduled before 15 Nov keep their old 13:00/20:00 times — just continue after the last one.)
- **From 27 Nov 2026 (free plan):** 5 posts/week, one per day at 21:00 UK, all three platforms.
  - Monday run: 3 videos → Mon, Tue, Wed 21:00.  Thursday run: 2 videos → Thu, Sat 21:00.
  - That is ~22 videos ≈ 88 tasks/month + 4 tasks for the monthly analytics check ≈ 92, under 100.
  - The owner can raise this later by upgrading Zapier — only change it if CLAUDE.md is updated.
- Never schedule into the past or before an already-scheduled post (check posted.md). Publer free allows max 10 pending posts per account.

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

## Animation service CTA (owner rule — the owner sells custom animations)
- Compilations: (paused) the service CTA is built in (side panel + outro + caption) — always.
- Shorts: about **1 in 5** videos carry the service mention — **subtle, never an advert** (owner rule). The on-screen CTA stays a normal engagement CTA; instead set `SERVICE = True` in the spec and call `chrome(d, t, CTA, PAYOFF, service=SERVICE)`: in the last ~1.5 s the watermark quietly becomes "ANIMATIONS FOR BRANDS · MR@PIXEVON.COM". In the caption add one low-key last line before the hashtags, varied, e.g. "Animation by Pixevon — mr@pixevon.com" / "We animate for brands too: mr@pixevon.com". Never two in a row; log `SERVICE` in the posted.md concept line.

## Owner's cartoon character (pending owner approval — keep OFF until this line says ON)
- Status: **OFF — owner reverted to the original white stick figure (15 Nov 2026).** Do not use `CHARACTER` or `FACES`.
- When ON: set `CHARACTER = True` in every spec; the hero (crack=True) is drawn with the owner's full-body drawings from `assets/poses/*.png` (stand, walk, run, sit_hug, kneel_pray, push, lift, bed_phone, victory, open_arms) — no cut-out rig. Engine pose names map to drawings automatically (lie→bed_phone which includes its own bed, so don't also draw `ctx.bed` under him; push→push; lift→lift WITH its own barbell, so don't draw `ctx.barbell`; arms_up→victory; proud→open_arms; slump/sit/floor→sit_hug; kneel→kneel_pray; squat→lift (exercise reads as lifting); walking→walk/stand two-pose cycle at ~6.3 rad/s). He reads best in 1–2 panel formats and episodes.
- **Only use the character when EVERY action the hero does in that video is one of the 10 drawings** (standing, walking, running, sitting hugging knees, kneeling, pushing, lifting a barbell, lying in bed with phone, arms up, open arms). If the story needs any action he has no drawing for (knocking, climbing stairs/hill, holding a phone while standing, reading, sitting at a desk, reaching, falling…), make that whole video with the stick figure instead — never show him frozen in the wrong pose. Other people are always regular grey stick figures. New drawings from the owner = new actions he can do.

## Monthly analytics check (separate scheduled task, 1st of each month)
Uses exactly 2 Zapier calls (4 tasks) — nothing else:
1. Publer `generate_top_posts` (selected_api `App232404CLIAPI`, workspace `6af6583ee39d7f4bffa1aa3e`, date_from/date_to = last month, sort_by `engagement_rate`).
2. Publer `find_analytics` (tool `publer_find_analytics_by_date_range`, same workspace, from/to = last month, chart_ids `["followers","video_views","engagement_rate"]`).
Then write `insights.md` (overwrite): followers and views trend, top 5 and bottom 5 posts matched to their FORMAT/series/topic via posted.md, and 3–5 plain rules for next month ("more STORY comebacks", "fewer TRIO", "phone/screen-time topics win"). Commit + push.
**Video runs: read `insights.md` first (if present) and lean towards what it says works**, while still obeying the VARIETY rules.

## Zapier budget rules (important on the free plan)
- Do NOT call inspect / discover / list / read actions on Zapier during normal runs — every successful call burns 2 tasks. All IDs needed are in this file.
- Only call `upload_media` and `create_post`. Use inspect only if one of those calls fails with a parameter error.
- If Zapier reports the task limit is reached: stop posting, keep the rendered videos committed in the repo, log them in posted.md as `NOT SCHEDULED (zapier limit)`, and say so clearly in the final report so the owner can post them manually or upgrade.

## If Zapier / Publer is unavailable (connector down, outage, 5xx errors)
- Still make and render all the videos, commit + push them, and log each in posted.md as
  `NNN | slug | FORMAT | PENDING (zapier unavailable) | planned_slot | concept` (planned_slot = the ISO time it should have gone out).
- Say so clearly in the run report. Do not burn retries in a loop — the separate **retry task** (Mon & Thu 14:17 and 18:17 UK) will post them.
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
