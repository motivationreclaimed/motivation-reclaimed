"""028 — GOLD3D · DESK · discipline (deep work): he sits at the desk for one focused block; people drift past with their phones and try to pull him away; he stays; bar fills; stands in gold. Slow camera orbit, no speed-up."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 9.0, 7.6
SEATED = dict(SIT, lean=6, head=4, uaL=32, faL=82, uaR=32, faR=82)
def camera(t):
    if t < PAYOFF:
        k = t / PAYOFF
        return Cam((lerp(-3.2, -1.0, k), lerp(1.5, 1.8, k), lerp(-4.6, -5.4, k)), (0.3, 0.8, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(-1.0, 0.4, k), lerp(1.8, 2.7, k), lerp(-5.4, -8.2, k)), (0.3, 0.9, 0.0))

PASS = [(0.2, 1, 4.5, 6.0, "quick look?"), (3.0, -1, 5.0, 6.0, "one reel."), (5.0, 1, 4.2, 7.0, "five minutes?")]    # start t, dir, z, speed, tag
def passer(k, t):
    t0, d, z, sp, _ = PASS[k]
    u = t - t0
    if u < 0 or u > 2.8: return None
    x = -3.2 + 2.1 * u if d > 0 else 3.2 - 2.1 * u
    return x, z, d

def frame(t, sub):
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    f = min(1.0, t / 7.4)
    room(img, cam, 0.3 * glow + 0.12)
    # chair, desk, laptop glow
    box(img, cam, -0.65, -0.05, 0, 0.4, -0.3, 0.3, (40, 40, 46), (28, 28, 34), (26, 26, 30), edge=(80, 72, 56))
    box(img, cam, 0.4, 1.1, 0, 0.72, -0.55, 0.55, (52, 48, 44), (32, 30, 30), (30, 28, 28), edge=(110, 92, 60))
    box(img, cam, 0.6, 0.9, 0.72, 0.74 + 0.2, -0.22, 0.22, (214, 170, 72), (120, 96, 50), (110, 88, 46), edge=(255, 210, 120), emis=emis, ecol=(255, 170, 60))
    floor_light(img, cam, (0.5, 0.05, 0.0), 0.35 + 0.5 * f, k=0.2)
    sit = t < PAYOFF - 0.3
    hp = SEATED if sit else mix(SEATED, STAND, ease((t - PAYOFF + 0.3) / 0.4))
    if t >= PAYOFF + 0.1: hp = mix(STAND, ARMS_V, ease((t - PAYOFF) / 0.5))
    hx = -0.35
    JH = joints(hx, 0.0, hp)
    if sit: JH = {k: v + np.array([0, 0.0, 0], np.float32) for k, v in JH.items()}
    figs = [(JH, True)]
    for k in range(3):
        q = passer(k, t)
        if q: figs.append((joints(q[0], q[1], pose_phone_walk(t * 6.5 + k), facing=q[2]), False))
    for J, hero in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow)
    aura(emis, cam, JH, max(glow, 0.15 + 0.2 * f)); floor_light(img, cam, (hx, 0.05, 0), glow)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, 0, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.5:
            a = int(255 * min(1, (1.5 - t) / 0.3)); spaced(d, (W / 2, 520), "ONE HOUR. NO PHONE.", 52, (a, a, a), sp=7)
        elif t < PAYOFF:
            mins = max(0, 60 - int(60 * f))
            spaced(d, (W / 2, 520), f"{mins:02d}:00", 78, (240, 240, 244), sp=10)
            d.rectangle([W / 2 - 200, 590, W / 2 + 200, 600], outline=(90, 90, 96)); d.rectangle([W / 2 - 200, 590, W / 2 - 200 + 400 * f, 600], fill=(214, 170, 72))
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "DEEP WORK. DONE.", 58, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for k in range(3):
            q = passer(k, t)
            if q and 0.9 < t - PASS[k][0] < 2.1:
                p = cam.proj(np.array([q[0], 2.0, q[1]], np.float32))
                if p and 120 < p[0] < W - 120: tag(d, p[0], p[1], PASS[k][4], False)
        if 2.4 <= t < 3.6:
            p = cam.proj(JH["head"] + np.array([0, 0.6, 0], np.float32))
            if p: tag(d, p[0], p[1], "not now.", True)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.2, "hit", 0.3), (3.4, "hit", 0.4), (4.6, "tick", 0.3), (5.9, "hit", 0.3), (6.5, "tick", 0.3)]
MOOD = "warm"
CTA = "Which hour will you protect? Comment below."
CAPTION = """One protected hour a day beats a whole day of half focus

I put the phone in another room and told no one. The first ten minutes are the hardest, then it gets quiet.

Which hour will you protect?

#focus #discipline #productivity #mindset #selfimprovement"""
