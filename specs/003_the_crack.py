"""003 — THE CRACK. Brand origin story: he breaks, the cracks fill with gold, he stands."""
import math
from engine.core import track, pose_track, breathe, ramp, ease_out

DURATION = 9.5
PAYOFF = 7.0
HERO = 0

CAPTION = """Broken is not the end. It's where the gold goes in. 🏺

Life cracks him and he falls. He stays down for a while, then fills every crack with discipline and stands back up stronger.

Your scars are proof you kept going. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.3, "rumble", 0.35), (1.5, "crack", 0.7), (1.9, "crack", 0.6), (2.6, "thud", 0.8),
          (4.0, "chime", 0.35), (4.8, "chime", 0.3), (5.7, "step", 0.4), (6.4, "step", 0.5)]

X = 540

def scene(ctx, t):
    ctx.ground_line()
    lit = 0.35 + 0.65 * ramp(t, 4.0, 6.5)
    ctx.spot(X, lit, width=360)
    pose = pose_track(t, [(0, "stand"), (1.4, "stand"), (2.0, "kneel"), (2.6, "floor"),
                          (5.6, "floor"), (6.2, "kneel"), (6.8, "stand"), (7.3, "proud")])
    shake = 0
    for t0 in (1.5, 1.9):
        if 0 <= t - t0 < 0.25: shake = 10 * (1 - (t - t0) / 0.25) * math.sin(t * 90)
    fill = ease_out(ramp(t, 4.0, 5.6))
    ctx.figure(X + shake, breathe(pose, t, 2.5), 1, crack=True, fill=fill, glow=ctx.payoff_glow)
    if 2.55 < t < 3.3: ctx.dust(X, ctx.ground, 2.6)
    if t >= 2.6: ctx.impact(2.6, 0.8)
    if 1.5 <= t < 2.1: ctx.sparks(X, ctx.ground - 420, 1.5, n=14, col=(140, 140, 150), speed=(80, 240), life=0.5)
    ctx.sparks(X, ctx.ground - 300, 5.5, n=30, col=(255, 210, 140), speed=(120, 380))

PANELS = [dict(label=lambda t: "BROKEN" if t < 4.0 else "RECLAIMED", color=None, scene=scene)]
