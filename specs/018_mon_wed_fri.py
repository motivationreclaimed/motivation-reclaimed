"""018 — MON · WED · FRI. STICK2D · SPLIT 2 · discipline (gym consistency). Training 'when I feel like it' vs on a fixed schedule; workouts counter over 12 weeks."""
import math
from engine.core import track, pose_track, blend, breathe, ramp, ease_io

DURATION = 8.6
PAYOFF = 7.3
HERO = 1
CTA = "Comment 'mon wed fri' and lock it in."

CAPTION = """Stop waiting to feel like it. Put the gym in your calendar (consistency)

Three fixed days beat seven good intentions. Decide once, then just turn up.

#consistency #gymmotivation #discipline #habits #motivation"""

SOUNDS = [(0.6, "tick", 0.3), (1.9, "hit", 0.35), (3.5, "tick", 0.3), (4.4, "hit", 0.3), (5.2, "tick", 0.3), (6.0, "hit", 0.3), (6.7, "tick", 0.3), (7.3, "chime", 0.4)]

def readout(ctx, big, small, frac, col):
    ctx.text(790, 190, big, 60, col)
    ctx.text(790, 250, small, 24, (150, 150, 158))
    ctx.bar(590, 290, 400, frac, col, h=18)

BX = 440
def bar_ground(ctx): return dict(hL=(BX - 10, ctx.ground - 38), hR=(BX + 10, ctx.ground - 38))

def mood(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 0.4, (150, 180, 255))
    ctx.barbell(bar_ground(ctx))
    keys = [(0, "slump"), (1.3, "slump"), (1.8, "stand"), (2.3, "squat"), (3.0, "lift"), (3.5, "lift"), (4.0, "slump")]
    p = pose_track(t, keys)
    x = track(t, [(1.3, 200), (1.9, BX - 20), (3.9, BX - 20), (4.6, 200)], lambda u: u) if 1.3 < t < 4.6 else 200
    s = ctx.figure(x, breathe(p, t, 1.0), 1, gy=ctx.ground if 1.3 < t < 4.0 else ctx.ground - 20)
    if 3.0 < t < 3.9: ctx.barbell(s)
    f = ease_io(ramp(t, 0.4, 6.6)); wk = max(1, int(12 * f))
    readout(ctx, "WORKOUTS  1", "WEEK %d  ·  FEELS LIKE IT" % wk, 1 / 36, (150, 180, 255))
    if 4.6 < t < 6.4: ctx.text(150, ctx.ground - 300, "tomorrow.", 34, (150, 160, 190))

def plan(ctx, t):
    ctx.ground_line()
    ctx.spot(340, 1.0)
    cyc = 1.9
    c = (t - 0.6) % cyc if t > 0.6 else None
    if t > 6.6:
        p = pose_track(t, [(6.6, "stand"), (7.1, "proud")])
        ctx.barbell(bar_ground(ctx)); s = ctx.figure(300, breathe(p, t, 1.2), 1, crack=True, glow=ctx.payoff_glow)
    else:
        keys = [(0, "stand"), (0.6, "stand"), (1.0, "squat"), (1.3, "squat"), (1.8, "lift"), (2.1, "lift"), (2.5, "stand")]
        p = pose_track(c if c is not None else 0.0, keys)
        s = ctx.figure(300 + 120 * ((ramp(c, 0.5, 0.9) - ramp(c, 2.2, 2.5)) if c is not None else 0), breathe(p, t, 1.2), 1, crack=True)
        if c is not None and c > 1.35 and c < 2.4: ctx.barbell(s)
        else: ctx.barbell(bar_ground(ctx))
    f = ease_io(ramp(t, 0.4, 6.6)); n = int(36 * f)
    readout(ctx, "WORKOUTS  %d" % n, "WEEK %d  ·  MON WED FRI" % max(1, int(12 * f)), f, (214, 170, 72))
    if t > 7.25: ctx.sparks(300, ctx.ground - 330, 7.3, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="WHEN I FEEL LIKE IT", color="slate", scene=mood),
    dict(label="MON · WED · FRI", color=None, scene=plan),
]
