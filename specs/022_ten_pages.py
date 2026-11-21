"""022 — TEN PAGES. STICK2D · PROGRESSION 2 · discipline (reading): ten pages a night. Night 1 vs night 365: one book in hand vs a shelf of twelve."""
import math
from engine.core import track, pose_track, blend, breathe, ramp, ease_io

DURATION = 8.8
PAYOFF = 7.5
HERO = 1
CTA = "Save this and read tonight."

CAPTION = """Ten pages a night. That's about twelve books a year (reading habit)

Not a big plan. Not a new year. Ten pages, lamp on, phone in another room.

Save this and read tonight.

#habits #selfimprovement #consistency #discipline #progress"""

SOUNDS = [(0.6, "tick", 0.3), (1.8, "tick", 0.3), (3.0, "tick", 0.3), (4.2, "tick", 0.3), (5.0, "whoosh", 0.4),
          (5.6, "tick", 0.3), (6.2, "tick", 0.3), (6.8, "tick", 0.3), (7.5, "chime", 0.4)]

def book(ctx, s, col=(190, 190, 200)):
    (lx, ly), (rx, ry) = s["hL"], s["hR"]
    cx, cy = (lx + rx) / 2, (ly + ry) / 2
    ctx.d.polygon([(cx - 34, cy + 20), (cx, cy + 8), (cx + 34, cy + 20), (cx + 34, cy - 22), (cx, cy - 34), (cx - 34, cy - 22)], fill=(50, 50, 58), outline=col)
    ctx.d.line([(cx, cy + 8), (cx, cy - 34)], fill=col, width=2)

def shelf(ctx, x, y, n, col):
    ctx.d.rectangle([x, y, x + 330, y + 8], fill=(80, 80, 90))
    for i in range(12):
        if i < n:
            h = 60 + (i * 37) % 28
            ctx.d.rectangle([x + 8 + i * 26, y - h, x + 8 + i * 26 + 20, y], fill=tuple(int(c * 0.55) for c in col), outline=col)

def night1(ctx, t):
    top = ctx.bed(260, 330)
    ctx.spot(300, 0.6, (150, 180, 255))
    s = ctx.figure(330, breathe(blend("sit", "stand", 0.0), t, 1.0), 1, gy=top + 6)
    book(ctx, s)
    pages = min(10, int(10 * ramp(t, 0.5, 4.6)))
    ctx.text(740, 205, "NIGHT 1", 44, (150, 180, 255))
    ctx.text(740, 262, "PAGE %d" % pages, 30, (150, 150, 158))
    shelf(ctx, 640, ctx.ground - 20, 0, (150, 180, 255))

def night365(ctx, t):
    top = ctx.bed(260, 330)
    ctx.spot(300, 1.0)
    s = ctx.figure(330, breathe(blend("sit", "stand", 0.0), t, 1.0), 1, crack=True, gy=top + 6, glow=ctx.payoff_glow)
    book(ctx, s, (214, 170, 72))
    f = ease_io(ramp(t, 0.5, 6.8))
    n = min(12, int(12 * f + 0.2))
    ctx.text(740, 205, "NIGHT %d" % max(1, int(365 * f)), 44, (214, 170, 72))
    ctx.text(740, 262, "BOOKS %d" % n, 30, (214, 170, 72))
    shelf(ctx, 640, ctx.ground - 20, n, (214, 170, 72))
    if t > 7.45: ctx.sparks(330, ctx.ground - 330, 7.5, n=22, col=(255, 210, 140), speed=(60, 240))

PANELS = [
    dict(label="NIGHT ONE", color="slate", scene=night1),
    dict(label="TEN PAGES A NIGHT", color=None, scene=night365),
]
