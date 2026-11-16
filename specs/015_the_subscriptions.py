"""015 — TOON3D · DROP · MONEY: he carries a stack of monthly subscriptions; drops them one by one (MONTHLY £84 -> £11). No speed-up."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 8.8, 7.5
SUBS = [("MUSIC", 11), ("CLOUD", 10), ("MAGAZINE", 8), ("APP", 9), ("VIDEO", 14), ("GYM", 32)]   # bottom -> top
BASE, TH = 1.42, 0.34
DROPS = [1.3, 2.3, 3.3, 4.3, 5.3]                     # top first (GYM, VIDEO, APP, MAGAZINE, CLOUD)
LAND = [(1.5, 0.7), (-1.6, 0.6), (2.2, 1.5), (-2.2, 1.4), (0.9, 2.0)]
TAGS = ["never went.", "still paying?", "unused.", "forgot this one.", "cancel."]
FALL = 0.55

def box_pos(i, t):
    """(x, y, z, alpha-ish) of box i (0 = bottom) at time t"""
    n = len(SUBS)
    if i == 0: return (0.0, BASE + 0.55 * ease((t - PAYOFF) / 0.7), 0.0)
    k = n - 1 - i
    td = DROPS[k]
    if t < td: return (0.0, BASE + i * TH, 0.0)
    u = min(1.0, (t - td) / FALL); lx, lz = LAND[k]
    y0 = BASE + i * TH
    y = y0 * (1 - u * u) + 0.0 * (u * u) + 0.0
    return (lx * ease(min(1, u * 1.1)), max(0.0, y), lz * ease(min(1, u * 1.1)))

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((2.6 - 3.6 * k, 2.3, -5.6 + 0.6 * k), (0.0, 2.15, 0.0))
    k = ease((t - PAYOFF) / 1.3)
    return Cam((lerp(-1.0, -3.6, k), lerp(2.3, 3.0, k), lerp(-5.0, -8.2, k)), (0.0, lerp(2.15, 1.9, k), 0.0))

def monthly(t):
    v = 84
    for k, td in enumerate(DROPS):
        if t >= td + 0.4: v -= SUBS[len(SUBS) - 1 - k][1]
    return v

def frame(t, sub):
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    drawn = []
    for i, (name, cost) in enumerate(SUBS):
        x, y, z = box_pos(i, t)
        keep = (i == 0)
        top = (150, 120, 70) if keep and t > 0.1 and t >= DROPS[-1] + 0.4 else (58, 58, 66)
        box(img, cam, x - 0.42, x + 0.42, y, y + TH - 0.03, z - 0.3, z + 0.3, top, (40, 40, 50), (34, 34, 42),
            edge=(125, 100, 62) if keep else (80, 82, 94), emis=emis if keep else None, ecol=(255, 170, 60) if keep else None)
        drawn.append((i, x, y, z))
    pose = T.ARMS_UP if t >= PAYOFF + 0.1 else T.STAND
    if t >= PAYOFF + 0.1: expr = "happy"
    elif t >= DROPS[-1] + 0.5: expr = "determined"
    else: expr = "worried" if t < 3.3 else "determined"
    draw_toon(img, emis, cam, np.array([0.0, 0.0, 0.0], np.float32), pose, "hero", expr, 1, glow=glow, bright=1.0)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (0, 1.6, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.2:
            spaced(d, (W / 2, 520), "WHAT ARE YOU PAYING FOR?", 46, (255, 255, 255), sp=6)
        elif t < PAYOFF + 0.1:
            spaced(d, (W / 2, 520), f"MONTHLY £{monthly(t)}", 78, (240, 240, 244), sp=8)
        else:
            a = ease((t - PAYOFF - 0.1) / 0.5)
            spaced(d, (W / 2, 520), "£11 A MONTH.", 70, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for i, x, y, z in drawn:
            p = cam.proj(np.array([x, y + TH / 2, z - 0.3], np.float32))
            if p and p[2] > 1:
                sz = max(15, int(F * 0.075 / p[2]))
                spaced(d, (p[0], p[1]), f"{SUBS[i][0]}  £{SUBS[i][1]}", sz, (150, 152, 162) if i else (255, 205, 130), sp=2)
        for k, td in enumerate(DROPS):
            if td + 0.1 <= t < td + 1.0:
                p = cam.proj(np.array([0.0, 3.2, 0.0], np.float32))
                if p: tag(d, p[0] + (170 if k % 2 == 0 else -170), p[1], TAGS[k], k == 4)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.3, "tick", 0.3), (0.9, "hit", 0.35)] + [(td + FALL * 0.9, "thud", 0.5) for td in DROPS] + \
         [(td + 0.45, "tick", 0.3) for td in DROPS] + [(PAYOFF - 0.3, "whoosh", 0.4)]
CTA = "Which one will you cancel? Comment below."
CAPTION = """Cancel one unused subscription today (money habits)

I checked my bank statement for 5 minutes once. Found three things I hadn't opened in months.

Which one will you cancel?

#moneyhabits #personalfinance #budgeting #discipline"""
AUTO_COMMENT = "What's the oldest subscription you're still paying for?"

if __name__ == "__main__":
    if sys.argv[1] == "--stills": stills("previews/015_the_subscriptions", frame, [0.1, 1.6, 2.7, 4.0, 5.8, 7.7, 8.7])
    else: render(sys.argv[1], frame, DUR, PAYOFF, SOUNDS)
