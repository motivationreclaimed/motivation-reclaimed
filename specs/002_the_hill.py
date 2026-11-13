"""002 — THE HILL. Same boulder, three people."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp, ease_in, POSES

DURATION = 8.5
PAYOFF = 6.3          # sound logo + gold glow moment
HERO = 2

CAPTION = """Same hill. Same boulder. Three different people. ⛰️

Excuses push until it gets hard. Waiting never starts. Discipline keeps pushing when nobody is watching.

Which one were you this week? Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(1.0, "rumble", 0.4), (3.35, "whoosh", 0.6), (4.35, "thud", 0.7), (4.9, "step", 0.4),
          (2.2, "rumble", 0.35), (4.0, "rumble", 0.4), (5.25, "thud", 0.6)]

X0, X1, RISE, R = 300, 800, 90, 80

def _push_pair(ctx, ys, bx, t, crack=False, glow=0.0):
    rot = bx / R
    ctx.boulder(bx, ys(bx) + 4, R, rot)
    fx = bx - 160
    ph = t * 2 * math.pi * 1.1
    p = POSES["push"].copy()
    p["thL"] += 12 * math.sin(ph); p["thR"] -= 12 * math.sin(ph)
    return ctx.figure(fx, p, 1, crack=crack, gy=ys(fx), glow=glow)

def excuses(ctx, t):
    ys = ctx.slope(X0, X1, RISE)
    ctx.spot(450, 0.8)
    if t < 3.3:
        bx = track(t, [(0, 330), (2.4, 540), (3.3, 560)])
        _push_pair(ctx, ys, bx, t)
    else:
        bx = track(t, [(3.3, 560), (4.35, 330)], ease_in)
        ctx.boulder(bx, ys(bx) + 4, R, bx / R)
        if 4.3 < t < 4.6: ctx.dust(bx, ctx.ground, 4.35)
        fx = track(t, [(3.3, 400), (4.8, 110)])
        gy = ys(fx)
        if t < 4.8:
            ph = (t - 3.3) * 2 * math.pi * 1.4
            ctx.figure(fx, walk(ph, 1.0), -1, gy=gy)
        else:
            ctx.figure(fx, pose_track(t, [(4.8, "stand"), (5.4, "slump")]), 1, gy=gy)

def waiting(ctx, t):
    ys = ctx.slope(X0, X1, RISE)
    ctx.spot(300, 0.6, (150, 180, 255))
    ctx.boulder(400, ctx.ground + 4, R, 0.3)
    s = ctx.figure(180, breathe(pose_track(t, [(0, "phone"), (5.0, "phone"), (5.8, blend("sit", "phone", 0.5))]), t), 1)
    ctx.phone(s)

def discipline(ctx, t):
    ys = ctx.slope(X0, X1, RISE)
    ctx.spot(620, 1.0)
    if t < 5.6:
        bx = track(t, [(0.0, 330), (5.3, 830), (5.6, 900)])
        _push_pair(ctx, ys, bx, t, crack=True)
    else:
        ctx.boulder(900, ys(900) + 4, R, 900 / R)
        fx = track(t, [(5.6, 700), (6.2, 760)])
        p = pose_track(t, [(5.6, "push"), (6.2, "proud")])
        ctx.figure(fx, breathe(p, t), 1, crack=True, gy=ys(fx), glow=ctx.payoff_glow)
    if t > 5.2: ctx.sparks(840, ys(840) - 10, 5.25, n=25, col=(230, 220, 200), speed=(80, 260))

PANELS = [
    dict(label="EXCUSES", color="slate", scene=excuses),
    dict(label="WAITING", color="sage", scene=waiting),
    dict(label="DISCIPLINE", color=None, scene=discipline),
]
