"""3D sample 2 — THE STAIRS: everyone wants the top. Steps he climbs light up gold."""
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

GREYS = [(-1.6, -1.2), (-2.3, 0.3), (-1.4, 1.5)]          # sitting at the bottom (x, z)

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
    # greys: sitting with phones; one tries, climbs 3 steps, sits down on step 3
    for k, (gx, gz) in enumerate(GREYS):
        if k == 1 and 1.6 <= s:
            x = min(-2.3 + (s - 1.6) * 1.1, 3 * RUN - 0.2)
            if x < 3 * RUN - 0.2: J = lift(joints(x, gz, dict(pose_run(s * 7), lean=16, hip=0.9)), h_smooth(x))
            else: J = lift(joints(x, gz, SIT), 3 * RISE - 0.05)
        else:
            J = joints(gx, gz, SIT)
        figs.append((J, False))
    for J, hero in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow)
        if not hero:
            p = cam.proj((J["hL"] + J["hR"]) / 2)
            if p:
                cv2.rectangle(img, (int(p[0]) - 4, int(p[1]) - 7), (int(p[0]) + 4, int(p[1]) + 7), (170, 200, 255), -1)
                blob(emis, p[0], p[1] - 8, 26, 26, (60, 110, 255), 0.8)
    aura(emis, cam, JH, glow); floor_light(img, cam, (hx, hy, 0), glow)
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
        for t0, t1, J, text, gold in ((1.5, 2.6, figs[3][0] if len(figs) > 3 else JH, "maybe monday.", False),
                                      (2.0, 3.1, JH, "one more.", True), (3.0, 3.6, figs[2][0], "too steep.", False)):
            if t0 <= t < t1:
                p = cam.proj(J["head"] + np.array([0, 0.75, 0], np.float32))
                if p: tag(d, p[0], p[1], text, gold)
        chrome(d, t, "Save this for the hard days.", PAYOFF)
    return img, ov

SOUNDS = [(0.5, "tick", 0.3), (1.3, "hit", 0.45)] + [(1.3 + k * 0.45, "step", 0.35) for k in range(5)] + \
         [(3.5, "whoosh", 0.6)] + [(3.7 + k * 0.4, "tick", 0.3) for k in range(5)] + [(5.6, "whoosh", 0.4)] + \
         [(5.7 + k * 0.45, "step", 0.4) for k in range(4)]

if __name__ == "__main__":
    if sys.argv[1] == "--stills": stills("/tmp/s3d/stairs", frame, [0.7, 2.4, 3.3, 4.6, 6.6, 8.0, 9.5])
    else: render(sys.argv[1], frame, DUR, PAYOFF, SOUNDS, blur=(3.6, 5.6))
