"""007 — THE MIRROR. Same mirror, two reflections. SPLIT 2."""
import math
from engine.core import track, pose_track, walk, breathe, ramp, ease_out, INK

DURATION = 9.0
PAYOFF = 6.2
HERO = 1

CAPTION = """The version of you that you could become is already waiting in the mirror. 🪞

One looks at who he is and turns away. The other looks at who he could be, gets up and walks until he matches him.

Stop avoiding the mirror and start becoming him. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.5, "rumble", 0.25), (2.9, "whoosh", 0.35), (2.2, "step", 0.4), (3.1, "step", 0.45),
          (4.0, "step", 0.45), (4.6, "step", 0.45), (4.8, "chime", 0.3)]

MX, MW, MH = 620, 280, 430
RX = MX + MW / 2

def glass(ctx):
    x0, x1 = ctx.mirror(MX, MW, MH)
    return x0, x1

def are(ctx, t):
    ctx.ground_line()
    ctx.spot(380, 0.5, width=220)
    glass(ctx)
    ctx.figure(RX + 20, breathe("floor", t, 1.0), -1, col=(150, 150, 160), alpha=0.55, scale=0.85, clamp=False, gy=ctx.ground - 12)
    face = 1 if t < 3.0 else -1
    ctx.figure(360, breathe("floor", t, 1.0), face)

def could(ctx, t):
    ctx.ground_line()
    ctx.spot(RX, 0.9, width=220)
    glass(ctx)
    ctx.light(RX, ctx.ground - 200, 160, None, 0.5 + 0.5 * ramp(t, 0, 2))
    ctx.figure(RX, breathe("proud", t, 1.0), -1, crack=True, col=(225, 215, 195), alpha=0.85, scale=0.85,
               clamp=False, gy=ctx.ground - 12, glow=ctx.payoff_glow * 0.6)
    p = pose_track(t, [(0, "floor"), (1.6, "floor"), (2.3, "kneel"), (3.1, "stand")])
    x = 300
    if 3.1 < t < 4.6:
        x = track(t, [(3.1, 300), (4.6, 440)], lambda u: u)
        p = walk((t - 3.1) * 2 * math.pi * 1.1)
    elif t >= 4.6:
        x = 440
        p = pose_track(t, [(4.6, "stand"), (5.6, "proud")])
    fill = ease_out(ramp(t, 4.6, 5.9))
    ctx.figure(x, breathe(p, t, 1.2), 1, crack=True, fill=fill, glow=ctx.payoff_glow)

PANELS = [
    dict(label="WHO YOU ARE", color="stone", scene=are),
    dict(label="WHO YOU COULD BE", color=None, scene=could),
]
