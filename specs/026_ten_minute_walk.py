"""026 — THE 10-MINUTE WALK. STICK2D · SPLIT 2 · discipline (focus/energy): sit through the afternoon dip vs a 10-minute walk break; energy bar drains vs refills."""
import math
from engine.core import track, pose_track, blend, walk, breathe, ramp, ease_io

DURATION = 8.8
PAYOFF = 7.5
HERO = 1
CTA = "Send this to someone who sits all day."

CAPTION = """Take a 10-minute walk when your focus dips. It beats another coffee

I used to push through the 3pm slump. Now I stand up and walk round the block. Same hour, better work.

#focus #habits #productivity #discipline #selfimprovement"""

SOUNDS = [(0.6, "tick", 0.3), (1.8, "tick", 0.3), (3.0, "tick", 0.3), (4.2, "tick", 0.3), (4.9, "whoosh", 0.4),
          (5.5, "step", 0.3), (6.0, "step", 0.3), (6.5, "step", 0.3), (7.5, "chime", 0.4)]

def readout(ctx, big, small, frac, col):
    ctx.text(790, 190, big, 52, col)
    ctx.text(790, 250, small, 24, (150, 150, 158))
    ctx.bar(590, 290, 400, frac, col, h=18)

def clk(m): return "%02d:%02d" % (m // 60, m % 60)

def sitting(ctx, t):
    ctx.ground_line()
    ctx.spot(300, 0.4, (150, 180, 255))
    f = ease_io(ramp(t, 0.4, 6.8))
    ctx.d.rectangle([380, ctx.ground - 150, 560, ctx.ground - 140], fill=(60, 60, 68))
    ctx.d.rectangle([450, ctx.ground - 140, 460, ctx.ground], fill=(60, 60, 68))
    p = blend("sit", "slump", f)
    ctx.figure(300, breathe(p, t, 1.0), 1, gy=ctx.ground)
    readout(ctx, clk(13 * 60 + int(120 * f)), "FOCUS", 0.8 - 0.65 * f, (150, 180, 255))
    if 3.5 < t < 5.0: ctx.text(300, ctx.ground - 330, "just one more tab.", 30, (150, 160, 190))

def walking(ctx, t):
    ctx.ground_line()
    ctx.spot(340, 1.0)
    f = ease_io(ramp(t, 0.4, 6.8))
    if t < 2.2:
        ctx.d.rectangle([380, ctx.ground - 150, 560, ctx.ground - 140], fill=(60, 60, 68))
        ctx.figure(300, breathe(blend("sit", "slump", ramp(t, 0, 1.5)), t, 1.0), 1, crack=True, gy=ctx.ground)
        foc = 0.15
    elif t < 6.6:
        x = 150 + 260 * (0.5 - 0.5 * math.cos((t - 2.2) * 1.1))
        face = 1 if math.sin((t - 2.2) * 1.1) > 0 else -1
        ctx.figure(x, walk((t - 2.2) * 2 * math.pi * 1.1), face, crack=True, gy=ctx.ground)
        foc = 0.15 + 0.7 * ramp(t, 2.2, 6.6)
    else:
        p = pose_track(t, [(6.6, "stand"), (7.1, "proud")])
        ctx.figure(300, breathe(p, t, 1.2), 1, crack=True, glow=ctx.payoff_glow)
        foc = 0.9
    readout(ctx, clk(13 * 60 + int(120 * f)) if t < 6.6 else "10 MIN", "FOCUS", foc, (214, 170, 72))
    if t > 7.45: ctx.sparks(300, ctx.ground - 330, 7.5, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="SIT THROUGH IT", color="slate", scene=sitting),
    dict(label="WALK 10 MINUTES", color=None, scene=walking),
]
