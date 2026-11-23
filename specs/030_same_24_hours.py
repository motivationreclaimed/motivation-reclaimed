"""030 — TOON3D · SPLIT · discipline (time/phone): SAME 24 HOURS. Two people side by side; one scrolls, one stacks focused hours (gold blocks). Clock 06:00 -> 22:00 (x4), then payoff."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 9.0, 7.7
def st(t): return t if t < 1.6 else (1.6 + 4 * (t - 1.6) if t < 5.6 else 17.6 + (t - 5.6))
def hour(s): return max(0, min(16, int((s - 1.6) / 1.0)))        # 0..16 hours elapsed since 06:00
def blocks(h): return h // 2                                   # one block every 2 hours -> 8

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-0.4, 0.4, k), lerp(1.5, 1.8, k), lerp(-5.4, -5.8, k)), (0.2, 1.0, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(0.4, 0.2, k), lerp(1.8, 3.0, k), lerp(-5.8, -9.2, k)), (0.2, 1.1, 0.0))

def frame(t, sub):
    s = st(t + sub); h = hour(s); nb = blocks(h)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow + 0.05 * nb)
    # his stack of focused blocks (right side, +x)
    for i in range(nb):
        box(img, cam, 1.5, 2.0, i * 0.24, (i + 1) * 0.24 - 0.02, -0.3, 0.3, (214, 170, 72), (170, 128, 44), (150, 112, 40), edge=(255, 210, 120), emis=emis, ecol=(255, 170, 60))
    # her/his rival: one dim block, never grows
    box(img, cam, -2.2, -1.7, 0, 0.1, -0.3, 0.3, (40, 40, 48), (30, 30, 36), (28, 28, 32), edge=(70, 70, 80))
    floor_light(img, cam, (0.6, 0.05, 0.0), 0.15 + 0.7 * nb / 8, k=0.2)
    phase = s * 0.7
    hx = 0.6 + 0.3 * math.sin(phase) if t < PAYOFF else 0.6
    hp = T.ARMS_UP if t >= PAYOFF + 0.1 else (T.walk(s * 5.0, 24) if (t < PAYOFF and math.cos(phase) > 0.55 or t < PAYOFF and math.cos(phase) < -0.55) else T.HOLD)
    people = [(np.array([hx, 0, 0.0], np.float32), hp, "hero", "happy" if t > PAYOFF else "determined", None),
              (np.array([-1.2, 0, 0.0], np.float32), T.PHONE, "mustard", "tired", "phone")]
    for P, ps, look, ex, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, ps, look, ex, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (0.6, 0.8, 0.0))
    img = compose(img, emis)
    def ov(d):
        clock = 6 * 60 + int(min(960, max(0, (s - 1.6) * 60)))
        if t < 1.6:
            a = int(255 * min(1, (1.6 - t) / 0.3)); spaced(d, (W / 2, 520), "SAME 24 HOURS.", 62, (a, a, a), sp=9)
        elif t < PAYOFF:
            spaced(d, (W / 2, 520), f"{clock // 60:02d}:{clock % 60:02d}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
        else:
            a = ease((t - PAYOFF - 0.1) / 0.5) if t > PAYOFF + 0.1 else 0.0
            spaced(d, (W / 2, 520), "USE THEM.", 72, tuple(int(c * a) for c in (255, 205, 130)), sp=12)
        for t0, t1, pt, text, gold in ((0.2, 1.4, np.array([-1.2, 2.1, 0.0], np.float32), "five more minutes.", False),
                                       (2.6, 4.0, np.array([-1.2, 2.1, 0.0], np.float32), "5H 40M.", False),
                                       (4.2, 5.6, np.array([0.6, 2.35, 0.0], np.float32), "8 FOCUSED HOURS.".lower(), True),
                                       (6.2, 7.5, np.array([-1.2, 2.1, 0.0], np.float32), "where did today go?", False)):
            if t0 <= t < t1:
                p = cam.proj(pt)
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.6, "whoosh", 0.6)] + [(1.8 + k * 0.5, "tick", 0.3) for k in range(8)] + [(5.6, "whoosh", 0.4), (7.0, "hit", 0.3)]
BLUR = (1.6, 5.6)
MOOD = "night"
CTA = "Comment 'use them' to start today."
CAPTION = """Same 24 hours as everyone else. The habit that changes is where they go

Nobody has more time than you. Some people just decide where it goes before the day starts.

Comment 'use them' to start today.

#motivation #mindset #discipline #habits #selfimprovement"""
