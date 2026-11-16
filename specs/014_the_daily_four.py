"""014 — THE DAILY £4. STICK2D · COUNTER · MONEY. Takeaway coffee every day vs home brew; 365 days of counters."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp, ease_io

DURATION = 8.2
PAYOFF = 7.0
HERO = 1
CTA = "Save this for payday."

CAPTION = """What a £4 daily habit really costs in a year (money habits)

£1,460. Not on a holiday, not on a big purchase. Just on a Tuesday, on the way to work.

Save this for payday. 🏺

#moneyhabits #saving #budgeting #habits #discipline"""
AUTO_COMMENT = "What's your small daily spend? Be honest."

SOUNDS = [(0.5, "tick", 0.3)] + [(0.9 + k * 0.9, "tick", 0.3) for k in range(7)] + [(0.7 + k * 0.9, "step", 0.3) for k in range(7)] + [(6.9, "chime", 0.4)]

def readout(ctx, big, small, frac, col):
    ctx.text(790, 190, big, 64, col)
    ctx.text(790, 250, small, 24, (150, 150, 158))
    ctx.bar(590, 290, 400, frac, col, h=18)

def pops(ctx, t, x, y, txt, col):
    for k in range(7):
        u = (t - (0.9 + k * 0.9)) / 0.8
        if 0 <= u <= 1:
            f = 1 - u
            ctx.text(x, y - 70 * u, txt, 34, tuple(int(c * f) for c in col))

def takeaway(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 0.4, (150, 180, 255))
    x = 300 + 150 * math.sin(t * 1.5)
    face = 1 if math.cos(t * 1.5) > 0 else -1
    ctx.figure(x, walk(t * 2 * math.pi * 1.1), face, gy=ctx.ground)
    pops(ctx, t, 300, ctx.ground - 420, "-£4", (200, 120, 120))
    f = ease_io(ramp(t, 0.5, 6.4))
    readout(ctx, "£{:,}".format(int(1460 * f)), "SPENT   ·   DAY %d" % max(1, int(365 * f)), f, (150, 180, 255))

def homebrew(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 1.0)
    p = pose_track(t, [(0, "stand"), (6.6, "stand"), (7.1, "proud")])
    ctx.figure(300, breathe(p, t, 1.2), 1, crack=True, glow=ctx.payoff_glow)
    pops(ctx, t, 300, ctx.ground - 420, "+£3", (214, 170, 72))
    f = ease_io(ramp(t, 0.5, 6.4))
    readout(ctx, "£{:,}".format(int(1095 * f)), "SAVED   ·   DAY %d" % max(1, int(365 * f)), f, (214, 170, 72))
    if t > 6.95: ctx.sparks(300, ctx.ground - 330, 7.0, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="£4 A DAY", sub="TAKEAWAY", color="slate", scene=takeaway),
    dict(label="£1 A DAY", sub="HOME BREW", color=None, scene=homebrew),
]
