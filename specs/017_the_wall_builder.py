"""017 — TOON3D · WALL · discipline (focus): 20 minutes a day. He lays one brick per day; his wall grows in the x4 speed-up, the scroller's stays one brick."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 8.8, 7.5
COLS, ROWS, BW, BH = 5, 4, 0.5, 0.3
NB = COLS * ROWS
WX0, WZ = 0.15, 1.0
def st(t): return t if t < 3.2 else (3.2 + 4 * (t - 3.2) if t < 5.6 else 12.8 + (t - 5.6))
def tplace(k): return 1.0 + k * 0.55
def nplaced(s): return max(0, min(NB, int((s - 1.0) / 0.55) + 1))

def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-1.0, 0.3, k), lerp(1.8, 2.1, k), lerp(-5.4, -5.0, k)), (lerp(0.0, 0.4, k), 1.05, 1.0))
    k = ease((t - PAYOFF) / 1.3)
    return Cam((lerp(0.3, 0.2, k), lerp(2.1, 3.4, k), lerp(-5.0, -8.8, k)), (lerp(0.4, 0.2, k), lerp(1.05, 1.5, k), 1.0))

def brick_xyz(k, s):
    r, c = divmod(k, COLS)
    x = WX0 + c * BW + (BW / 2 if r % 2 else 0); y = r * BH
    u = min(1.0, (s - tplace(k)) / 0.2)
    return x, y + (1 - u) * (1 - u) * 0.9, u

def frame(t, sub):
    s = st(t + sub)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    n = nplaced(s)
    for k in reversed(range(NB)):
        if k >= n: continue
        x, y, u = brick_xyz(k, s)
        gold = glow > 0.2
        top = (150, 118, 66) if gold else (66, 62, 58)
        box(img, cam, x - BW / 2 + 0.02, x + BW / 2 - 0.02, y, y + BH - 0.03, WZ - 0.25, WZ + 0.25, top, (44, 42, 44) if not gold else (120, 92, 52), (36, 36, 40),
            edge=(130, 104, 62), emis=emis if (k == n - 1 or gold) else None, ecol=(255, 170, 60))
    # the scroller's own wall: one brick, never grows
    box(img, cam, -2.65, -2.15, 0, BH - 0.03, 0.9, 1.4, (48, 48, 54), (34, 34, 40), (30, 30, 36), edge=(70, 72, 82))
    # hero
    hx = WX0 - 0.9
    if t >= PAYOFF + 0.1: hp, ex = T.ARMS_UP, "happy"
    else:
        ph = (s - 1.0) % 0.55
        hp, ex = (T.HOLD if (n < NB and ph < 0.3) else T.STAND), "determined"
    if n >= NB and t < PAYOFF: hp = T.STAND
    people = [(np.array([hx, 0, 0.3], np.float32), hp, "hero", ex, None),
              (np.array([-1.9, 0, 0.9], np.float32), T.SIT_SAD if s > 11 else T.SIT, "grey", "tired", "phone")]
    heads = []
    for P, pose, look, ex_, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, pose, look, ex_, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (1.4, 0.8, 1.0))
    img = compose(img, emis)
    day = 1 + int(59 * n / NB)
    def ov(d):
        if t < 1.4:
            a = int(255 * min(1, (1.4 - t) / 0.3)); spaced(d, (W / 2, 520), "20 MINUTES. DAILY.", 56, (a, a, a), sp=8)
        elif 3.2 <= t < 5.9:
            spaced(d, (W / 2, 520), f"DAY {day}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "BRICK BY BRICK.", 60, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for t0, t1, pt, text, gold in ((1.5, 2.7, np.array([hx, 2.35, 0.3], np.float32), "just 20.", True),
                                       (1.9, 3.0, np.array([-1.9, 1.6, 0.9], np.float32), "later.", False),
                                       (6.0, 7.2, np.array([-1.9, 1.6, 0.9], np.float32), "still later.", False)):
            if t0 <= t < t1:
                p = cam.proj(pt)
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "hit", 0.4), (1.5, "thud", 0.3), (2.0, "thud", 0.3), (2.6, "thud", 0.3), (3.2, "whoosh", 0.6)] + \
         [(3.4 + k * 0.4, "thud", 0.3) for k in range(5)] + [(5.6, "whoosh", 0.4), (6.2, "thud", 0.4)]
BLUR = (3.2, 5.6)
MOOD = "hopeful"
CTA = "Save this for the hard days."
CAPTION = """Discipline is twenty focused minutes a day, not one heroic weekend

Nobody sees the first bricks. They're still the whole wall.

Save this for the hard days.

#discipline #focus #consistency #motivation #habits"""

if __name__ == "__main__":
    if sys.argv[1] == "--stills": stills("previews/017_the_wall_builder", frame, [0.0, 1.6, 2.6, 4.2, 5.8, 7.6, 8.6])
    else: render(sys.argv[1], frame, DUR, PAYOFF, SOUNDS, blur=BLUR, mood=MOOD)
