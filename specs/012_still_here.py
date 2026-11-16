"""3D sample 3 — THE GYM: January, everyone's here. One by one they quit; he's still lifting."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine3d.r3d import *

DUR, PAYOFF = 8.9, 7.6
def st(t): return t if t < 3.0 else (3.0 + 4 * (t - 3.0) if t < 5.6 else 13.4 + (t - 5.6))

SQ_UP = dict(hip=0.95, lean=4, thL=4, shL=4, thR=-4, shR=-4, uaL=-40, faL=150, uaR=-40, faR=150, head=-4)
SQ_DN = dict(hip=0.56, lean=36, thL=80, shL=-14, thR=78, shR=-14, uaL=-30, faL=160, uaR=-30, faR=160, head=-20)
PRESS = dict(SQ_UP, uaL=178, faL=178, uaR=178, faR=178, head=-10, lean=-2)
def squat(ph): return mix(SQ_UP, SQ_DN, (1 - math.cos(ph)) / 2)

# greys: x, z, scene-time they quit, what they say
GREYS = [(-2.2, 1.2, 2.2, "this is too hard."), (2.3, 1.4, 6.5, ""), (-3.6, 3.0, 9.5, ""), (3.7, 2.9, 13.6, "monday.")]
MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL"]

def camera(t):
    k = ease(t / DUR); a = lerp(-1.05, -0.62, k)
    R = lerp(7.4, 5.0, ease((t - 6.8) / 3.0)) if t > 6.8 else 7.4
    y = lerp(1.9, 1.35, ease((t - 6.8) / 3.0)) if t > 6.8 else 1.9
    return Cam((R * math.sin(a), y, -R * math.cos(a)), (0.0, 1.05, 0.9))

def frame(t, sub):
    s = st(t + sub)
    glow = ease((t - PAYOFF) / 0.6) if t > PAYOFF else 0.0
    cam = camera(t)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img)
    room(img, cam, 0.3 * glow)
    for x0 in (-4.5, 0.0, 4.5):                                    # lifting platforms
        box(img, cam, x0 - 1.4, x0 + 1.4, 0, 0.04, -1.0 + (0 if x0 == 0 else 1.8), 1.0 + (0 if x0 == 0 else 1.8),
            (26, 26, 31), (20, 20, 24), (22, 22, 26), edge=(60, 60, 68))
    figs = []
    # hero: squats, then at the end presses the bar overhead
    if s < 1.0: hp = SQ_UP
    elif t < 7.2: hp = squat((s - 1.0) * 4.4)
    else: hp = mix(SQ_UP, PRESS, ease((t - 7.2) / 0.4))
    JH = joints(0.0, 0.0, hp, facing=-1)
    figs.append((JH, True, 1.0, True))
    for k, (gx, gz, tq, _) in enumerate(GREYS):
        if s < tq:
            J = joints(gx, gz, squat((s - 1.0) * 4.0 + k * 1.3) if s > 1.0 else SQ_UP, facing=-1); figs.append((J, False, 1.0, True))
        else:                                                          # quits: walks off, bar left on the floor
            u = s - tq; a = max(0.0, 1 - u / 1.6)
            if a > 0: figs.append((joints(gx - u * 1.3, gz + u * 0.4, pose_phone_walk(u * 6), facing=-1), False, a, False))
            figs.append(({"hL": np.array([gx, 0.22, gz], np.float32), "hR": np.array([gx, 0.22, gz], np.float32), "hip": np.array([gx, 0.2, gz], np.float32)}, None, 1.0, True))
    for J, hero, a, bar in sorted(figs, key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
        if hero is not None: draw_figure(img, emis, cam, J, hero=hero, warm=0.6 * glow, alpha=a)
        if bar: barbell(img, emis, cam, J, gold=bool(hero), alpha=a)
    aura(emis, cam, JH, glow); floor_light(img, cam, (0, 0.05, 0), glow)
    if glow > 0: sparks(emis, cam, t, PAYOFF, (0, 0, 0))
    img = compose(img, emis)
    reps = int(max(0.0, min(st(7.2), s) - 1.0) * 24)          # running total (12 sets a week)
    def ov(d):
        if t < 1.3:
            a = int(255 * min(1, (1.3 - t) / 0.3)); spaced(d, (W / 2, 520), "JANUARY. EVERYONE'S HERE.", 48, (a, a, a), sp=6)
        elif t < PAYOFF:
            m = MONTHS[min(3, int(max(0, s - 1.0) / 3.6))]
            spaced(d, (W / 2, 520), m, 70, (240, 240, 244), sp=10)
            if 3.0 <= t < 5.6: spaced(d, (W / 2, 585), "× 4", 30, (150, 150, 160), sp=6)
        else:
            a = ease((t - PAYOFF - 0.1) / 0.5); spaced(d, (W / 2, 520), "STILL HERE.", 70, tuple(int(c * a) for c in (255, 205, 130)), sp=10)
        p = cam.proj(JH["head"] + np.array([0, 0.5, 0], np.float32))
        if p and t > 1.0: spaced(d, (p[0], p[1] - 30), f"REPS {reps}", 34, (255, 205, 130), sp=5)
        for k, (gx, gz, tq, text) in enumerate(GREYS):
            if text and tq - 1.0 <= s < tq + 0.3 and (t < 3.0 or t >= 5.6):
                q = cam.proj(np.array([gx, 2.0, gz], np.float32))
                if q: tag(d, q[0], q[1], text, False)
        if 1.6 <= t < 2.6:
            q = cam.proj(JH["head"] + np.array([0, 1.0, 0], np.float32))
            if q: tag(d, q[0], q[1], "one more.", True)
        chrome(d, t, "Send this to your gym partner.", PAYOFF)
    return img, ov

SOUNDS = [(0.6, "tick", 0.3), (1.0, "hit", 0.4), (1.7, "thud", 0.35), (2.3, "thud", 0.5), (2.9, "whoosh", 0.6)] + \
         [(3.2 + k * 0.5, "thud", 0.3) for k in range(5)] + [(5.6, "whoosh", 0.4), (5.85, "thud", 0.5), (6.4, "step", 0.3), (6.8, "step", 0.3), (7.2, "hit", 0.4)]

BLUR = (3.0, 5.6)
CAPTION = """January gym vs April gym: who's still there? (gym motivation)

I didn't get stronger in January. I got stronger in the months nobody posts about.

Send this to your gym partner.

#gymmotivation #discipline #habits #mindset"""
CTA = 'Send this to your gym partner.'

if __name__ == "__main__":
    if sys.argv[1] == "--stills": stills("previews/012_still_here", frame, [0.7, 1.9, 3.8, 5.0, 6.1, 7.4, 9.0])
    else: render(sys.argv[1], frame, DUR, PAYOFF, SOUNDS, blur=(3.0, 5.6))
