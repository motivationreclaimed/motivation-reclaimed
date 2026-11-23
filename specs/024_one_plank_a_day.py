"""024 — GOLD3D · BRIDGE · discipline (small daily action): a gap too wide to jump. Others stare or pace; he lays one plank a day (x4), then runs across into the light."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 9.2, 7.8
G0, G1, NP = 1.0, 5.0, 8
PL = (G1 - G0) / NP
def nplanks(t):
    if t < 1.0: return 0
    if t < 3.2: return min(3, 1 + int((t - 1.0) / 0.9))
    return min(NP, 3 + int((t - 3.2) / 0.44)) if t < 5.5 else NP
def hero_x(t, n):
    if t < 5.7: return G0 + PL * n - 0.35
    if t < 7.3: return (G1 - 0.35) + 2.0 * ease((t - 5.7) / 1.6)
    return G1 + 1.65
def camera(t, hx):
    if t < PAYOFF: return Cam((hx - 1.6, 1.7, -5.8), (hx + 1.4, 1.0, 0.0))
    k = ease((t - PAYOFF) / 1.2); c = camera(PAYOFF - 0.01, hx)
    return Cam((lerp(c.C[0], c.C[0] + 0.8, k), lerp(1.7, 2.5, k), lerp(-5.8, -8.4, k)), (hx + 1.0, 1.1, 0.0))

def frame(t, sub):
    tt = t + sub
    n = nplanks(tt); hx = hero_x(tt, n)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    far = 0.2 + 0.6 * n / NP
    cam = camera(t, hx)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow + 0.2 * far)
    quad(img, cam, [(G0, 0.01, -1.0), (G1, 0.01, -1.0), (G1, 0.01, 1.0), (G0, 0.01, 1.0)], (2, 2, 3))
    floor_light(img, cam, (G1 + 1.6, 0.05, 0.0), far, k=0.22)
    for i in reversed(range(n)):
        x0 = G0 + i * PL
        fresh = (i == n - 1 and tt < 5.5)
        box(img, cam, x0, x0 + PL - 0.03, 0.0, 0.14, -0.7, 0.7, (120, 96, 60), (70, 56, 38), (60, 48, 32), edge=(214, 170, 72),
            emis=emis if fresh else None, ecol=(255, 170, 60))
    if t >= PAYOFF + 0.1: hp = mix(STAND, ARMS_V, ease((t - PAYOFF) / 0.5))
    elif 5.7 <= t < 7.3: hp = dict(pose_run(t * 7.5), lean=12)
    elif n < NP or t < 5.7:
        k = 0.5 - 0.5 * math.cos(tt * 2 * math.pi / 0.9)
        hp = mix(STAND, dict(STAND, uaL=120, faL=135, uaR=120, faR=135, lean=10), k)
    else: hp = STAND
    JH = joints(hx, 0.0, hp)
    figs = [(JH, True)]
    pace = -1.0 + 0.35 * math.sin(t * 0.9)
    figs.append((joints(pace, -1.1, pose_phone_walk(t * 6.0) if True else STAND, facing=1 if math.cos(t * 0.9) > 0 else -1), False))
    figs.append((joints(-0.3, 1.4, PHONE_STAND), False))
    for J, hero in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow)
    aura(emis, cam, JH, glow); floor_light(img, cam, (hx, 0.05, 0), glow)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, 0, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.5:
            a = int(255 * min(1, (1.5 - t) / 0.3)); spaced(d, (W / 2, 520), "THE GAP LOOKS TOO WIDE.", 46, (a, a, a), sp=6)
        elif 3.2 <= t < 5.7:
            spaced(d, (W / 2, 520), f"DAY {1 + int(59 * n / NP)}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
        elif t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "ONE PLANK A DAY.", 60, tuple(int(c * a) for c in (255, 205, 130)), sp=8)
        for t0, t1, J, text, gold in ((0.2, 1.3, figs[2][0], "too far.", False), (1.9, 3.0, JH, "just one.", True), (2.2, 3.2, figs[1][0], "no way across.", False)):
            if t0 <= t < t1:
                p = cam.proj(J["head"] + np.array([0, 0.7, 0], np.float32))
                if p and 80 < p[0] < W - 80: tag(d, p[0], p[1], text, gold)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "thud", 0.5), (1.9, "thud", 0.5), (2.8, "thud", 0.5), (3.2, "whoosh", 0.6)] + \
         [(3.4 + k * 0.44, "thud", 0.35) for k in range(5)] + [(5.5, "whoosh", 0.4)] + [(5.9 + k * 0.35, "step", 0.3) for k in range(4)]
BLUR = (3.2, 5.5)
MOOD = "hopeful"
CTA = "Comment 'plank' and lay one today."
CAPTION = """You don't jump the gap. You build across it, one small plank a day

Nobody believed in the bridge at plank two. It's still how every bridge gets built.

Comment 'plank' and lay one today.

#discipline #consistency #motivation #mindset #habits"""
