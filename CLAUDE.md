# Motivation Reclaimed — content engine & posting playbook

Faceless motivation channel. Instagram / TikTok / YouTube Shorts, all posted through Publer via the Zapier connector.
Business email: mr@pixevon.com. Handles: @motivationreclaimed (IG, TikTok), @motivation_reclaimed (YouTube).

## Brand rules (never break)
- Black background, paper-grain texture, calm palette. Stacked panels (2–4), one-word UPPERCASE labels in a Times New Roman–style serif (Liberation Serif, set in the engine — never switch back to mono/sans fonts).
- Brand character: white stick figure. The HERO (the right way, usually the last panel) always has the gold kintsugi crack (`crack=True`).
- No titles and no hook text. Only the panel labels (+ optional short sub-line). Straight to the point.
- **Every video has an on-screen CTA** (owner's rule): set `CTA = "..."` in the spec. The engine shows it for the WHOLE video, in italic serif, in its own band directly above the panels — never over the animation and never lower on screen (the panel stack ends at a fixed line; the bottom is covered by app UI). Do not override `PANEL_H` or the layout. Keep it ≤ 8 words, calm tone.
  Rotate CTA types and never repeat the exact wording of the last ~10 videos: comment a word ("Comment 'reclaim' if this is you."), comment an answer ("Which one are you? Comment below."), save ("Save this for the hard days."), share ("Send this to someone who needs it."), small commitment ("Comment 'day 1' and start today."). Match it to the concept.
- Every video ends with the PAYOFF: hero glows gold, other panels fade, sound logo plays (automatic when `PAYOFF` is set).
- Watermark "MOTIVATION RECLAIMED" is automatic.
- **Length: 8–10 s.** Do not change unless the owner updates this line.
- Tone: calm, motivating, no hype, no shouting. Never repeat a concept already in `posted.md`.

## VARIETY (owner's explicit rule — do not keep making the same 3-panel comparison)
Rotate formats. Never use the same format twice in a row, and use the classic "3 labelled panels" in at most 1 of every 4 videos.
Formats (record the format in posted.md):
- **SPLIT 2** — two panels, e.g. YOU vs YOU, BEFORE / AFTER, 3 HOURS / 3 MINUTES (`PANELS` with 2 entries).
- **STORY** — one full-screen scene (1 panel, figure auto-scaled 1.6×), a short wordless story: fall → get up, crack fills with gold, walking against a crowd. Labels optional (`label: ""`).
- **PROGRESSION 4** — four panels as a timeline: DAY 1 / DAY 30 / DAY 100 / DAY 365.
- **TRIO 3** — the classic three-way comparison (limit as above).
- **COUNTER** — one scene with a changing on-screen number/day counter or progress bar (`ctx.text`).
- **REVERSE** — starts at the gold payoff, then shows how he got there.
Also vary: props, settings (hill, stairs, gym, bed, rain, road, crowd, door), pacing, which panel is the hero, and sound events.
Hero still carries the gold crack and the PAYOFF ending still closes every video — that is the signature that stays constant.

## Making a video
1. Pick the next unused concept from `ideas.md` whose format differs from the previous post (or invent a new one in the same spirit). Check `posted.md` first.
2. Write `specs/NNN_slug.py` (copy the structure of `specs/002_the_hill.py`): `DURATION`, `PAYOFF`, `HERO`, `CAPTION`, `SOUNDS`, `PANELS`.
   Helpers live in `engine/core.py`: `ctx.figure(x, pose, facing, crack, gy, glow=ctx.payoff_glow)`, poses in `POSES`
   (stand, proud, push, sit, slump, kneel, arms_up, reach, phone, lift, squat, lie), `walk(phase, speed)`, `climb(phase)`,
   `pose_track`, `track`, props (`slope`, `stairs`, `boulder`, `wall`, `barbell`, `phone`, `bed`, `flag`, `text`),
   effects (`spot`, `light`, `sparks`, `dust`, `impact`). Extend the engine when a concept needs a new prop or pose.
3. Check ONE preview sheet: `python3 make.py specs/NNN_slug.py --stills 1.5 4 PAYOFF+1` and look at it. Fix clipping/overlaps.
4. Render: `python3 make.py specs/NNN_slug.py` → `videos/NNN_slug.mp4` (~30 s).

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
4. Append a line to `posted.md`: `NNN | slug | FORMAT | scheduled_at | concept one-liner`. Commit + push.

## Schedule (date-based — check today's date first)
Zapier trial started 13 Nov 2026 and ends ~27 Nov 2026, then the account is on Zapier FREE (100 tasks/month).
Every successful Zapier tool call costs 2 tasks, and each video needs 2 calls (upload_media + create_post) = 4 tasks.

- **Until 26 Nov 2026 (trial):** 2 posts/day at 13:00 and 20:00 UK, all three platforms. Each run schedules 7 videos.
- **From 27 Nov 2026 (free plan):** 5 posts/week, one per day at 20:00 UK, all three platforms.
  - Monday run: 3 videos → Mon, Tue, Wed 20:00.  Thursday run: 2 videos → Thu, Sat 20:00.
  - That is ~22 videos ≈ 88 tasks/month, leaving a small buffer under 100.
  - The owner can raise this later by upgrading Zapier — only change it if CLAUDE.md is updated.
- Never schedule into the past or before an already-scheduled post (check posted.md). Publer free allows max 10 pending posts per account.

## Zapier budget rules (important on the free plan)
- Do NOT call inspect / discover / list / read actions on Zapier during normal runs — every successful call burns 2 tasks. All IDs needed are in this file.
- Only call `upload_media` and `create_post`. Use inspect only if one of those calls fails with a parameter error.
- If Zapier reports the task limit is reached: stop posting, keep the rendered videos committed in the repo, log them in posted.md as `NOT SCHEDULED (zapier limit)`, and say so clearly in the final report so the owner can post them manually or upgrade.

## Housekeeping (keeps the free GitHub repo small)
- Publer copies each video when `upload_media` runs, so old video files are no longer needed.
- At the start of every run, `git rm` any `videos/*.mp4` whose post is scheduled more than 7 days in the past (per posted.md). Keep specs and logs.

## Keeping credits low
- One preview sheet per video, one render. No extra re-renders unless something is visibly broken.
- Reuse/extend engine helpers instead of writing new drawing code per video.
