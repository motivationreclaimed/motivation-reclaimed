"""027 — TOON3D · REVERSE · discipline (failing is part of the count): opens on the gold success (ATTEMPT 47), REWINDs, a fast montage of fails with FAIL stamps, then the final attempt at normal speed -> PASS -> gold PAYOFF."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *
from engine3d import toon as T

DUR, PAYOFF = 9.2, 7.9
LH = 1.1                                   # ledge height
X0, XEDGE, XTOP = -1.2, 1.0, 2.5

def ok_anim(u):                            # the successful jump, u in 0..1 -> (x, y, pose, expr)
    if u < 0.4:
        v = u / 0.4; return X0 + (0.9 - X0) * v, 0.0, T.run(v * 9.0), "determined"
    if u < 0.72:
        v = (u - 0.4) / 0.32
        return 0.9 + 1.6 * ease(v), LH * ease(v) + 0.45 * math.sin(math.pi * v), T.ARMS_UP if 0.35 < v < 0.9 else T.run(v * 9), "determined"
    return XTOP, LH, T.STAND, "happy"
def fail_anim(u):
    if u < 0.55:
        v = u / 0.55; return X0 + (XEDGE - 0.15 - X0) * v, 0.0, T.run(v * 7.0), "worried"
    return XEDGE - 0.15, 0.0, T.SIT_SAD, "sad"

def state(t):
    """-> (x, y, pose, expr, counter_text, mode)"""
    if t < 1.5: x, y, p, e = ok_anim(1.0); return x, y, p, e, "ATTEMPT 47", "top"
    if t < 2.4:
        u = (t - 1.5) / 0.9; x, y, p, e = ok_anim(1 - u); return x, y, p, e, f"ATTEMPT {max(1, 47 - int(46 * u))}", "rewind"
    if t < 5.6:
        loc = (t - 2.4) % 0.4; n = 1 + int(45 * (t - 2.4) / 3.2)
        x, y, p, e = fail_anim(loc / 0.4); return x, y, p, e, f"ATTEMPT {n}", "fail" if loc > 0.22 else "run"
    if t < 7.6:
        x, y, p, e = ok_anim((t - 5.6) / 2.0); return x, y, p, e, "ATTEMPT 47", "last"
    return XTOP, LH, (T.ARMS_UP if t >= PAYOFF + 0.1 else T.STAND), "happy", "ATTEMPT 47", "top"

def camera(t):
    if t < PAYOFF: return Cam((lerp(0.2, 0.7, t / PAYOFF), 1.7, -6.2), (1.0, 0.95, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(0.7, 1.2, k), lerp(1.7, 2.8, k), lerp(-6.2, -9.0, k)), (1.4, 1.1, 0.0))

def frame(t, sub):
    tt = t + sub
    x, y, pose, expr, ctext, mode = state(tt)
    glow = 0.45 if (t < 1.5) else (ease((t - PAYOFF) / 0.6) if t > PAYOFF else (0.5 if t > 7.4 else 0.0))
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    box(img, cam, XEDGE, XTOP + 2.0, 0, LH, -0.9, 0.9, (66, 62, 56), (34, 34, 40), (30, 30, 36), edge=(120, 100, 66),
        emis=emis if glow > 0.2 else None, ecol=(150, 100, 40))
    floor_light(img, cam, (XEDGE - 0.4, 0.05, 0.0), 0.15 + 0.5 * glow, k=0.2)
    people = [(np.array([x, y, 0.0], np.float32), pose, "hero", expr, None),
              (np.array([-2.3, 0, 2.0], np.float32), T.PHONE, "grey", "tired", "phone"),
              (np.array([-1.7, 0, 2.6], np.float32), T.PHONE, "teal", "tired", "phone")]
    for P, ps, look, ex, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        draw_toon(img, emis, cam, P, ps, look, ex, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    if t > PAYOFF: sparks(emis, cam, t, PAYOFF, (XTOP, LH + 0.8, 0.0))
    img = compose(img, emis)
    if mode == "rewind": g = img.mean(2, keepdims=True); img = g + (img - g) * 0.3
    def ov(d):
        if t < 1.5:
            a = int(255 * min(1, (1.5 - t) / 0.3)); spaced(d, (W / 2, 520), "NOBODY SAW ATTEMPT 1.", 48, (a, a, a), sp=6)
            spaced(d, (W / 2, 590), ctext, 34, (214, 170, 72), sp=8)
        elif t < 7.6 and t >= 1.5:
            col = (214, 170, 72) if mode in ("last",) else (240, 240, 244)
            spaced(d, (W / 2, 520), ctext, 64, col, sp=9)
            if mode == "rewind":
                for dx in (-34, 6):
                    d.polygon([(W / 2 + dx + 28, 590), (W / 2 + dx + 28, 640), (W / 2 + dx, 615)], fill=(200, 200, 205))
            if mode == "fail": spaced(d, (W / 2, 600), "FAIL", 34, (150, 150, 160), sp=10)
            if t >= 7.35: spaced(d, (W / 2, 600), "PASS", 40, (255, 205, 130), sp=12)
        elif t >= 7.6:
            if t >= PAYOFF + 0.1:
                a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "IT'S PART OF THE COUNT.", 46, tuple(int(c * a) for c in (255, 205, 130)), sp=7)
            else: spaced(d, (W / 2, 520), "ATTEMPT 47", 64, (214, 170, 72), sp=9); spaced(d, (W / 2, 600), "PASS", 40, (255, 205, 130), sp=12)
        if 0.2 <= t < 1.3:
            p = cam.proj(np.array([x, y + 2.3, 0.0], np.float32))
            if p: tag(d, p[0], p[1], "47th try.", True)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.5, "whoosh", 0.6)] + [(2.4 + k * 0.4 + 0.24, "thud", 0.3) for k in range(8)] + [(5.6, "whoosh", 0.4), (6.1, "step", 0.3), (6.4, "step", 0.3), (6.7, "step", 0.3), (7.3, "hit", 0.5)]
BLUR = (2.4, 5.6)
MOOD = "tense"
CTA = "Comment your attempt number."
CAPTION = """Nobody sees attempt 1 to 46. They only see the jump on 47

Failing is part of the count. It always was. I just stopped quitting at 12.

Comment your attempt number.

#mindset #consistency #nevergiveup #motivation #discipline"""
