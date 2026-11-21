"""021 — GOLD3D · WALL · discipline (comeback / persistence): one walks away, one waits for a sign, he chips at the wall a little every day (x4 speed-up), then walks through into the light."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 9.4, 8.0
WX, WT = 2.1, 0.5                    # wall x, thickness
COLS, ROWS, CW, RH = 5, 5, 0.62, 0.42
HOLE = [(c, r) for r in range(3) for c in (1, 2, 3)] + [(2, 3), (2, 4)]       # bricks he removes, in order
HOLE.sort(key=lambda q: (q[1], q[0]))
def st(t): return t if t < 3.0 else (3.0 + 4 * (t - 3.0) if t < 5.4 else 12.6 + (t - 5.4))
def hit_time(k): return 1.0 + k * 1.05
def removed(s): return max(0, min(len(HOLE), int((s - 1.0) / 1.05)))
def hero_x(t):
    if t < 6.0: return 0.9
    return 0.9 + 3.0 * ease((t - 6.0) / 1.9)

def camera(t):
    if t < PAYOFF:
        return Cam((lerp(-2.0, -0.6, t / PAYOFF), 1.7, -5.8), (lerp(1.0, 1.9, t / PAYOFF), 1.05, 0.0))
    k = ease((t - PAYOFF) / 1.2)
    return Cam((lerp(-0.6, 0.6, k), lerp(1.7, 2.4, k), lerp(-5.8, -8.0, k)), (2.4, 1.2, 0.0))

def frame(t, sub):
    s = st(t + sub)
    n = removed(s)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    leak = 0.15 + 0.6 * n / len(HOLE)
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow + 0.25 * leak)
    gone = set(HOLE[:n])
    for r in range(ROWS):
        for c in range(COLS):
            if (c, r) in gone: continue
            z0 = (c - COLS / 2) * CW
            box(img, cam, WX, WX + WT, r * RH, (r + 1) * RH - 0.03, z0 + 0.02, z0 + CW - 0.02, (58, 56, 54), (40, 40, 44), (34, 34, 38),
                edge=(100, 90, 74))
    # light behind the wall, leaking through the hole
    floor_light(img, cam, (WX + 1.5, 0.05, 0.0), leak, k=0.2)
    figs = []
    hx = hero_x(t)
    if t >= PAYOFF + 0.1: hp = mix(STAND, ARMS_V, ease((t - PAYOFF) / 0.5))
    elif t >= 6.0: hp = mix(STAND, pose_run(t * 6.0), 0.55)
    elif n < len(HOLE):
        k = 0.5 - 0.5 * math.cos((s - 1.0) * 2 * math.pi / 1.05)
        hp = mix(STAND, dict(STAND, uaL=125, faL=140, uaR=125, faR=140, lean=8), k)
    else: hp = STAND
    JH = joints(hx, 0.0, hp)
    figs.append((JH, True, 1.0))
    # one walks away
    u = max(0.0, t - 1.0)
    ax = -0.3 - 1.8 * u
    if t < 3.4: figs.append((joints(ax, -0.9, pose_phone_walk(t * 6.5) if t > 1.0 else PHONE_STAND, facing=1 if t < 1.0 else -1), False, max(0.0, 1 - u / 1.5)))
    # one sits and waits
    figs.append((joints(-1.7, 1.4, SIT), False, 1.0))
    for J, hero, a in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow, alpha=a)
    aura(emis, cam, JH, glow); floor_light(img, cam, (hx, 0.05, 0), glow)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, 0, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.4:
            a = int(255 * min(1, (1.4 - t) / 0.3)); spaced(d, (W / 2, 520), "THREE FACE THE WALL.", 50, (a, a, a), sp=7)
        elif 3.0 <= t < 5.6:
            spaced(d, (W / 2, 520), f"DAY {1 + int(59 * n / len(HOLE))}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "A LITTLE EVERY DAY.", 56, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for t0, t1, J, text, gold in ((1.2, 2.3, joints(ax, -0.9, STAND), "too hard.", False), (2.0, 3.0, JH, "one more.", True), (0.1, 1.2, joints(-1.7, 1.4, SIT), "wait for a sign.", False),
                                      (6.2, 7.4, joints(-1.7, 1.4, SIT), "still waiting.", False)):
            if t0 <= t < t1:
                p = cam.proj(J["head"] + np.array([0, 0.7, 0], np.float32))
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "thud", 0.5), (2.05, "thud", 0.5), (3.0, "whoosh", 0.6)] + [(3.2 + k * 0.28, "thud", 0.35) for k in range(8)] + \
         [(5.4, "whoosh", 0.4), (6.4, "step", 0.3), (6.9, "step", 0.3), (7.4, "step", 0.3)]
BLUR = (3.0, 5.4)
MOOD = "tense"
CTA = "Save this for when it feels impossible."
CAPTION = """Persistence looks boring until the wall finally breaks (mindset)

I stopped asking how big the wall was. I only asked what I could chip off today.

Save this for when it feels impossible.

#mindset #discipline #mentalstrength #nevergiveup #motivation"""
