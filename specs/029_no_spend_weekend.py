"""029 — ONE QUIET WEEKEND. STICK2D · COUNTER · MONEY: every weekend out vs one no-spend weekend a month. Kept counter over 12 weeks."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp, ease_io

DURATION = 8.4
PAYOFF = 7.1
HERO = 1
CTA = "Comment 'quiet' if you'll try it."

CAPTION = """Try one no-spend weekend a month. Free walks, home food, no checkout

It felt strange for about a day. Then it felt like getting a small pay rise back.

#moneyhabits #budgeting #saving #discipline #habits"""

SOUNDS = [(0.5, "tick", 0.3)] + [(0.9 + k * 1.0, "tick", 0.3) for k in range(6)] + [(5.8, "whoosh", 0.3), (7.0, "chime", 0.4)]

def readout(ctx, big, small, frac, col):
    ctx.text(790, 190, big, 60, col)
    ctx.text(790, 250, small, 24, (150, 150, 158))
    ctx.bar(590, 290, 400, frac, col, h=18)

def pops(ctx, t, x, y, txt, col, n=6, gap=1.0):
    for k in range(n):
        u = (t - (0.9 + k * gap)) / 0.8
        if 0 <= u <= 1: ctx.text(x, y - 70 * u, txt, 34, tuple(int(c * (1 - u)) for c in col))

def out(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 0.4, (150, 180, 255))
    x = 300 + 150 * math.sin(t * 1.4)
    ctx.figure(x, walk(t * 2 * math.pi * 1.1), 1 if math.cos(t * 1.4) > 0 else -1, gy=ctx.ground)
    pops(ctx, t, 300, ctx.ground - 300, "-£60", (200, 120, 120))
    f = ease_io(ramp(t, 0.5, 6.4))
    readout(ctx, "£{:,}".format(int(720 * f)), "SPENT  ·  WEEK %d" % max(1, int(12 * f)), f, (150, 180, 255))

def quiet(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 1.0)
    p = pose_track(t, [(0, "stand"), (6.6, "stand"), (7.1, "proud")])
    if t < 6.6:
        x = 300 + 120 * math.sin(t * 0.9)
        ctx.figure(x, walk(t * 2 * math.pi * 0.8), 1 if math.cos(t * 0.9) > 0 else -1, crack=True, gy=ctx.ground)
    else:
        ctx.figure(300, breathe(p, t, 1.2), 1, crack=True, glow=ctx.payoff_glow)
    pops(ctx, t, 300, ctx.ground - 300, "£0", (214, 170, 72), n=1, gap=1.0)
    f = ease_io(ramp(t, 0.5, 6.4))
    readout(ctx, "£{:,}".format(int(240 * f)), "KEPT  ·  WEEK %d" % max(1, int(12 * f)), f, (214, 170, 72))
    if t > 6.95: ctx.sparks(300, ctx.ground - 330, 7.0, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="EVERY WEEKEND OUT", color="slate", scene=out),
    dict(label="ONE QUIET WEEKEND", color=None, scene=quiet),
]
