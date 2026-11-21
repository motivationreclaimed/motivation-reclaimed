"""019 — GOLD3D · CROWD · discipline (phone/screen time): everyone walks the same way, heads down. He looks up, turns, walks the other way. No speed-up."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 9.0, 7.8
SPEED = 1.15
CROWD = [(-5.5, 1.4), (-4.2, 2.4), (-3.0, 1.6), (-1.9, 2.8), (-0.6, 1.5), (0.5, 2.6), (1.4, 1.5), (2.8, 2.3), (4.0, 1.6), (5.2, 2.9), (-6.6, 2.0), (6.4, 2.2)]
TURN, GO = 2.4, 3.1

def hero_state(t):
    if t < TURN: return SPEED * t, 1, "walk"
    x0 = SPEED * TURN
    if t < GO: return x0, 1, "look"
    u = t - GO
    if t < PAYOFF - 0.6: return x0 - 1.25 * u, -1, "walkback"
    return x0 - 1.25 * (PAYOFF - 0.6 - GO), 1, "end"

def camera(t):
    hx = hero_state(t)[0]
    if t < PAYOFF:
        return Cam((hx * 0.8 + 0.4, 1.7, -5.6 + 0.6 * math.sin(t * 0.3)), (hx * 0.85 + 0.2, 1.05, 0.2))
    k = ease((t - PAYOFF) / 1.2); c = camera(PAYOFF - 0.01)
    return Cam((lerp(c.C[0], c.C[0] + 0.5, k), lerp(1.7, 2.6, k), lerp(-5.6, -8.2, k)), (c.C[0] + 0.2, 1.1, 0.2))

def frame(t, sub):
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    hx, hf, mode = hero_state(t)
    if mode == "walk": hp = pose_phone_walk(t * 7.2)
    elif mode == "look": hp = mix(PHONE_STAND, STAND, ease((t - TURN) / 0.4))
    elif mode == "walkback": hp = dict(pose_run(t * 7.0), lean=8, hip=0.95, head=-4)
    else: hp = mix(STAND, ARMS_V, ease((t - PAYOFF) / 0.5)) if t > PAYOFF else STAND
    JH = joints(hx, 0.0, hp, facing=hf)
    figs = [(JH, True, 1.0)]
    for k, (x0, z) in enumerate(CROWD):
        x = x0 + SPEED * t
        if x > 7.5: x -= 13.0
        figs.append((joints(x, z, pose_phone_walk(t * 7.2 + k * 1.7), facing=1), False, 1.0))
    for J, hero, a in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow, alpha=a)
    aura(emis, cam, JH, glow); floor_light(img, cam, (hx, 0.05, 0), glow)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, 0, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.5:
            a = int(255 * min(1, (1.5 - t) / 0.3)); spaced(d, (W / 2, 520), "EVERYONE'S LOOKING DOWN.", 44, (a, a, a), sp=6)
        if t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "EYES UP.", 76, tuple(int(c * a) for c in (255, 205, 130)), sp=12)
        if 0.9 <= t < 2.1:
            q = cam.proj(np.array([CROWD[3][0] + SPEED * t, 2.1, CROWD[3][1]], np.float32))
            if q: tag(d, q[0], q[1], "one more scroll.", False)
        if TURN + 0.2 <= t < TURN + 1.3:
            q = cam.proj(JH["head"] + np.array([0, 0.6, 0], np.float32))
            if q: tag(d, q[0], q[1], "wait.", True)
        if 4.2 <= t < 5.6:
            q = cam.proj(JH["head"] + np.array([0, 0.6, 0], np.float32))
            if q: tag(d, q[0], q[1], "eyes up.", True)
        chrome(d, t, CTA, PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.0, "tick", 0.3), (1.5, "tick", 0.3), (TURN, "hit", 0.45), (TURN + 0.1, "whoosh", 0.4), (3.1, "thud", 0.3)] + \
         [(3.2 + k * 0.5, "step", 0.3) for k in range(8)]
MOOD = "night"
CTA = "Comment 'eyes up' if this is you."
CAPTION = """Eyes up for one hour a day. Phone down, focus up (self improvement)

I counted how many people on my commute never looked up once. Then I counted myself.

#selfimprovement #focus #mindset #habits #discipline"""
