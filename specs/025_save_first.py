"""025 — TOON3D · JAR/PILE · MONEY (save first): payday. He puts a coin in the jar first; the scroller orders instead. MONTH counter x4: jar fills to £1,200, parcels pile up, nothing left."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 9.4, 8.0
def st(t): return t if t < 3.0 else (3.0 + 4 * (t - 3.0) if t < 5.6 else 13.4 + (t - 5.6))
def month(s): return max(0, min(12, int((s - 0.8) / 1.0)))
JX = (0.1, 0.8)

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-0.9, 0.3, k), lerp(1.6, 1.9, k), lerp(-5.2, -5.8, k)), (0.9, 1.0, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(0.3, 0.9, k), lerp(1.9, 3.0, k), lerp(-5.8, -9.0, k)), (0.9, 1.1, 0.0))

def frame(t, sub):
    s = st(t + sub); m = month(s)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow + 0.1 * m / 12)
    # parcel pile (his rival's)
    for i in range(m):
        c, lv = i % 2, i // 2
        box(img, cam, 2.7 + c * 0.45, 3.1 + c * 0.45, lv * 0.27, (lv + 1) * 0.27 - 0.02, -0.25, 0.2, (92, 72, 52), (66, 52, 38), (56, 44, 32), edge=(120, 100, 76))
    # the jar and its gold fill
    box(img, cam, JX[0], JX[1], 0, 1.0, -0.35, 0.35, (30, 30, 36), (22, 22, 28), (20, 20, 26), edge=(150, 130, 90))
    if m > 0:
        fh = 0.92 * m / 12
        box(img, cam, JX[0] + 0.04, JX[1] - 0.04, 0.02, fh, -0.31, 0.31, (214, 170, 72), (170, 128, 44), (150, 112, 40), edge=(255, 210, 120), emis=emis, ecol=(255, 170, 60))
    floor_light(img, cam, (0.45, 0.05, 0.0), 0.1 + 0.8 * m / 12, k=0.2)
    pose_h = T.ARMS_UP if t >= PAYOFF + 0.1 else (T.HOLD if (s % 1.0) < 0.5 and s < 13.4 else T.STAND)
    people = [(np.array([-0.7, 0, 0.0], np.float32), pose_h, "hero", "happy" if t > PAYOFF else "determined", None),
              (np.array([1.9, 0, 0.3], np.float32), T.PHONE, "coral", "tired", "phone")]
    for P, pose, look, ex, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, pose, look, ex, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (0.45, 0.8, 0.0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.5:
            a = int(255 * min(1, (1.5 - t) / 0.3)); spaced(d, (W / 2, 520), "PAYDAY. WHAT FIRST?", 52, (a, a, a), sp=7)
        elif 3.0 <= t < 5.8:
            spaced(d, (W / 2, 520), f"MONTH {max(1, m)}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), f"SAVED £{m * 100:,}", 32, (214, 170, 72), sp=6)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "SAVE FIRST.", 70, tuple(int(c * a) for c in (255, 205, 130)), sp=10)
        for t0, t1, pt, text, gold in ((0.3, 1.5, np.array([1.9, 2.1, 0.3], np.float32), "one more order.", False),
                                       (1.5, 2.8, np.array([-0.7, 2.35, 0.0], np.float32), "jar first.", True),
                                       (6.1, 7.5, np.array([1.9, 2.1, 0.3], np.float32), "what's left?", False)):
            if t0 <= t < t1:
                p = cam.proj(pt)
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (0.9, "hit", 0.4), (1.9, "hit", 0.4), (3.0, "whoosh", 0.6)] + [(3.2 + k * 0.2, "tick", 0.3) for k in range(10)] + [(5.6, "whoosh", 0.4)]
BLUR = (3.0, 5.6)
MOOD = "hopeful"
CTA = "Save this for payday."
CAPTION = """Pay yourself first. The simplest money habit I know

I used to save what was left on the 30th. There was never anything left. Now the jar gets filled before anything else.

Save this for payday.

#moneyhabits #saving #personalfinance #discipline #habits"""
