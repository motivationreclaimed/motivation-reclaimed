"""TEMPLATE (owner-approved): 3D gold world + cartoon cast — CLIMB (stairs). Copy to specs/NNN_slug.py and rewrite the story.
Cartoon people are drawn with draw_toon(img, emis, cam, feet_xyz, pose, look, expr, facing, prop, glow, bright)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 10.0, 7.6
N, RUN, RISE = 20, 0.45, 0.2
TOPX = N * RUN

def st(t):                      # scene time with x4 speed-up
    return t if t < 3.6 else (3.6 + 4 * (t - 3.6) if t < 5.6 else 11.6 + (t - 5.6))
def hero_x(s): return min(TOPX + 0.6, max(0.0, (s - 1.3) * 0.77)) - 0.3
def h_at(x): return 0.0 if x < 0 else min(N, int(x / RUN) + 1) * RISE
def h_smooth(x): return min(N * RISE, max(0.0, (x + 0.2) / RUN * RISE))
def lift(J, dy): return {k: v + np.array([0, dy, 0], np.float32) for k, v in J.items()}

GREYS = [(-2.9, -0.7), (-2.3, 1.2), (-3.5, 2.5)]          # sitting at the bottom (x, z)

def _cam_unused(): pass
def camera(t, hx, hy):
    def follow(x, y): return (x - 4.2, y + 1.7, -5.2), (x + 1.4, y + 0.7, 0.0)
    if t < 1.3:
        k = ease(t / 1.3); c, g = follow(-0.6, 0)
        return Cam((c[0] - 2.5 * (1 - k), c[1] + 0.8 * (1 - k), c[2] - 2 * (1 - k)), g)
    if t < 7.4: return Cam(*follow(hx, hy))
    k = ease((t - 7.4) / 2.4); c, g = follow(hx, hy)
    return Cam((lerp(c[0], 0.5, k), lerp(c[1], 4.6, k), lerp(c[2], -13.0, k)), (lerp(g[0], 4.2, k), lerp(g[1], 2.2, k), 0.0))

def frame(t, sub):
    s = st(t + sub); hx = hero_x(s); hy = h_smooth(hx)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t, hx, hy)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    lit = int((hx + 0.3) / RUN) + 1
    wave = (t - PAYOFF) / 1.2 * N if t > PAYOFF else -1
    for i in reversed(range(N)):                          # far steps first
        on = i < lit; g = i <= wave
        top = (70, 64, 56) if on else (38, 39, 45); front = (24, 24, 28); side = (30, 30, 35)
        if g: top = (150, 120, 70)
        box(img, cam, i * RUN, (i + 1) * RUN if i < N - 1 else TOPX + 2.5, 0, (i + 1) * RISE, -0.75, 0.75, top, front, side,
            edge=(110, 92, 60) if on else (55, 56, 64), emis=emis if (on or g) else None,
            ecol=(255, 170, 60) if g else (90, 60, 20))
    # hero
    if s < 1.3: hp = STAND
    elif hx < TOPX + 0.25: hp = dict(pose_run(s * 9.0), lean=20, hip=0.9)
    elif t < PAYOFF: hp = STAND
    else: hp = mix(STAND, ARMS_V, ease((t - PAYOFF) / 0.5))
    JH = lift(joints(hx, 0.0, hp), hy)
    figs = [(JH, True)]
    from engine3d import toon as T
    from engine3d.r3d import draw_toon
    if s < 1.3: th = T.STAND
    elif hx < TOPX + 0.25: th = T.walk(s * 9.0, 34)
    elif t < PAYOFF: th = T.STAND
    else: th = T.ARMS_UP if t > PAYOFF + 0.15 else T.STAND
    people = [(np.array([hx, hy, 0.0], np.float32), th, "hero", "happy" if t > PAYOFF else "determined", None)]
    looks = ["grey", "teal", "coral"]
    for k, (gx, gz) in enumerate(GREYS):
        if k == 1 and 1.6 <= s:
            x = min(-2.3 + (s - 1.6) * 1.1, 3 * RUN - 0.2)
            if x < 3 * RUN - 0.2: people.append((np.array([x, h_smooth(x), gz], np.float32), T.walk(s * 7, 30), looks[k], "worried", None))
            else: people.append((np.array([x, 3 * RISE, gz], np.float32), T.SIT_SAD, looks[k], "sad", None))
        else:
            people.append((np.array([gx, 0, gz], np.float32), T.PHONE if k != 0 else T.SIT, looks[k], "tired", "phone"))
    P_ = {}
    for P, pose, look, expr, prop in sorted(people, key=lambda q: -cam.depth(q[0] + np.array([0, 1, 0], np.float32))):
        P_[look] = draw_toon(img, emis, cam, P, pose, look, expr, 1, prop=prop, glow=glow if look == "hero" else 0, bright=1.0 if look == "hero" else 0.85)
    figs = [(JH, True)] + [(lift(joints(P[0], P[2], SIT), P[1]), False) for P, *_ in people[1:]]
    if glow > 0: sparks(emis, cam, t, PAYOFF, (hx, hy, 0))
    img = compose(img, emis)
    def ov(d):
        if t < 1.4:
            a = int(255 * min(1, (1.4 - t) / 0.3)); spaced(d, (W / 2, 520), "EVERYONE WANTS THE TOP.", 50, (a, a, a), sp=7)
        if 3.6 <= t < 5.8:
            spaced(d, (W / 2, 520), f"DAY {8 + int(192 * min(1, (t - 3.6) / 2.0))}", 84, (240, 240, 244), sp=10)
            spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
        if t >= PAYOFF + 0.1:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "ONE STEP A DAY.", 64, tuple(int(c * a) for c in (255, 205, 130)), sp=9)
        for t0, t1, J, text, gold in (
                                      (2.0, 3.1, JH, "one more.", True), (3.0, 3.6, figs[2][0], "too steep.", False)):
            if t0 <= t < t1:
                p = cam.proj(J["head"] + np.array([0, 0.75, 0], np.float32))
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, "Save this for the hard days.", PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.3, "hit", 0.45)] + [(1.3 + k * 0.45, "step", 0.35) for k in range(5)] + \
         [(3.5, "whoosh", 0.6)] + [(3.7 + k * 0.4, "tick", 0.3) for k in range(5)] + [(5.6, "whoosh", 0.4)] + \
         [(5.7 + k * 0.45, "step", 0.4) for k in range(4)]

BLUR = (3.6, 5.6)
CAPTION = """One step a day is how anyone reaches the top (discipline & consistency)

Everyone wants the view. Almost nobody wants step 4 on a Tuesday.

Which step are you on right now?

#discipline #consistency #selfimprovement #motivation"""
CTA = 'Save this for the hard days.'

if __name__ == "__main__":
    if sys.argv[1] == "--stills": stills("previews/011_one_step_a_day", frame, [0.7, 2.4, 3.3, 4.6, 6.6, 8.0, 9.5])
    else: render(sys.argv[1], frame, DUR, PAYOFF, SOUNDS, blur=(3.6, 5.6))
