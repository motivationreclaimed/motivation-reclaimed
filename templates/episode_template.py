"""EPISODE template (60–90 s) — Rebuild Episode: "The phone sleeps outside".
Copy to specs/NNN_slug.py and rewrite BEATS/scene for a new story. Structure that must stay:
  * HOOK in the first second (a striking line + something already moving/counting).
  * A RE-HOOK every 6–10 s: new beat = label change (NIGHT 1 / DAY 4 …), new subtitle, a sound hit,
    and something visibly new (prop, light, counter). Each subtitle should make the viewer want the next one.
  * One continuous story about the Reclaimed man, one practical idea, payoff + CTA at the end.
"""
import math
from engine.core import track, pose_track, walk, breathe, ramp, ease_out, beat

DURATION = 70.0
PAYOFF = 62.0
HERO = 0
CTA = "Comment 'tonight' if you'll try it."

CAPTION = """Rebuild Series, Episode 1: one rule fixed his mornings (phone discipline)

He didn't delete anything. He just stopped letting the phone sleep next to him.

What's the first thing you check in the morning?

#discipline #habits #morningroutine #selfimprovement #motivation"""

SLEEP = dict(hip=14, lean=84, thL=-86, shL=-90, thR=-82, shR=-88, uaL=60, faL=80, uaR=80, faR=100)
SCROLL = dict(SLEEP, uaR=150, faR=175)
TOSS = dict(SLEEP, lean=96, uaL=120, faL=140)

# (start, label, [(t0, t1, subtitle), ...])
BEATS = [
    (0.0,  "",          [(0.0, 5.8, "He checked his phone 96 times yesterday.")]),
    (6.0,  "THE RULE",  [(6.0, 9.6, "So he made one rule."), (9.8, 15.8, "The phone sleeps outside the bedroom.")]),
    (16.0, "NIGHT 1",   [(16.0, 19.8, "Night one was awful."), (20.0, 23.8, "His hand kept reaching for nothing.")]),
    (24.0, "DAY 4",     [(24.0, 28.4, "On day four he nearly gave in."), (28.6, 32.8, "He walked to the door… and turned back.")]),
    (33.0, "DAY 7",     [(33.0, 37.4, "Then the mornings started to change."), (37.6, 41.8, "He woke before the alarm.")]),
    (42.0, "DAY 14",    [(42.0, 46.6, "The hour he used to scroll"), (46.8, 51.8, "became the hour he trained.")]),
    (52.0, "DAY 30",    [(52.0, 61.8, "Screen time")]),
    (62.0, "RECLAIMED", [(62.0, 65.8, "One rule. Thirty nights."), (66.0, 70.0, "Phone out of the bedroom. Start tonight.")]),
]

SOUNDS = [(0.2, "tick", 0.4), (1.0, "tick", 0.4), (1.8, "tick", 0.45), (2.6, "tick", 0.5), (3.4, "hit", 0.4)]
for b in BEATS[1:]:
    SOUNDS.append((b[0], "whoosh", 0.35))          # every re-hook gets a sound cue
SOUNDS += [(10.5, "step", 0.4), (11.3, "step", 0.4), (12.1, "step", 0.4), (13.4, "thud", 0.45),
           (24.2, "rumble", 0.3), (29.0, "step", 0.4), (29.8, "step", 0.4), (30.9, "hit", 0.5),
           (37.6, "chime", 0.3), (44.0, "thud", 0.6), (49.0, "thud", 0.6), (55.0, "tick", 0.4), (57.0, "hit", 0.45)]

def label(t):
    return BEATS[beat(t, BEATS)[0]][1]

def counter(ctx, t, x, y):
    n = int(96 * ease_out(ramp(t, 0.2, 4.0)))
    ctx.text(x, y, str(n), 120, (150, 180, 255))
    ctx.text(x, y + 80, "PICK-UPS", 26, (110, 120, 140))
    ctx.light(x, y, 120, (150, 180, 255), 0.4)

