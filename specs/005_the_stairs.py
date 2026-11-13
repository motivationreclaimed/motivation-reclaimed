"""005 — THE STAIRS. Same staircase, four points in time. PROGRESSION 4."""
import math
from engine.core import track, pose_track, climb, walk, breathe, ramp, clamp, blend

DURATION = 9.0
PAYOFF = 6.4
HERO = 3
FIG_SCALE = 0.55

CAPTION = """Day 1 is supposed to feel hard. That's how you know you started. 🪜

The same stairs, four points in time: on day 1 he barely makes one step, by day 30 and day 100 he climbs higher, and on day 365 he stands at the top.

Keep showing up and the climb gets yours. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.6, "step", 0.35), (1.2, "step", 0.35), (1.9, "thud", 0.45), (2.4, "step", 0.35), (3.0, "step", 0.35),
          (3.4, "thud", 0.35), (3.8, "step", 0.4), (4.4, "step", 0.4), (5.0, "step", 0.45), (5.6, "step", 0.45),
          (6.0, "whoosh", 0.4)]

X0, N, SW, SH = 200, 6, 90, 16
START = 110

def make(stop_x, t_stop, end_pose, flag=False):
    def scene(ctx, t):
        ctx.stairs(X0, N, SW, SH)
        top = ctx.ground - N * SH
        ys = lambda x: ctx.ground - SH * clamp((x - X0) / SW + 0.5, 0, N)
        ctx.spot(stop_x, 0.4 + 0.6 * (stop_x / 900), width=200)
        if flag: ctx.flag(960, top, t * 3)
        if t < t_stop:
            x = track(t, [(0.3, START), (t_stop, stop_x)], lambda u: u)
            p = climb((t - 0.3) * 2 * math.pi * 1.0) if t > 0.3 else blend("stand", "stand", 0)
            ctx.figure(x, p, 1, crack=ctx.is_hero, gy=ys(x))
        else:
            p = pose_track(t, [(t_stop, "stand"), (t_stop + 0.6, end_pose)])
            ctx.figure(stop_x, breathe(p, t, 1.2), 1, crack=ctx.is_hero, gy=ys(stop_x), glow=ctx.payoff_glow)
            if flag and t > 6.0: ctx.sparks(960, top - 90, 6.0, n=20, col=(230, 220, 200), speed=(60, 200))
    return scene

PANELS = [
    dict(label="DAY 1", color="slate", scene=make(300, 1.6, "floor")),
    dict(label="DAY 30", color="sage", scene=make(470, 3.0, "kneel")),
    dict(label="DAY 100", color="sand", scene=make(650, 4.4, "stand")),
    dict(label="DAY 365", color=None, scene=make(880, 5.8, "proud", flag=True)),
]
