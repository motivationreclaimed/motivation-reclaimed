"""016 — PHONE ACROSS THE ROOM. STICK2D · SPLIT 2 · discipline (sleep)."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp, ease_io

DURATION = 8.4
PAYOFF = 7.1
HERO = 1
CTA = "Comment 'charger' and try it tonight."

CAPTION = """Charge your phone across the room. Sleep gets better fast (habits)

I stopped scrolling at 1am the day my phone stopped living next to my pillow.

Try it for one week.

#habits #sleep #focus #selfimprovement #discipline"""
AUTO_COMMENT = "What time did you actually fall asleep last night?"

SOUNDS = [(0.6, "tick", 0.3), (1.8, "tick", 0.3), (3.0, "tick", 0.3), (4.2, "tick", 0.3), (5.0, "whoosh", 0.4),
          (5.8, "tick", 0.4), (6.4, "step", 0.4), (6.8, "step", 0.4), (7.0, "chime", 0.4)]

SLEEP = dict(hip=14, lean=84, thL=-86, shL=-90, thR=-82, shR=-88, uaL=60, faL=80, uaR=80, faR=100)
SCROLL = dict(SLEEP, uaR=150, faR=175)

def clock(ctx, x, label, col=(200, 200, 205)):
    gy = ctx.ground
    ctx.d.rounded_rectangle([x - 70, gy - 118, x + 70, gy - 70], 8, fill=(20, 20, 24), outline=(90, 90, 100))
    ctx.text(x, gy - 94, label, 30, col)

def hm(m): return "%02d:%02d" % ((m // 60) % 24, m % 60)

def late(ctx, t):
    top = ctx.bed(360, 330)
    ctx.spot(520, 0.5, (150, 180, 255))
    mins = 23 * 60 + int(190 * ease_io(ramp(t, 0.3, 6.3)))
    clock(ctx, 860, hm(mins), (150, 180, 255))
    s = ctx.figure(505, breathe(SCROLL, t, 1.5), 1, gy=top)
    ctx.phone(s)
    ctx.text(560, 190, "SLEEP  %dH" % max(3, 8 - int(5 * ramp(t, 0.3, 6.3))), 44, (150, 180, 255))

def early(ctx, t):
    top = ctx.bed(150, 300)
    ctx.spot(760, 1.0)
    # phone charging far away on a shelf
    ctx.d.rectangle([880, ctx.ground - 150, 1000, ctx.ground - 140], fill=(60, 60, 68))
    ctx.d.rounded_rectangle([925, ctx.ground - 200, 955, ctx.ground - 150], 4, fill=(70, 90, 140))
    mins = 22 * 60 + 30 + int(480 * ease_io(ramp(t, 0.3, 6.3)))
    clock(ctx, 640, hm(mins), (214, 170, 72))
    if t < 5.9:
        p = SLEEP
        ctx.figure(255, breathe(p, t, 2.0), 1, crack=True, gy=top)
    else:
        p = pose_track(t, [(5.9, "sit"), (6.3, "stand"), (6.8, "stand"), (7.2, "proud")])
        x = track(t, [(5.9, 280), (6.8, 380)])
        ctx.figure(x, breathe(p, t, 1.5), 1, crack=True, glow=ctx.payoff_glow, gy=None if t > 6.2 else top + 6)
    ctx.text(560, 190, "SLEEP  %dH" % (8 if t > 5.5 else 3 + int(5 * ramp(t, 0.3, 5.5))), 44, (214, 170, 72))
    if t > 7.05: ctx.sparks(380, ctx.ground - 330, 7.1, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="PHONE IN BED", color="slate", scene=late),
    dict(label="PHONE ACROSS THE ROOM", color=None, scene=early),
]
