"""008 — THE CROWD. Everyone walks one way; he turns around. STORY."""
import math
from engine.core import track, pose_track, walk, breathe, ramp, ease_io

DURATION = 9.0
PAYOFF = 6.4
HERO = 0
FIG_SCALE = 1.15

CAPTION = """If everyone is going the same way, ask yourself where it actually leads. 🚶

He walks with the crowd until he stops, turns around and walks the other way alone, straight into the light.

Discipline often means walking alone for a while. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.2, "rumble", 0.3), (1.6, "step", 0.4), (2.4, "whoosh", 0.4)] + \
         [(2.7 + 0.45 * k, "step", 0.35 + 0.02 * k) for k in range(7)]

CROWD = [(0, 0.55, 1.0, 0.0), (1, 0.35, 0.8, -70), (2, 0.5, 1.0, 0.0), (3, 0.3, 0.8, -70),
         (4, 0.55, 1.0, 0.0), (5, 0.35, 0.8, -70), (6, 0.45, 1.0, 0.0), (7, 0.3, 0.8, -70)]

def scene(ctx, t):
    ctx.ground_line()
    lt = ramp(t, 2.4, 6.0)
    ctx.light(1080, ctx.ground - 350, 260 + 200 * lt, None, 0.25 + 0.75 * lt)
    ctx.spot(900, 0.3 + 0.7 * lt, width=300)
    for (i, a, sc, dy) in sorted(CROWD, key=lambda c: c[2]):
        span = 1500
        x = (i * span / len(CROWD) + 600 - t * 150 * (0.9 + 0.1 * (i % 3))) % span - 200
        ctx.figure(x, walk(t * 2 * math.pi * 1.05 + i * 1.3), -1, col=(150, 152, 165), alpha=a * (1 - 0.5 * ramp(t, PAYOFF, PAYOFF + 0.6)),
                   scale=ctx.scale * sc, gy=ctx.ground + dy, clamp=False)
    if t < 1.5:
        x = track(t, [(0, 620), (1.5, 420)], lambda u: u)
        p, face = walk(t * 2 * math.pi * 1.05), -1
    elif t < 2.4:
        x, face = 420, (-1 if t < 2.1 else 1)
        p = pose_track(t, [(1.5, "stand"), (2.4, "stand")])
    elif t < 5.8:
        x = track(t, [(2.4, 420), (5.8, 820)], lambda u: u)
        p, face = walk((t - 2.4) * 2 * math.pi * 1.1), 1
    else:
        x, face = 820, 1
        p = pose_track(t, [(5.8, "stand"), (6.4, "proud")])
    ctx.figure(x, breathe(p, t, 1.5), face, crack=True, glow=ctx.payoff_glow)

PANELS = [dict(label=lambda t: "EVERYONE" if t < 2.1 else "YOU", color=None, scene=scene)]
