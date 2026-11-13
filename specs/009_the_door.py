"""009 — THE DOOR. Starts at the open door, then rewinds to how he got there. REVERSE."""
import math
from engine.core import track, pose_track, walk, breathe, ramp, ease_out, blend

DURATION = 9.5
PAYOFF = 6.6
HERO = 1

CAPTION = """Every open door you see started as a door that said no for weeks. 🚪

We start at the end: one door open, full of light. Then we rewind: one man knocks once and walks away, the other knocks every single day until it opens.

Persistence is the key nobody wants to carry. Follow for daily motivation and discipline. 🏺

#motivation #discipline #mindset #selfimprovement #motivationalvideo"""

SOUNDS = [(0.2, "chime", 0.25), (1.4, "whoosh", 0.6), (2.2, "hit", 0.4), (2.45, "hit", 0.35)] + \
         [(2.2 + 0.32 * k, "hit", 0.3) for k in range(1, 10)] + [(5.4, "rumble", 0.4), (5.9, "step", 0.4), (6.3, "step", 0.45)]

DX, DW, DH = 640, 150, 300
KNOCK_A = dict(blend("stand", "reach", 0.0), uaR=80, faR=135)
KNOCK_B = dict(blend("stand", "reach", 0.0), uaR=70, faR=95)

def knock(t, t0, n, rate=0.32):
    if t < t0 or t > t0 + n * rate: return blend("stand", "stand", 0)
    u = ((t - t0) / rate) % 1
    return blend(KNOCK_A, KNOCK_B, math.sin(u * math.pi))

def once(ctx, t):
    ctx.ground_line()
    ctx.spot(DX + DW / 2, 0.5, width=200)
    ctx.door(DX, DW, DH, 0, 0)
    if t < 1.4: return
    if t < 3.2:
        x = track(t, [(1.4, 300), (2.0, 560)])
        p = walk(t * 2 * math.pi) if t < 2.0 else knock(t, 2.2, 2)
        ctx.figure(x, p, 1)
    else:
        x = track(t, [(3.2, 560), (5.2, 120)], lambda u: u)
        ctx.figure(x, walk((t - 3.2) * 2 * math.pi * 1.1) if t < 5.2 else "stand", -1)

def daily(ctx, t):
    ctx.ground_line()
    if t < 1.4:  # the end, shown first
        ctx.door(DX, DW, DH, 1, 1)
        ctx.figure(DX + 40, breathe("proud", t, 1.0), 1, crack=True, glow=0.5)
        return
    if t < 1.75:
        ctx.impact(1.4, 1.2)
    opened = ease_out(ramp(t, 5.4, 6.0))
    ctx.door(DX, DW, DH, opened, opened)
    ctx.spot(DX + DW / 2, 0.4 + 0.6 * opened, width=220)
    day = 1 if t < 2.2 else min(47, 1 + int((t - 2.2) / 0.32 * 5.2))
    ctx.text(930, 120, "DAY %d" % day, 46, (214, 170, 72))
    if t < 5.6:
        x = track(t, [(1.4, 300), (2.0, 560)])
        p = walk(t * 2 * math.pi) if t < 2.0 else knock(t, 2.2, 10)
        ctx.figure(x, p, 1, crack=True)
    else:
        x = track(t, [(5.6, 560), (6.4, DX + 40)])
        p = walk((t - 5.6) * 2 * math.pi) if t < 6.4 else pose_track(t, [(6.4, "stand"), (6.9, "proud")])
        ctx.figure(x, breathe(p, t, 1.0), 1, crack=True, glow=ctx.payoff_glow)

PANELS = [
    dict(label="KNOCKS ONCE", color="slate", scene=once),
    dict(label="KNOCKS DAILY", color=None, scene=daily),
]
