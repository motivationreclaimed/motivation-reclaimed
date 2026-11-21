"""020 — TOON3D · SHELF · MONEY: three wants on a shelf, 30-day wait (x4 speed-up). Two fade away; the real one stays. A scroller buys everything now and his pile grows."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 9.4, 8.0
def st(t): return t if t < 3.2 else (3.2 + 4 * (t - 3.2) if t < 5.6 else 12.8 + (t - 5.6))
def day(s): return int(1 + 29 * min(1.0, max(0.0, (s - 0.8) / 12.0)))
ITEMS = [("TRAINERS", 90, 0.2, 8), ("GADGET", 60, 1.05, 20), ("JACKET", 120, 1.9, None)]   # name, £, x, day it fades

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-1.5, -0.4, k), lerp(1.8, 2.1, k), lerp(-5.4, -5.0, k)), (lerp(-0.3, 0.2, k), 1.05, 1.0))
    k = ease((t - PAYOFF) / 1.3)
    return Cam((-0.4, lerp(2.1, 3.2, k), lerp(-5.0, -8.4, k)), (0.2, lerp(1.05, 1.4, k), 1.0))

def frame(t, sub):
    s = st(t + sub); d_ = day(s)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    saved = 0
    for name, cost, x, fd in ITEMS:
        sc = 1.0
        if fd is not None and d_ >= fd:
            sc = max(0.0, 1 - (day_frac(s) - fd) / 0.8) if False else max(0.0, 1.0 - (1 + 29 * min(1.0, max(0.0, (s - 0.8) / 12.0)) - fd) / 1.2)
            saved += cost
        keep = fd is None
        top = (150, 118, 66) if (keep and glow > 0.2) else (62, 62, 70)
        # pedestal
        box(img, cam, x - 0.34, x + 0.34, 0, 0.22, 0.75, 1.25, (34, 34, 40), (24, 24, 28), (28, 28, 32), edge=(70, 72, 82))
        if sc > 0.3:
            h_ = 0.62 * sc
            box(img, cam, x - 0.28 * sc ** 0.5, x + 0.28 * sc ** 0.5, 0.22, 0.22 + h_, 0.85, 1.15, top, (46, 46, 54), (40, 40, 48),
                edge=(255, 190, 90) if keep else (110, 112, 126), emis=emis if keep else None, ecol=(255, 170, 60))
    # scroller buys everything now
    ng = min(6, 1 + int(max(0.0, s - 0.8) / 0.9))
    for i in range(ng):
        box(img, cam, -2.4, -1.85, i * 0.3, i * 0.3 + 0.27, 0.9, 1.4, (52, 52, 60), (40, 40, 48), (34, 34, 42), edge=(96, 98, 112))
    people = []
    if t >= PAYOFF + 0.1: hp, ex = T.ARMS_UP, "happy"
    else: hp, ex = T.STAND, ("worried" if t < 1.6 else "determined")
    hx = -0.75
    people = [(np.array([hx, 0, 0.3], np.float32), hp, "hero", ex, None),
              (np.array([-1.9, 0, 0.9], np.float32), T.PHONE, "coral", "tired", "phone")]
    for P, pose, look, ex_, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, pose, look, ex_, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (1.9, 0.8, 1.0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.4:
            a = int(255 * min(1, (1.4 - t) / 0.3)); spaced(d, (W / 2, 520), "WANT IT NOW?", 60, (a, a, a), sp=9)
        elif 3.2 <= t < 5.9:
            spaced(d, (W / 2, 520), f"DAY {d_}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), f"SAVED £{saved}   × 4", 30, (255, 205, 130) if saved else (150, 150, 160), sp=5)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "WAIT 30 DAYS.", 62, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for name, cost, x, fd in ITEMS:
            p = cam.proj(np.array([x, 0.0, 0.95], np.float32))
            if p and t < PAYOFF + 0.3:
                col_ = (150, 152, 162) if fd else (255, 205, 130)
                spaced(d, (p[0], p[1] + 34), name, 17, col_, sp=1); spaced(d, (p[0], p[1] + 58), f"£{cost}", 19, col_, sp=1)
        p = cam.proj(np.array([-2.0, 2.3, 0.9], np.float32))
        if p and 1.2 <= t < 2.4: tag(d, p[0], p[1], "buy it now.", False)
        p = cam.proj(np.array([hx, 2.35, 0.3], np.float32))
        if p and 1.6 <= t < 2.8: tag(d, p[0], p[1], "ask me in 30 days.", True)
        if 6.0 <= t < 7.4:
            p = cam.proj(np.array([1.9, 1.6, 1.0], np.float32))
            if p: tag(d, p[0], p[1], "still want this.", True)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "hit", 0.4), (1.6, "thud", 0.3), (3.2, "whoosh", 0.6), (3.5, "tick", 0.3), (4.0, "tick", 0.3),
          (4.5, "tick", 0.3), (5.0, "tick", 0.3), (5.6, "whoosh", 0.4), (6.2, "tick", 0.3)]
BLUR = (3.2, 5.6)
MOOD = "warm"
CTA = "Which want will you test for 30 days?"
CAPTION = """The 30-day rule: wait a month before any non-essential buy (money habits)

I write it on a list and look again in 30 days. Most of it stops mattering by day nine.

Which want will you test for 30 days?

#moneyhabits #personalfinance #saving #budgeting #discipline"""