def scene(ctx, t):
    W, gy = ctx.w, ctx.ground
    i, u = beat(t, BEATS)
    ctx.ground_line()
    door_x = W - 230
    # the door is the story's anchor: the phone lives just outside it from the rule onwards
    if i >= 1:
        ctx.door(door_x, open_=0.0, light=0.0)
        if 13.4 <= t < 62:
            ctx.d.rounded_rectangle([door_x + 170, gy - 30, door_x + 196, gy - 4], 4, fill=(30, 34, 46), outline=(170, 190, 230))
            if i in (2, 3): ctx.light(door_x + 183, gy - 18, 60, (150, 180, 255), 0.5 + 0.3 * math.sin(t * 5))
    for s0, s1, line in BEATS[i][2]:
        ctx.subtitle(line, s0, s1)

    if i == 0:                                   # HOOK: scrolling in bed, counter racing up
        top = ctx.bed(140, 360)
        ctx.spot(330, 0.45, (150, 180, 255))
        s = ctx.figure(300, breathe(SCROLL, t, 1.2), 1, crack=True, gy=top)
        ctx.phone(s)
        counter(ctx, t, W - 220, 420)
    elif i == 1:                                 # THE RULE: gets up, walks the phone to the door
        top = ctx.bed(140, 360)
        ctx.spot(W / 2, 0.6)
        if t < 10.2:
            p = pose_track(t, [(6.0, SCROLL), (8.0, SCROLL), (9.0, "sit"), (10.2, "stand")])
            s = ctx.figure(track(t, [(8.0, 300), (10.2, 460)]), p, 1, crack=True, gy=top if t < 9.0 else None)
            ctx.phone(s)
        else:
            x = track(t, [(10.2, 460), (13.2, door_x + 120)], lambda v: v)
            p = walk((t - 10.2) * 6.3) if t < 13.2 else pose_track(t, [(13.2, "stand"), (13.6, "kneel"), (14.4, "stand")])
            s = ctx.figure(x, p, 1, crack=True)
            if t < 13.4: ctx.phone(s, glow=False)
    elif i == 2:                                 # NIGHT 1: restless, reaching for a phone that isn't there
        top = ctx.bed(140, 360)
        ctx.spot(330, 0.3, (120, 130, 170))
        p = pose_track(t, [(16, SLEEP), (17.5, TOSS), (18.5, SLEEP), (20.5, SCROLL), (21.3, SLEEP), (22.5, TOSS)])
        ctx.figure(300, breathe(p, t, 1.5), 1, crack=True, gy=top)
        ctx.text(W / 2, 330, "00:%02d" % (47 + int((t - 16) * 1.5)), 54, (120, 130, 160))
    elif i == 3:                                 # DAY 4: nearly gives in, walks to the door, turns back
        ctx.spot(W / 2, 0.45)
        if t < 28.6:
            ctx.figure(420, breathe("slump", t, 2), 1, crack=True)
        else:
            x = track(t, [(28.6, 420), (30.6, door_x - 10), (31.4, door_x - 10), (32.9, door_x - 160)], lambda v: v)
            moving = 28.6 < t < 30.6 or 31.4 < t < 32.9
            f = 1 if t < 31.0 else -1
            ctx.figure(x, walk((t - 28.6) * 6.3) if moving else "stand", f, crack=True)
    elif i == 4:                                 # DAY 7: dawn light, wakes before the alarm
        top = ctx.bed(140, 360)
        ctx.spot(W / 2, 0.4 + 0.6 * ramp(t, 33, 38), (255, 210, 150))
        p = pose_track(t, [(33, SLEEP), (37.6, SLEEP), (38.6, "sit"), (39.8, "stand"), (41.5, "proud")])
        ctx.figure(track(t, [(37.6, 300), (39.8, 470)]), p, 1, crack=True, gy=top if t < 38.6 else None)
        ctx.text(W - 200, 330, "05:58", 54, (230, 200, 150))
    elif i == 5:                                 # DAY 14: the scroll hour becomes the training hour
        ctx.spot(W / 2, 0.9)
        p = pose_track(t, [(42, "stand"), (43, "squat"), (44, "lift"), (45.5, "squat"), (47, "lift"), (48.5, "squat"), (49, "lift")])
        s = ctx.figure(W / 2, p, 1, crack=True)
        ctx.barbell(s)
        if t > 44: ctx.dust(W / 2, gy, 44.0)
        if t > 49: ctx.dust(W / 2, gy, 49.0)
    elif i == 6:                                 # DAY 30: screen time bar shrinks
        ctx.spot(W / 2, 1.0)
        ctx.figure(W / 2 - 180, breathe("proud", t, 2), 1, crack=True)
        k = ease_out(ramp(t, 54.5, 58.5))
        mins = int(370 - (370 - 100) * k)
        ctx.text(W / 2 + 170, 330, "%dh %02dm" % (mins // 60, mins % 60), 70, (230, 230, 235))
        ctx.text(W / 2 + 170, 400, "A DAY", 26, (130, 130, 140))
        ctx.bar(W / 2 + 20, 450, 300, mins / 370.0)
    else:                                        # PAYOFF: gold, sound logo (automatic)
        ctx.spot(W / 2, 1.0)
        ctx.figure(W / 2, breathe("proud", t, 2), 1, crack=True, glow=ctx.payoff_glow)
        ctx.sparks(W / 2, gy - 320, 62.2, n=34, col=(255, 210, 140), speed=(120, 380))

PANELS = [dict(label=label, color=None, scene=scene)]
