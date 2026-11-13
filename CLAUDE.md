# Motivation Reclaimed — content engine & posting playbook

Faceless motivation channel. Instagram / TikTok / YouTube Shorts, all posted through Publer via the Zapier connector.
Business email: mr@pixevon.com. Handles: @motivationreclaimed (IG, TikTok), @motivation_reclaimed (YouTube).

## Brand rules (never break)
- Black background, paper-grain texture, calm palette. Stacked panels (2–4), one-word UPPERCASE labels in mono font.
- Brand character: white stick figure. The HERO (the right way, usually the last panel) always has the gold kintsugi crack (`crack=True`).
- No titles, no hook text, no end card question. Only the panel labels (+ optional short sub-line). Straight to the point.
- Every video ends with the PAYOFF: hero glows gold, other panels fade, sound logo plays (automatic when `PAYOFF` is set).
- Watermark "MOTIVATION RECLAIMED" is automatic. Length 8–10 s.
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

## Caption format (SEO)
```
<one-line hook with the core idea> <one emoji>

<2 short sentences explaining the three panels>

<one line lesson>. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo
```
Exactly 5 hashtags. Keywords motivation / discipline / mindset early in the text.

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

## Schedule
- Default slots (UK time): 13:00 and 20:00 daily. Publer free plan allows max 10 pending posts per account, so a run schedules at most 7 posts.
- Each run: make and schedule the posts for the next ~3–4 days, starting after the last scheduled time in `posted.md`.

## Keeping credits low
- One preview sheet per video, one render. No extra re-renders unless something is visibly broken.
- Reuse/extend engine helpers instead of writing new drawing code per video.
