"""004 — THE ALARM. Same alarm, two mornings. SPLIT 2."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp

DURATION = 9.0
PAYOFF = 6.4
HERO = 1

CAPTION = """Discipline is decided in the first 5 seconds after the alarm. ⏰

One hits snooze, then snooze again, then scrolls in bed until the morning is gone. The other gets up on the first ring and is already training.

Win the morning, win the day. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.6, "tick", 0.5), (0.8, "tick", 0.5), (1.0, "tick", 0.5), (1.6, "hit", 0.35),
          (3.0, "tick", 0.45), (3.2, "tick", 0.45), (3.6, "hit", 0.3),
          (1.7, "step", 0.4), (2.5, "step", 0.4), (3.1, "step", 0.4), (4.3, "whoosh", 0.5), (5.15, "thud", 0.6)]

SLEEP = dict(hip=14, lean=84, thL=-86, shL=-90, thR=-82, shR=-88, uaL=60, faL=80, uaR=80, faR=100)
REACH = dict(SLEEP, uaR=150, faR=120)
SCROLL = dict(SLEEP, uaR=150, faR=175)

def clock(ctx, x, label, ring):
    gy = ctx.ground
    ctx.d.rectangle([x - 50, gy - 70, x + 50, gy], fill=(36, 36, 42), outline=(80, 80, 90))
    ctx.d.rounded_rectangle([x - 44, gy - 118, x + 44, gy - 74], 8, fill=(20, 20, 24), outline=(90, 90, 100))
    on = ring and int(ctx.t * 8) % 2 == 0
    col = (240, 150, 120) if on else (200, 200, 205)
    ctx.text(x, gy - 96, label, 26, col)
    if on: ctx.light(x, gy - 96, 80, (240, 140, 110), 0.8)

def snooze(ctx, t):
    top = ctx.bed(360, 330)
    ctx.spot(520, 0.5, (150, 180, 255))
    ring = 0.6 < t < 1.6 or 3.0 < t < 3.6
    lab = "06:00" if t < 3.0 else ("06:09" if t < 4.4 else ("06:4%d" % min(9, int((t - 4.4) * 3)) if t < 7.6 else "07:52"))
    clock(ctx, 860, lab, ring)
    p = pose_track(t, [(0, SLEEP), (1.1, SLEEP), (1.5, REACH), (1.8, SLEEP), (3.2, SLEEP), (3.5, REACH),
                       (3.8, SLEEP), (4.4, SLEEP), (4.9, SCROLL)])
    s = ctx.figure(505, breathe(p, t, 1.5), 1, gy=top)
    if t > 4.7: ctx.phone(s)

def now(ctx, t):
    top = ctx.bed(150, 300)
    ctx.spot(760, 1.0)
    clock(ctx, 70, "06:00" if t < 3.5 else "06:01", 0.6 < t < 1.0)
    bx = 800
    if t < 1.6:
        p = pose_track(t, [(0, SLEEP), (0.9, SLEEP), (1.6, "sit")])
        x = track(t, [(0.9, 260), (1.6, 380)])
        ctx.figure(x, p, 1, crack=True, gy=top if t < 1.25 else top + 6)
        ctx.barbell(dict(hL=(bx - 10, ctx.ground - 38), hR=(bx + 10, ctx.ground - 38)))
    elif t < 3.5:
        x = track(t, [(1.6, 380), (3.5, bx - 20)], lambda u: u)
        p = walk((t - 1.6) * 2 * math.pi * 1.2) if t > 2.0 else pose_track(t, [(1.6, "sit"), (2.0, "stand")])
        ctx.figure(x, p, 1, crack=True, gy=None if t > 1.8 else top + 6)
        ctx.barbell(dict(hL=(bx - 10, ctx.ground - 38), hR=(bx + 10, ctx.ground - 38)))
    else:
        p = pose_track(t, [(3.5, "stand"), (4.1, "squat"), (4.4, "squat"), (5.15, "lift")])
        s = ctx.figure(bx - 20, breathe(p, t, 1.5), 1, crack=True, glow=ctx.payoff_glow)
        if t < 3.9: ctx.barbell(dict(hL=(bx - 10, ctx.ground - 38), hR=(bx + 10, ctx.ground - 38)))
        else: ctx.barbell(s)
        if t > 5.1: ctx.sparks(bx - 20, ctx.ground - 330, 5.15, n=22, col=(230, 220, 200), speed=(80, 240))

PANELS = [
    dict(label="SNOOZE", color="slate", scene=snooze),
    dict(label="NOW", color=None, scene=now),
]
