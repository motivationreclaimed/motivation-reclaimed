"""006 — THE PHONE. 3 hours of scrolling vs 3 minutes of training a day. COUNTER."""
import math
from engine.core import track, pose_track, blend, breathe, ramp, ease_io

DURATION = 9.0
PAYOFF = 6.3
HERO = 1

CAPTION = """3 hours a day scrolling. 3 minutes a day building. Guess which one changes your life. 📱

The screen-time counter climbs while his goal stays at zero. The other trains just 3 minutes a day, and day by day the bar fills to 100%.

Small daily discipline beats endless scrolling. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.5, "tick", 0.3), (1.5, "tick", 0.3), (2.5, "tick", 0.3), (3.5, "tick", 0.3), (4.5, "tick", 0.3),
          (1.0, "step", 0.35), (2.0, "step", 0.35), (3.0, "step", 0.35), (4.0, "step", 0.4), (5.0, "step", 0.45),
          (5.6, "chime", 0.35)]

def readout(ctx, big, small, frac, col):
    ctx.text(790, 190, big, 64, col)
    ctx.text(790, 250, small, 24, (150, 150, 158))
    ctx.bar(590, 290, 400, frac, col, h=18)

def scroll(ctx, t):
    ctx.ground_line()
    gy = ctx.ground
    ctx.d.rounded_rectangle([150, gy - 70, 470, gy], 14, fill=(44, 46, 56))
    ctx.d.rounded_rectangle([140, gy - 150, 190, gy], 14, fill=(52, 54, 64))
    ctx.spot(300, 0.5, (150, 180, 255))
    s = ctx.figure(300, breathe(blend("sit", "phone", 0.3), t, 1.0), 1, gy=gy - 70 + 48, clamp=False)
    ctx.phone(s)
    mins = int(180 * ease_io(ramp(t, 0.3, 5.6)))
    readout(ctx, "%d:%02d" % (mins // 60, mins % 60), "SCREEN TIME   ·   GOAL 0%", 0.0, (150, 180, 255))

def train(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 1.0)
    if t < 5.6:
        u = (1 - math.cos(2 * math.pi * (t - 0.5))) / 2 if t > 0.5 else 0
        p = blend("stand", "squat", u)
    else:
        p = pose_track(t, [(5.6, "stand"), (6.1, "proud")])
    ctx.figure(300, breathe(p, t, 1.2), 1, crack=True, glow=ctx.payoff_glow)
    f = ease_io(ramp(t, 0.5, 5.6))
    readout(ctx, "DAY %d" % max(1, int(90 * f)), "3 MIN / DAY   ·   GOAL %d%%" % int(100 * f), f, (214, 170, 72))
    if t > 5.55: ctx.sparks(990, 299, 5.6, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="3 HOURS", sub="SCROLLING", color="slate", scene=scroll),
    dict(label="3 MINUTES", sub="TRAINING", color=None, scene=train),
]
