"""023 — TOON3D · DOOR · discipline (starting): the 5-minute rule. Everyone hesitates outside; he opens the door, goes in for just five minutes (x4 countdown), stays."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 9.2, 7.8
DX = 3.0                                   # door plane x
def st(t): return t if t < 3.4 else (3.4 + 4 * (t - 3.4) if t < 5.6 else 12.2 + (t - 5.6))
def open_k(t): return ease((t - 1.5) / 0.7)
def hero_x(t):
    if t < 2.0: return -0.4
    if t < 3.4: return -0.4 + 4.4 * ease((t - 2.0) / 1.4)
    return 4.0

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-2.0, 0.3, k), lerp(1.8, 2.0, k), -5.6), (lerp(1.2, 2.5, k), 1.05, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(0.3, 1.0, k), lerp(2.0, 3.0, k), lerp(-5.6, -9.0, k)), (2.6, lerp(1.05, 1.4, k), 0.0))

def frame(t, sub):
    s = st(t + sub)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    ok = open_k(t)
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow + 0.3 * ok)
    # light behind the door
    box(img, cam, DX + 1.3, DX + 1.4, 0, 2.5, -1.0, 1.0, (120, 92, 52), (190, 150, 80), (120, 92, 52), edge=(255, 190, 90), emis=emis, ecol=(255, 175, 70))
    # frame: jambs + lintel
    stone = ((48, 48, 56), (34, 34, 40), (30, 30, 36))
    box(img, cam, DX, DX + 0.3, 0, 2.3, -0.8, -0.6, *stone, edge=(110, 92, 60))
    box(img, cam, DX, DX + 0.3, 0, 2.3, 0.6, 0.8, *stone, edge=(110, 92, 60))
    box(img, cam, DX, DX + 0.3, 2.1, 2.4, -0.8, 0.8, *stone, edge=(110, 92, 60))
    # leaf slides away along z
    z0 = lerp(-0.6, 0.35, ok)
    box(img, cam, DX + 0.05, DX + 0.2, 0, 2.1, z0, 0.6, (40, 40, 48), (28, 28, 34), (26, 26, 30), edge=(120, 100, 66), emis=emis if ok > 0.1 else None, ecol=(150, 100, 40))
    floor_light(img, cam, (DX + 0.8, 0.05, 0.0), 0.15 + 0.7 * ok, k=0.22)
    hx = hero_x(t)
    walking = 2.0 <= t < 3.4
    if t >= PAYOFF + 0.1: hp, ex = T.ARMS_UP, "happy"
    elif walking: hp, ex = T.walk(t * 9.0, 34), "determined"
    elif t >= 3.4: hp, ex = (T.HOLD if int(s * 1.1) % 2 else T.STAND), "determined"
    else: hp, ex = T.STAND, "worried"
    people = [(np.array([hx, 0, 0.0], np.float32), hp, "hero", ex, None),
              (np.array([-0.9, 0, 1.0], np.float32), T.PHONE, "grey", "tired", "phone"),
              (np.array([1.0, 0, 1.5], np.float32), T.PHONE, "coral", "tired", "phone")]
    for P, pose, look, ex_, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, pose, look, ex_, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, 0.8, 0.0))
    img = compose(img, emis)
    rem = max(0.0, 300 * (1 - (s - 3.4) / (12.2 - 3.4)))
    def ov(d):
        if t < 1.4:
            a = int(255 * min(1, (1.4 - t) / 0.3)); spaced(d, (W / 2, 520), "JUST FIVE MINUTES.", 54, (a, a, a), sp=8)
        elif 3.4 <= t < 5.8:
            spaced(d, (W / 2, 520), f"{int(rem // 60)}:{int(rem % 60):02d}", 90, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 592), "× 4", 30, (150, 150, 160), sp=6)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "START FOR FIVE.", 62, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for t0, t1, pt, text, gold in ((0.0, 1.0, np.array([-0.9, 2.0, 1.0], np.float32), "tomorrow.", False),
                                       (1.0, 2.1, np.array([-0.4, 2.35, 0.0], np.float32), "just five.", True),
                                       (1.2, 2.2, np.array([1.0, 2.0, 1.5], np.float32), "not in the mood.", False),
                                       (6.0, 7.3, np.array([-0.9, 2.0, 1.0], np.float32), "still outside.", False),
                                       (6.2, 7.5, np.array([4.0, 2.35, 0.0], np.float32), "one more set.", True)):
            if t0 <= t < t1:
                p = cam.proj(pt)
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "hit", 0.4), (1.6, "whoosh", 0.4), (2.2, "step", 0.3), (2.6, "step", 0.3), (3.0, "step", 0.3), (3.4, "whoosh", 0.6)] + \
         [(3.6 + k * 0.45, "tick", 0.3) for k in range(5)] + [(5.6, "whoosh", 0.4), (6.4, "hit", 0.3)]
BLUR = (3.4, 5.6)
MOOD = "hopeful"
CTA = "Comment 'five' and start now."
CAPTION = """The 5-minute rule: start for five minutes, then decide (habits)

The hardest part is the door, not the work. Five minutes in, you usually stay.

Comment 'five' and start now.

#habits #discipline #selfdiscipline #focus #motivation"""
